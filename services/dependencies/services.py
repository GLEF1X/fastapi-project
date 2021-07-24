import typing

from aioredis import Redis


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def cache_process(
        self,
        key: str,
        value: typing.Optional[typing.Any] = None,
        *,
        expire: int = 0,
        overwrite: bool = False
    ) -> typing.Any:
        cached_value = await self._redis.get(key)
        if overwrite or not cached_value:
            await self._redis.set(key, value, expire=expire)
        return cached_value or value
