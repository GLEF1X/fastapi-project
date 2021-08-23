#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import UJSONResponse

api_router = APIRouter()


@api_router.get("/healthcheck", response_class=UJSONResponse, tags=["healthcheck"])
async def healthcheck():
    return {"health": True}
