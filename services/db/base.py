import contextlib
from typing import Optional, NoReturn, Callable

import sqlalchemy as sa
import sqlalchemy.ext.declarative
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from data.config import CONNECTION_URL

Base = sa.ext.declarative.declarative_base()


class Database:

    def __init__(self, connection_url: Optional[str] = None):
        """
        Initialize a sqlalchemy engine and session factory
        :param connection_url: url to establish a connection with db
        """
        connection_url = connection_url if connection_url else CONNECTION_URL
        self._engine = create_async_engine(connection_url, echo=False,
                                           pool_size=40,
                                           max_overflow=0)
        self._session_factory = sessionmaker(bind=self._engine,
                                             expire_on_commit=False,
                                             class_=AsyncSession,
                                             autocommit=False)

    async def create_database(self, drop_all: bool = False) -> NoReturn:
        async with self._engine.begin() as conn:
            conn: AsyncSession
            if drop_all:
                await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @contextlib.asynccontextmanager
    async def session(
            self
    ) -> Callable[..., contextlib.AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        finally:
            await session.close()
