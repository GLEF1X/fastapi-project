from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from core.config import settings
from middlewares.process_time_middleware import add_process_time_header
from views.exception_handlers import http_405_exception_handler, \
    request_exception_handler, http_401_exception_handler

ALLOWED_METHODS = ["POST", "PUT", "DELETE", "GET"]


def setup_application() -> FastAPI:
    app = FastAPI(**settings.api_kwargs, exception_handlers={
        405: http_405_exception_handler,
        RequestValidationError: request_exception_handler,
        401: http_401_exception_handler
    })
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        expose_headers=["User-Agent", "Authorization"]
    )
    # app.add_event_handler("shutdown", on_shutdown)
    return app
