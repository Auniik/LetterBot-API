from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import Response
from app.models.PromptTemplate import get_all_prompt_templates, get_prompt_template, save_prompt_template, \
    update_prompt_template, delete_prompt_template
from app.schema.prompt_template import PromptTemplateDTO

router = APIRouter()


@router.get('')
async def index(db: AsyncSession = Depends(get_db)):
    items = await get_all_prompt_templates(db)
    return Response.code(200).send(data=items)


@router.get('/{id}')
async def show(id: int, db: AsyncSession = Depends(get_db)):
    item = await get_prompt_template(db, id)
    if not item:
        return Response.code(404).send_message(message="Prompt template not found")
    return Response.code(200).send(data=item)


@router.post('')
async def store(body: PromptTemplateDTO, db: AsyncSession = Depends(get_db)):
    is_saved = await save_prompt_template(db, body)
    if not is_saved:
        return Response.code(400).send_message(message="Failed to save prompt template")
    return Response.code(201).send_message(message="Prompt template saved successfully")


@router.patch('/{id}')
async def update(id: int, body: PromptTemplateDTO, db: AsyncSession = Depends(get_db)):
    is_updated = await update_prompt_template(db, id, body)
    if not is_updated:
        return Response.code(404).send_message(message="Prompt template not found")
    return Response.code(200).send_message(message="Prompt template updated successfully")


@router.delete('/{id}')
async def destroy(id: int, db: AsyncSession = Depends(get_db)):
    is_deleted = await delete_prompt_template(db, id)
    if not is_deleted:
        return Response.code(404).send_message(message="Prompt template not found")
    return Response.code(200).send_message(message="Prompt template deleted successfully")
