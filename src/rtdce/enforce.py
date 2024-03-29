from typing import Type, get_origin, get_args, Any, Union, Literal
from dataclasses import is_dataclass, fields, asdict

from .exceptions import NotDataclassException, UnsupportedType


def supports_isinstance(origin):
    return origin not in [Union, Literal]


def generic_isinstance(value: Any, field_type: Type) -> bool:
    if isinstance(field_type, type):
        return isinstance(value, field_type)

    if origin := get_origin(field_type):
        if supports_isinstance(origin) and not isinstance(value, origin):
            return False

        if args := get_args(field_type):
            if origin is dict:
                key_type, value_type = args
                for key, dict_value in value.items():
                    if not generic_isinstance(key, key_type):
                        return False
                    if not generic_isinstance(dict_value, value_type):
                        return False
            elif origin is list:
                value_type = args[0]
                for list_value in value:
                    if not generic_isinstance(list_value, value_type):
                        return False
            elif origin is Union:
                for arg in args:
                    if generic_isinstance(value, arg):
                        return True
                return False
            elif origin is Literal:
                for arg in args:
                    if value == arg:
                        return True
                return False
    return True


def enforce(dc: Type):
    if not is_dataclass(dc):
        raise NotDataclassException()

    dc_dict = asdict(dc)
    dc_fields = fields(dc)

    for field in dc_fields:
        value = dc_dict.get(field.name)

        if not generic_isinstance(value, field.type):
            raise TypeError(
                f'"{value}" invalid value for field "{field.name}" of type "{field.type}"'
            )
