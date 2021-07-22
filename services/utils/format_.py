import json
from typing import Union, List, Any, Type, TypeVar, Dict

_T = TypeVar("_T")
BoundedDict = TypeVar("BoundedDict", bound=Dict[Any, Any])


def into_complex_obj(
        lst_of_objects: Union[List[Union[dict, str]], dict],
        model: Type[_T]
) -> List[_T]:
    """
    Parse simple objects, which cant raise ValidationError

    :param lst_of_objects: usually its response.response_data
    :param model: pydantic model, which will parse core
    """
    return [model.from_orm(obj) for obj in lst_of_objects]


def to_json_string(obj: Any) -> str:
    return json.dumps(obj)


def dict_(**dictionary: BoundedDict) -> BoundedDict:
    """
    Pop NoneType values and convert everything to str, designed?for=params
    :param dictionary: source dict
    :return: filtered dict
    """
    return {k: str(v) for k, v in dictionary.items() if v is not None}
