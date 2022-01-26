from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

api_router = APIRouter()


@api_router.get("/healthcheck", response_class=ORJSONResponse, tags=["healthcheck"])
async def healthcheck():
    return {"health": True}
