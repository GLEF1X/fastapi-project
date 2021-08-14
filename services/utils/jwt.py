#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import datetime
from typing import Final, Dict, Any, Optional, cast

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

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


def create_jwt_token(*, jwt_content: Dict[Any, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = jwt_content.copy()
    if expires_delta is not None:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token_for_user(user: _DB_User) -> str:
    return create_jwt_token(
        jwt_content=TokenData(username=user.username).dict(),
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


async def authenticate_user(username: str, password: str, user_repository: UserRepository) -> _DB_User:
    user: _DB_User = await user_repository.get_user_by_username(username)
    if not user or not verify_password(password, cast(str, user.password)):
        raise UserIsNotAuthenticated()
    return user
