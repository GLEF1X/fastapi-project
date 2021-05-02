import json
from typing import Optional, Union, NoReturn

import asyncpg
from pydantic import BaseModel, Field, validate_email, validator

from services.misc import User as PUser
from .postgresql import BaseDB


class User(BaseDB, BaseModel):
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

    async def create_table(self) -> str:
        sql = f"""
                CREATE TABLE IF NOT EXISTS {self.db_name}(
                    id           INT GENERATED ALWAYS AS IDENTITY NOT NULL PRIMARY KEY,
                    first_name   VARCHAR(80)                      NOT NULL,
                    last_name    VARCHAR(80)                      NOT NULL,
                    phone_number VARCHAR(20)                      NOT NULL,
                    email        VARCHAR(50)                      NOT NULL DEFAULT 'unknown'
                    );
                CREATE EXTENSION IF NOT EXISTS pg_trgm;
                CREATE INDEX IF NOT EXISTS trgm_idx_users_first_name ON {self.db_name} USING gin (first_name gin_trgm_ops);
                CREATE INDEX IF NOT EXISTS users_email_idx ON {self.db_name} USING gin (email gin_trgm_ops);
        )"""
        return await self.execute(command=sql, execute=True)

    async def add_entry(
            self,
            first_name: str,
            last_name: str,
            phone_number: str,
            email: Optional[str] = None,
            **kwargs
    ) -> PUser:
        sql = f"""INSERT INTO {self.db_name}(first_name, last_name, phone_number, email)
                 VALUES ($1, $2, $3, $4)
                 RETURNING *"""
        db_answer = await self.execute(sql, first_name, last_name,
                                       phone_number,
                                       email, fetchrow=True)
        return self.parse_record(
            json.dumps(dict(d))
        )

    @classmethod
    def parse_record(cls, record: asyncpg.Record) -> PUser:
        data = json.dumps(dict(record.items()), indent=4)
        return PUser.parse_raw(data)
