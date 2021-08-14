import abc
from typing import Any, Optional

import fastapi_jinja
from fastapi import FastAPI

from src.core import ApplicationSettings
from src.core.settings import TEMPLATES_DIR


class BaseApplicationBuilder(abc.ABC):
    app: FastAPI

    def __init__(self) -> None:
        self._settings = ApplicationSettings()

    @abc.abstractmethod
    def configure(self) -> Optional[Any]:
        raise NotImplementedError

    @staticmethod
    def configure_templates() -> None:
        fastapi_jinja.global_init(TEMPLATES_DIR)
