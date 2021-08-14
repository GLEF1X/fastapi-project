#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

from typing import no_type_check

from sqlalchemy import types


class HashedPassword(types.TypeDecorator):
    impl = types.VARCHAR

    cache_ok = True

    @no_type_check
    def process_bind_param(self, value, dialect):
        from src.services.utils.jwt import get_password_hash  # to avoid Circular import error

        return get_password_hash(value)

    @no_type_check
    def process_result_value(self, value, dialect):
        return value
