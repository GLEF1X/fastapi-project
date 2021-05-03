import typing

from sqlalchemy import insert, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .base import Session
from .models import *


async def add_user(**kwargs: typing.Any) -> User:
    async with Session.begin() as session:
        session: AsyncSession
        query_insert = insert(User).values(
            **kwargs
        ).returning(User)
        result = (await session.execute(
            query_insert
        )).first()
    return result


async def select_user(user_id: int) -> typing.Optional[User]:
    async with Session.begin() as session:
        session: AsyncSession
        query = select(User).where(User.id == user_id)
        result = (await session.execute(query)).scalars().first()
    return result


async def get_all_users() -> typing.Tuple[
    typing.List[typing.Optional[User]], int
]:
    async with Session.begin() as session:
        session: AsyncSession
        query = select(User).order_by(User.id)
        result = (await session.execute(query)).scalars().all()

    return result


async def count_users() -> typing.Optional[int]:
    async with Session.begin() as session:
        session: AsyncSession
        count = (await session.execute(func.count(User.id))).scalars().first()
    return count


async def add_product(**kwargs: typing.Any) -> Product:
    async with Session.begin() as session:
        session: AsyncSession
        query_insert = insert(Product).values(
            **kwargs
        ).returning(Product)
        result = (await session.execute(
            query_insert
        )).first()
    return result


__all__ = ('add_user', 'select_user', 'get_all_users')
