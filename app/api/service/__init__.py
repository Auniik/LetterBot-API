from fastapi import APIRouter
from . import service

service_router = APIRouter()

service_router.include_router(service.router, prefix="/service", tags=["Search"])