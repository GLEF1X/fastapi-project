import pathlib
import time

import pytest
from alembic import config as alembic_config, command
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker

from services.database import User
from services.database.models import SizeEnum
from services.database.repositories.product import ProductRepository
from services.database.repositories.user import UserRepository
from services.utils import jwt
from services.utils.other.api_installation import DevApplicationBuilder, Director


@pytest.fixture()
def path_to_alembic_ini() -> str:
    return str(pathlib.Path(__name__).absolute().parent.parent.parent / "alembic.ini")


@pytest.fixture()
def path_to_migrations() -> str:
    return str(pathlib.Path(__name__).absolute().parent.parent.parent / "services" / "database" / "migrations")


@pytest.fixture(autouse=True)
async def apply_migrations(path_to_alembic_ini: str, path_to_migrations: str):
    alembic_cfg = alembic_config.Config(path_to_alembic_ini)
    alembic_cfg.set_main_option('script_location', path_to_migrations)
    command.upgrade(alembic_cfg, 'head')
    yield
    command.downgrade(alembic_cfg, 'base')


@pytest.fixture()
def app(apply_migrations: None):
    director = Director(DevApplicationBuilder())
    return director.configure()


@pytest.fixture()
async def initialized_app(app: FastAPI):
    async with LifespanManager(app):
        yield app


@pytest.fixture()
def session_maker(initialized_app: FastAPI) -> sessionmaker:
    return initialized_app.state.db_components.sessionmaker


@pytest.fixture()
async def client(initialized_app: FastAPI):
    async with AsyncClient(
            app=initialized_app,
            base_url="http://test",
            headers={
                "Content-Type": "application/json",
                "User-Agent": "FastAPI/Test/0.0.1"
            },
    ) as client:
        yield client


@pytest.fixture()
async def user_for_test(session_maker: sessionmaker):
    repository = UserRepository(session_maker)
    return await repository.add_user(email="test@test.com", password="password", username="username",
                                    first_name="Gleb", last_name="Garanin", phone_number="+7657676556",
                                    balance=666)


@pytest.fixture()
async def product_for_test(session_maker: sessionmaker):
    product_repository = ProductRepository(session_maker)
    return await product_repository.add_product(
        name="Pencil",
        unit_price=50.00,
        size=SizeEnum.SMALL
    )


@pytest.fixture()
def token(user_for_test: User):
    return jwt.create_access_token_for_user(user_for_test)


@pytest.fixture(name="settings")
def application_settings_fixture(app: FastAPI):
    return app.state.settings


@pytest.fixture()
def authorized_client(client: AsyncClient, token: str) -> AsyncClient:
    client.headers = {
        "Authorization": f"Bearer {token}",
        **client.headers,
    }
    return client
