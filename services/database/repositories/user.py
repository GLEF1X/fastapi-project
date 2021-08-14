import typing

from sqlalchemy import insert, delete

from services.database.exceptions import UnableToDelete
from services.database.models import User
from services.database.repositories.base import BaseRepository, Model
from services.database.utils import wrap_result


class UserRepository(BaseRepository[User]):
    model = User

    async def add(self, **kwargs: typing.Any) -> Model:
        from api.v1.dependencies.security import get_password_hash

        async with self._transaction:
            hashed_password = get_password_hash(kwargs.pop("password"))
            stmt = insert(self.model).values(**kwargs, password=hashed_password).returning(self.model)
            result = (await self._session.execute(stmt)).first()
        return typing.cast(Model, result)

    async def delete_by_user_id(self, user_id: int) -> None:
        async with self._transaction:
            query_delete = delete(self.model).where(User.id == user_id).returning(User)
            result = (await self._session.execute(query_delete)).scalars().first()
        if not isinstance(result, User):
            raise UnableToDelete()

    async def get_user_by_username(self, username: str) -> Model:
        return wrap_result(await self._select_one(self.model.username == username))

    async def get_user_by_id(self, user_id: int) -> Model:
        return wrap_result(await self._select_one(self.model.id == user_id))

    async def get_all_users(self) -> typing.List[Model]:
        return wrap_result(await self._select_all(), typing.List[Model])

    async def get_users_count(self) -> int:
        return await self._count()

    async def delete_user(self, user_id: int):
        return await self._delete(self.model.id == user_id)
