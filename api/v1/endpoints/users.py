from typing import Optional, List

from fastapi import Header, Path, HTTPException, Depends, APIRouter
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from api.v1.dependencies.database import get_repository
from api.v1.dependencies.security import get_current_user
from services.database.exceptions import UnableToDelete
from services.database.repositories.user import UserRepository
from services.misc import User, DefaultResponse
from services.misc.schemas import ObjectCount, SimpleResponse
from services.utils.endpoints_specs import UserBodySpec
from services.utils.responses import bad_response, not_found

api_router = APIRouter()


# noinspection PyUnusedLocal
@api_router.get("/users/{user_id}/info", response_model=User, tags=["Users"], name="users:get_user_info")
async def get_user_info(
        user_id: int,
        user: User = Depends(get_current_user),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    if not user_agent:
        return bad_response()
    entry: User = await user_repository.get_user_by_id(user_id)
    try:
        return User.from_orm(entry)
    except ValidationError:
        return not_found(user_id)


# noinspection PyUnusedLocal
@api_router.get(
    "/users/all",
    response_model=List[User],
    responses={400: {"model": DefaultResponse}},
    tags=["Users"],
    name="users:get_all_users"
)
async def get_all_users(
        user: User = Depends(get_current_user),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    if not user_agent:
        return bad_response()
    users: List[User] = await user_repository.get_all_users()
    return users


@api_router.put(
    "/users/create", responses={400: {"model": DefaultResponse}}, tags=["Users"],
    name="users:create_user"
)
async def create_user(
        user: User = UserBodySpec.item,
        user_agent: str = Header(..., title="User-Agent"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    """*Create a new user in database"""
    payload = user.dict(exclude_unset=True)
    try:
        await user_repository.add_user(**payload)
    except IntegrityError:
        return bad_response("A user with such core is already registered.")

    return {"success": True, "User-Agent": user_agent}


# noinspection PyUnusedLocal
@api_router.post(
    "/users/count",
    response_description="Return an integer or null",
    response_model=ObjectCount,
    tags=["Users"],
    summary="Return count of users in database",
    name="users:get_users_count"
)
async def get_users_count(
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user: User = Depends(get_current_user),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    if not user_agent:
        return bad_response()
    return {"count": await user_repository.get_users_count()}


# noinspection PyUnusedLocal
@api_router.delete(
    "/users/{user_id}/delete",
    response_description="return nothing",
    tags=["Users"],
    summary="Delete user from database",
    response_model=SimpleResponse,
    name="users:delete_user"
)
async def delete_user(
        user_id: int = Path(...),
        user: User = Depends(get_current_user),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    if not user_agent:
        return bad_response()
    try:
        await user_repository.delete_user(user_id=user_id)
    except UnableToDelete:
        raise HTTPException(
            status_code=400, detail=f"There isn't entry with id={user_id}"
        )
    return {"message": f"User with id {user_id} was successfully deleted from database"}
