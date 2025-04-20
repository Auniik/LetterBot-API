import asyncio

from starlette.responses import JSONResponse


class TimeoutMiddleware:
    def __init__(self, app, timeout: int):
        self.app = app
        self.timeout = timeout

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            try:
                await asyncio.wait_for(self.app(scope, receive, send), timeout=self.timeout)
            except asyncio.TimeoutError:
                response = JSONResponse(
                    {"detail": "Request processing time exceeded the limit."}, status_code=408
                )
                await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)