import typing
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.services.database import UnableToDelete
from src.services.database.models import User
from src.services.database.repositories.base import BaseRepository, Model
from src.utils.database_utils import manual_cast, filter_payload
from src.utils.password_hashing.protocol import PasswordHasherProto


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session_or_pool: typing.Union[sessionmaker, AsyncSession],
                 password_hasher: PasswordHasherProto):
        super().__init__(session_or_pool)
        self._password_hasher = password_hasher

    async def add_user(self, *, first_name: str, last_name: str,
                       phone_number: str, email: str, password: str, balance: typing.Union[Decimal, float, None] = None,
                       username: typing.Optional[str] = None) -> Model:
        prepared_payload = filter_payload(locals(), exclude=('password', ))
        prepared_payload["password_hash"] = self._password_hasher.hash(password)
        return manual_cast(await self._insert(**prepared_payload))

    async def delete_user(self, user_id: int) -> None:
        try:
            await self._delete(self.model.id == user_id)
        except IntegrityError:
            raise UnableToDelete()

    async def get_user_by_username(self, username: str) -> Model:
        return manual_cast(await self._select_one(self.model.username == username))

    async def get_user_by_id(self, user_id: int) -> Model:
        return manual_cast(await self._select_one(self.model.id == user_id))

    async def get_all_users(self) -> typing.List[Model]:
        return manual_cast(await self._select_all(), typing.List[Model])

    async def get_users_count(self) -> int:
        return await self._count()

    async def update_password_hash(self, new_pwd_hash: str, user_id: int) -> None:
        await self._update(self.model.id == user_id, password_hash=new_pwd_hash)

