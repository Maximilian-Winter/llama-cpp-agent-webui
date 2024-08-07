import asyncio
import json
import os
from typing import List, Optional

from dotenv import load_dotenv
from sse_starlette import EventSourceResponse
from fastapi import FastAPI, Request, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import copy

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse

from pydantic import BaseModel

from ToolAgents.agents import MistralAgent, ChatAPIAgent
from ToolAgents.provider import LlamaCppSamplingSettings, LlamaCppServerProvider, OpenAIChatAPI, OpenAISettings
from ToolAgents.utilities import ChatHistory

from chat_database import ChatDatabase

load_dotenv()

# provider = LlamaCppServerProvider(server_address="http://127.0.0.1:8080")
# mistral_agent = MistralAgent(llm_provider=provider, debug_output=True)
# llm_sampling_settings = LlamaCppSamplingSettings()

provider = OpenAIChatAPI(api_key=os.getenv("API_KEY"), base_url="https://openrouter.ai/api/v1", model="meta-llama/llama-3.1-405b-instruct")
mistral_agent = ChatAPIAgent(chat_api=provider, debug_output=True)
llm_sampling_settings = OpenAISettings()

chat_history = ChatHistory()
db = ChatDatabase()


# Pydantic models for validation
class AgentCreate(BaseModel):
    name: str
    description: str
    instructions: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None


class ChatCreate(BaseModel):
    title: str
    agent_id: int


class MessageCreate(BaseModel):
    chat_id: int
    role: str
    content: str


class MessageEdit(BaseModel):
    id: int
    content: str


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    instructions: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    chat_id: int
    timestamp: str


class Message(BaseModel):
    id: int
    role: str
    content: str
    timestamp: str


class Settings(BaseModel):
    max_tokens: int
    temperature: float
    top_p: float
    top_k: int
    min_p: float
    typ_p: float
    tfsz: float
    rep_pen: float
    rep_pen_range: int


class ChatResponse(BaseModel):
    id: int
    title: str
    timestamp: str
    agent: AgentResponse
    messages: List[MessageResponse]
    settings: Settings


class GenerationRequest(BaseModel):
    chat_id: int
    agent_id: int
    messages: List[Message]
    settings: Settings


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def llama(request: Request):
    return {"error": "File not found!"}
    # return templates.TemplateResponse("../src/a.html", {"request": request})


# Serve files
@app.get("/{name_file}")
def get_file(name_file: str):
    if os.path.exists(path=os.getcwd() + "../static/" + name_file):
        return FileResponse(path=os.getcwd() + "../static/" + name_file)
    else:
        print("File: " + name_file + "doesn't exist!")
    return {"error": "File not found!"}


@app.post("/llama/complete")
async def complete_llama(request: Request, generationRequest: GenerationRequest):
    chat_id = generationRequest.chat_id
    if chat_id == -1:
        chat_id = db.add_chat_with_agent_id("New Chat", agent_id=generationRequest.agent_id)
        db.add_or_update_chat_settings(chat_id, generationRequest.settings.model_dump())
    else:
        db.add_or_update_chat_settings(chat_id, generationRequest.settings.model_dump())
    messages_ids = []
    global llm_sampling_settings, mistral_agent, chat_history
    chat_history = ChatHistory()
    agent = db.get_agent_by_id(generationRequest.agent_id)
    system_message = agent.instructions

    chat_history.add_system_message(system_message)

    for message in generationRequest.messages:
        if message.id == -1:
            message_id, _ = db.add_message(chat_id, message.role, message.content)
        else:
            message_id = message.id
        if message.role != "system":
            chat_history.add_message(message.role, message.content)
        messages_ids.append(message_id)

    settings_dict = generationRequest.settings.model_dump()
    llm_sampling_settings.max_tokens = settings_dict["max_tokens"]
    llm_sampling_settings.temperature = settings_dict["temperature"]
    llm_sampling_settings.top_p = settings_dict["top_p"]
    # llm_sampling_settings.typical_p = settings_dict["typ_p"]
    # llm_sampling_settings.min_p = settings_dict["min_p"]
    # llm_sampling_settings.top_k = settings_dict["top_k"]
    # llm_sampling_settings.repeat_penalty = settings_dict["rep_pen"]
    # llm_sampling_settings.repeat_penalty_range = settings_dict["rep_pen_range"]
    # llm_sampling_settings.tfs_z = settings_dict["tfsz"]

    return {"chat_id": chat_id, "messages": messages_ids}


@app.get("/llama/stream")
async def stream_llama(request: Request):
    global llm_sampling_settings, mistral_agent, chat_history

    async def async_generator():
        for item in mistral_agent.get_streaming_response(
                messages=chat_history.to_list(),
                settings=llm_sampling_settings):
            yield item

    async def server_sent_events():
        async for item in async_generator():
            if await request.is_disconnected():
                break

            result = copy.deepcopy(item)
            text = result

            yield {"data": text}
        yield {"data": "GENERATION_STOPPED"}

    return EventSourceResponse(server_sent_events())


# Endpoints
@app.post("/agents/", response_model=AgentResponse)
def create_agent(agent: AgentCreate):
    agent_id = db.add_agent(agent.name, agent.description, agent.instructions)
    if agent_id:
        return {"id": agent_id, "name": agent.name, "description": agent.description,
                "instructions": agent.instructions}
    raise HTTPException(status_code=400, detail="Failed to create agent.")


@app.put("/agents/{agent_id}")
def update_agent(agent_id: int, agent: AgentUpdate):
    db.update_agent(agent_id, agent.name, agent.description, agent.instructions)
    return {"message": "Agent updated successfully."}


@app.delete("/agents/{agent_id}")
def delete_agent(agent_id: int):
    db.delete_agent(agent_id)
    return {"message": "Agent deleted successfully."}


@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: int):
    db.delete_chat(chat_id)
    return {"message": "Chat deleted successfully."}


@app.delete("/messages/{message_id}")
def delete_message(message_id: int):
    if db.delete_message(message_id):
        return {"message": "Message deleted successfully."}
    raise HTTPException(status_code=404, detail="Message not found.")


@app.post("/chats/", response_model=ChatResponse)
def create_chat(chat: ChatCreate):
    chat_id = db.add_chat_with_agent_id(chat.title, chat.agent_id)
    if chat_id:
        return db.get_chat_details(chat_id)  # Assuming you implement a method to fetch chat details
    raise HTTPException(status_code=400, detail="Failed to create chat.")


@app.post("/messages/", response_model=MessageResponse)
def create_message(message: MessageCreate):
    message_id, timestamp = db.add_message(message.chat_id, message.role, message.content)
    if message_id:
        return {"id": message_id, "chat_id": message.chat_id, "role": message.role, "content": message.content,
                "timestamp": timestamp.strftime("%d/%m/%Y %H:%M:%S")}
    raise HTTPException(status_code=400, detail="Failed to add message.")


@app.put("/messages/")
def edit_message(message: MessageEdit):
    if db.edit_message(message.id, message.content):
        return {"message": "Successfully edited message."}
    raise HTTPException(status_code=400, detail="Failed to add message.")


@app.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int):
    chat = db.get_chat_details(chat_id)
    if chat:
        return chat
    raise HTTPException(status_code=404, detail="Chat not found.")


@app.put("/chats/{chat_id}/settings")
def update_chat_settings(chat_id: int, settings: Settings):
    db.add_or_update_chat_settings(chat_id, settings.model_dump())
    return {"message": "Chat settings updated successfully."}


@app.put("/chats/{chat_id}/{title}")
def get_chat(chat_id: int, title: str):
    result = db.set_chat_title(chat_id, title)  # You need to implement this method in ChatDatabase
    if result:
        return {"message": "Title changed successfully."}
    raise HTTPException(status_code=404, detail="Chat not found.")


# Fetch all agents
@app.get("/agents/", response_model=List[AgentResponse])
def get_all_agents():
    agents = db.get_all_agents()
    return [{"id": agent.id, "name": agent.name, "description": agent.description, "instructions": agent.instructions}
            for agent in agents]


# Fetch all chats
@app.get("/chats/", response_model=List[ChatResponse])
def get_all_chats():
    chats = db.get_all_chats()
    # Assuming you extend get_all_chats to include agent and messages or adjust here accordingly
    return [db.get_chat_details(chat.id) for chat in chats]


# Search chats by title
@app.get("/chats/search/", response_model=List[ChatResponse])
def search_chats(title: str):
    chats = db.search_chats_by_title(title)
    return [{
        "id": chat.id,
        "title": chat.title,
        "agent": {
            "id": chat.agent.id,
            "name": chat.agent.name,
            "instructions": chat.agent.instructions
        } if chat.agent else None,
        "messages": [{
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
            "chat_id": chat.id
        } for message in chat.messages]
    } for chat in chats]


# Fetch all messages from a specific chat
@app.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
def get_chat_messages(chat_id: int):
    messages = db.get_all_messages_from_chat(chat_id)
    return [{
        "id": message.id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
        "chat_id": chat_id
    } for message in messages]


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "localhost"), port=os.getenv("PORT", 8042))
