import socket
from enum import Enum
from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.middlewares.context_capture import transaction_id_context


class StatusType(str, Enum):
    SUCCESS = "S"
    FAILED = "F"


class Status(BaseModel):
    type: StatusType
    code: str
    message: str = ""
    description: str = ""
    hostId: str = ""
    transactionId: str = ""


class Response:
    def __init__(self, status_code: int, error_code: str, status_type: StatusType = StatusType.SUCCESS):
        self.status_code = status_code
        self.status_type = status_type
        self.error_code = error_code
        self.error_message = ""
        self.error_description = ""
        self.data = None

    @staticmethod
    def code(status_code: int, error_code: str = None, status_type: StatusType = StatusType.SUCCESS) -> 'Response':
        return Response(status_code=status_code, error_code=error_code, status_type=status_type)

    def send_error(self, data: Any = None, headers=None) -> JSONResponse:
        self.data = data
        return self._build_response(headers=headers)

    def send(self, data: Any = None, headers=None) -> JSONResponse:
        self.data = data
        return self._build_response(headers=headers)

    def send_message(self, message: str) -> JSONResponse:
        if not self.data:
            self.data = {}

        self.data['message'] = message
        return self._build_response()

    def _build_response(self, headers=None) -> JSONResponse:
        hostname = socket.gethostname()
        transaction_id = transaction_id_context.get()

        status = Status(
            type=self.status_type,
            code=self.error_code,
            message=self.error_message,
            description=self.error_description,
            hostId=hostname,
            transactionId=transaction_id,
        )
        safe_data = jsonable_encoder(self.data)
        safe_status = jsonable_encoder(status)

        response_payload = {
            "status": safe_status,
            "data": safe_data or {},
        }
        return JSONResponse(content=response_payload, status_code=self.status_code, headers=headers)
