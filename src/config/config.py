import pathlib
import secrets
from typing import Dict, Any, List, Union

from attr import Factory
from attrs import define, field
from omegaconf import MISSING
from pydantic import PostgresDsn

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


def _make_fastapi_instance_kwargs(settings: "ServerSettings") -> Dict[str, Any]:
    if (
            settings.app_title == MISSING or
            settings.project_version == MISSING or
            settings.docs_url == MISSING or
            settings.redoc_url == MISSING or
            settings):
        return {}

    return {
        "debug": True,
        "title": settings.app_title,
        "version": settings.project_version,
        "docs_url": settings.docs_url,
        "redoc_url": settings.redoc_url,
        "openapi_url": settings.openapi_root
        if not settings.is_in_prod
        else "/openapi.json",
    }


@define
class DatabaseSettings:
    user: str = MISSING
    password: str = MISSING
    host: str = MISSING
    db_name: str = MISSING

    connection_uri: str = field(default="")

    def __attrs_post_init__(self) -> None:
        sync_connection_url = PostgresDsn.build(
            scheme="postgresql",
            user=self.user,
            password=self.password,
            host=self.host,
            path=f"/{self.db_name or ''}",
        )
        # Get asyncpg+postgresql link to connect
        self.connection_uri = sync_connection_url.replace("postgresql", "postgresql+asyncpg")




@define
class SecuritySettings:
    jwt_secret_key: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    jwt_access_token_expire_in_minutes: int = 60 * 24 * 8


@define
class ServerSettings:
    app_title: str = MISSING
    project_version: str = MISSING
    docs_url: str = MISSING
    redoc_url: str = MISSING
    openapi_root: str = MISSING
    is_in_prod: bool = MISSING
    templates_dir: str = (BASE_DIR / "src" / "templates")
    api_path_prefix: str = "/api/v1"

    host: str = MISSING
    port: int = MISSING

    fastapi_instance_kwargs: Dict[str, Any] = Factory(_make_fastapi_instance_kwargs, takes_self=True)
    security: SecuritySettings = SecuritySettings()

    allowed_headers: List[str] = [
        "Content-Type",
        "Authorization",
        "accept",
        "Accept-Encoding",
        "Content-Length",
        "Origin",
    ]

    backend_cors_origins: List[str] = field(
        default=["http://localhost", "http://localhost:4200", "http://localhost:3000", ]
    )


@define
class RabbitMQSettings:
    uri: str = MISSING


@define
class ExternalAPISettings:
    QIWI_SECRET: str = MISSING
    QIWI_API_TOKEN: str = MISSING
    PHONE_NUMBER: str = MISSING


@define
class Config:
    database: DatabaseSettings = DatabaseSettings()
    server: ServerSettings = ServerSettings()
    external_api: ExternalAPISettings = ExternalAPISettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
