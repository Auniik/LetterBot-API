import asyncio
import os
import socket
import time
from datetime import datetime

import orjson
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config import settings
from app.core.logger import logger
from app.middlewares.context_capture import client_ip_context, transaction_id_context, get_redis_log_context, \
    get_db_log_context, get_http_log_context


class TransactionLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        headers = request.headers
        start_time = time.time()
        ss_id = request.headers.get('NA')
        platform = request.headers.get('NA')
        version = request.headers.get('NA')
        client_ip = client_ip_context.get()
        host_name = os.getenv('K_REVISION', socket.gethostname())

        response = await call_next(request)

        # Capture response body
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = (chunk for chunk in response_body)

        # Send the response back immediately
        final_response = Response(
            content=b"".join(response_body),
            status_code=response.status_code,
            headers=dict(response.headers)
        )

        # Non-blocking post-response processing with error handling
        task = asyncio.create_task(self.process_post_response(
            response_body, start_time, host_name, headers,
            ss_id, platform, version, client_ip, transaction_id_context.get(), request,
            response
        ))
        task.add_done_callback(self.handle_task_exception)

        return final_response

        # return Response(content=b"".join(response_body), status_code=response.status_code, headers=dict(response.headers))

    async def process_post_response(
        self,
        response_body,
        start_time,
        host_name,
        headers,
        ss_id,
        platform,
        version,
        client_ip,
        transaction_id,
        request,
        response
    ):
        # Determine the environment zone
        api = "_".join(request.url.path.split("/")[-1:]) or ""
        zone = get_zone(settings)

        debug_loggable = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "gcpTypeLogs": "debug",
            "logger": "stash",
            "host": host_name,
            "zone": zone,
            "domain": "TAP",
            "app": settings.APP_NAME,
            "source": "TRUEAPP",  # Can be GBSearch
            "ssId": ss_id,
            "txId": transaction_id,
            "reqIP": client_ip,
            "APIName": f"{api}.{request.method}",
            "level": "DEBUG",
            "mode": "async",
            "message": {
                "startTime": start_time,
                "url": str(request.url),
                "routePattern": api,
                "method": request.method,
                "userAgent": request.headers.get("user-agent"),
                "request": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(headers),
                    "query": dict(request.query_params),
                },
                "response": {
                    "headers": None,
                    "code": None,
                    "duration": 0,
                },
                "redis": [],
                "database": [],
                "http": {},
            }
        }
        # Error defaults
        err_type, err_code, err_msg, srv_status = "T", "T-GBS-99999", "", "false"

        try:
            # Asynchronous JSON decoding with orjson for non-blocking behavior
            response_text = b"".join(response_body).decode('utf-8')
            response_data = orjson.loads(response_text)
            status = response_data.get("status", {})
            debug_loggable["message"]["response"] = {
                "headers": dict(response.headers),
                "code": response.status_code,
                "duration": (time.time() - start_time),
                "body": response_data if response.status_code > 200 else None
            }
            err_type = status.get("statusType", err_type)
            err_code = status.get("errorCode", err_code)
            err_msg = status.get("errorMessage", err_msg)
            srv_status = 'true' if err_type == "S" else 'false'
        except Exception:
            pass

        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)


        # Prepare log entry
        loggable = {
            "@timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z"),
            "logger": "stash",
            "host": host_name,
            "zone": zone,
            "domain": "GBS",
            "app": settings.APP_NAME,
            "source": "TRUEAPP",  # Can be GBSearch
            "ssId": ss_id,
            "txId": transaction_id,
            "segment": "NA",
            "brand": headers.get('x-user-brand', 'NA'),
            "mainDigitalId": headers.get('x-user-id', 'NA'),
            "profileId": "NA",
            "digitalId": headers.get('x-user-id', 'NA'),
            "reqIP": client_ip,
            "APIName": f"{api}.{request.method}",
            "errType": err_type,
            "errCode": err_code,
            "errMsg": err_msg,
            "srvStatus": srv_status,
            "resTime": response_time,
            "platform": platform,
            "appVersion": version,
            "gcpTypeLogs": "transaction"
        }

        # Non-blocking log writing
        logger.info(loggable)

        debug_loggable["message"]["redis"] = get_redis_log_context()
        debug_loggable["message"]["database"] = get_db_log_context()
        debug_loggable["message"]["http"] = get_http_log_context()
        logger.info(debug_loggable)

    def handle_task_exception(self, task):
        try:
            task.result()
        except Exception as e:
            logger.error(f'An error occurred in process_post_response: {e}')