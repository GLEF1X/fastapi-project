import typing

from sqlalchemy import insert

from .base import Session
from .models import *


async def add_user(**kwargs: typing.Any) -> User:
    async with Session.begin() as session:
        query_insert = insert(User).values(
            **kwargs
        ).returning(User)
        result = await session.execute(
            query_insert
        )
        return result.first()


__all__ = ('add_user',)
