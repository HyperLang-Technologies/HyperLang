from typing import Any


def all_values(values: Any) -> bool:
    return all(values)


def any_values(values: Any) -> bool:
    return any(values)


def is_callable(value: Any) -> bool:
    return callable(value)


def length(value: Any) -> int:
    return len(value)


def type_name(value: Any, declared_type: str | None = None) -> str:
    if declared_type is not None:
        return declared_type
    return type(value).__name__
