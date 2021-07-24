import enum

import sqlalchemy as sa
from sqlalchemy import Identity

from services.database.models.base import Base


class SizeEnum(enum.Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "XL"
    VERY_LARGE = "XXL"


class Product(Base):
    """Таблица продуктов"""

    id = sa.Column(sa.Integer, Identity(always=True, cache=5), primary_key=True)
    name = sa.Column(sa.VARCHAR(255), unique=True, index=True)
    unit_price = sa.Column(sa.Numeric(precision=8), server_default="1")
    size = sa.Column(sa.Enum(SizeEnum))
    description = sa.Column(sa.Text, default=None, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
