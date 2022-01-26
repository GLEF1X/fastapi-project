from datetime import datetime, timedelta
from typing import NewType, Any, Dict

import jwt
from argon2.exceptions import VerificationError
from fastapi import HTTPException
from fastapi.security import SecurityScopes, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from src.api.v1.dto import TokenPayload
from src.resources import api_string_templates
from src.services.database.models.user import User
from src.services.database.repositories.user_repository import UserRepository
from src.utils.exceptions import UserIsUnauthorized
from src.utils.password_hashing.protocol import PasswordHasherProto

JWTToken = NewType("JWTToken", str)


class JWTSecurityGuardService:

    def __init__(self, oauth2_scheme: OAuth2PasswordBearer, user_repository: UserRepository,
                 password_hasher: PasswordHasherProto, secret_key: str, algorithm: str):
        self._oauth2_scheme = oauth2_scheme
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def __call__(self, request: Request, security_scopes: SecurityScopes) -> User:
        jwt_token = await self._oauth2_scheme(request)
        if jwt_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=api_string_templates.TOKEN_IS_MISSING,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_payload = self._decode_token(token=jwt_token)

        for scope in security_scopes.scopes:
            if scope not in token_payload.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=api_string_templates.SCOPES_MISSING,
                    headers={"WWW-Authenticate": "Bearer"},
                )

        return await self._retrieve_user_or_raise_exception(token_payload.username)

    def _decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret_key, algorithm=self._algorithm)
            return TokenPayload(username=payload["username"], scopes=payload.get("scopes", []))
        except (jwt.DecodeError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=api_string_templates.TOKEN_IS_INCORRECT,
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def _retrieve_user_or_raise_exception(self, username: str) -> User:
        if user := await self._user_repository.get_user_by_username(username=username):  # type: User
            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=api_string_templates.USER_DOES_NOT_EXIST_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )


class JWTAuthenticationService:
    def __init__(self, user_repository: UserRepository, password_hasher: PasswordHasherProto,
                 secret_key: str, algorithm: str, token_expires_in_minutes: float = 30) -> None:
        self._token_expires_in_minutes = token_expires_in_minutes
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def authenticate_user(self, form_data: OAuth2PasswordRequestForm) -> JWTToken:
        if not (user := await self._user_repository.get_user_by_username(form_data.username)):
            raise UserIsUnauthorized(hint=api_string_templates.INCORRECT_LOGIN_INPUT)

        if self._password_hasher.check_needs_rehash(user.password_hash):
            await self._user_repository.update_password_hash(
                new_pwd_hash=self._password_hasher.hash(form_data.password),
                user_id=user.id
            )

        try:
            self._password_hasher.verify(user.password_hash, form_data.password)
        except VerificationError:
            raise UserIsUnauthorized(hint=api_string_templates.INCORRECT_LOGIN_INPUT)

        return JWTToken(self._generate_jwt_token({
            "sub": form_data.username,
            "scopes": form_data.scopes,
        }))

    def _generate_jwt_token(self, token_payload: Dict[str, Any]) -> str:
        token_payload = {
            "exp": datetime.utcnow() + timedelta(self._token_expires_in_minutes),
            **token_payload
        }
        filtered_payload = {k: v for k, v in token_payload.items() if v is not None}
        return jwt.encode(filtered_payload, self._secret_key, algorithm=self._algorithm)
