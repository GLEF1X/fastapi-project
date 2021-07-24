from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Path
from starlette import status

from services.database.repositories.product import ProductRepository
from services.dependencies.containers import Application
from services.misc import Product
from services.utils.responses import get_pydantic_model_or_raise_exception

api_router = APIRouter()


@api_router.get(
    "/products/get/{product_id}",
    responses={
        200: {"model": Product},
    },
)
@inject
async def get_product_by_id(
    product_id: int = Path(...),
    product_repository: ProductRepository = Depends(
        Provide[Application.services.product_repository]
    ),
) -> Product:
    product = await product_repository.select_one(
        product_repository.model.id == product_id
    )
    return await get_pydantic_model_or_raise_exception(Product, product)


@api_router.get("/test_api/{user_id}/items/{item_id}", status_code=status.HTTP_200_OK)
async def read_user_item(
    user_id: int,
    item_id: str,
    short: bool = False,
    q: Optional[str] = Query(None, max_length=50, deprecated=True),
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
