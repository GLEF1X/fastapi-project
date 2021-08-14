from __future__ import annotations

import contextlib
import typing
from abc import ABC
from typing import cast

from sqlalchemy import lambda_stmt, select, update, exists, delete, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSessionTransaction, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import Executable

from src.services.database.models.base import ASTERISK
from src.services.database.utils import filter_payload

Model = typing.TypeVar("Model")
TransactionContext = typing.AsyncContextManager[AsyncSessionTransaction]


class BaseRepository(ABC, typing.Generic[Model]):
    """
    We define a base class for the repository hierarchy, making it possible to use the base CRUD methods,
    so that they do not creep into inherited classes
    """

    # You need to define this variable in child classes
    model: typing.ClassVar[typing.Type[Model]]

    def __init__(self, session_or_pool: typing.Union[sessionmaker, AsyncSession]) -> None:
        """

        :param session_or_pool: async session from async context manager
        """
        if isinstance(session_or_pool, sessionmaker):
            self._session: AsyncSession = typing.cast(AsyncSession, session_or_pool())
        else:
            self._session = session_or_pool

    @contextlib.asynccontextmanager
    async def __transaction(self) -> typing.AsyncGenerator:
        """Yield an :class:`_asyncio.AsyncSessionTransaction` object."""
        if not self._session.in_transaction() and self._session.is_active:
            async with self._session.begin() as transaction:  # type: AsyncSessionTransaction
                yield transaction
        else:
            yield  # type: ignore

    @staticmethod
    def proxy_bulk_save(session: Session, *instances) -> None:
        return session.bulk_save_objects(*instances)

    @property
    def _transaction(self) -> TransactionContext:
        """Mypy friendly :function:`BaseRepository.transaction` representation"""
        return self.__transaction()

    async def _insert(self, **values: typing.Any) -> Model:
        """Add model into database"""
        async with self._transaction:
            insert_stmt = (
                insert(self.model)
                    .values(**filter_payload(values))
                    .on_conflict_do_nothing()
                    .returning(self.model)
            )
            result = (await self._session.execute(insert_stmt)).mappings().first()
        return self._convert_to_model(**typing.cast(typing.Dict[str, typing.Any], result))

    async def _select_all(self, *clauses: typing.Any) -> typing.List[Model]:
        """
        Selecting data from table and filter by kwargs data

        :param clauses:
        :return:
        """
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        async with self._transaction:
            result = (
                (await self._session.execute(typing.cast(Executable, stmt)))
                    .scalars()
                    .all()
            )

        return result

    async def _select_one(self, *clauses: typing.Any) -> Model:
        """
        Return scalar value

        :return:
        """
        query_model = self.model
        stmt = lambda_stmt(lambda: select(query_model))
        stmt += lambda s: s.where(*clauses)
        async with self._transaction:
            result = (
                (await self._session.execute(typing.cast(Executable, stmt)))
                    .scalars()
                    .first()
            )

        return typing.cast(Model, result)

    async def _update(self, *clauses: typing.Any, **values: typing.Any) -> None:
        """
        Update values in database, filter by `telegram_id`

        :param clauses: where conditionals
        :param values: key/value for update
        :return:
        """
        async with self._transaction:
            stmt = update(self.model).where(*clauses).values(**values).returning(None)
            await self._session.execute(stmt)
        return None

    async def _exists(self, *clauses: typing.Any) -> typing.Optional[bool]:
        """Check is user exists in database"""
        async with self._transaction:
            stmt = exists(select(self.model).where(*clauses)).select()
            result = (await self._session.execute(stmt)).scalar()
        return typing.cast(typing.Optional[bool], result)

    async def _delete(self, *clauses: typing.Any) -> typing.List[Model]:
        async with self._transaction:
            stmt = delete(self.model).where(*clauses).returning(ASTERISK)
            result = (await self._session.execute(stmt)).scalars().all()
        return typing.cast(typing.List[Model], result)

    async def _count(self) -> int:
        async with self._transaction:
            count = (await self._session.execute(func.count(ASTERISK))).scalars().first()
        return cast(int, count)

    def _convert_to_model(self, **kwargs) -> Model:
        return self.model(**kwargs)  # type: ignore
