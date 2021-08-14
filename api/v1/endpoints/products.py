from typing import Optional

from fastapi import Header, Depends, APIRouter
from fastapi.responses import Response

from api.v1.dependencies.database import get_repository
from services.database.repositories.product import ProductRepository
from services.misc import DefaultResponse
from services.misc.schemas import Product, User
from services.utils.endpoints_specs import ProductBodySpec
from services.utils.responses import bad_response

api_router = APIRouter()


# noinspection PyUnusedLocal
@api_router.put(
    "/products/create",
    tags=["Product"],
    responses={400: {"model": DefaultResponse}},
    status_code=201,
    name="products:create_product"
)
async def create_product(
        user: User,
        product: Product = ProductBodySpec.item,
        user_agent: Optional[str] = Header(None, title="User-Agent"),
        product_crud: ProductRepository = Depends(get_repository(ProductRepository)),
):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **unit_price**: required
    - **size**: size of item
    """
    if not user_agent:
        return bad_response()
    await product_crud.add_product(**product.dict(exclude_unset=True))
    return Response(status_code=201, headers={"User-Agent": user_agent})
