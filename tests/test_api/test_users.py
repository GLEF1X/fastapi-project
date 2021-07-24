from unittest import mock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from services.database.repositories.user import UserRepository

pytestmark = pytest.mark.asyncio


async def test_create_user(client: AsyncClient, app: FastAPI) -> None:
    repository_mock = mock.Mock(spec=UserRepository)
    repository_mock.add.return_value = None
    with app.container.services.user_repository.override(repository_mock):  # type: ignore
        response = await client.put(
            "/api/v1/users/create",
            headers={"User-Agent": "Test"},
            json={
                "first_name": "Gleb",
                "last_name": "Garanin",
                "username": "GLEF1X",
                "phone_number": "+7900232132",
                "email": "glebgar567@gmail.com",
                "password": "qwerty12345",
                "balance": 5,
            },
        )
    assert response.status_code == 200
    assert response.json() == {"success": True, "User-Agent": "Test"}
