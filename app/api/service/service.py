from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db

router = APIRouter()


@router.post("/test")
async def service(request: Request, db: AsyncSession = Depends(get_db)):
    ...
