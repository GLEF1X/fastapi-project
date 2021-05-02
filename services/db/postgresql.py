import abc
import enum
from typing import (
    Optional,
    Union,
    List,
    overload,
    Literal,
    final,
    Tuple,
    Any,
    Dict,
    Protocol
)

import asyncpg
from loguru import logger

from data import config


class FormatType(enum.Enum):
    OR_ = ' AND '
    AND_ = ' OR '


class DBProto(Protocol):
    async def setup(self, *args: Any, **kwargs: Any) -> None: ...

    async def create_table(self) -> None: ...


class WithDefaultsValues(DBProto):
    async def add_defaults(self, *args: Any, **kwargs: Any) -> Any: ...


class BaseDB(abc.ABC):
    """Базовый класс базы данных"""

    def __init__(self, db_name: Optional[str] = None) -> None:
        self.pool: Optional[asyncpg.Pool] = None
        if isinstance(db_name, str):
            self.db_name = db_name
        else:
            self.db_name = self.__class__.__name__.lower() + "s"

    @final
    @logger.catch
    async def create(self) -> None:
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    @overload
    async def execute(self,
                      command: str,
                      *args: Any,
                      fetch: Literal[True],
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False) -> Optional[List[asyncpg.Record]]:
        ...

    @overload
    async def execute(self,
                      command: str,
                      *args: Any,
                      fetch: bool = False,
                      fetchval: Literal[True],
                      fetchrow: bool = False,
                      execute: bool = False
                      ) -> Optional[asyncpg.Record]:
        ...

    @overload
    async def execute(self,
                      command,
                      *args: Any,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: Literal[True],
                      execute: bool = False
                      ) -> Optional[Any]:
        ...

    @overload
    async def execute(self,
                      command: str,
                      *args: Any,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: Literal[True]
                      ) -> str:
        ...

    @logger.catch
    async def execute(self, command: str, *args: Any,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ) -> Optional[Union[Any, List[asyncpg.Record], str]]:
        async with self.pool.acquire() as connection:
            connection: asyncpg.Connection
            async with connection.transaction(isolation='read_committed'):
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    @logger.catch
    @abc.abstractmethod
    async def create_table(self) -> None:
        raise NotImplementedError()

    @logger.catch
    async def drop_table(self) -> None:
        await self.execute(
            f"DROP TABLE IF EXISTS {self.db_name}", execute=True
        )

    @logger.catch
    async def select_all(self) -> Optional[List[asyncpg.Record]]:
        sql = f"SELECT * FROM {self.db_name}"
        return await self.execute(
            sql, fetch=True
        )

    @staticmethod
    def format_arguments(
            sql: str,
            parameters: Dict[str, Union[str, int, float]],
            format_type: FormatType = FormatType.AND_
    ) -> Tuple[str, tuple]:
        sql += f" {format_type.value} ".join([
            f"{item} = ${num}" for num, item in enumerate(parameters.keys(),
                                                          start=1)
        ])
        return sql, tuple(parameters.values())

    @abc.abstractmethod
    async def add_entry(self, *args: Any, **kwargs: Any) -> asyncpg.Record:
        raise NotImplementedError()

    @overload
    async def select_entry(
            self,
            fetch_all: Literal[True],
            **kwargs: Any
    ) -> Optional[List[asyncpg.Record]]:
        ...

    @overload
    async def select_entry(
            self,
            fetch_all: Literal[False],
            **kwargs: Any
    ) -> Optional[asyncpg.Record]:
        ...

    @logger.catch
    async def select_entry(
            self,
            fetch_all: bool = False,
            **kwargs) -> Union[Optional[List[asyncpg.Record]], asyncpg.Record]:
        sql = f"""SELECT * FROM {self.db_name} WHERE """
        sql, parameters = self.format_arguments(sql, kwargs)
        if fetch_all:
            return await self.execute(sql, *parameters, fetch=True)
        return await self.execute(sql, *parameters, fetchrow=True)

    @logger.catch
    async def setup(self) -> None:
        await self.create()
        # await self.create_table()

    @logger.catch
    async def delete_entry(self, **kwargs: Any) -> str:
        sql = f"""DELETE FROM {self.db_name} WHERE """
        sql, parameters = self.format_arguments(sql, kwargs)
        return (await self.execute(sql, *parameters, execute=True)).replace(
            "DELETE ", "")

    @logger.catch
    async def update_entry(self, update_values: Dict[str, Any],
                           **kwargs: Any) -> Optional[List[asyncpg.Record]]:
        update_params = "".join(
            [f"{key} = '{value}'" for key, value in update_values.items()]
        )
        sql = f"""UPDATE {self.db_name} SET {update_params}
WHERE """
        sql, parameters = self.format_arguments(sql, kwargs)
        sql += """
RETURNING *
        """
        return await self.execute(sql, *parameters, fetchrow=True)
