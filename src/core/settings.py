from __future__ import annotations

import pathlib
import secrets
from functools import lru_cache
from typing import Optional, Dict, Any, List, Union, TypeVar

from pydantic import BaseSettings, Field, AnyHttpUrl, PostgresDsn, validator, EmailStr

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
ENV_PATH = str(BASE_DIR / ".env")
TEMPLATES_DIR = str(BASE_DIR / "src" / "templates")
T = TypeVar("T")


@lru_cache()
def get_settings() -> ApplicationSettings:
    return ApplicationSettings()


class DatabaseSettings(BaseSettings):
    USER: str = Field(..., env="POSTGRES_USER")
    PASS: str = Field(..., env="POSTGRES_PASSWORD")
    HOST: Union[str, AnyHttpUrl] = Field(..., env="POSTGRES_HOST")
    NAME: str = Field(..., env="POSTGRES_DB")
    # Here is type str instead of PostgresDsn, because PostgresDsn does not support asyncpg+postgresql connection
    CONNECTION_URL: Optional[str] = None

    @validator("CONNECTION_URL", pre=True)
    def assemble_db_connection_url(cls, v: T, values: Dict[str, Any]) -> T:
        if isinstance(v, PostgresDsn):
            return v
        sync_connection_url = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("USER"),
            password=values.get("PASS"),
            host=values.get("HOST"),
            path=f"/{values.get('NAME') or ''}",
        )
        # Get asyncpg+postgresql link to connect
        return sync_connection_url.replace("postgresql", "postgresql+asyncpg")

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


class FastAPISettings(BaseSettings):
    APP_NAME: str = Field(..., env="APP_NAME")
    API_VERSION: str = Field(..., env="API_VERSION")
    DOCS_URL: str = Field(..., env="DOCS_URL")
    REDOC_URL: str = Field(..., env="REDOC_URL")
    OPEN_API_ROOT: str = Field(..., env="DEFAULT_OPEN_API_ROOT")
    IS_PRODUCTION: str = Field(..., env="IS_PRODUCTION")
    TEMPLATES_DIR: str = str(BASE_DIR / "templates")

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    api_kwargs: Optional[Dict[str, Any]] = None

    @validator("api_kwargs", pre=True)
    def set_api_kwargs(
            cls, v: Optional[Dict[str, Any]], values: Dict[str, Any]
    ) -> Union[dict, Dict[str, Optional[bool]]]:
        if isinstance(v, dict):
            return v
        return {
            "debug": True,
            "title": values.get("APP_NAME"),
            "version": values.get("API_VERSION"),
            "docs_url": values.get("DOCS_URL"),
            "redoc_url": values.get("REDOC_URL"),
            "openapi_url": values.get("OPEN_API_ROOT")
            if not values.get("IS_PRODUCTION")
            else "/openapi.json",
            "openapi_tags": values.get("tags_metadata"),
        }

    ALLOWED_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "accept",
        "Accept-Encoding",
        "Content-Length",
        "Origin",
    ]

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",  # type: ignore
        "http://localhost:4200",  # type: ignore
        "http://localhost:3000",  # type: ignore
    ]  # type: ignore

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


class RedisSettings(BaseSettings):
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PASSWORD: str = Field(..., env="REDIS_PASSWORD")

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


class APIServicesSettings(BaseSettings):
    QIWI_SECRET: Optional[str] = Field(None, env="QIWI_SECRET")
    QIWI_API_TOKEN: Optional[str] = Field(None, env="QIWI_API_TOKEN")
    PHONE_NUMBER: Optional[str] = Field(None, env="PHONE_NUMBER")

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


class TestSettings(BaseSettings):
    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr = "superuser@example.com"  # type: ignore
    FIRST_SUPERUSER_PASSWORD: str = "secret_password_12345"
    USERS_OPEN_REGISTRATION: bool = False


class SystemSettings(BaseSettings):
    BASE_DIR: pathlib.Path = pathlib.Path(__name__).parent.parent
    LOGGING_CONFIG_PATH: pathlib.Path = BASE_DIR / "logging_config.json"


class ApplicationSettings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    fastapi: FastAPISettings = FastAPISettings()  # noqa
    redis: RedisSettings = RedisSettings()
    api: APIServicesSettings = APIServicesSettings()
    tests: TestSettings = TestSettings()
    system_settings: SystemSettings = SystemSettings()

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"


__all__ = ("BASE_DIR", "ApplicationSettings", "TEMPLATES_DIR", "get_settings")
