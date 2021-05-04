import time
from typing import Coroutine, Any, Callable

from fastapi.openapi.models import Response
from starlette.requests import Request


async def add_process_time_header(request: Request,
                                  call_next: Callable[
                                      [Request], Coroutine[Any, Any, Response]
                                  ]
                                  ) -> Response:
    start_time = time.monotonic()
    response = await call_next(request)
    process_time = time.monotonic() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
