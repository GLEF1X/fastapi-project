import sys
from typing import Any, Optional, Dict, no_type_check

import uvicorn
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from api import setup_routers
from api.v1 import endpoints, not_for_production
from api.v1.endpoints import basic
from middlewares.process_time_middleware import add_process_time_header
from services.database.models.base import DatabaseComponents
from services.dependencies.containers import Application
from services.utils import security
from services.utils.other.builder_base import BaseApplicationConfiguratorBuilder
from views import home
from views.home import api_router

ALLOWED_METHODS = ["POST", "PUT", "DELETE", "GET"]


@inject
async def on_startup(db: DatabaseComponents = Provide[Application.services.db]) -> None:
    # await db.recreate()
    ...


class ApplicationConfiguratorBuilder(BaseApplicationConfiguratorBuilder):
    """Class, that provides the installation of FastAPI application"""

    def __init__(self) -> None:
        super(ApplicationConfiguratorBuilder, self).__init__()
        self.app = FastAPI(**self._settings.fastapi.api_kwargs)  # type: ignore
        self.app.settings = self._settings  # type: ignore

        self._openapi_schema: Optional[Dict[str, Any]] = None
        self._container = Application()

    def configure_openapi(self) -> None:
        """
        Method, which configure openapi schema

        :return: configured instance of FastAPI
        """
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
        """
        Method, which setup middlewares

        :return:
        """
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
        self.app.add_event_handler("startup", on_startup)

    def configure_application_state(self):
        components = DatabaseComponents(drivername="postgresql+asyncpg",
                                        username=self._settings.database.USER,
                                        password=self._settings.database.PASS,
                                        host=self._settings.database.HOST,
                                        database=self._settings.database.NAME)
        self.app.state.pool = components.sessionmaker

    def configure(self) -> None:
        self.configure_routes()
        self.setup_middlewares()
        self.configure_application_state()
        self.configure_events()
        self.configure_templates()


class Director:
    def __init__(self, builder: BaseApplicationConfiguratorBuilder) -> None:
        if not isinstance(builder, BaseApplicationConfiguratorBuilder):
            raise TypeError("You passed on invalid builder")
        self._builder = builder

    @property
    def builder(self) -> BaseApplicationConfiguratorBuilder:
        return self._builder

    @builder.setter
    def builder(self, new_builder: BaseApplicationConfiguratorBuilder):
        self._builder = new_builder

    def configure(self) -> FastAPI:
        self._builder.configure()
        return self.builder.app

    def run(self, **kwargs) -> None:
        """
        !NOT FOR PRODUCTION! \n
        Function, which start an application

        :return: None, just run application with uvicorn
        """
        uvicorn.run(self._builder.app, **kwargs)  # type: ignore  # noqa


__all__ = ("Director", "ApplicationConfiguratorBuilder")
