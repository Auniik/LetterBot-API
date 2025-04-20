import json
import time

import httpx
from fastapi import HTTPException

from app.middlewares.context_capture import get_http_log_context

async def api_call(method: str, url: str, data: dict = None, headers: dict = None, srv_type=None, srv_name=None):
    start_time = time.time()
    debug_loggable = {
        "operation": "api_call",
        "url": url,
        "method": method,
        "request": {
            "headers": headers or None,
            "data": data or None,
        },
        "response": {
            "headers": {},
            "code": 0,
        },
        "duration": 0.0,
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, json=data, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            debug_loggable["response"]["headers"] = dict(response.headers)
            debug_loggable["response"]["code"] = response.status_code
            debug_loggable["duration"] = time.time() - start_time
            length = response.headers.get("Content-Length")
            data = response.json()
            response_data = response.json()
            if length and int(length) < 1000:
                debug_loggable["response"]["data"] = response_data
            return data
    except httpx.HTTPStatusError as exc:
        try:
            data = exc.response.json()
        except:
            data = {}
        error_message = f'HTTPStatusError: [{method}] {url} - {exc.response.status_code}'
        debug_loggable["response"]["error"] = json.dumps(data) + error_message
        debug_loggable["response"]["code"] = exc.response.status_code
        debug_loggable["response"]["headers"] = dict(exc.response.headers)
        debug_loggable["duration"] = time.time() - start_time

        raise HTTPException(status_code=exc.response.status_code, detail=str(exc))
    except Exception as general_error:
        error_message = f'{str(type(general_error))}: [{method}] {url} - {str(general_error)}'
        debug_loggable["response"]["error"] = str(general_error) + error_message
        debug_loggable["duration"] = time.time() - start_time
        raise HTTPException(status_code=500, detail=error_message)
    finally:
        loggable = get_http_log_context()
        loggable.append(debug_loggable)
