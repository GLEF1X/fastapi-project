from typing import Optional

import fastapi.responses
from dependency_injector.wiring import inject
from fastapi import Header, Body

from api.application import api_router
from services.db import crud
from services.misc import DefaultResponse
from services.misc.pydantic_models import Product
from services.utils.response_validation import bad_response


@api_router.put("/products/create", tags=["Product"],
                responses={400: {"model": DefaultResponse}}, status_code=201)
@inject
async def create_product(
        product: Product = Body(..., example={
            "name": "Apple MacBook 15",
            "unit_price": 7000,
            "description": "Light and fast laptop",
            "size": "S"
        }),
        user_agent: Optional[str] = Header(None, title="User-Agent"),
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
    await crud.add_product(**product.dict(exclude_unset=True))
    return fastapi.responses.Response(status_code=201,
                                      headers={
                                          "User-Agent": user_agent
                                      })
