#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

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
