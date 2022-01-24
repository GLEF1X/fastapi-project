import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from src.services.database import User

pytestmark = pytest.mark.asyncio


async def test_login(authorized_client: AsyncClient, app: FastAPI, test_user: User) -> None:
    response = await authorized_client.post(
        app.url_path_for("oauth:login"),
        data={"username": test_user.username, "password": "password"}
    )
    assert response.status_code == 200
