from __future__ import annotations

import ctypes
import functools
from multiprocessing import Manager, Process
from multiprocessing.managers import ValueProxy, SyncManager
from typing import Callable, TypeVar, Any, Dict, Generic, Optional, cast

_T = TypeVar("_T")


class CustomProcess(Process):
    def execute(self, timeout: Optional[float] = None) -> None:
        self.start()
        self.join(timeout=timeout)


class ProcessManager(Generic[_T]):
    """
    Helps to run CPU bound task in a separate process.
    Example of usage:
    >>> def my_func(float_proxy: ValueProxy[float]) -> ValueProxy[float]:
    ...     x = 5 ** 2  # calculate certain big value
    ...     float_proxy.set(x)
    ...     return float_proxy
    >>> mng = ProcessManager(func=my_func, ctype=ctypes.c_float, default=float(0))
    >>> with mng as result:
    >>>     # some your staff and logic with result value
    >>>     # On shutdown, it will terminate the process and Manager, that has spawned ValueProxy

    """

    def __init__(
            self,
            func: Callable[[ValueProxy[_T], Any], ValueProxy[_T]],
            default: _T,
            ctype: Any,
            args: tuple = (),
            kwargs: Optional[Dict[Any, Any]] = None,
    ):
        self._target = func
        self._manager = Manager()
        self.__proxy_value = self.manager.Value(ctype, default)
        self._ctype = ctype
        self._args = args
        self._kwargs = kwargs or {}
        self._process: Optional[CustomProcess] = None

    @property
    def process(self) -> CustomProcess:
        if not (process := self._process):
            self._process = CustomProcess(target=self._wrap_func(), args=self._args, kwargs=self._kwargs)
        return cast(CustomProcess, process or self._process)

    @property
    def manager(self) -> SyncManager:
        return self._manager

    def _wrap_func(self) -> functools.partial[ValueProxy[_T]]:
        return functools.partial(self._target, self.__proxy_value)

    def execute_function(self) -> _T:
        self.process.execute()
        return self.__proxy_value.value

    def shutdown(self) -> None:
        if (process := self.process) is not None:
            process.close()
        self.manager.shutdown()

    def __enter__(self) -> _T:
        return self.execute_function()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        return self.shutdown()
