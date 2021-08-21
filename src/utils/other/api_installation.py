import logging
from typing import Any, Optional, Dict, no_type_check

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api import setup_routers
from src.api.v1.dependencies.database import UserRepositoryDependencyMarker, ProductRepositoryDependencyMarker
from src.api.v1.dependencies.security import JWTBasedOAuth, AuthenticationDependencyMarker
from src.api.v1.errors.http_error import http_error_handler
from src.api.v1.errors.validation_error import http422_error_handler
from src.core import ApplicationSettings
from src.core.events import create_on_startup_handler, create_on_shutdown_handler
from src.middlewares.process_time_middleware import add_process_time_header
from src.services.database.models.base import DatabaseComponents
from src.services.database.repositories.product import ProductRepository
from src.services.database.repositories.user import UserRepository
from src.utils.jwt import SECRET_KEY
from src.utils.logging_ import CustomizeLogger
from src.utils.other.builder_base import AbstractFastAPIApplicationBuilder
from src.views import setup_routes

ALLOWED_METHODS = ["POST", "PUT", "DELETE", "GET"]


class DevelopmentApplicationBuilder(AbstractFastAPIApplicationBuilder):
    """Class, that provides the installation of FastAPI application"""

    def __init__(self, settings: ApplicationSettings) -> None:
        super(DevelopmentApplicationBuilder, self).__init__(settings=settings)
        self.app: FastAPI = FastAPI(**self._settings.fastapi.api_kwargs)  # type: ignore
        self.app.settings = self._settings  # type: ignore
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
            allow_origins=self._settings.fastapi.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=ALLOWED_METHODS,
            allow_headers=self._settings.fastapi.BACKEND_CORS_ORIGINS,
            expose_headers=["User-Agent", "Authorization"],
        )
        self.app.add_middleware(middleware_class=SessionMiddleware, secret_key=SECRET_KEY)

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
        components = DatabaseComponents(drivername="postgresql+asyncpg",
                                        username=self._settings.database.USER,
                                        password=self._settings.database.PASS,
                                        host=self._settings.database.HOST,
                                        database=self._settings.database.NAME)
        self.app.state.db_components = components  # do gracefully dispose engine on shutdown application
        self.app.state.settings = self._settings
        self.app.dependency_overrides.update(
            {
                UserRepositoryDependencyMarker: lambda: UserRepository(components.sessionmaker),
                ProductRepositoryDependencyMarker: lambda: ProductRepository(components.sessionmaker),
                AuthenticationDependencyMarker: lambda: JWTBasedOAuth(UserRepository(components.sessionmaker))
            }
        )


class DevelopmentApplicationBuilderLoggedProxy(AbstractFastAPIApplicationBuilder):

    def __init__(self, settings: ApplicationSettings, logger: Optional[logging.Logger] = None) -> None:
        super(DevelopmentApplicationBuilderLoggedProxy, self).__init__(settings)
        self._underlying_builder = DevelopmentApplicationBuilder(settings=settings)
        self.app = self._underlying_builder.app
        if logger is None:
            self.app.state.logger = CustomizeLogger.make_logger(
                config_path=settings.system_settings.LOGGING_CONFIG_PATH,
                to_disable=["uvicorn.access", "uvicorn.asgi", "uvicorn.error"]
            )
        else:
            self.app.state.logger = logger

    def configure_openapi_schema(self) -> None:
        self.app.state.logger.info("Configuring API schema")
        self._underlying_builder.configure_openapi_schema()
        self.app.state.logger.info("API schema configured successfully")

    def setup_middlewares(self) -> None:
        self.app.state.logger.info("Configuring middlewares")
        self._underlying_builder.setup_middlewares()
        self.app.state.logger.info("Middlewares configured successfully")

    def configure_routes(self) -> None:
        self.app.state.logger.info("Configuring routes")
        self._underlying_builder.configure_routes()
        self.app.state.logger.info("Routes configured successfully")

    def configure_events(self) -> None:
        self.app.state.logger.info("Configuring events")
        self._underlying_builder.configure_events()
        self.app.state.logger.info("Events configured successfully")

    def configure_exception_handlers(self) -> None:
        self.app.state.logger.info("Configuring exception handlers")
        self._underlying_builder.configure_exception_handlers()
        self.app.state.logger.info("Exception handlers configured successfully")

    def configure_application_state(self) -> None:
        self.app.state.logger.info("Configuring application state and DI")
        self._underlying_builder.configure_application_state()
        self.app.state.logger.info("Application state and DI configured successfully")


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


__all__ = ("Director", "DevelopmentApplicationBuilder", "DevelopmentApplicationBuilderLoggedProxy")
