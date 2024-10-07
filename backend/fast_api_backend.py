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
from file_database import FileManager
from template_database import TemplateManager, TemplateType

load_dotenv()

# provider = LlamaCppServerProvider(server_address="http://127.0.0.1:8080")
# mistral_agent = MistralAgent(llm_provider=provider, debug_output=True)
# llm_sampling_settings = LlamaCppSamplingSettings()

provider = OpenAIChatAPI(api_key=os.getenv("API_KEY"), base_url="https://openrouter.ai/api/v1",
                         model="meta-llama/llama-3.1-405b-instruct")
mistral_agent = ChatAPIAgent(chat_api=provider, debug_output=True)
llm_sampling_settings = OpenAISettings()

chat_history = ChatHistory()


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


class FileCreate(BaseModel):
    path: str
    content: str


class FileUpdate(BaseModel):
    content: str


class FileResponseDatabase(BaseModel):
    id: int
    path: str
    filename: str
    content: str
    created_at: str
    updated_at: str


class FilePathResponseDatabase(BaseModel):
    id: int
    path: str


class FileFromPathRequest(BaseModel):
    path: str


class TemplateBase(BaseModel):
    template_type: TemplateType
    template_name: str
    content: str


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    template_type: Optional[TemplateType] = None
    template_name: Optional[str] = None
    content: Optional[str] = None


class TemplateResponse(TemplateBase):
    id: int


class TemplateSetBase(BaseModel):
    name: str
    user_message_template_id: int
    rag_user_message_template_id: int
    file_combining_template_id: int
    file_output_template_id: int


class TemplateSetCreate(TemplateSetBase):
    pass


class TemplateSetUpdate(BaseModel):
    name: Optional[str] = None
    user_message_template_id: Optional[int] = None
    rag_user_message_template_id: Optional[int] = None
    file_combining_template_id: Optional[int] = None
    file_output_template_id: Optional[int] = None


class TemplateSetResponse(TemplateSetBase):
    id: int


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
template_manager = TemplateManager()
file_db = FileManager()
db = ChatDatabase()


@app.post("/llama/complete")
async def complete_llama(generationRequest: GenerationRequest):
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
    return [
        {"id": agent.id, "name": agent.name, "description": agent.description, "instructions": agent.instructions}
        for agent in agents]


# Fetch all chats
@app.get("/chats/", response_model=List[ChatResponse])
def get_all_chats():
    chats = db.get_all_chats()
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


@app.post("/files/", response_model=FileResponseDatabase)
def create_file(file: FileCreate):
    try:
        file_id = file_db.add_file(file.path, file.content)
        file_record = file_db.get_file(file_id)
        if file_record:
            return FileResponseDatabase(
                id=file_record.id,
                path=file_record.path,
                filename=file_record.filename,
                content=file_record.content,
                created_at=file_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=file_record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/files/{file_id}", response_model=FileResponseDatabase)
def get_file(file_id: int):
    file_record = file_db.get_file(file_id)
    if file_record:
        return FileResponseDatabase(
            id=file_record.id,
            path=file_record.path,
            filename=file_record.filename,
            content=file_record.content,
            created_at=file_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=file_record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    else:
        raise HTTPException(status_code=404, detail="File not found.")


@app.post("/files/path/", response_model=FileResponseDatabase)
def get_file_by_path(request: FileFromPathRequest):
    file_record = file_db.get_file_by_path(request.path)
    if file_record:
        return FileResponseDatabase(
            id=file_record.id,
            path=file_record.path,
            filename=file_record.filename,
            content=file_record.content,
            created_at=file_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=file_record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    else:
        raise HTTPException(status_code=404, detail="File not found.")


@app.put("/files/{file_id}", response_model=FileResponseDatabase)
def update_file(file_id: int, file: FileUpdate):
    try:
        file_db.update_file(file_id, file.content)
        file_record = file_db.get_file(file_id)
        return FileResponseDatabase(
            id=file_record.id,
            path=file_record.path,
            filename=file_record.filename,
            content=file_record.content,
            created_at=file_record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=file_record.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/files/{file_id}")
def delete_file(file_id: int):
    try:
        file_db.delete_file(file_id)
        return {"message": "File deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/files/", response_model=List[FileResponseDatabase])
def list_files():
    files = file_db.get_all_files()
    return [
        FileResponseDatabase(
            id=file.id,
            path=file.path,
            filename=file.filename,
            content=file.content,
            created_at=file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=file.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        )
        for file in files
    ]


@app.get("/file-paths/", response_model=List[FilePathResponseDatabase])
def list_file_paths():
    files = file_db.get_all_file_paths()
    return [
        FilePathResponseDatabase(
            id=file.id,
            path=file.path,
        )
        for file in files
    ]


# Template endpoints
@app.post("/templates/", response_model=TemplateResponse)
def create_template(template: TemplateCreate):
    try:
        new_template = template_manager.add_template(
            template.template_type,
            template.template_name,
            template.content
        )
        return TemplateResponse(id=new_template.id, **template.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/templates/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int):
    template = template_manager.get_template(template_id)
    if template:
        return TemplateResponse(
            id=template.id,
            template_type=template.template_type,
            template_name=template.template_name,
            content=template.content
        )
    raise HTTPException(status_code=404, detail="Template not found")


@app.get("/templates/", response_model=List[TemplateResponse])
def get_all_templates():
    templates = template_manager.get_all_templates()
    return [TemplateResponse(
        id=template.id,
        template_type=template.template_type,
        template_name=template.template_name,
        content=template.content
    ) for template in templates]


@app.get("/templates/type/{template_type}", response_model=List[TemplateResponse])
def get_templates_by_type(template_type: TemplateType):
    templates = template_manager.get_all_templates_filtered_by_type(template_type)
    return [TemplateResponse(
        id=template.id,
        template_type=template.template_type,
        template_name=template.template_name,
        content=template.content
    ) for template in templates]


@app.put("/templates/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template_update: TemplateUpdate):
    try:
        template_manager.update_template(
            template_id,
            template_type=template_update.template_type,
            template_name=template_update.template_name,
            content=template_update.content
        )
        updated_template = template_manager.get_template(template_id)
        return TemplateResponse(
            id=updated_template.id,
            template_type=updated_template.template_type,
            template_name=updated_template.template_name,
            content=updated_template.content
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/templates/{template_id}")
def delete_template(template_id: int):
    if template_manager.delete_template(template_id):
        return {"message": "Template deleted successfully"}
    raise HTTPException(status_code=404, detail="Template not found")


# Template Set endpoints
@app.post("/template-sets/", response_model=TemplateSetResponse)
def create_template_set(template_set: TemplateSetCreate):
    try:
        new_template_set = template_manager.add_template_set(
            template_set.name,
            template_set.user_message_template_id,
            template_set.rag_user_message_template_id,
            template_set.file_combining_template_id,
            template_set.file_output_template_id
        )
        return TemplateSetResponse(id=new_template_set.id, **template_set.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/template-sets/{template_set_id}", response_model=TemplateSetResponse)
def get_template_set(template_set_id: int):
    template_set = template_manager.get_template_set(template_set_id)
    if template_set:
        return TemplateSetResponse(
            id=template_set.id,
            name=template_set.name,
            user_message_template_id=template_set.user_message_template_id,
            rag_user_message_template_id=template_set.rag_user_message_template_id,
            file_combining_template_id=template_set.file_combining_template_id,
            file_output_template_id=template_set.file_output_template_id
        )
    raise HTTPException(status_code=404, detail="Template set not found")


@app.get("/template-sets/", response_model=List[TemplateSetResponse])
def get_all_template_sets():
    template_sets = template_manager.get_all_template_sets()
    return [TemplateSetResponse(
        id=template_set.id,
        name=template_set.name,
        user_message_template_id=template_set.user_message_template_id,
        rag_user_message_template_id=template_set.rag_user_message_template_id,
        file_combining_template_id=template_set.file_combining_template_id,
        file_output_template_id=template_set.file_output_template_id
    ) for template_set in template_sets]


@app.put("/template-sets/{template_set_id}", response_model=TemplateSetResponse)
def update_template_set(template_set_id: int, template_set_update: TemplateSetUpdate):
    try:
        template_manager.update_template_set(
            template_set_id,
            **template_set_update.model_dump(exclude_unset=True)
        )
        updated_template_set = template_manager.get_template_set(template_set_id)
        return TemplateSetResponse(
            id=updated_template_set.id,
            name=updated_template_set.name,
            user_message_template_id=updated_template_set.user_message_template_id,
            rag_user_message_template_id=updated_template_set.rag_user_message_template_id,
            file_combining_template_id=updated_template_set.file_combining_template_id,
            file_output_template_id=updated_template_set.file_output_template_id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.delete("/template-sets/{template_set_id}")
def delete_template_set(template_set_id: int):
    if template_manager.delete_template_set(template_set_id):
        return {"message": "Template set deleted successfully"}
    raise HTTPException(status_code=404, detail="Template set not found")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": str(exc.detail), "request_body": (await request.body()).decode("utf-8")},
    )


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "localhost"), port=os.getenv("PORT", 8042))
