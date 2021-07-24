import asyncio
from typing import Generator, Any, AsyncGenerator, cast, Dict
from unittest.mock import Mock

import pytest
from _pytest.fixtures import FixtureRequest
from fastapi import FastAPI
from httpx import AsyncClient

from core import ApplicationSettings
from services.database import User
from services.database.repositories.user import UserRepository
from services.utils.other.api_installation import (
    ApplicationConfiguratorBuilder,
    Director,
)
from services.utils.security import get_password_hash

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
def event_loop(
    request: FixtureRequest,
) -> Generator[asyncio.AbstractEventLoop, Any, Any]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def app() -> Generator[FastAPI, Any, Any]:
    director = Director(ApplicationConfiguratorBuilder())
    yield director.configure()


@pytest.fixture(scope="module")
def settings(app: FastAPI) -> Generator[ApplicationSettings, Any, Any]:
    yield cast(ApplicationSettings, app.settings)  # type: ignore


@pytest.fixture(scope="module")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(app=app, base_url="http://test") as client:  # noqa
        yield client


@pytest.fixture(scope="module", name="auth_user")
def auth_user(settings: ApplicationSettings) -> User:
    # noinspection PyArgumentList
    return User(
        id=1,
        username="GLEF1X",
        first_name="Глеб",
        last_name="Гаранин",
        email=settings.tests.FIRST_SUPERUSER,
        balance=1,
        password=settings.tests.FIRST_SUPERUSER_PASSWORD,
        hashed_password=get_password_hash(settings.tests.FIRST_SUPERUSER_PASSWORD),
    )


@pytest.fixture(scope="module", name="token")
async def access_token_fixture(
    client: AsyncClient, app: FastAPI, settings: ApplicationSettings, auth_user
) -> str:
    login_data = {
        "username": settings.tests.FIRST_SUPERUSER,
        "password": settings.tests.FIRST_SUPERUSER_PASSWORD,
    }
    repository_mock = Mock(spec=UserRepository)
    repository_mock.select_one.return_value = auth_user
    with app.container.services.user_repository.override(repository_mock):  # type: ignore  # noqa
        response = await client.post(
            settings.fastapi.API_V1_STR + "/oauth",
            data=login_data,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )
    json_ = response.json()
    return json_["access_token"]


@pytest.fixture(name="auth_headers", scope="module")
def auth_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
