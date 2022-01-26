import logging
import time
from typing import Optional, cast, Type, Dict, Any
from sqlalchemy import inspect, event
from sqlalchemy.dialects.postgresql.asyncpg import (
    AsyncAdapt_asyncpg_cursor,
    PGExecutionContext_asyncpg,
)
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection
from sqlalchemy.future import Connection
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.decl_api import (
    registry,
    DeclarativeMeta,
    declared_attr,
    has_inherited_table
)
from sqlalchemy.util import ImmutableProperties

logger = logging.getLogger("sqlalchemy.execution")

mapper_registry = registry()
ASTERISK = "*"


class Base(metaclass=DeclarativeMeta):
    """Declarative meta for mypy"""

    __abstract__ = True
    __mapper_args__ = {"eager_defaults": True}

    # these are supplied by the sqlalchemy-stubs or sqlalchemy2-stubs, so may be omitted
    # when they are installed
    registry = mapper_registry
    metadata = mapper_registry.metadata

    @declared_attr
    def __tablename__(self) -> Optional[str]:
        if not has_inherited_table(cast(Type[Base], self)):
            return cast(Type[Base], self).__qualname__.lower() + "s"
        return None

    def _get_attributes(self) -> Dict[Any, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __str__(self) -> str:
        attributes = "|".join(str(v) for k, v in self._get_attributes().items())
        return f"{self.__class__.__qualname__} {attributes}"

    def __repr__(self) -> str:
        table_attrs = cast(ImmutableProperties, inspect(self).attrs)
        primary_keys = " ".join(
            f"{key.name}={table_attrs[key.name].value}"
            for key in inspect(self.__class__).primary_key
        )
        return f"{self.__class__.__qualname__}->{primary_keys}"

    def as_dict(self) -> Dict[Any, Any]:
        return self._get_attributes()


# noinspection PyUnusedLocal
def before_execute_handler(
        conn: Connection,
        cursor: AsyncAdapt_asyncpg_cursor,
        statement: str,
        parameters: tuple,
        context: PGExecutionContext_asyncpg,
        executemany: bool,
):
    conn.info.setdefault("query_start_time", []).append(time.monotonic())


# noinspection PyUnusedLocal
def after_execute(
        conn: Connection,
        cursor: AsyncAdapt_asyncpg_cursor,
        statement: str,
        parameters: tuple,
        context: PGExecutionContext_asyncpg,
        executemany: bool,
):
    total = time.monotonic() - conn.info["query_start_time"].pop(-1)
    # sqlalchemy bug, executed twice `#4181` issue number
    logger.debug("Query Complete!")
    logger.debug("Total Time: %s", total)


class DatabaseComponents:
    def __init__(self, connection_uri: str, **engine_kwargs) -> None:
        self.__engine_kwargs = engine_kwargs or {}
        self.engine = create_async_engine(url=connection_uri, **self.__engine_kwargs)
        self.sessionmaker = sessionmaker(  # NOQA
            self.engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )
        self.setup_db_events()

    def setup_db_events(self) -> None:
        event.listen(
            self.engine.sync_engine, "before_cursor_execute", before_execute_handler
        )
        event.listen(self.engine.sync_engine, "after_cursor_execute", after_execute)

    async def recreate(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_all(conn: AsyncConnection) -> None:
        await conn.run_sync(Base.metadata.drop_all)
