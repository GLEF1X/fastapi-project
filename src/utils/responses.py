from typing import Optional, Type, Any, TypeVar, Union

from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

from src.resources import api_string_templates

Model = TypeVar("Model")


class BadRequestJsonResponse(ORJSONResponse):

    def __init__(self,
                 content: Any = None,
                 headers: dict = None,
                 media_type: str = None,
                 background: BackgroundTask = None, ):
        super(BadRequestJsonResponse, self).__init__(
            content=content,
            status_code=status.HTTP_400_BAD_REQUEST,
            headers=headers,
            media_type=media_type,
            background=background
        )


class NotFoundJsonResponse(ORJSONResponse):

    def __init__(self,
                 content: Any = None,
                 headers: dict = None,
                 media_type: str = None,
                 background: BackgroundTask = None, ):
        super(NotFoundJsonResponse, self).__init__(
            content=content,
            status_code=status.HTTP_404_NOT_FOUND,
            headers=headers,
            media_type=media_type,
            background=background
        )


def get_pydantic_model_or_return_raw_response(
        model: Type[Model], db_obj: Optional[Any] = None
) -> Union[ORJSONResponse, Model]:
    if db_obj is None:
        return NotFoundJsonResponse(content=api_string_templates.OBJECT_NOT_FOUND)
    try:
        return model.from_orm(db_obj)  # type: ignore
    except ValidationError:
        return BadRequestJsonResponse()
