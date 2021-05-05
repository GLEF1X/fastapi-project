import abc
import contextlib
import typing

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(abc.ABC):
    """ Base class of CRUD operations with sqlalchemy """

    @abc.abstractmethod
    def __init__(self, session_factory: typing.Callable[
        ..., contextlib.AbstractAsyncContextManager[AsyncSession]
    ]):
        self.session_factory = session_factory
