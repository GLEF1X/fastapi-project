from fastapi import Header, Depends, APIRouter
from fastapi.responses import Response

from src.api.v1.dependencies.database import ProductRepositoryDependencyMarker
from src.api.v1.dependencies.security import JWTBasedOAuth
from src.services.database.repositories.product import ProductRepository
from src.services.misc import DefaultResponse
from src.services.misc.schemas import Product
from src.utils.endpoints_specs import ProductBodySpec

api_router = APIRouter(dependencies=[Depends(JWTBasedOAuth())])


# noinspection PyUnusedLocal
@api_router.put(
    "/products/create",
    tags=["Product"],
    responses={400: {"model": DefaultResponse}},
    status_code=201,
    name="products:create_product"
)
async def create_product(
        product: Product = ProductBodySpec.item,
        user_agent: str = Header(..., title="User-Agent"),
        product_crud: ProductRepository = Depends(ProductRepositoryDependencyMarker),
):
    """
    Create an item with all the information:

    - **name**: each item must have a name
    - **description**: a long description
    - **unit_price**: required
    - **size**: size of item
    """
    await product_crud.add_product(**product.dict(exclude_unset=True, exclude_none=True))
    return Response(status_code=201, headers={"User-Agent": user_agent})
