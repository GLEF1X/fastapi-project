import typing
from datetime import datetime
from decimal import Decimal

from src.services.database import Product
from src.services.database.models import SizeEnum
from src.services.database.repositories.base import BaseRepository, Model
from src.utils.database_utils import manual_cast, filter_payload


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
        payload = filter_payload(locals())
        return manual_cast(await self._insert(**payload))

    async def get_product_by_id(self, product_id: int) -> Model:
        return manual_cast(await self._select_one(self.model.id == product_id))
