from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from services.db.crud import ProductRepository
from services.dependencies.containers import Application
from services.misc import Product

api_router = APIRouter()


@api_router.get("/products/get/{product_id}", response_model=Product)
@inject
async def get_product_by_id(
        product_id: int,
        product_repository: ProductRepository = Depends(Provide[Application.services.product_repository])
):
    product = await product_repository.select_one(product_repository.model.id == product_id)
    return Product.from_orm(product)
