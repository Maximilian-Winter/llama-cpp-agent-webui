import asyncio
import json
from typing import List

from llama_cpp import Llama, LlamaCache
from sse_starlette import EventSourceResponse
from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import copy

from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse

from pydantic import BaseModel

from llama_cpp_agent.llm_agent import LlamaCppAgent
from llama_cpp_agent.providers.llama_cpp_endpoint_provider import LlamaCppEndpointSettings
from llama_cpp_agent.messages_formatter import MessagesFormatterType

main_model = LlamaCppEndpointSettings(completions_endpoint_url="http://127.0.0.1:8080/completion")
wrapped_model = LlamaCppAgent(main_model, debug_output=True,
                              system_prompt="You are an helpful AI assistant.",
                              predefined_messages_formatter_type=MessagesFormatterType.CHATML, )
settings_dict = {}


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


class GenerationRequest(BaseModel):
    messages: List[dict]
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
    return templates.TemplateResponse("../src/index.html", {"request": request})


# Serve files
@app.get("/{name_file}")
def get_file(name_file: str):
    if os.path.exists(path=os.getcwd() + "../static/" + name_file):
        return FileResponse(path=os.getcwd() + "../static/" + name_file)
    else:
        print("File: " + name_file + "doesn't exist!")


@app.post("/llama/complete")
async def complete_llama(request: Request, generationRequest: GenerationRequest):
    global settings_dict, wrapped_model
    wrapped_model.messages = generationRequest.messages
    settings_dict = generationRequest.settings.model_dump()
    settings_dict["n_predict"] = settings_dict.pop("max_tokens")
    settings_dict["tfs_z"] = settings_dict.pop("tfsz")
    settings_dict["repeat_last_n"] = settings_dict.pop("rep_pen_range")
    settings_dict["repeat_penalty"] = settings_dict.pop("rep_pen")
    settings_dict["typical_p"] = settings_dict.pop("typ_p")
    return {"session_id": "1234"}


@app.get("/llama/stream")
async def stream_llama(request: Request):
    global settings_dict, wrapped_model

    async def async_generator():
        for item in wrapped_model.get_chat_response_generator(penalize_nl=False, yield_streaming_responses=True, **settings_dict):
            yield item

    async def server_sent_events():
        async for item in async_generator():
            if await request.is_disconnected():
                break

            result = copy.deepcopy(item)
            text = result

            yield {"data": text}

    return EventSourceResponse(server_sent_events())


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(app, host=os.getenv("HOST", "localhost"), port=os.getenv("PORT", 8000))
