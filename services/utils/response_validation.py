from typing import Optional

from starlette.responses import JSONResponse


def bad_response() -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={
            "error": "You didnt pass User-Agent in headers",
            "success": False
        }
    )


def not_found(obj_id: Optional[int] = None) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": f"There isn't no user with id={obj_id}",
            "success": False
        }
    )
