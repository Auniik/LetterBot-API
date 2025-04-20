import contextvars
from datetime import datetime

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

headers_context = contextvars.ContextVar("headers", default={})
transaction_id_context = contextvars.ContextVar("transaction_id", default=f"NA")
client_ip_context = contextvars.ContextVar("client_ip", default="NA")
route_name_context = contextvars.ContextVar("url", default="")

redis_log_context = contextvars.ContextVar("redis_log_context", default=None)
db_log_context = contextvars.ContextVar("db_log_context", default=None)
http_log_context = contextvars.ContextVar("http_log_context", default=None)


class ContextCaptureMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        headers_context.set(dict(request.headers))
        txn_id = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        transaction_id_context.set(txn_id)
        client_ip_context.set(request.client.host if request.client else 'NA')
        api = "_".join(request.url.path.split("/")[-1:]) or ""
        route_name_context.set(f"{api}.{request.method}")
        redis_log_context.set([])
        db_log_context.set([])
        http_log_context.set([])
        response = await call_next(request)
        return response


def get_redis_log_context():
    log_context = redis_log_context.get()
    if log_context is None:
        redis_log_context.set([])
        return redis_log_context.get()
    return log_context

def get_db_log_context():
    log_context = db_log_context.get()
    if log_context is None:
        db_log_context.set([])
        return db_log_context.get()
    return log_context

def get_http_log_context():
    log_context = http_log_context.get()
    if log_context is None:
        http_log_context.set([])
        return http_log_context.get()
    return log_context