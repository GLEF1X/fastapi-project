import typing
import warnings

from services.database import Product
from services.database.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def add(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        warnings.warn(
            "Deprecated call. Use `insert` instead of it", category=DeprecationWarning
        )
        return await self.insert(**kwargs)
