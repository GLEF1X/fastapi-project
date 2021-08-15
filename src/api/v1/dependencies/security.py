#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import abc
from typing import Dict, Any, Protocol

from fastapi import HTTPException
from jose import jwt, JWTError
from starlette import status

from src.resources import api_string_templates
from src.services.utils.jwt import SECRET_KEY, ALGORITHM


class AuthenticationProto(Protocol):
    validation_exception: HTTPException

    @abc.abstractmethod
    def decode_token(self, token: str) -> Dict[Any, Any]:
        raise NotImplementedError

    async def __call__(self, token: str) -> None: ...


class JWTBasedAuthenticationImpl(AuthenticationProto):
    validation_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=api_string_templates.MALFORMED_PAYLOAD,
        headers={"WWW-Authenticate": "Bearer"},
    )

    def decode_token(self, token: str) -> Dict[Any, Any]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise self.validation_exception

    def extract_user_name_from_decoded(self, decoded_data: Dict[Any, Any]) -> str:
        try:
            return decoded_data["username"]
        except KeyError:
            raise self.validation_exception

    async def __call__(self, token: str) -> None:
        payload = self.decode_token(token)
        self.extract_user_name_from_decoded(payload)
