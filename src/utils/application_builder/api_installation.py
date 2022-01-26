import contextlib
from typing import Any, Optional, Dict, no_type_check

from argon2 import PasswordHasher
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from starlette.config import Config as StarletteConfig
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api import setup_routers
from src.api.v1.dependencies.database import UserRepositoryDependencyMarker, ProductRepositoryDependencyMarker
from src.api.v1.dependencies.services import SecurityGuardServiceDependencyMarker, \
    ServiceAuthorizationDependencyMarker, OAuthServiceDependencyMarker, RPCDependencyMarker
from src.api.v1.errors.http_error import http_error_handler
from src.api.v1.errors.validation_error import http422_error_handler
from src.config.config import Config, BASE_DIR
from src.core.events import create_on_startup_handler, create_on_shutdown_handler
from src.middlewares.process_time_middleware import add_process_time_header
from src.services.amqp.mailing import send_email
from src.services.amqp.rpc import RabbitMQService, Consumer
from src.services.database.models.base import DatabaseComponents
from src.services.database.repositories.product_repository import ProductRepository
from src.services.database.repositories.user_repository import UserRepository
from src.services.security.jwt_service import JWTSecurityGuardService, JWTAuthenticationService
from src.services.security.oauth import OAuthSecurityService, OAuthIntegration
from src.utils.application_builder.builder_base import AbstractFastAPIApplicationBuilder
from src.views import setup_routes

ALLOWED_METHODS = ["POST", "PUT", "DELETE", "GET"]


class DevelopmentApplicationBuilder(AbstractFastAPIApplicationBuilder):
    """Class, that provides the installation of FastAPI application"""

    def __init__(self, config: Config) -> None:
        super(DevelopmentApplicationBuilder, self).__init__(config=config)
        self.app: FastAPI = FastAPI(**self._config.server.fastapi_instance_kwargs)  # type: ignore
        self.app.config = self._config  # type: ignore
        self._openapi_schema: Optional[Dict[str, Any]] = None

    def configure_openapi_schema(self) -> None:
        self._openapi_schema = get_openapi(
            title="GLEF1X API",
            version="0.0.1",
            description="This is a very custom OpenAPI schema",
            routes=self.app.routes,
        )
        self._openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        self.app.openapi_schema = self._openapi_schema

    @no_type_check
    def setup_middlewares(self):
        self.app.add_middleware(BaseHTTPMiddleware, dispatch=add_process_time_header)
        self.app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=self._config.server.backend_cors_origins,
            allow_credentials=True,
            allow_methods=ALLOWED_METHODS,
            allow_headers=self._config.server.backend_cors_origins,
            expose_headers=["User-Agent", "Authorization"],
        )
        self.app.add_middleware(
            middleware_class=SessionMiddleware,
            secret_key="!secret"
        )  # TODO replace with real token

    @no_type_check
    def configure_routes(self):
        setup_routes(self.app)
        self.app.include_router(setup_routers())

    def configure_events(self) -> None:
        self.app.add_event_handler("startup", create_on_startup_handler(self.app))
        self.app.add_event_handler("shutdown", create_on_shutdown_handler(self.app))

    def configure_exception_handlers(self) -> None:
        self.app.add_exception_handler(RequestValidationError, http422_error_handler)
        self.app.add_exception_handler(HTTPException, http_error_handler)

    def configure_application_state(self) -> None:
        db_components = DatabaseComponents(self._config.database.connection_uri)
        # do gracefully dispose engine on shutdown application
        self.app.state.db_components = db_components
        self.app.state.config = self._config

        pwd_hasher = PasswordHasher()
        rmq_service = RabbitMQService(
            self._config.rabbitmq.uri,
            Consumer(name="send_email", callback=send_email)
        )

        async def rmq_service_spin_up():
            async with rmq_service as rpc:
                yield rpc

        self.app.dependency_overrides.update(
            {
                UserRepositoryDependencyMarker: lambda: UserRepository(
                    db_components.sessionmaker, pwd_hasher
                ),
                ProductRepositoryDependencyMarker: lambda: ProductRepository(db_components.sessionmaker),
                OAuthServiceDependencyMarker: lambda: OAuthSecurityService(
                    StarletteConfig(BASE_DIR / ".env"),
                    OAuthIntegration(
                        name='google',
                        overwrite=False,
                        kwargs=dict(
                            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
                            client_kwargs={
                                'scope': 'openid email profile'
                            }
                        )
                    )
                ),
                SecurityGuardServiceDependencyMarker: lambda: JWTSecurityGuardService(
                    oauth2_scheme=OAuth2PasswordBearer(
                        tokenUrl="/api/v1/oauth",
                        scopes={
                            "me": "Read information about the current user.",
                            "items": "Read items."
                        },
                    ),
                    user_repository=UserRepository(db_components.sessionmaker, pwd_hasher),
                    password_hasher=pwd_hasher,
                    secret_key=self._config.server.security.jwt_secret_key,
                    algorithm="HS256"
                ),
                ServiceAuthorizationDependencyMarker: lambda: JWTAuthenticationService(
                    user_repository=UserRepository(db_components.sessionmaker, pwd_hasher),
                    password_hasher=pwd_hasher,
                    secret_key=self._config.server.security.jwt_secret_key,
                    algorithm="HS256",
                    token_expires_in_minutes=self._config.server.security.jwt_access_token_expire_in_minutes
                ),
                RPCDependencyMarker: rmq_service_spin_up
            }
        )


class Director:
    def __init__(self, builder: AbstractFastAPIApplicationBuilder) -> None:
        if not isinstance(builder, AbstractFastAPIApplicationBuilder):
            raise TypeError("You passed on invalid builder")
        self._builder = builder

    @property
    def builder(self) -> AbstractFastAPIApplicationBuilder:
        return self._builder

    @builder.setter
    def builder(self, new_builder: AbstractFastAPIApplicationBuilder):
        self._builder = new_builder

    def build_app(self) -> FastAPI:
        self.builder.configure_routes()
        self.builder.setup_middlewares()
        self.builder.configure_application_state()
        self.builder.configure_templates()
        self.builder.configure_exception_handlers()
        # We run `configure_events(...)` in the end of configure method, because we need to pass to on_shutdown and
        # on_startup handlers configured application
        self.builder.configure_events()
        return self.builder.app


__all__ = ("Director", "DevelopmentApplicationBuilder")
