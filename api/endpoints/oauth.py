from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from api import api_router
from services.utils.security import authenticate_user, \
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


@api_router.post("/oauth", tags=["Test"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
