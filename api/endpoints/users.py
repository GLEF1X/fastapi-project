from typing import Optional, List

from dependency_injector.wiring import Provide, inject
from fastapi import Header, Body, Path, HTTPException, Depends
from pydantic import ValidationError

from api.application import api_router
from api.config import DETAIL_RESPONSES
from services.db import UnableToDelete
from services.db.crud import UserRepository
from services.dependencies.containers import Application
from services.misc import User, DefaultResponse
from services.misc.schemas import ObjectCount, SimpleResponse
from services.utils.responses import bad_response, not_found
from services.utils.security import get_password_hash


@api_router.get("/users/{user_id}/info", response_model=User,
                responses=DETAIL_RESPONSES, tags=["Users"])
@inject
async def get_user_info(
        user_id: int,
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(
            Provide[Application.services.user_repository]
        )
):
    if not user_agent:
        return bad_response()
    entry = await user_repository.select(user_id=user_id)
    try:
        return User.from_orm(entry)
    except ValidationError:
        return not_found(user_id)


@api_router.get("/users/all", response_model=List[User],
                responses={400: {"model": DefaultResponse}}, tags=["Users"])
async def get_all_users(
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(
            Provide[Application.services.user_repository]
        )
):
    if not user_agent:
        return bad_response()
    users = await user_repository.select_all()
    return users


@api_router.put('/users/create', responses={400: {"model": DefaultResponse}},
                tags=["Users"])
async def create_user(
        us: User = Body(..., example={
            "first_name": "Gleb",
            "last_name": "Garanin",
            "username": "GLEF1X",
            "phone_number": "+7900232132",
            "email": "glebgar567@gmail.com",
            "password": "qwerty12345",
            "balance": 5
        }),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(
            Provide[Application.services.user_repository]
        )
):
    """*Create a new user in database"""
    if not user_agent:
        return bad_response()
    payload = us.dict(exclude_unset=True)
    payload.update(
        {"hashed_password": get_password_hash(us.password)}
    )
    await user_repository.add(**payload)

    return {"success": True, "User-Agent": user_agent}


@api_router.post("/users/count",
                 response_description="Return an integer or null",
                 response_model=ObjectCount,
                 tags=["Users"],
                 summary="Return count of users in database")
async def get_users_count(
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(
            Provide[Application.services.user_repository]
        )
):
    if not user_agent:
        return bad_response()
    return {"count": await user_repository.count()}


@api_router.delete("/users/{user_id}/delete",
                   response_description="return nothing",
                   tags=["Users"], summary="Delete user from db",
                   response_model=SimpleResponse)
async def delete_user(
        user_id: int = Path(...),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(
            Provide[Application.services.user_repository]
        )
):
    if not user_agent:
        return bad_response()
    try:
        await user_repository.delete(user_id)
    except UnableToDelete:
        raise HTTPException(
            status_code=400,
            detail=f"There isn't entry with id={user_id}"
        )
    return {"response": "user deleted"}
