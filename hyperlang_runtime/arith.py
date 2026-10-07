from typing import Any

from .runtime import Runtime


def _number(value: str, runtime: Runtime) -> int | float:
    variable = runtime.get_var(value)
    if variable is not None:
        value = variable["value"]
    elif isinstance(value, str):
        try:
            value = float(value) if "." in value else int(value)
        except ValueError:
            pass
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError(f"Arithmetic requires numbers. Got '{value}' instead.")
    return value


def arith(operation: str, a: str, b: str | None, runtime: Runtime) -> Any:
    first_data = runtime.get_var(a)
    first = first_data["value"] if first_data else _number(a, runtime)
    if isinstance(first, (list, tuple, set)):
        if operation == "sum":
            return sum(first)
        if operation == "max":
            return max(first)
        if operation == "min":
            return min(first)
        raise TypeError(f"Operation '{operation}' does not support collection arguments.")
    if not isinstance(first, (int, float)) or isinstance(first, bool):
        raise TypeError(f"Arithmetic requires numbers. Got '{first}' instead.")

    if operation == "abs":
        return abs(first)
    if operation == "round":
        return round(first)
    if operation == "bin":
        if not isinstance(first, int):
            raise TypeError("bin() requires an integer.")
        return bin(first)
    if operation == "hex":
        if not isinstance(first, int):
            raise TypeError("hex() requires an integer.")
        return hex(first)
    if operation == "oct":
        if not isinstance(first, int):
            raise TypeError("oct() requires an integer.")
        return oct(first)
    if b is None:
        raise ValueError(f"Operation '{operation}' requires a second operand.")
    second = _number(b, runtime)
    if operation == "add":
        return first + second
    if operation == "sub":
        return first - second
    if operation == "mul":
        return first * second
    if operation in ("div", "divmod") and second == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    if operation == "mod" and second == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    if operation == "div":
        return first / second
    if operation == "mod":
        return first % second
    if operation == "max":
        return max(first, second)
    if operation == "min":
        return min(first, second)
    if operation == "pow":
        return pow(first, second)
    if operation == "divmod":
        return list(divmod(first, second))
    raise ValueError(f"Unknown arithmetic operation: {operation}")
