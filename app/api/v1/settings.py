from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.response import Response
from app.models.Setting import get_all_settings, update_setting
from app.schema.settings import SettingUpdateDTO

router = APIRouter()

@router.get('')
async def index(request: Request, db: AsyncSession = Depends(get_db),):
    items = await get_all_settings(db)
    return Response.code(200, 'T-GBS-00901').send(data=items)


@router.post('')
async def store(request: Request):
    ...

@router.patch('/{id}')
async def update(id: int, body: SettingUpdateDTO, db: AsyncSession = Depends(get_db)):
    is_updated = await update_setting(db, id, body)
    if is_updated:
        return Response.code(200, 'S-GBS-11111').send_message('Updated successfully')
    else:
        return Response.code(400, 'B-GBS-00000').send_message('Update failed')

@router.delete('/{id}')
async def destroy(request: Request):
    ...
