#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from datetime import timedelta

import pytest
from jose import jwt

from src.services.database import User
from src.services.utils.jwt import (
    ALGORITHM,
    create_access_token_for_user,
    create_jwt_token,
    get_username_from_token, SECRET_KEY
)


def test_creating_jwt_token() -> None:
    token = create_jwt_token(
        jwt_content={"content": "payload"},
        expires_delta=timedelta(minutes=1),
    )
    parsed_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert parsed_payload["content"] == "payload"


def test_creating_token_for_user(test_user: User) -> None:
    token = create_access_token_for_user(user=test_user)
    parsed_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert parsed_payload["username"] == test_user.username


def test_retrieving_token_from_user(test_user: User) -> None:
    token = create_access_token_for_user(user=test_user)
    username = get_username_from_token(token, SECRET_KEY)
    assert username == test_user.username


def test_error_when_wrong_token() -> None:
    with pytest.raises(ValueError):
        get_username_from_token("asdf", "asdf")


def test_error_when_wrong_token_shape() -> None:
    token = create_jwt_token(
        jwt_content={"content": "payload"},
        expires_delta=timedelta(minutes=1),
    )
    with pytest.raises(ValueError):
        get_username_from_token(token, SECRET_KEY)
