from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware

from data import config
from middlewares.process_time_middleware import add_process_time_header
from views.exception_handlers import http_405_exception_handler, \
    request_exception_handler, http_401_exception_handler

tags_metadata = [
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here."
    },
    {
        "name": "Test",
        "description": "Test queries"
    },
    {
        "name": "Product",
        "description": "Operations with products."
    }
]

api_kwargs = {
    'debug': True,
    'title': config.APP_NAME,
    'version': config.API_VERSION,
    'docs_url': config.DOCS_URL,
    'redoc_url': config.REDOC_URL,
    'openapi_url': config.OPEN_API_ROOT if not config.IS_PRODUCTION else None,
    'openapi_tags': tags_metadata
}


def setup_application() -> FastAPI:
    app = FastAPI(**api_kwargs, exception_handlers={
        405: http_405_exception_handler,
        RequestValidationError: request_exception_handler,
        401: http_401_exception_handler
    })
    app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
    return app
