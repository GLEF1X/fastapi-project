import datetime
from typing import Optional, Any, Union

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError
from starlette import status

from services.db import crud
from services.misc import TokenData, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth")

SECRET_KEY = "d9721f6c989b5165f273e6c78bdbc67b169097095023118bd7709ec2b613868c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> Any:
    return pwd_context.hash(password)


def create_access_token(
        data: dict,
        expires_delta: Optional[datetime.timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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
            await crud.select_user(username=token_data.username)
        )
        if user is None:
            raise ValidationError
    except ValidationError:
        raise credentials_exception
    return user


async def authenticate_user(username: str, password: str) -> Union[bool, User]:
    user = await crud.select_user(username=username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


__all__ = (
    'oauth2_scheme',
    'verify_password',
    'get_password_hash',
    'get_current_user',
    'authenticate_user',
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'create_access_token'
)
