from typing import Union

from fastapi import APIRouter, FastAPI

from .home import api_router


def setup_routes(main_router: Union[FastAPI, APIRouter], include_in_schema: bool = False):
    main_router.include_router(api_router, include_in_schema=include_in_schema)
