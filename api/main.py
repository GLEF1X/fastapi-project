from typing import Optional

from fastapi import Header, APIRouter
from starlette.responses import JSONResponse

from services.db import crud
from services.misc import User, DefaultResponse

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/test")
async def test(user_agent: Optional[str] = Header(...)):
    """ Test query """
    return {"success": True, "User-Agent": user_agent}


@api_router.put('/users/create/', responses={400: {"model": DefaultResponse}})
async def create_user(
        us: User,
        user_agent: Optional[str] = Header(None, title="User-Agent")
):
    """*Create a new user in database"""
    if not user_agent:
        return JSONResponse(
            status_code=400,
            content={
                "error": "You didnt pass User-Agent in headers",
                "success": False
            }
        )
    await crud.add_user(**us.dict())

    return {"success": True, "User-Agent": user_agent}
