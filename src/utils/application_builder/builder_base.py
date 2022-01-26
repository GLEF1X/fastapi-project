import abc

import fastapi_jinja
from fastapi import FastAPI

from src.config.config import Config


class AbstractFastAPIApplicationBuilder(metaclass=abc.ABCMeta):
    app: FastAPI

    def __init__(self, config: Config) -> None:
        self._config = config

    @abc.abstractmethod
    def configure_openapi_schema(self) -> None:
        pass

    @abc.abstractmethod
    def setup_middlewares(self) -> None:
        pass

    @abc.abstractmethod
    def configure_routes(self) -> None:
        pass

    @abc.abstractmethod
    def configure_events(self) -> None:
        pass

    @abc.abstractmethod
    def configure_exception_handlers(self) -> None:
        pass

    @abc.abstractmethod
    def configure_application_state(self) -> None:
        pass

    def configure_templates(self) -> None:
        fastapi_jinja.global_init(self._config.server.templates_dir)
