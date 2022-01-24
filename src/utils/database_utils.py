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
