#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import datetime
from typing import Final, Dict, Any, Optional, cast

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from api.v1.dependencies.database import get_repository
from services.database import User as _DB_User
from services.database.repositories.user import UserRepository
from services.misc import User, TokenData
from services.utils.exceptions import UserIsNotAuthenticated

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth")
SECRET_KEY: Final[
    str
] = "d9721f6c989b5165f273e6c78bdbc67b169097095023118bd7709ec2b613868c"
ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
        data: Dict[Any, Any], expires_delta: Optional[datetime.timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    try:
        user = User.from_orm(
            await user_repository.select_one(
                user_repository.model.username == token_data.username
            )
        )
        if user is None:
            raise ValidationError
    except ValidationError:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str, user_repository: UserRepository) -> _DB_User:
    user = await user_repository.select_one(user_repository.model.username == username)
    if not user or not verify_password(password, cast(str, user.password)):
        raise UserIsNotAuthenticated()
    return user
