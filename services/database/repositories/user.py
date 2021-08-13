import typing

from sqlalchemy import insert, delete

from services.database.exceptions import UnableToDelete
from services.database.models import User
from services.database.repositories.base import BaseRepository, Model


class UserRepository(BaseRepository[User]):
    model = User

    async def add(self, **kwargs: typing.Any) -> Model:
        from api.v1.dependencies.security import get_password_hash

        async with self.transaction:
            hashed_password = get_password_hash(kwargs.pop("password"))
            stmt = (
                insert(self.model)
                .values(**kwargs, password=hashed_password)
                .returning(self.model)
            )
            result = (await self.session.execute(stmt)).first()
        return typing.cast(Model, result)

    async def delete_by_user_id(self, user_id: int) -> None:
        async with self.transaction:
            query_delete = delete(self.model).where(User.id == user_id).returning(User)
            result = (await self.session.execute(query_delete)).scalars().first()
        if not isinstance(result, User):
            raise UnableToDelete()
