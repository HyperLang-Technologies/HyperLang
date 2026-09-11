# HyperLang Interpreter
# Copyleft 🄯 2026 HyperLang Tecnhologies

import shlex


variables = {}


TYPES = {
    "int": int,
    "float": float,
    "string": str,
    "bool": bool
}


def parse_value(value, expected_type):
    if expected_type not in TYPES:
        raise ValueError(f"Unknown type: {expected_type}")

    if expected_type == "string":
        if (
            len(value) >= 2
            and value[0] == '"'
            and value[-1] == '"'
        ):
            return value[1:-1]

        if (
            len(value) >= 2
            and value[0] == "'"
            and value[-1] == "'"
        ):
            return value[1:-1]

        if value in variables:
            result = variables[value]["value"]

            if not isinstance(result, str):
                raise TypeError(
                    f"Variable '{value}' is not a string."
                )

            return result

        raise ValueError(
            f"Expected a string for type '{expected_type}'."
        )

    if expected_type == "bool":
        if value == "true":
            return True

        if value == "false":
            return False

        if value in variables:
            result = variables[value]["value"]

            if not isinstance(result, bool):
                raise TypeError(
                    f"Variable '{value}' is not a boolean."
                )

            return result

        raise ValueError(
            f"Expected 'true' or 'false' for type '{expected_type}'."
        )

    if value in variables:
        result = variables[value]["value"]
        actual_type = variables[value]["type"]

        if actual_type != expected_type:
            raise TypeError(
                f"Variable '{value}' is type '{actual_type}', "
                f"not '{expected_type}'."
            )

        return result

    if expected_type == "int":
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"'{value}' is not a valid integer."
            )

    if expected_type == "float":
        try:
            return float(value)
        except ValueError:
            raise ValueError(
                f"'{value}' is not a valid float."
            )


def arith(operation, a, b):
    if a in variables:
        a = variables[a]["value"]

    if b in variables:
        b = variables[b]["value"]

    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise TypeError("Arithmetic requires numbers.")

    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise TypeError("Arithmetic requires numbers.")

    if operation == "add":
        return a + b

    elif operation == "sub":
        return a - b

    elif operation == "mul":
        return a * b

    elif operation == "div":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")

        return a / b

    else:
        raise ValueError(
            f"Unknown arithmetic operation: {operation}"
        )


def interpret(line):
    parts = shlex.split(line, posix=False)

    if not parts:
        return

    # --------------------------------
    # define var
    # --------------------------------

    if parts[0] == "define":
        if len(parts) != 6:
            raise SyntaxError(
                "Usage: define var <name>: <type> = <value>"
            )

        if parts[1] != "var":
            raise SyntaxError(
                "Expected 'var' after 'define'."
            )

        name = parts[2]

        if not name.endswith(":"):
            raise SyntaxError(
                "Expected ':' after the variable name."
            )

        name = name[:-1]

        variable_type = parts[3]

        if variable_type not in TYPES:
            raise ValueError(
                f"Unknown type: {variable_type}"
            )

        if parts[4] != "=":
            raise SyntaxError(
                "Expected '=' after the variable type."
            )

        value = parts[5]

        parsed_value = parse_value(value, variable_type)

        variables[name] = {
            "type": variable_type,
            "value": parsed_value
        }

    # --------------------------------
    # arith
    # --------------------------------

    elif parts[0] == "arith":
        if len(parts) != 4:
            raise SyntaxError(
                "Usage: arith <operation> <number> <number>"
            )

        operation = parts[1]
        a = parts[2]
        b = parts[3]

        result = arith(operation, a, b)

        print(result)

    # --------------------------------
    # text
    # --------------------------------

    elif parts[0] == "text":
        if len(parts) < 3:
            raise SyntaxError(
                "Usage: text <input/output> <value>"
            )

        action = parts[1]

        if action == "output":
            value = " ".join(parts[2:])

            if (
                len(value) >= 2
                and value[0] == '"'
                and value[-1] == '"'
            ):
                value = value[1:-1]

            elif (
                len(value) >= 2
                and value[0] == "'"
                and value[-1] == "'"
            ):
                value = value[1:-1]

            elif value in variables:
                value = variables[value]["value"]

            else:
                raise ValueError(
                    f"Variable '{value}' is not defined."
                )

            print(value)

        elif action == "input":
            if len(parts) != 3:
                raise SyntaxError(
                    "Usage: text input <variable>"
                )

            name = parts[2]

            if name not in variables:
                raise ValueError(
                    f"Variable '{name}' is not defined."
                )

            if variables[name]["type"] != "string":
                raise TypeError(
                    f"Variable '{name}' must be a string for text input."
                )

            variables[name]["value"] = input()

        else:
            raise SyntaxError(
                f"Unknown text operation: {action}"
            )

    else:
        raise SyntaxError(
            f"Unknown command: {parts[0]}"
        )


def run_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                interpret(line)

            except (
                SyntaxError,
                ValueError,
                TypeError,
                ZeroDivisionError
            ) as error:
                print(f"Error on line {line_number}: {error}")
                raise SystemExit(1)