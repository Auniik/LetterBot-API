# import time

from fastapi import FastAPI

from .context_capture import ContextCaptureMiddleware
# from .profiler import ProfilerMiddleware
from .timeout import TimeoutMiddleware
from .transaction_log import TransactionLogMiddleware



def register_middlewares(app: FastAPI):
    app.add_middleware(TransactionLogMiddleware)
    app.add_middleware(ContextCaptureMiddleware)
    # app.add_middleware(ProfilerMiddleware)
    # app.add_middleware(TimeoutMiddleware, timeout=5)

