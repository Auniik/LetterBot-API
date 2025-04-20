from fastapi import APIRouter
from . import settings, prompt_template

v1 = APIRouter()

v1.include_router(settings.router, prefix="/settings", tags=['Settings'])

v1.include_router(prompt_template.router, prefix="/prompt-templates", tags=['Prompt Templates'])