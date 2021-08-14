import typing
from datetime import datetime
from decimal import Decimal

from services.database import Product
from services.database.models import SizeEnum
from services.database.repositories.base import BaseRepository, Model


class ProductRepository(BaseRepository[Product]):
    model = Product

    async def add_product(self, *,
                          name: str,
                          unit_price: typing.Union[float, Decimal],
                          size: SizeEnum,
                          product_id: typing.Optional[int] = None,
                          description: typing.Optional[str] = None,
                          created_at: typing.Optional[datetime] = None
                          ) -> Model:
        return await self._insert(
            name=name,
            unit_price=unit_price,
            size=size,
            description=description,
            created_at=created_at,
            id=product_id
        )
