import contextlib
import typing

from sqlalchemy import insert, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from . import User, Product, UnableToDelete


class UserRepository:

    def __init__(
            self,
            session_factory: typing.Callable[
                ..., contextlib.AbstractAsyncContextManager[AsyncSession]
            ]
    ) -> None:
        self.session_factory = session_factory

    async def add(self, **kwargs: typing.Any) -> User:
        from services.utils.security import get_password_hash
        async with self.session_factory() as session:
            async with session.begin():
                session: AsyncSession
                query_insert = insert(User).values(
                    **kwargs
                ).returning(User)
                result = (await session.execute(
                    query_insert
                )).first()
                query_update = update(User).where(
                    User.id == result.id
                ).values(hashed_password=get_password_hash(result.password))
                await session.execute(query_update)
        return result

    async def select(
            self,
            username: typing.Optional[str] = None,
            user_id: typing.Optional[int] = None
    ) -> typing.Optional[User]:
        async with self.session_factory() as session:
            async with session.begin():
                basic_query = select(User)
                if user_id:
                    query = basic_query.where(User.id == user_id)
                if username:
                    query = basic_query.where(User.username == username)
                result = (await session.execute(query)).scalars().first()
        return result

    async def select_all(self) -> typing.Tuple[
        typing.List[typing.Optional[User]], int
    ]:
        async with self.session_factory() as session:
            async with session.begin():
                session: AsyncSession
                query = select(User).order_by(User.id)
                result = (await session.execute(query)).scalars().all()

        return result

    async def count(self) -> typing.Optional[int]:
        async with self.session_factory() as session:
            async with session.begin():
                session: AsyncSession
                count = (
                    await session.execute(
                        func.count(User.id))
                ).scalars().first()
        return count

    async def delete(self, user_id: int) -> None:
        async with self.session_factory() as session:
            async with session.begin():
                session: AsyncSession
                query_delete = delete(User).where(
                    User.id == user_id).returning(
                    User)
                result = (
                    await session.execute(query_delete)).scalars().first()
            if not isinstance(result, User):
                raise UnableToDelete()


class ProductRepository:

    def __init__(
            self,
            session_factory: typing.Callable[
                ..., contextlib.AbstractAsyncContextManager[AsyncSession]
            ]
    ) -> None:
        self.session_factory = session_factory

    async def add(self, **kwargs: typing.Any) -> Product:
        async with self.session_factory() as session:
            async with session.begin():
                query_insert = insert(Product).values(
                    **kwargs
                ).returning(Product)
                result = (await session.execute(
                    query_insert
                )).first()
        return result
