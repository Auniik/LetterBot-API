import traceback
from contextlib import asynccontextmanager

import redis
import sqlalchemy
from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from app.core.logger import logger
from app.core.response import Response


def handle_global_exceptions(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code == 405:
            return Response.code(405).send_error(
                error_message="Request method not supported",
                error_description=str(exc)
            )
        elif exc.status_code == 404:
            return Response.code(404).send_error(
                error_message="Endpoint URL not found",
                error_description=str(exc)
            )
        elif exc.status_code == 401:
            return Response.code(401, 'B-GBS-00401').send_error(
                error_message="Unauthorized",
                error_description=str(exc)
            )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for e in exc.errors():
            item = {
                "loc": e["loc"][1] if len(e["loc"]) > 1 else e["loc"][0],
                "msg": e["msg"].replace("Value error, ", ""),
                "type": e["type"],
            }
            errors.append(item)

        return Response.code(422, 'B-GBS-000401').send(data={
            "message": "Validation error",
            "errors": errors,
        })


    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(request: Request, exc: IntegrityError):
        return Response.code(500, 'T-GBS-00000').send_error(
            error_message="An integrity error occurred. Please try again later.",
            error_description=str(exc)
        )
    @app.exception_handler(sqlalchemy.exc.ProgrammingError)
    async def syntax_exception_handler(request: Request, exc: sqlalchemy.exc.ProgrammingError):
        return Response.code(500, 'T-GBS-00101').send_error(
            error_message="SQL syntax error",
            error_description=str(exc)
        )
    @app.exception_handler(sqlalchemy.exc.OperationalError)
    async def db_connection_exception_handler(request: Request, exc: sqlalchemy.exc.OperationalError):
        return Response.code(500, 'T-GBS-00102').send_error(
            error_message="Database connection error",
            error_description=str(exc)
        )
    @app.exception_handler(redis.exceptions.ConnectionError)
    async def redis_connection_exception_handler(request: Request, exc: redis.exceptions.ConnectionError):
        return Response.code(500, 'T-GBS-00103').send_error(
            error_message="Redis connection error",
            error_description=str(exc)
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return Response.code(400, 'T-GBS-99999').send_error(
            error_message="Unknown error",
            error_description=str(exc)
        )
