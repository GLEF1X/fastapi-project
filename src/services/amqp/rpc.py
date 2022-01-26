import aio_pika


class AMQPClient:

    def __init__(self, rpc: aio_pika.patterns.RPC):
        self._rpc = rpc

    async def add_task(self, name: str):
        await self._rpc.register()
