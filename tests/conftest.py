"""
In conftest.py I mark most scope of fixtures as "module",
because performance if migrations will be executed for each function(by default) will be poor
"""
import asyncio
import pathlib

import pytest
from alembic import config as alembic_config, command
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient, Headers
from sqlalchemy.orm import sessionmaker

from src.services.database import User
from src.services.database.models import SizeEnum
from src.services.database.repositories.product import ProductRepository
from src.services.database.repositories.user import UserRepository
from src.services.utils import jwt
from src.services.utils.other.api_installation import DevApplicationBuilder, Director


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def path_to_alembic_ini() -> str:
    return str(pathlib.Path(__name__).absolute().parent.parent.parent / "alembic.ini")


@pytest.fixture(scope="module")
def path_to_migrations_folder() -> str:
    return str(pathlib.Path(__name__).absolute().parent.parent.parent / "src" / "services" / "database" / "migrations")


@pytest.fixture(autouse=True, scope="module")
async def apply_migrations(path_to_alembic_ini: str, path_to_migrations_folder: str):
    alembic_cfg = alembic_config.Config(path_to_alembic_ini)
    alembic_cfg.set_main_option('script_location', path_to_migrations_folder)
    command.upgrade(alembic_cfg, 'head')
    yield
    command.downgrade(alembic_cfg, 'base')


@pytest.fixture(scope="module")
def app(apply_migrations: None):
    director = Director(DevApplicationBuilder())
    return director.configure()


@pytest.fixture(scope="module")
async def initialized_app(app: FastAPI):
    async with LifespanManager(app):
        yield app


@pytest.fixture(scope="module")
def session_maker(initialized_app: FastAPI) -> sessionmaker:
    return initialized_app.state.db_components.sessionmaker


@pytest.fixture(scope="module")
async def client(initialized_app: FastAPI):
    async with AsyncClient(
            app=initialized_app,
            base_url="http://test",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture(name="test_user", scope="module")
async def user_for_test(session_maker: sessionmaker):
    repository = UserRepository(session_maker)
    return await repository.add_user(email="test@test.com", password="password", username="username",
                                     first_name="Gleb", last_name="Garanin", phone_number="+7657676556",
                                     balance=666)


@pytest.fixture(name="test_product", scope="module")
async def product_for_test(session_maker: sessionmaker):
    product_repository = ProductRepository(session_maker)
    return await product_repository.add_product(
        name="Pencil",
        unit_price=50.00,
        size=SizeEnum.SMALL
    )


@pytest.fixture(scope="module")
def token(test_user: User):
    return jwt.create_access_token_for_user(test_user)


@pytest.fixture(name="settings", scope="module")
def application_settings_fixture(app: FastAPI):
    return app.state.settings


@pytest.fixture(scope="module")
def authorized_client(client: AsyncClient, token: str) -> AsyncClient:
    client.headers = Headers({"Authorization": f"Bearer {token}"})
    return client
