import pathlib
import secrets
from typing import Dict, Any, List

from attrs import define, field
from omegaconf import MISSING

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


@define
class DatabaseSettings:
    user: str = MISSING
    password: str = MISSING
    host: str = "localhost"
    db_name: str = "postgres"

    connection_uri: str = field(default=MISSING)
    conn_kwargs: Dict[Any, Any] = MISSING


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
    templates_dir: str = (BASE_DIR / "templates")
    api_path_prefix: str = "/api/v1"

    host: str = MISSING
    port: int = MISSING

    api_kwargs: Dict[str, Any] = field(default=MISSING)
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
class ExternalAPISettings:
    QIWI_SECRET: str = MISSING
    QIWI_API_TOKEN: str = MISSING
    PHONE_NUMBER: str = MISSING


@define
class Config:
    database: DatabaseSettings = DatabaseSettings()
    server: ServerSettings = ServerSettings()
    external_api: ExternalAPISettings = ExternalAPISettings()
