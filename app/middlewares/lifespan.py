import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.debug("🚀 LIFESPAN | Starting up the application...")
    try:
        await init_db()
        logger.info("🟢 LIFESPAN | Application startup: Initializing resources.")
        yield
    except Exception as e:
        logger.error("❌ LIFESPAN | Exception occurred during application lifespan", exc_info=True)
        logger.error(f"⚠️ LIFESPAN | Error: {e}")
        logger.error(f"🧵 LIFESPAN | Traceback: {traceback.format_exc()}")
    finally:
        logger.debug("🛑 LIFESPAN | Shutting down the application...")