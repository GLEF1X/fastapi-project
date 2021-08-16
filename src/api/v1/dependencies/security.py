#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from typing import Dict, Any

from fastapi import HTTPException
from fastapi.security import SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError
from starlette import status

from src.resources import api_string_templates
from src.services.database.models.user import User
from src.services.database.repositories.user import UserRepository
from src.services.misc import TokenData
from src.services.utils.jwt import SECRET_KEY, ALGORITHM


class AuthenticationDependencyMarker:  # pragma: no cover
    pass


def _retrieve_authorization_prefix(security_scopes: SecurityScopes) -> str:
    if security_scopes.scopes:
        return f'Bearer scope="{security_scopes.scope_str}"'
    return "Bearer"


def _check_security_scopes(security_scopes: SecurityScopes, token_data: TokenData, prefix: str):
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": prefix},
            )


class JWTBasedOAuth:
    validation_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=api_string_templates.MALFORMED_PAYLOAD,
        headers={"WWW-Authenticate": "Bearer"},
    )

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    def decode_token(self, token: str) -> Dict[Any, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise self.validation_exception

    def extract_token_data_from_decoded(self, decoded_data: Dict[Any, Any]) -> TokenData:
        try:
            return TokenData(username=decoded_data["username"], scopes=decoded_data.get("scopes", []))
        except (KeyError, ValidationError):
            raise self.validation_exception

    async def retrieve_user_or_raise_exception(self, token_data: TokenData) -> User:
        user: User = await self._user_repository.get_user_by_username(username=token_data.username)
        if user is None:
            raise self.validation_exception
        return user

    async def __call__(self, token: str, security_scopes: SecurityScopes) -> User:
        prefix = _retrieve_authorization_prefix(security_scopes)
        payload = self.decode_token(token)
        token_data = self.extract_token_data_from_decoded(payload)
        _check_security_scopes(security_scopes=security_scopes, token_data=token_data, prefix=prefix)
        return await self.retrieve_user_or_raise_exception(token_data=token_data)
