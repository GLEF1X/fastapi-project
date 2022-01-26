from typing import List

from aio_pika.patterns import RPC
from fastapi import Path, HTTPException, Depends, APIRouter
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, DatabaseError
from starlette.background import BackgroundTasks

from src.api.v1.dependencies.database import UserRepositoryDependencyMarker
from src.api.v1.dependencies.services import SecurityGuardServiceDependencyMarker, RPCDependencyMarker
from src.api.v1.dto import ObjectCountDTO, SimpleResponse, UserDTO, DefaultResponse
from src.resources import api_string_templates
from src.services.database.repositories.user_repository import UserRepository
from src.utils.endpoints_specs import UserBodySpec
from src.utils.responses import NotFoundJsonResponse, BadRequestJsonResponse

api_router = APIRouter(dependencies=[Depends(SecurityGuardServiceDependencyMarker)])


# noinspection PyUnusedLocal
@api_router.get("/users/{user_id}/info", response_model=UserDTO, tags=["Users"],
                name="users:get_user_info")
async def get_user_info(
        user_id: int,
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker)
):
    user = await user_repository.get_user_by_id(user_id)
    try:
        return UserDTO.from_orm(user)
    except ValidationError:
        return NotFoundJsonResponse(content=api_string_templates.USER_DOES_NOT_EXIST_ERROR)


# noinspection PyUnusedLocal
@api_router.get(
    "/users/all",
    response_model=List[UserDTO],
    responses={400: {"model": DefaultResponse}},
    tags=["Users"],
    name="users:get_all_users"
)
async def get_all_users(user_repository: UserRepository = Depends(UserRepositoryDependencyMarker)):
    return await user_repository.get_all_users()


@api_router.put(
    "/users/create", responses={400: {"model": DefaultResponse}}, tags=["Users"],
    name="users:create_user"
)
async def create_user(
        background_tasks: BackgroundTasks,
        user: UserDTO = UserBodySpec.item,
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
        rpc: RPC = Depends(RPCDependencyMarker),
):
    """*Create a new user in database"""
    payload = user.dict(exclude_unset=True)
    try:
        await user_repository.add_user(**payload)
    except IntegrityError:
        return BadRequestJsonResponse(content=api_string_templates.USERNAME_TAKEN)

    background_tasks.add_task(rpc.call, method_name="send_email")

    return {"success": True}


# noinspection PyUnusedLocal
@api_router.post(
    "/users/count",
    response_description="Return an integer or null",
    response_model=ObjectCountDTO,
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
    except DatabaseError:
        raise HTTPException(
            status_code=400, detail=f"There isn't entry with id={user_id}"
        )
    return {"message": f"UserDTO with id {user_id} was successfully deleted from database"}
