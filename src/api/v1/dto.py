import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr

from src.services.database.models import SizeEnum


class UserDTO(BaseModel):
    first_name: str = Field(..., example="Gleb", title="Имя")
    last_name: str = Field(..., example="Garanin", title="Фамилия")
    phone_number: Optional[str] = Field(
        None,
        regex=r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$",
        min_length=10,
        max_length=15,
        title="Номер мобильного телефона",
        example="+7900232132",
    )
    email: EmailStr = Field(
        ..., title="Адрес электронной почты", example="glebgar567@gmail.com"
    )
    balance: float
    password: str = Field(..., example="qwerty12345")
    id: Optional[int] = None
    username: str = Field(..., example="GLEF1X")

    class Config:
        orm_mode = True


class ProductDTO(BaseModel):
    id: Optional[int] = None
    name: str
    unit_price: float
    size: SizeEnum
    description: str
    created_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True
        schema_extra = {
            "name": "Apple MacBook 15",
            "unit_price": 7000,
            "description": "Light and fast laptop",
        }
        keep_untouched = ()
        use_enum_values = True

    def patch_enum_values(self) -> None:
        self.Config.use_enum_values = False


class DefaultResponse(BaseModel):
    error: str
    success: bool = False


class ObjectCountDTO(BaseModel):
    count: int = Field(..., example=44)


class SimpleResponse(BaseModel):
    message: str = Field(...)


class TestResponse(BaseModel):
    success: bool = True
    user_agent: Optional[str] = Field(None, alias="User-Agent")


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    username: str
    scopes: List[str] = []
