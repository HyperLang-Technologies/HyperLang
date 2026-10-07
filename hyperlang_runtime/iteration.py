from collections.abc import Iterable
from typing import Any, Callable


def enumerate_values(values: Iterable[Any], start: int = 0) -> list[tuple[int, Any]]:
    return list(enumerate(values, start))


def filter_values(function: Callable[[Any], Any], values: Iterable[Any]) -> list[Any]:
    return [value for value in values if function(value)]


def map_values(function: Callable[[Any], Any], values: Iterable[Any]) -> list[Any]:
    return [function(value) for value in values]


def reversed_values(values: Any) -> list[Any]:
    try:
        return list(reversed(values))
    except TypeError as error:
        raise TypeError("reversed() requires a reversible iterable.") from error


def slice_values(values: Any, start: int, stop: int | None, step: int | None = None) -> Any:
    if not isinstance(values, (str, list, tuple, bytes, bytearray)):
        raise TypeError("slice() requires a string, list, tuple, bytes, or bytearray.")
    return values[slice(start, stop, step)]


def sorted_values(values: Iterable[Any], reverse: bool = False) -> list[Any]:
    try:
        return sorted(values, reverse=reverse)
    except TypeError as error:
        raise TypeError(f"sorted() cannot compare these values: {error}") from error


def zip_values(*values: Iterable[Any]) -> list[tuple[Any, ...]]:
    if len(values) < 2:
        raise TypeError("zip() requires at least two iterables.")
    return list(zip(*values))
