from fastapi import FastAPI

from app.api import health
from app.api.v1 import v1
from app.api import service
from app.core.exceptions import handle_global_exceptions
from app.middlewares import register_middlewares
from app.middlewares.lifespan import lifespan

app = FastAPI(
    debug=True,
    lifespan=lifespan,
    title="LetterBot",
    version="1.0",
    docs_url="/docs"
)


handle_global_exceptions(app)
register_middlewares(app)

app.include_router(health.router)
@app.get("/")
def hello():
    return ["Hello, the LetterBot BRAIN"]

app.include_router(v1, prefix="/api/v1")
# app.include_router(service.service_router, prefix="/service/v1")