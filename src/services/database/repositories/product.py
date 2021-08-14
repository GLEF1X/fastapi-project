import typing
from datetime import datetime
from decimal import Decimal

from src.services.database import Product
from src.services.database.models import SizeEnum
from src.services.database.repositories.base import BaseRepository, Model
from src.services.database.utils import wrap_result


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
        return wrap_result(await self._insert(
            name=name,
            unit_price=unit_price,
            size=size,
            description=description,
            created_at=created_at,
            id=product_id
        ))

    async def get_product_by_id(self, product_id: int) -> Model:
        return wrap_result(await self._select_one(self.model.id == product_id))
