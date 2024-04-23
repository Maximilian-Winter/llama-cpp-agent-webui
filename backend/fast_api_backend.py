import asyncio
import json
from typing import List, Optional

from llama_cpp import Llama, LlamaCache
from sse_starlette import EventSourceResponse
from fastapi import FastAPI, Request, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import copy

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse

from pydantic import BaseModel

from llama_cpp_agent.llm_agent import LlamaCppAgent
from llama_cpp_agent.providers.llama_cpp_endpoint_provider import LlamaCppEndpointSettings
from llama_cpp_agent.messages_formatter import MessagesFormatterType

from chat_database import ChatDatabase

main_model = LlamaCppEndpointSettings(completions_endpoint_url="http://127.0.0.1:8080/completion")
wrapped_model = LlamaCppAgent(main_model, debug_output=True,
                              system_prompt="",
                              predefined_messages_formatter_type=MessagesFormatterType.NEURAL_CHAT, )
settings_dict = {}
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


class ChatResponse(BaseModel):
    id: int
    title: str
    timestamp: str
    agent: AgentResponse
    messages: List[MessageResponse]


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


class Message(BaseModel):
    id: int
    role: str
    content: str


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
    messages_ids = []
    converted_messages = []

    for message in generationRequest.messages:
        if message.id == -1:
            message_id = db.add_message(chat_id, message.role, message.content)
        else:
            message_id = message.id
        converted_messages.append({"role": message.role, "content": message.content})
        messages_ids.append(message_id)
    global settings_dict, wrapped_model
    agent = db.get_agent_by_id(generationRequest.agent_id)
    system_message = agent.instructions
    wrapped_model.system_prompt = system_message
    wrapped_model.messages = converted_messages
    settings_dict = generationRequest.settings.model_dump()
    settings_dict["n_predict"] = settings_dict.pop("max_tokens")
    settings_dict["tfs_z"] = settings_dict.pop("tfsz")
    settings_dict["repeat_last_n"] = settings_dict.pop("rep_pen_range")
    settings_dict["repeat_penalty"] = settings_dict.pop("rep_pen")
    settings_dict["typical_p"] = settings_dict.pop("typ_p")
    return {"chat_id": chat_id, "messages": messages_ids}


@app.get("/llama/stream")
async def stream_llama(request: Request):
    global settings_dict, wrapped_model

    async def async_generator():
        for item in wrapped_model.get_chat_response_generator(penalize_nl=False,
                                                              **settings_dict):
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
        return {"id": agent_id, "name": agent.name, "instructions": agent.instructions}
    raise HTTPException(status_code=400, detail="Failed to create agent.")


@app.put("/agents/{agent_id}")
def update_agent(agent_id: int, agent: AgentUpdate):
    db.update_agent(agent_id, agent.name, agent.description, agent.instructions)
    return {"message": "Agent updated successfully."}


@app.post("/chats/", response_model=ChatResponse)
def create_chat(chat: ChatCreate):
    chat_id = db.add_chat_with_agent_id(chat.title, chat.agent_id)
    if chat_id:
        return db.get_chat_details(chat_id)  # Assuming you implement a method to fetch chat details
    raise HTTPException(status_code=400, detail="Failed to create chat.")


@app.post("/messages/", response_model=MessageResponse)
def create_message(message: MessageCreate):
    message_id = db.add_message(message.chat_id, message.role, message.content)
    if message_id:
        return {"id": message_id, "chat_id": message.chat_id, "role": message.role, "content": message.content}
    raise HTTPException(status_code=400, detail="Failed to add message.")


@app.get("/chats/{chat_id}", response_model=ChatResponse)
def get_chat(chat_id: int):
    chat = db.get_chat_details(chat_id)  # You need to implement this method in ChatDatabase
    if chat:
        return chat
    raise HTTPException(status_code=404, detail="Chat not found.")


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
    return [{
        "id": chat.id,
        "title": chat.title,
        "timestamp": chat.timestamp.strftime("%m/%d/%Y, %H:%M:%S"),
        "agent": {
            "id": chat.agent.id,
            "name": chat.agent.name,
            "description": chat.agent.description,
            "instructions": chat.agent.instructions
        } if chat.agent else None,
        "messages": [{
            "id": message.id,
            "role": message.role,
            "content": message.content,
            "chat_id": chat.id
        } for message in chat.messages]
    } for chat in chats]


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
        "chat_id": chat_id
    } for message in messages]


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "localhost"), port=os.getenv("PORT", 8000))
