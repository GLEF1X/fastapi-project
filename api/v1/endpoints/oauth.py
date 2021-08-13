from datetime import timedelta

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from api.v1.dependencies.database import get_repository
from services.database.repositories.user import UserRepository
from services.utils.exceptions import UserIsNotAuthenticated
from api.v1.dependencies.security import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, authenticate_user

api_router = APIRouter()


@api_router.post("/oauth", tags=["Test"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(get_repository(UserRepository)),
):
    try:
        user = await authenticate_user(form_data.username, form_data.password, user_repository)
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
