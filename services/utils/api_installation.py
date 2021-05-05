import types
from typing import NoReturn, Any, Optional, Dict, Tuple

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from api_v1 import endpoints, application, setup_routers
from core.config import settings
from middlewares.process_time_middleware import add_process_time_header
from services.abstracts import BaseAPIApplicationConfigBuilder
from services.db import Database
from services.dependencies.containers import Application
from services.utils import security
from views import home
from views.exception_handlers import http_405_exception_handler, \
    request_exception_handler, http_401_exception_handler
from views.home import api_router


async def on_startup() -> NoReturn:
    db = Database()
    await db.create_database()


class APIApplicationBuilder(BaseAPIApplicationConfigBuilder):
    """Class, that provides the installation of FastAPI application"""

    def __init__(
            self,
            additional_methods: Optional[Tuple[str]] = None
    ) -> None:
        super(APIApplicationBuilder, self).__init__()
        self.app = FastAPI(**settings.api_kwargs, exception_handlers={
            405: http_405_exception_handler,
            RequestValidationError: request_exception_handler,
            401: http_401_exception_handler
        })
        self._openapi_schema: Optional[Dict[str, Any]] = None
        self._container = Application()
        self.__additional_methods = additional_methods

    @property
    def methods_to_execute(self) -> Optional[Tuple[str]]:
        return self.__additional_methods

    def configure_openapi(self) -> NoReturn:
        """
        Method, which configure openapi schema

        :param app: instance of FastAPI
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

    def setup_middlewares(self) -> NoReturn:
        """
        Method, which setup middlewares

        :return:
        """
        self.app.add_middleware(BaseHTTPMiddleware,
                                dispatch=add_process_time_header)
        self.app.add_middleware(
            middleware_class=CORSMiddleware,
            allow_origins=settings.ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=settings.ALLOWED_METHODS,
            allow_headers=settings.ALLOWED_HEADERS,
            expose_headers=["User-Agent", "Authorization"]
        )

    def configure_routes(self) -> None:
        self.app.include_router(home.api_router, include_in_schema=False)
        self.app.include_router(api_router, include_in_schema=True)
        self.app.include_router(setup_routers(), include_in_schema=True)

    def configure_dependency_injector(self):
        self._container.config.from_dict(
            {
                "services": {
                    "REDIS_PASSWORD": settings.REDIS_PASSWORD,
                    "REDIS_HOST": settings.REDIS_HOST
                },
                "apis": {
                    "QIWI_TOKEN": settings.QIWI_API_TOKEN,
                    "QIWI_SECRET": settings.QIWI_SECRET
                }
            }
        )
        self._container.wire(
            packages=[endpoints],
            modules=[application, security]
        )

    def configure_event_handlers(self) -> NoReturn:
        self.app.add_event_handler("startup", on_startup)

    def print_hello_world(self):
        print("HELLO WORLD")


class Configurator:
    """
    Class, which is part of the pattern 'Builder'.   
    Sets up application, using a class of BaseAPIApplicationConfigBuilder inheritor,
    which is passed to it in the constructor
    
    """
    __slots__ = ('_builder', '__configured')

    def __init__(self, builder: BaseAPIApplicationConfigBuilder) -> None:
        if not isinstance(builder, BaseAPIApplicationConfigBuilder):
            raise Exception("You passed on invalid builder")
        self._builder = builder
        self.__configured = False

    @property
    def builder(self) -> BaseAPIApplicationConfigBuilder:
        return self._builder

    @builder.setter
    def builder(self, new_builder: BaseAPIApplicationConfigBuilder):
        self._builder = new_builder

    def configure(self) -> FastAPI:
        self._builder.configure_templates(settings.TEMPLATES_DIR)
        self._builder.configure_dependency_injector()
        self._builder.configure_routes()
        self._builder.setup_middlewares()
        self._builder.configure_event_handlers()
        self._execute_additional_methods()
        self.__configured = True
        return self._builder.app

    def _execute_additional_methods(self) -> None:
        cls_dict = self.builder.__class__.__dict__.values()
        [
            func(self.builder) for func in cls_dict if isinstance(
            func, types.FunctionType
        )
        ]

    def run_application(self, **kwargs) -> NoReturn:
        """
        Function, which start an application
        :param kwargs: key/value params for run application with uvicorn
        :return: None, just run application with uvicorn
        """
        if not self.__configured:
            raise Exception(
                "You didnt configure the application, so you cant run this"
            )
        uvicorn.run(self._builder.app, debug=True, **kwargs)


__all__ = ('Configurator', 'APIApplicationBuilder')
