from typing import Optional

from dependency_injector.wiring import inject, Provide
from fastapi import Header, APIRouter, Depends

from services.misc.pydantic_models import TestResponse
from services.redis.containers import Application
from services.redis.services import RedisService

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/test", tags=["Test"], response_model=TestResponse)
@inject
async def test(
        user_agent: Optional[str] = Header(...),
        service: RedisService = Depends(Provide[Application.services.redis_])
):
    """ Test query """
    value = await service.cache_process('cached_', 1, expire=40)
    return {"success": True, "User-Agent": user_agent, "value": value}
