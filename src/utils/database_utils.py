#  Copyright (c) 2021. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from src.services.database.repositories.base import Model

T = typing.TypeVar("T")
Dictionary = typing.TypeVar("Dictionary", bound=typing.Dict[typing.Any, typing.Any])


@typing.overload
def manual_cast(result: typing.Any) -> "Model": ...


@typing.overload
def manual_cast(result: typing.Any, cast_type: typing.Type[T]) -> T: ...


# noinspection PyUnusedLocal
def manual_cast(result, cast_type=None):
    return result


@typing.no_type_check
def filter_payload(payload):
    return {k: v for k, v in payload.items() if k not in ['cls', 'self'] and v is not None}
