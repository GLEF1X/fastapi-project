from typing import Any, Optional, Dict, no_type_check

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from src.api import setup_routers
from src.api.v1.dependencies.database import UserRepositoryDependencyMarker, ProductRepositoryDependencyMarker
from src.api.v1.dependencies.security import JWTBasedAuthenticationImpl, AuthenticationProto
from src.api.v1.errors.http_error import http_error_handler
from src.api.v1.errors.validation_error import http422_error_handler
from src.core.events import create_on_startup_handler, create_on_shutdown_handler
from src.middlewares.process_time_middleware import add_process_time_header
from src.services.database.models.base import DatabaseComponents
from src.services.database.repositories.product import ProductRepository
from src.services.database.repositories.user import UserRepository
from src.services.utils.other.builder_base import BaseApplicationBuilder
from views import home
from views.home import api_router

ALLOWED_METHODS = ["POST", "PUT", "DELETE", "GET"]


class DevelopmentApplicationBuilder(BaseApplicationBuilder):
    """Class, that provides the installation of FastAPI application"""

    def __init__(self) -> None:
        super(DevelopmentApplicationBuilder, self).__init__()
        self.app = FastAPI(**self._settings.fastapi.api_kwargs)  # type: ignore
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

    @no_type_check
    def configure_routes(self):
        self.app.include_router(home.api_router, include_in_schema=False)
        self.app.include_router(api_router)
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
                AuthenticationProto: lambda: JWTBasedAuthenticationImpl()
            }
        )

    def configure(self) -> None:
        self.configure_routes()
        self.setup_middlewares()
        self.configure_application_state()
        self.configure_templates()
        self.configure_exception_handlers()
        # We run `configure_events(...)` in the end of configure method, because we need to pass to on_shutdown and
        # on_startup handlers configured application
        self.configure_events()


class Director:
    def __init__(self, builder: BaseApplicationBuilder) -> None:
        if not isinstance(builder, BaseApplicationBuilder):
            raise TypeError("You passed on invalid builder")
        self._builder = builder

    @property
    def builder(self) -> BaseApplicationBuilder:
        return self._builder

    @builder.setter
    def builder(self, new_builder: BaseApplicationBuilder):
        self._builder = new_builder

    def configure(self) -> FastAPI:
        self._builder.configure()
        return self.builder.app

    def run(self, **kwargs) -> None:
        """
        !NOT FOR PRODUCTION! \n
        Function, which start an application \n
        Instead of it use gunicorn with uvicorn workers. e.g. \n
        gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

        :return: None, just run application with uvicorn
        """
        uvicorn.run(self._builder.app, **kwargs)  # type: ignore  # noqa


__all__ = ("Director", "DevelopmentApplicationBuilder")
