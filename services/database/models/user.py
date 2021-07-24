import sqlalchemy as sa
from sqlalchemy import Identity

from services.database.models.base import Base


class User(Base):
    id = sa.Column(sa.BigInteger, Identity(always=True, cache=5), primary_key=True)
    first_name = sa.Column(sa.VARCHAR(100), unique=False)
    last_name = sa.Column(sa.VARCHAR(100), unique=False)
    phone_number = sa.Column(sa.Text, unique=False)
    email = sa.Column(sa.VARCHAR(70), unique=True)
    password = sa.Column(sa.Text, unique=False)
    balance = sa.Column(sa.DECIMAL, server_default="0")
    username = sa.Column(sa.VARCHAR(70), nullable=False, unique=True, index=True)
    hashed_password = sa.Column(sa.Text, nullable=True, unique=True)
