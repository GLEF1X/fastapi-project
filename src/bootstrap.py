from src.core import ApplicationSettings
from src.utils.gunicorn_app import StandaloneApplication
from src.utils.logging import LoggingConfig, configure_logging
from src.utils.other.api_installation import Director, DevelopmentApplicationBuilder


def run_application() -> None:
    """
    !NOT FOR PRODUCTION! \n
    Function, which start an application \n
    Instead of it use gunicorn with uvicorn workers. e.g. \n
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

    :return: None, just run application with uvicorn
    """
    settings = ApplicationSettings()
    log_config = configure_logging(LoggingConfig())
    director = Director(DevelopmentApplicationBuilder(settings=settings))
    app = director.build_app()
    options = {
        "bind": "%s:%s" % (settings.fastapi.HOST, settings.fastapi.PORT),
        "worker_class": "uvicorn.workers.UvicornWorker",
        "reload": True,
        "disable_existing_loggers": False,
        "preload_app": True,
        "logconfig_dict": log_config
    }
    gunicorn_app = StandaloneApplication(app, options)
    gunicorn_app.run()


if __name__ == "__main__":
    run_application()
