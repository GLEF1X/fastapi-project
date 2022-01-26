import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.api.v1.dto import ProductDTO
from src.services.database.models import SizeEnum

pytestmark = pytest.mark.asyncio


async def test_create_product(authorized_client: AsyncClient, app: FastAPI) -> None:
    product = ProductDTO(name="blouse", unit_price=50.00, description="Pretty blouse", size=SizeEnum.SMALL)
    product.patch_enum_values()
    response = await authorized_client.put(app.url_path_for("products:create_product"), json=product.dict())
    assert response.status_code == 201
