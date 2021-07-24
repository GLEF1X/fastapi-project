import sqlalchemy as sa
from sqlalchemy import Identity

from services.database.models.base import Base


class Order(Base):
    """Таблица заказов"""

    order_id = sa.Column(sa.Integer, Identity(always=True, cache=5), primary_key=True)
    product_id = sa.Column(
        sa.SmallInteger,
        sa.ForeignKey("products.id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    quantity = sa.Column(sa.SmallInteger, server_default="1")
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
