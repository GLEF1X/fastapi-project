import dataclasses
import logging.config
from typing import Callable, Union, Dict, Any, Optional

import orjson
import sentry_sdk
import structlog
from sqlalchemy import log as sa_log
from structlog_sentry import SentryProcessor

ProcessorType = Callable[
    [
        structlog.types.WrappedLogger, str, structlog.types.EventDict
    ], Union[str, bytes]
]


@dataclasses.dataclass()
class LoggingConfig:
    render_json_logs: bool = False
    disable_sqlalchemy_repetetive_logs: bool = True
    sentry_dsn: Optional[str] = None


class RenderProcessorFactory:

    def __init__(self, render_json_logs: bool = False,
                 serializer: Callable[..., Union[str, bytes]] = orjson.dumps):
        self._render_json_logs = render_json_logs
        self._serializer = serializer

    def get_processor(self) -> ProcessorType:
        if self._render_json_logs:
            return structlog.processors.JSONRenderer(serializer=self._serializer)
        else:
            return structlog.dev.ConsoleRenderer()


def configure_logging(cfg: LoggingConfig) -> Dict[str, Any]:
    if cfg.sentry_dsn is not None:
        sentry_sdk.init(cfg.sentry_dsn, traces_sample_rate=1.0)
    if cfg.disable_sqlalchemy_repetetive_logs:
        sa_log._add_default_handler = lambda _: None  # type: ignore
    render_processor = RenderProcessorFactory(cfg.render_json_logs).get_processor()
    time_stamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        structlog.stdlib.add_log_level,
        time_stamper,
        SentryProcessor(level=logging.ERROR),
    ]
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processors": [
                    structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    render_processor,
                ],
                "foreign_pre_chain": pre_chain,
            },
        },
        "handlers": {
            "default": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": "DEBUG",
                "propagate": True,
            },
            "gunicorn.access": {"handlers": ["default"]},
            "gunicorn.error": {"handlers": ["default"]},
            "uvicorn.access": {"handlers": ["default"]},
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["default"]
        },
    }
    logging.config.dictConfig(config)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            time_stamper,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.AsyncBoundLogger,  # type: ignore  # noqa
        cache_logger_on_first_use=True,
    )
    return config
