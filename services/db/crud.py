import typing

from sqlalchemy import insert, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from . import User, Product, UnableToDelete
from .base import BaseRepo, Model


class UserRepository(BaseRepo[User]):
    model = User

    def __init__(self, session_or_pool: typing.Union[sessionmaker, AsyncSession]) -> None:
        super().__init__(session_or_pool)

    async def add(self, **kwargs: typing.Any) -> User:
        from services.utils.security import get_password_hash
        async with self.transaction:
            query_insert = insert(self.model).values(
                **kwargs
            ).returning(self.model)
            result = (await self.session.execute(
                query_insert
            )).first()
            query_update = update(self.model).where(
                self.model.id == result.id
            ).values(hashed_password=get_password_hash(result.password))
            await self.session.execute(query_update)
        return result

    async def select(
            self,
            username: typing.Optional[str] = None,
            user_id: typing.Optional[int] = None
    ) -> typing.Optional[Model]:
        async with self.transaction:
                basic_query = select(self.model)
                if user_id:
                    query = basic_query.where(self.model.id == user_id)
                if username:
                    query = basic_query.where(self.model.username == username)
                result = (await self.session.execute(query)).scalars().first()
        return result

    async def select_all(self) -> typing.Tuple[
        typing.List[typing.Optional[Model]], int
    ]:
        async with self.transaction:
            query = select(self.model).order_by(User.id)
            result = (await self.session.execute(query)).scalars().all()

        return result

    async def count(self) -> typing.Optional[int]:
        async with self.transaction:
            count = (
                await self.session.execute(
                    func.count(self.model.id))
            ).scalars().first()
        return count

    async def delete_by_user_id(self, user_id: int) -> None:
        async with self.transaction:
            query_delete = delete(self.model).where(
                User.id == user_id).returning(
                User)
            result = (
                await self.session.execute(query_delete)).scalars().first()
        if not isinstance(result, User):
            raise UnableToDelete()

    def __call__(self, *args, **kwargs):
        return self


class ProductRepository(BaseRepo[Product]):
    model = Product

    def __init__(self, session_or_pool: typing.Union[sessionmaker, AsyncSession]) -> None:
        super().__init__(session_or_pool)

    async def add(self, **kwargs: typing.Any) -> Product:
        async with self.transaction:
            query_insert = insert(Product).values(
                **kwargs
            ).returning(Product)
            result = (await self.session.execute(
                query_insert
            )).first()
        return result
