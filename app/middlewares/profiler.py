from pyinstrument.profiler import Profiler
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class ProfilerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        profiler = Profiler()
        profiler.start()
        response = await call_next(request)
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
        return response