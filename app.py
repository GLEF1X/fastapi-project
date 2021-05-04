from typing import Any

import fastapi_jinja
import uvicorn

from api_v1 import endpoints, application, api_router
from core.config import settings
from services.db.base import Database
from services.dependencies.containers import Application
from services.utils import security
from services.utils.api_installation import setup_application
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
    fastapi_jinja.global_init(settings.TEMPLATES_DIR)


def configure_routes() -> None:
    app.include_router(home.api_router, include_in_schema=False)
    app.include_router(api_router, include_in_schema=True)


def configure_dependency_injector():
    container = Application()
    container.config.from_dict(
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
    container.wire(packages=[endpoints], modules=[application, security])


@app.on_event('startup')
async def on_startup() -> Any:
    db = Database()
    await db.create_database()


if __name__ == '__main__':
    main()
else:
    configure()
