from typing import Optional

from fastapi import Header, APIRouter, Depends

from api.v1.dependencies.security import get_current_user
from services.misc.schemas import TestResponse, User

fundamental_api_router = APIRouter(prefix="/api/v1")


@fundamental_api_router.get("/test", tags=["Test"], response_model=TestResponse)
async def test(
    user: User = Depends(get_current_user),
    user_agent: Optional[str] = Header(...),
):
    return {"success": True, "User-Agent": user_agent}
