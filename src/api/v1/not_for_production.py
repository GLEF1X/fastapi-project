#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from typing import Optional, Union

from fastapi import APIRouter, Depends, Query, Path
from starlette import status
from starlette.responses import JSONResponse

from src.api.v1.dependencies.database import get_repository
from src.api.v1.dependencies.security import get_current_user
from src.services.database.repositories.product import ProductRepository
from src.services.misc import Product
from src.services.utils.responses import get_pydantic_model_or_return_raw_response

api_router = APIRouter(dependencies=[Depends(get_current_user)])


@api_router.get(
    "/products/get/{product_id}",
    responses={
        200: {"model": Product},
    }
)
async def get_product_by_id(
        product_id: int = Path(...),
        product_repository: ProductRepository = Depends(get_repository(ProductRepository)),
) -> Union[JSONResponse, Product]:
    product = await product_repository._select_one(product_repository.model.id == product_id)
    return get_pydantic_model_or_return_raw_response(Product, product)


@api_router.get("/test_api/{user_id}/items/{item_id}", status_code=status.HTTP_200_OK, include_in_schema=False)
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
