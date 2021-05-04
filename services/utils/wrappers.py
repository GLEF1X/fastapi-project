import multiprocessing
from typing import TypeVar, Callable, Any, NoReturn

F = TypeVar('F', bound=Callable[..., Any])

__cache = {}


def wrapper(func: F, *args: Any, **kwargs: Any) -> Any:
    pool = __cache.get("pool")
    if pool is None:
        pool = multiprocessing.Pool(processes=4)
        __cache.update(pool=pool)
    res = pool.apply_async(func, args=args, kwds=kwargs).get(timeout=1)
    return res


def on_shutdown() -> NoReturn:
    pool: multiprocessing.pool.Pool = __cache.get("pool")
    if pool is not None:
        pool.close()
