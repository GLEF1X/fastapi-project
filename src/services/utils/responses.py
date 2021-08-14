from typing import Optional, Type, Any, TypeVar

from fastapi import HTTPException
from pydantic import ValidationError
from starlette.responses import JSONResponse

Model = TypeVar("Model")


def bad_response(msg: Optional[str] = None) -> JSONResponse:
    msg = msg if isinstance(msg, str) else "You didnt pass User-Agent in headers"
    return JSONResponse(status_code=400, content={"error": msg, "success": False})


def not_found(obj_id: Optional[int] = None) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": f"There isn't no user with id={obj_id}", "success": False},
    )


async def get_pydantic_model_or_raise_exception(
    model: Type[Model], db_obj: Optional[Any] = None
) -> Model:
    if db_obj is None:
        raise HTTPException(
            status_code=404,
            detail={"success": "false", "description": "Object not found"},
        )
    try:
        return model.from_orm(db_obj)  # type: ignore
    except ValidationError:
        raise HTTPException(
            status_code=400,
            detail={"success": "false", "description": "Server validation error"},
        )
