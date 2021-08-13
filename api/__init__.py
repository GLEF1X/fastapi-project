from fastapi import APIRouter

from .v1 import not_for_production
from api.v1.endpoints import users, basic, products
from .v1.endpoints import oauth


def setup_routers() -> APIRouter:
    fundamental_api_router = basic.fundamental_api_router
    fundamental_api_router.include_router(users.api_router)
    fundamental_api_router.include_router(oauth.api_router)
    fundamental_api_router.include_router(products.api_router)
    fundamental_api_router.include_router(not_for_production.api_router)
    return fundamental_api_router


__all__ = ("setup_routers",)
