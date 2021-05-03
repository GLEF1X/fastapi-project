import fastapi_jinja
import uvicorn

from api import endpoints, application, api_router
from data import config
from services import connect
from services.redis.containers import Application
from services.utils.other import setup_application
from views import home

app = setup_application()


def main():
    configure()
    uvicorn.run(app, debug=True)


def configure() -> None:
    configure_templates()
    configure_dependency_injector()
    configure_routes()


def configure_templates() -> None:
    fastapi_jinja.global_init(config.TEMPLATES_DIR)


def configure_routes() -> None:
    app.include_router(home.api_router, include_in_schema=False)
    app.include_router(api_router, include_in_schema=True)


def configure_dependency_injector():
    container = Application()
    container.config.from_dict(
        {
            "services": {
                "REDIS_PASSWORD": config.REDIS_PASSWORD,
                "REDIS_HOST": config.REDIS_HOST
            },
            "apis": {
                "QIWI_TOKEN": config.QIWI_API_TOKEN,
                "QIWI_SECRET": config.QIWI_SECRET
            }
        }
    )
    container.wire(packages=[endpoints], modules=[application])


@app.on_event('startup')
async def on_startup():
    await connect()


if __name__ == '__main__':
    main()
else:
    configure()
