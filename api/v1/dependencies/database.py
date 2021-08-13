#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from typing import Callable, Type, cast

from fastapi import Depends
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from services.database.repositories.base import BaseRepository


def _get_session_maker(request: Request) -> sessionmaker:
    return cast(sessionmaker, request.app.state.db_components.sessionmaker)


def get_repository(repo_type: Type[BaseRepository]) -> Callable[[sessionmaker], BaseRepository]:
    def _get_repo(conn: sessionmaker = Depends(_get_session_maker)) -> BaseRepository:
        return repo_type(conn)

    return _get_repo
