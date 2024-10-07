from typing import Optional, List

import fastapi
from fastapi import HTTPException
from pydantic import BaseModel

from template_database import TemplateManager, TemplateType

template_api_router = fastapi.APIRouter()
template_manager = TemplateManager()


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


# Template endpoints
@template_api_router.post("/templates/", response_model=TemplateResponse)
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


@template_api_router.get("/templates/{template_id}", response_model=TemplateResponse)
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


@template_api_router.get("/templates/", response_model=List[TemplateResponse])
def get_all_templates():
    templates = template_manager.get_all_templates()
    return [TemplateResponse(
        id=template.id,
        template_type=template.template_type,
        template_name=template.template_name,
        content=template.content
    ) for template in templates]


@template_api_router.get("/templates/type/{template_type}", response_model=List[TemplateResponse])
def get_templates_by_type(template_type: TemplateType):
    templates = template_manager.get_all_templates_filtered_by_type(template_type)
    return [TemplateResponse(
        id=template.id,
        template_type=template.template_type,
        template_name=template.template_name,
        content=template.content
    ) for template in templates]


@template_api_router.put("/templates/{template_id}", response_model=TemplateResponse)
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


@template_api_router.delete("/templates/{template_id}")
def delete_template(template_id: int):
    if template_manager.delete_template(template_id):
        return {"message": "Template deleted successfully"}
    raise HTTPException(status_code=404, detail="Template not found")


# Template Set endpoints
@template_api_router.post("/template-sets/", response_model=TemplateSetResponse)
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


@template_api_router.get("/template-sets/{template_set_id}", response_model=TemplateSetResponse)
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


@template_api_router.get("/template-sets/", response_model=List[TemplateSetResponse])
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


@template_api_router.put("/template-sets/{template_set_id}", response_model=TemplateSetResponse)
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


@template_api_router.delete("/template-sets/{template_set_id}")
def delete_template_set(template_set_id: int):
    if template_manager.delete_template_set(template_set_id):
        return {"message": "Template set deleted successfully"}
    raise HTTPException(status_code=404, detail="Template set not found")
