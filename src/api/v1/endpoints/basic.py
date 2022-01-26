from fastapi import APIRouter, Depends

from src.api.v1.dependencies.database import UserRepositoryDependencyMarker
from src.services.database.repositories.user_repository import UserRepository
from src.api.v1.dto import TestResponse

fundamental_api_router = APIRouter(prefix="/api/v1")


@fundamental_api_router.post("/test", tags=["Test"], response_model=TestResponse)
async def test(a: UserRepository = Depends(UserRepositoryDependencyMarker)):
    return {"success": True}
