import typing
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from src.services.database.exceptions import UnableToDelete
from src.services.database.models import User
from src.services.database.repositories.base import BaseRepository, Model
from src.services.database.utils import wrap_result, filter_none


class UserRepository(BaseRepository[User]):
    model = User

    async def add_user(self, *, first_name: str, last_name: str,
                       phone_number: str, email: str, password: str, balance: typing.Union[Decimal, float, None] = None,
                       username: typing.Optional[str] = None) -> Model:
        from src.services.utils.jwt import get_password_hash
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "phone_number": phone_number,
            "email": email,
            "balance": balance,
            "username": username
        }
        async with self._transaction:
            hashed_password = get_password_hash(password)
            stmt = insert(self.model) \
                .values(**filter_none(payload), password=hashed_password) \
                .on_conflict_do_nothing() \
                .returning(self.model)
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
