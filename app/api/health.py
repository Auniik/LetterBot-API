import requests
from fastapi import APIRouter, Depends, Request
from objprint import objprint
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_redis
from app.core.database import get_db
from app.core.response import Response

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    result = {
        "database": False,
        # "redis": False,
    }
    # r = (await db.execute(text('SELECT true'))).fetchone()
    # result["database"] = r[0]

    # try:
    #     # Check Redis connection
    #     redis_conn = get_redis(0)
    #     result["redis"] = redis_conn.ping()
    # except Exception as e:
    #     print(e)

    return Response.code(200, 'S-GBS-11111').send(
        data=result,
    )

@router.get("/test")
async def test(request: Request, db: AsyncSession = Depends(get_db)):
    language = 'en'
    result = []

    return Response.code(200, 'S-GBS-11111').send(
        data=result
    )