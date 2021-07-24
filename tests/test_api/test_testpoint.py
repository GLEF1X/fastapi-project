from typing import Dict
from unittest import mock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core import ApplicationSettings
from services.database import User
from services.database.repositories.user import UserRepository

pytestmark = pytest.mark.asyncio


async def test_testpoint(
    auth_headers: Dict[str, str],
    client: AsyncClient,
    app: FastAPI,
    auth_user: User,
    settings: ApplicationSettings,
):
    repo_mock = mock.Mock(spec=UserRepository)
    repo_mock.select_one.return_value = auth_user
    with app.container.services.user_repository.override(repo_mock):  # type: ignore  # noqa
        response = await client.get(
            settings.fastapi.API_V1_STR + "/test", headers=auth_headers
        )

    assert response.status_code == 200
