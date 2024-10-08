from dotenv import load_dotenv

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, JSONResponse

load_dotenv()

from fast_api_chat_agent_endpoints import chat_agent_api_router
from fast_api_file_endpoints import file_api_router
from fast_api_template_endpoints import template_api_router

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_agent_api_router)
app.include_router(file_api_router)
app.include_router(template_api_router)


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
