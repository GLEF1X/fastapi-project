from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import UJSONResponse

api_router = APIRouter()


@api_router.get("/healthcheck", response_class=UJSONResponse, tags=["healthcheck"])
async def healthcheck():
    return {"health": True}
