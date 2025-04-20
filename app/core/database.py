import time

from sqlalchemy import event, Engine
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.logger import logger
from app.middlewares.context_capture import get_db_log_context

connection_url = URL.create(
    drivername = "postgresql+asyncpg",
    username = settings.DB_USER,
    password = settings.DB_PASSWORD,
    host = settings.DB_HOST,
    port = settings.DB_PORT,
    database = settings.DB_NAME
)

engine = create_async_engine(
    connection_url,
    pool_size=100,  # Maximum number of connections in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond the pool_size
    pool_timeout=5,  # Seconds to wait before timing out on getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    echo=False,
)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        logger.debug("🎯 Sync db tables")
        done = await conn.run_sync(Base.metadata.create_all, checkfirst=True)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info['query_start_time'] = time.time()
    conn.info['query'] = {
        "query": statement,
    }

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time']
    query_entry = conn.info['query']
    query_entry["duration"] = total_time
    loggable = get_db_log_context()
    loggable.append(query_entry)