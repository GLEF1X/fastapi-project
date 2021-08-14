#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from typing import Callable, Coroutine, Any

from fastapi import FastAPI


# noinspection PyUnusedLocal
def create_on_startup_handler(app: FastAPI) -> Callable[..., Coroutine[Any, Any, None]]:
    async def on_startup() -> None:
        ...

    return on_startup


def create_on_shutdown_handler(app: FastAPI) -> Callable[..., Coroutine[Any, Any, None]]:
    async def on_shutdown() -> None:
        await app.state.db_components.engine.dispose()

    return on_shutdown
