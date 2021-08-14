from typing import Dict
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.core import ApplicationSettings
from src.services.database import User

pytestmark = pytest.mark.asyncio


async def test_testpoint(
        auth_headers: Dict[str, str],
        client: AsyncClient,
        app: FastAPI,
        auth_user: User,
        settings: ApplicationSettings,
        authorized_mock: Mock
):
    response = await client.get(
        settings.fastapi.API_V1_STR + "/test", headers=auth_headers
    )

    assert response.status_code == 200
