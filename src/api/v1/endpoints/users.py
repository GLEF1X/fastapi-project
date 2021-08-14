from typing import List

from fastapi import Path, HTTPException, Depends, APIRouter
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.api.v1.dependencies.database import UserRepositoryDependencyMarker
from src.api.v1.dependencies.security import get_current_user
from src.resources import api_string_templates
from src.services.database.exceptions import UnableToDelete
from src.services.database.repositories.user import UserRepository
from src.services.misc import User, DefaultResponse
from src.services.misc.schemas import ObjectCount, SimpleResponse
from src.services.utils.endpoints_specs import UserBodySpec
from src.services.utils.responses import NotFoundJsonResponse, BadRequestJsonResponse

api_router = APIRouter(dependencies=[Depends(get_current_user)])


# noinspection PyUnusedLocal
@api_router.get("/users/{user_id}/info", response_model=User, tags=["Users"], name="users:get_user_info")
async def get_user_info(
        user_id: int,
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
):
    entry: User = await user_repository.get_user_by_id(user_id)
    try:
        return User.from_orm(entry)
    except ValidationError:
        return NotFoundJsonResponse(content=api_string_templates.USER_DOES_NOT_EXIST_ERROR)


# noinspection PyUnusedLocal
@api_router.get(
    "/users/all",
    response_model=List[User],
    responses={400: {"model": DefaultResponse}},
    tags=["Users"],
    name="users:get_all_users"
)
async def get_all_users(user_repository: UserRepository = Depends(UserRepositoryDependencyMarker)):
    users: List[User] = await user_repository.get_all_users()
    return users


@api_router.put(
    "/users/create", responses={400: {"model": DefaultResponse}}, tags=["Users"],
    name="users:create_user"
)
async def create_user(
        user: User = UserBodySpec.item,
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
):
    """*Create a new user in database"""
    payload = user.dict(exclude_unset=True)
    try:
        await user_repository.add_user(**payload)
    except IntegrityError:
        return BadRequestJsonResponse(content=api_string_templates.USER_IS_ALREADY_FOLLOWED)

    return {"success": True}


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
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
):
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
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
):
    try:
        await user_repository.delete_user(user_id=user_id)
    except UnableToDelete:
        raise HTTPException(
            status_code=400, detail=f"There isn't entry with id={user_id}"
        )
    return {"message": f"User with id {user_id} was successfully deleted from database"}
