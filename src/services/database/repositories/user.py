import typing
from decimal import Decimal

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError

from src.services.database import UnableToDelete
from src.services.database.models import User
from src.services.database.repositories.base import BaseRepository, Model
from src.services.database.utils import wrap_result, filter_payload


class UserRepository(BaseRepository[User]):
    model = User

    async def add_user(self, *, first_name: str, last_name: str,
                       phone_number: str, email: str, password: str, balance: typing.Union[Decimal, float, None] = None,
                       username: typing.Optional[str] = None) -> Model:
        prepared_payload = filter_payload(locals())
        async with self._transaction:
            stmt = insert(self.model) \
                .values(**prepared_payload) \
                .on_conflict_do_nothing() \
                .returning(self.model)
            result = (await self._session.execute(stmt)).first()
        return typing.cast(Model, result)

    async def delete_user(self, user_id: int) -> None:
        try:
            await self._delete(self.model.id == user_id)
        except IntegrityError:
            raise UnableToDelete()

    async def get_user_by_username(self, username: str) -> Model:
        return wrap_result(await self._select_one(self.model.username == username))

    async def get_user_by_id(self, user_id: int) -> Model:
        return wrap_result(await self._select_one(self.model.id == user_id))

    async def get_all_users(self) -> typing.List[Model]:
        return wrap_result(await self._select_all(), typing.List[Model])

    async def get_users_count(self) -> int:
        return await self._count()
