import asyncio
from typing import Any, Optional, Callable, Dict, Hashable

import orjson
from aio_pika import connect_robust, Connection, Channel, DeliveryMode
from aio_pika.patterns import RPC
from aio_pika.pool import Pool
from attr import define, field


class JsonRPC(RPC):
    SERIALIZER = orjson
    CONTENT_TYPE = "application/json"

    def serialize(self, data: Any) -> bytes:
        return self.SERIALIZER.dumps(data, default=repr)

    def serialize_exception(self, exception: Exception) -> bytes:
        return self.serialize(
            {
                "error": {
                    "type": exception.__class__.__name__,
                    "message": repr(exception),
                    "args": exception.args,
                }
            }
        )



@define
class Consumer:
    callback: Callable[..., Any]
    name: str
    kwargs: Dict[str, Any] = field(factory=dict)


class RabbitMQService:

    def __init__(self, uri: str, *consumers: Consumer, **connect_kw: Any):
        self._uri = uri
        self._connect_kw = connect_kw
        self._connection_pool: Pool[Connection] = Pool(self._get_connection, max_size=15)
        self._channel_pool: Pool[Channel] = Pool(self._get_channel, max_size=10)
        self._rpc: Optional[RPC] = None
        self._consumers = consumers

    async def _get_channel(self) -> Channel:
        async with self._connection_pool.acquire() as connection:
            return await connection.channel()

    async def _get_connection(self) -> Connection:
        return await connect_robust(self._uri, **self._connect_kw)

    async def __aenter__(self) -> RPC:
        async with self._connection_pool.acquire():
            async with self._channel_pool.acquire() as channel:
                rpc = JsonRPC(channel)
                await rpc.initialize()
                self._rpc = rpc

                for consumer in self._consumers:
                    await self._rpc.register(consumer.name, consumer.callback, **consumer.kwargs)

                return self._rpc

    async def __aexit__(self, exc_type, exc_val, exc_tb): pass
