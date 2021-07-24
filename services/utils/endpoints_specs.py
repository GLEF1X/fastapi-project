from dataclasses import dataclass
from typing import Any

from fastapi import Body


@dataclass
class ProductBodySpec:
    item: Any = Body(
        ...,
        example={
            "name": "Apple MacBook 15",
            "unit_price": 7000,
            "description": "Light and fast laptop",
            "size": "S",
        },
    )


@dataclass
class UserBodySpec:
    item: Any = Body(
        ...,
        example={
            "first_name": "Gleb",
            "last_name": "Garanin",
            "username": "GLEF1X",
            "phone_number": "+7900232132",
            "email": "glebgar567@gmail.com",
            "password": "qwerty12345",
            "balance": 5,
        },
    )
