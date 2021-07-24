from datetime import timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from services.database.repositories.user import UserRepository
from services.dependencies.containers import Application
from services.utils.exceptions import UserIsNotAuthenticated
from services.utils.security import (
    authenticate_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
)

api_router = APIRouter()


@api_router.post("/oauth", tags=["Test"])
@inject
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_crud: UserRepository = Depends(Provide[Application.services.user_repository]),
):
    try:
        user = await authenticate_user(
            form_data.username, form_data.password, user_crud
        )
    except UserIsNotAuthenticated as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
