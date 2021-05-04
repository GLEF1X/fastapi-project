import pathlib
from typing import Optional, Dict, Any, List, Union

from fastapi import Body
from pydantic import (
    BaseSettings,
    Field,
    AnyHttpUrl,
    PostgresDsn,
    validator,
    Extra
)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
ENV_PATH = str(BASE_DIR / '.env')


class Settings(BaseSettings):
    # PostgreSQL db config
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASS: str = Field(..., env="DB_PASS")
    DB_HOST: Union[str, AnyHttpUrl] = Field(..., env="DB_HOST")
    DB_NAME: str = Field(..., env="DB_NAME")
    CONNECTION_URL: Optional[str] = None

    # FastApi config
    APP_NAME: str = Field(..., env="APP_NAME")
    API_VERSION: str = Field(..., env="API_VERSION")
    DOCS_URL: str = Field(..., env="DOCS_URL")
    REDOC_URL: str = Field(..., env="REDOC_URL")
    OPEN_API_ROOT: str = Field(..., env="DEFAULT_OPEN_API_ROOT")

    IS_PRODUCTION: str = Field(..., env="IS_PRODUCTION")

    TEMPLATES_DIR = str(BASE_DIR / "templates")

    # Redis config
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PASSWORD: str = Field(..., env="REDIS_PASSWORD")

    # Qiwi Config
    QIWI_SECRET: str = Field(..., env="QIWI_SECRET")
    QIWI_API_TOKEN: str = Field(..., env="QIWI_API_TOKEN")

    @validator("CONNECTION_URL", pre=True)
    def assemble_db_connection(cls, v: Optional[str],
                               values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        sync_connection_url = PostgresDsn.build(
            scheme="postgresql",
            user=values.get("DB_USER"),
            password=values.get("DB_PASS"),
            host=values.get("DB_HOST"),
            path=f"/{values.get('DB_NAME') or ''}",
        )
        return sync_connection_url.replace("postgresql", "postgresql+asyncpg")

    # Специальные настройки тегов для API
    tags_metadata: List[Dict[str, str]] = [
        {
            "name": "Users",
            "description": "Operations with users. The **login** logic is also here."
        },
        {
            "name": "Test",
            "description": "Test queries"
        },
        {
            "name": "Product",
            "description": "Operations with products."
        }
    ]

    # Настройки приложения FastAPI
    api_kwargs: Dict[str, Any] = {
        'debug': True,
        'title': APP_NAME,
        'version': API_VERSION,
        'docs_url': DOCS_URL,
        'redoc_url': REDOC_URL,
        'openapi_url': OPEN_API_ROOT if not IS_PRODUCTION else None,
        'openapi_tags': tags_metadata
    }

    PRODUCT_BODY: Any = Field(default=Body(..., example={
        "name": "Apple MacBook 15",
        "unit_price": 7000,
        "description": "Light and fast laptop",
        "size": "S"
    }))

    USER_BODY: Any = Field(default=Body(..., example={
        "first_name": "Gleb",
        "last_name": "Garanin",
        "username": "GLEF1X",
        "phone_number": "+7900232132",
        "email": "glebgar567@gmail.com",
        "password": "qwerty12345",
        "balance": 5
    }))

    ALLOWED_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "accept",
        "Accept-Encoding",
        "Content-Length",
        "Origin"
    ]

    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
    ]

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = Extra.allow


settings = Settings()

__all__ = ("BASE_DIR", "settings")
