import fastapi_jinja
import uvicorn
from fastapi import FastAPI

import services
from data import config
from views import home, api

api_kwargs = {
    'debug': True,
    'title': config.APP_NAME,
    'version': config.API_VERSION,
    'docs_url': config.DOCS_URL,
    'redoc_url': config.REDOC_URL,
    'openapi_url': config.OPEN_API_ROOT if not config.IS_PRODUCTION else None
}

app = FastAPI(**api_kwargs)


def main():
    configure()
    uvicorn.run(app, debug=True)


def configure() -> None:
    configure_templates()
    configure_routes()


def configure_templates() -> None:
    fastapi_jinja.global_init(config.TEMPLATES_DIR)


def configure_routes() -> None:
    app.include_router(home.api_router, include_in_schema=False)
    app.include_router(api.api_router, include_in_schema=True)


@app.on_event('startup')
async def on_startup():
    await services.connect()


if __name__ == '__main__':
    main()
else:
    configure()
