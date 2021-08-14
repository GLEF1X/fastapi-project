#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from pydantic import ValidationError
from starlette import status

from src.api.v1.dependencies.database import UserRepositoryDependencyMarker
from src.services.database.repositories.user import UserRepository
from src.services.misc import User, TokenData
from src.services.utils.jwt import SECRET_KEY, ALGORITHM, oauth2_scheme


async def get_current_user(  # TODO refactor this function(decomposition)
        token: str = Depends(oauth2_scheme),
        user_repository: UserRepository = Depends(UserRepositoryDependencyMarker),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    try:
        user = User.from_orm(await user_repository.get_user_by_username(token_data.username))
        if user is None:
            raise ValidationError
    except ValidationError:
        raise credentials_exception
    return user
