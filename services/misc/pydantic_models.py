
from typing import Optional, Union, NoReturn, Any

from email_validator import validate_email
from pydantic import BaseModel, Field, validator


class User(BaseModel):
    id: Optional[int] = Field(default=None)
    first_name: str = Field(..., example="Gleb", title="Имя")
    last_name: str = Field(..., example="Garanin", title="Фамилия")
    phone_number: Optional[str] = Field(
        ..., regex=r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$",
        min_length=10, max_length=15, title="Номер мобильного телефона",
        example="+7900232132"
    )
    email: Optional[str] = Field(..., title="Адрес электронной почты",
                                 example="glebgar567@gmail.com")

    @validator("email")
    def validate_em(cls, v: ...) -> Union[str, NoReturn]:
        if not validate_email(v):
            raise ValueError("bad email format")
        return v


class DefaultResponse(BaseModel):
    error: str
    success: bool
