#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import functools

from fastapi import FastAPI


def create_on_startup_handler(app: FastAPI):
    # noinspection PyUnusedLocal
    async def on_startup(application: FastAPI) -> None:
        ...

    return functools.partial(on_startup, application=app)


def create_on_shutdown_handler(app: FastAPI):
    async def on_shutdown(application: FastAPI) -> None:
        await application.state.components.engine.dispose()

    return functools.partial(on_shutdown, application=app)
