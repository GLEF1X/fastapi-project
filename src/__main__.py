import pathlib
from typing import Union

import cattrs
from omegaconf import OmegaConf

from src.config.config import Config, BASE_DIR
from src.utils.application_builder.api_installation import Director, DevelopmentApplicationBuilder
from src.utils.gunicorn_app import StandaloneApplication
from src.utils.logging import LoggingConfig, configure_logging


def run_application() -> None:
    config = _parse_config(BASE_DIR / "src" / "config" / "config.yaml")
    stdlib_logconfig_dict = configure_logging(LoggingConfig())
    director = Director(DevelopmentApplicationBuilder(config=config))
    app = director.build_app()
    options = {
        "bind": "%s:%s" % (config.server.host, config.server.port),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "reload": True,
        "disable_existing_loggers": False,
        "preload_app": True,
        "logconfig_dict": stdlib_logconfig_dict
    }
    gunicorn_app = StandaloneApplication(app, options)
    gunicorn_app.run()


def _parse_config(path_to_config: Union[str, pathlib.Path]) -> Config:
    dictionary_config = OmegaConf.to_container(OmegaConf.merge(
        OmegaConf.load(path_to_config),
        OmegaConf.structured(Config)
    ), resolve=True)
    return cattrs.structure(dictionary_config, Config)


if __name__ == "__main__":
    run_application()
