from typing import Dict
from unittest import mock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core import ApplicationSettings
from services.database import User
from services.database.repositories.user import UserRepository

pytestmark = pytest.mark.asyncio


async def test_create_user(client: AsyncClient, app: FastAPI, settings: ApplicationSettings) -> None:
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


async def test_users_count(client: AsyncClient, auth_headers: Dict[str, str], app: FastAPI,
                           settings: ApplicationSettings, authorized_mock: mock.Mock) -> None:
    authorized_mock.count.return_value = 2
    with app.container.services.user_repository.override(authorized_mock):  # type: ignore
        response = await client.post(
            settings.fastapi.API_V1_STR + "/users/count",
            headers={"User-Agent": "Test", **auth_headers},
        )

    assert response.status_code == 200
    assert isinstance(response.json().get("count"), int)


async def test_get_user_info(client: AsyncClient, auth_headers: Dict[str, str], app: FastAPI,
                             settings: ApplicationSettings, auth_user: User, authorized_mock: mock.Mock):
    with app.container.services.user_repository.override(authorized_mock):  # type: ignore
        response = await client.get(
            settings.fastapi.API_V1_STR + f"/users/{auth_user.id}/info",
            headers={"User-Agent": "Test", **auth_headers},
        )

    assert response.status_code == 200


async def test_get_all_users(client: AsyncClient, auth_headers: Dict[str, str], app: FastAPI,
                             settings: ApplicationSettings, auth_user: User, authorized_mock: mock.Mock):
    authorized_mock.select_all.return_value = [auth_user]
    with app.container.services.user_repository.override(authorized_mock):  # type: ignore
        response = await client.get(
            settings.fastapi.API_V1_STR + "/users/all",
            headers={"User-Agent": "Test", **auth_headers},
        )

    assert response.status_code == 200


async def test_delete_user(client: AsyncClient, auth_headers: Dict[str, str], app: FastAPI,
                           settings: ApplicationSettings, auth_user: User, authorized_mock: mock.Mock):
    authorized_mock.delete.return_value = auth_user
    with app.container.services.user_repository.override(authorized_mock):  # type: ignore
        response = await client.delete(
            settings.fastapi.API_V1_STR + f"/users/{auth_user.id}/delete",
            headers={"User-Agent": "Test", **auth_headers},
        )

    assert response.status_code == 200
    assert response.json() == {"message": f"User with id {auth_user.id} was successfully deleted from database"}
