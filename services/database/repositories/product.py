import typing
import warnings

from services.database import Product
from services.database.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def add_product(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        return await self._insert(**kwargs)
