import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.services.database import User

pytestmark = pytest.mark.asyncio


async def test_create_user(authorized_client: AsyncClient, app: FastAPI) -> None:
    response = await authorized_client.put(
        app.url_path_for("users:create_user"),
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
    assert response.json().get("success") is True


async def test_users_count(authorized_client: AsyncClient, app: FastAPI) -> None:
    response = await authorized_client.post(app.url_path_for("users:get_users_count"))
    assert response.status_code == 200
    assert isinstance(response.json().get("count"), int)


async def test_get_user_info(authorized_client: AsyncClient, app: FastAPI, test_user: User) -> None:
    response = await authorized_client.get(app.url_path_for("users:get_user_info", user_id=str(test_user.id)))
    assert response.status_code == 200


async def test_get_all_users(authorized_client: AsyncClient, app: FastAPI) -> None:
    response = await authorized_client.get(app.url_path_for("users:get_all_users"))
    assert response.status_code == 200


async def test_delete_user(authorized_client: AsyncClient, app: FastAPI, test_user: User) -> None:
    response = await authorized_client.delete(app.url_path_for("users:delete_user", user_id=str(test_user.id)))
    assert response.status_code == 200
    assert response.json() == {"message": f"UserDTO with id {test_user.id} was successfully deleted from database"}
