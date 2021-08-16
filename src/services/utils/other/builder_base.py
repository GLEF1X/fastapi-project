import abc

import fastapi_jinja
from fastapi import FastAPI

from src.core import ApplicationSettings
from src.core.settings import TEMPLATES_DIR


class AbstractFastAPIApplicationBuilder(metaclass=abc.ABCMeta):

    def __init__(self, settings: ApplicationSettings) -> None:
        self._settings = settings
        self.app: FastAPI = FastAPI(**self._settings.fastapi.api_kwargs)  # type: ignore
        self.app.settings = self._settings  # type: ignore

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

    @staticmethod
    def configure_templates() -> None:
        fastapi_jinja.global_init(TEMPLATES_DIR)
