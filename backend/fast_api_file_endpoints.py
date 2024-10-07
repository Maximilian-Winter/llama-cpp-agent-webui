import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from file_database import FileManager

file_db = FileManager()
file_api_router = fastapi.APIRouter()


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


@file_api_router.post("/files/", response_model=FileResponseDatabase)
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


@file_api_router.get("/files/{file_id}", response_model=FileResponseDatabase)
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


@file_api_router.post("/files/path/", response_model=FileResponseDatabase)
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


@file_api_router.put("/files/{file_id}", response_model=FileResponseDatabase)
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


@file_api_router.delete("/files/{file_id}")
def delete_file(file_id: int):
    try:
        file_db.delete_file(file_id)
        return {"message": "File deleted successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@file_api_router.get("/files/", response_model=List[FileResponseDatabase])
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


@file_api_router.get("/file-paths/", response_model=List[FilePathResponseDatabase])
def list_file_paths():
    files = file_db.get_all_file_paths()
    return [
        FilePathResponseDatabase(
            id=file.id,
            path=file.path,
        )
        for file in files
    ]
