#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.services.database.models import SizeEnum
from src.services.misc import Product

pytestmark = pytest.mark.asyncio


async def test_create_product(authorized_client: AsyncClient, app: FastAPI):
    product = Product(name="blouse", unit_price=50.00, description="Pretty blouse", size=SizeEnum.SMALL)
    product.patch_enum_values()
    response = await authorized_client.put(app.url_path_for("products:create_product"), json=product.dict())
    assert response.status_code == 201
