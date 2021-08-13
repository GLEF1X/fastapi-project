from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException  # noqa
from starlette.requests import Request
from starlette.responses import PlainTextResponse


async def validation_exception_handler(request: Request, exc):
    return PlainTextResponse(str(exc), status_code=400)


async def custom_http_exception_handler(request, exc):
    print(f"OMG! An HTTP error!: {repr(exc)}")
    return await http_exception_handler(request, exc)
