import enum

import sqlalchemy as sa

from .base import Base


class SizeEnum(enum.Enum):
    SMALL = 'S'
    MEDIUM = 'M'
    LARGE = 'XL'
    VERY_LARGE = 'XXL'


class User(Base):
    __tablename__ = 'users'
    id = sa.Column(sa.BigInteger, sa.Identity(), primary_key=True)
    first_name = sa.Column(sa.VARCHAR(100), unique=False)
    last_name = sa.Column(sa.VARCHAR(100), unique=False)
    phone_number = sa.Column(sa.Text, unique=False)
    email = sa.Column(sa.VARCHAR(70), unique=True)
    password = sa.Column(sa.Text, unique=False)
    balance = sa.Column(sa.DECIMAL, default=0, server_default='0')
    username = sa.Column(sa.VARCHAR(70), nullable=False, unique=True,
                         index=True)
    hashed_password = sa.Column(sa.Text, nullable=True, unique=True)

    __mapper_args__ = {"eager_defaults": True}

    def __init__(self, id, first_name, last_name, phone_number, email,
                 balance) -> None:
        self.email = email
        self.phone_number = phone_number
        self.balance = balance
        self.last_name = last_name
        self.first_name = first_name
        self.id = id

    def __repr__(self) -> str:
        return "<Users('%s', '%s', '%s', '%s')>" % (
            self.id, self.first_name, self.last_name, self.balance
        )


class Product(Base):
    """Таблица продуктов"""
    __tablename__ = 'products'
    id = sa.Column(sa.Integer, sa.Identity(), primary_key=True)
    name = sa.Column(sa.VARCHAR(255), unique=True, index=True)
    unit_price = sa.Column(sa.Numeric(precision=8), server_default='1')
    size = sa.Column(sa.Enum(SizeEnum))
    description = sa.Column(sa.Text, default=None, nullable=True)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())

    __mapper_args__ = {"eager_defaults": True}


class Order(Base):
    """Таблица заказов"""
    __tablename__ = 'orders'
    order_id = sa.Column(sa.Integer, sa.Identity(), primary_key=True)
    product_id = sa.Column(sa.SmallInteger, sa.ForeignKey('products.id'))
    quantity = sa.Column(sa.SmallInteger, default=1)
    created_at = sa.Column(sa.DateTime, default=sa.func.now())

    __mapper_args__ = {"eager_defaults": True}


__all__ = (
    'User', 'Order', 'Product', 'SizeEnum'
)
