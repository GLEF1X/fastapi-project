#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import typing

from services.database.repositories.base import Model

T = typing.TypeVar("T")


@typing.overload
def wrap_result(result: typing.Any) -> Model: ...


@typing.overload
def wrap_result(result: typing.Any, cast_type: typing.Type[T]) -> T: ...


# noinspection PyUnusedLocal
def wrap_result(result, cast_type=None):
    return result
