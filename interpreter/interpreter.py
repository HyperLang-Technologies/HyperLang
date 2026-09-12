# HyperLang Interpreter
# Copyleft 🄯 2026 HyperLang Technologies

import shlex


variables = {}


TYPES = {
    "int": int,
    "float": float,
    "string": str,
    "bool": bool,
    "list": list
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

    if expected_type == "list":
        # Strip outer quotes if they exist (allows spaces inside list definitions)
        if len(value) >= 2 and (
            (value.startswith('"') and value.endswith('"')) or 
            (value.startswith("'") and value.endswith("'"))
        ):
            value = value[1:-1]

        if len(value) >= 2 and value.startswith("[") and value.endswith("]"):
            content = value[1:-1].strip()
            if not content:
                return []
            
            raw_items = [item.strip() for item in content.split(",")]
            parsed_items = []
            for item in raw_items:
                if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                    parsed_items.append(item[1:-1])
                elif item.isdigit():
                    parsed_items.append(int(item))
                elif item in variables:
                    parsed_items.append(variables[item]["value"])
                else:
                    parsed_items.append(item)
            return parsed_items

        if value in variables:
            result = variables[value]["value"]
            if not isinstance(result, list):
                raise TypeError(f"Variable '{value}' is not a list.")
            return list(result)

        raise ValueError(
            f"Expected a list literal or list variable for type '{expected_type}'."
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
    else:
        try:
            a = float(a) if '.' in str(a) else int(a)
        except ValueError:
            pass

    if b in variables:
        b = variables[b]["value"]
    else:
        try:
            b = float(b) if '.' in str(b) else int(b)
        except ValueError:
            pass

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
    # comments
    # --------------------------------
    
    line = line.strip()

    if not line or line.startswith("#"):
        return

    if "#" in line:
        line = line.split("#", 1)[0].rstrip()

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
    # list
    # --------------------------------

    elif parts[0] == "list":
        if len(parts) < 3:
            raise SyntaxError(
                "Usage: list <append|get|len> <list_var> [args]"
            )

        action = parts[1]
        target_var = parts[2]

        if target_var not in variables:
            raise ValueError(
                f"Variable '{target_var}' is not defined."
            )

        if variables[target_var]["type"] != "list":
            raise TypeError(
                f"Variable '{target_var}' is not a list."
            )

        lst = variables[target_var]["value"]

        if action == "append":
            if len(parts) != 4:
                raise SyntaxError(
                    "Usage: list append <list_var> <value>"
                )
            
            val = parts[3]
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            elif val in variables:
                val = variables[val]["value"]
            elif val.isdigit():
                val = int(val)

            lst.append(val)

        elif action == "get":
            if len(parts) != 5:
                raise SyntaxError(
                    "Usage: list get <list_var> <index> <dest_var>"
                )
            
            index_str = parts[3]
            dest_var = parts[4]

            if index_str in variables:
                index = variables[index_str]["value"]
            else:
                try:
                    index = int(index_str)
                except ValueError:
                    raise ValueError(
                        f"Index '{index_str}' must be an integer."
                    )

            if dest_var not in variables:
                raise ValueError(
                    f"Destination variable '{dest_var}' is not defined."
                )

            try:
                variables[dest_var]["value"] = lst[index]
            except IndexError:
                raise IndexError(
                    f"Index {index} out of range for list '{target_var}'."
                )

        elif action == "len":
            if len(parts) != 4:
                raise SyntaxError(
                    "Usage: list len <list_var> <dest_var>"
                )

            dest_var = parts[3]
            if dest_var not in variables:
                raise ValueError(
                    f"Destination variable '{dest_var}' is not defined."
                )

            variables[dest_var]["value"] = len(lst)

        else:
            raise SyntaxError(
                f"Unknown list operation: {action}"
            )

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
                ZeroDivisionError,
                IndexError
            ) as error:
                print(f"Error on line {line_number}: {error}")
                raise SystemExit(1)