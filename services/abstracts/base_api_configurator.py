import abc
from typing import NoReturn, Optional

import fastapi_jinja
from fastapi import FastAPI


class BaseAPIApplicationConfigBuilder(abc.ABC):

    def __init__(self) -> None:
        self.app: Optional[FastAPI] = None

    @abc.abstractmethod
    def configure_routes(self) -> NoReturn:
        raise NotImplementedError

    def setup_middlewares(self) -> NoReturn:
        """If you need to setup some middlewares"""

    @staticmethod
    def configure_templates(templates_dir: str) -> NoReturn:
        fastapi_jinja.global_init(templates_dir)

    def configure_dependency_injector(self) -> NoReturn:
        """ Configure dependencies """

    def configure_event_handlers(self) -> NoReturn:
        """
        In this method you should to configure events like
        'shutdown' and 'startup'
        """
