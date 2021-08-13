#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from typing import Callable, Type, Union

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from services.database.repositories.base import BaseRepository


def _get_db_pool(request: Request) -> Union[AsyncSession, sessionmaker]:
    return request.app.state.pool


def get_repository(repo_type: Type[BaseRepository]) -> Callable[[Union[AsyncSession, sessionmaker]], BaseRepository]:
    def _get_repo(conn: Union[AsyncSession, sessionmaker] = Depends(_get_db_pool)) -> BaseRepository:
        return repo_type(conn)

    return _get_repo
