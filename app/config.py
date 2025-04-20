import os
from pathlib import Path

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_PORT: int = 3000
    APP_ENV: str = "local"
    APP_URL: str = "http://localhost:3000"
    TIMEZONE: str = 'Asia/Dhaka'
    APP_NAME: str = 'letter-bot-api'

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "secret"
    REDIS_DB_NO: int = 0

    BASE_DIR: str = Path(__file__).resolve().parent.parent.as_posix()
    STORAGE_DIR: str = Path(__file__).resolve().parent.parent.joinpath('storage').as_posix()

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
if os.getenv("APP_ENV") == "local":
    pprint(settings.model_dump())