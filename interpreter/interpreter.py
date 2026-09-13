# HyperLang Interpreter
# Copyleft 🄯 2026 HyperLang Technologies

import shlex
import sys

# Call stack for variable scoping. Index 0 is global.
call_stack = [{}]
functions = {}

TYPES = {
    "int": int,
    "float": float,
    "string": str,
    "bool": bool,
    "list": list
}

class ReturnException(Exception):
    pass

# --- Scope Helpers ---

def get_var(name):
    if name in call_stack[-1]:
        return call_stack[-1][name]
    if name in call_stack[0]:
        return call_stack[0][name]
    return None

def define_var(name, var_type, value):
    # Defines a new variable in the current local scope
    call_stack[-1][name] = {"type": var_type, "value": value}

def update_var(name, var_type, value):
    # Updates an existing variable (local first, then global)
    if name in call_stack[-1]:
        call_stack[-1][name] = {"type": var_type, "value": value}
    elif name in call_stack[0]:
        call_stack[0][name] = {"type": var_type, "value": value}
    else:
        raise ValueError(f"Variable '{name}' is not defined.")

# ---------------------

def parse_value(value, expected_type):
    if expected_type not in TYPES:
        raise ValueError(f"Unknown type: {expected_type}")

    if expected_type == "string":
        if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
            return value[1:-1]
        if len(value) >= 2 and value[0] == "'" and value[-1] == "'":
            return value[1:-1]
        var_data = get_var(value)
        if var_data:
            result = var_data["value"]
            if not isinstance(result, str):
                raise TypeError(f"Variable '{value}' is not a string.")
            return result
        raise ValueError(f"Expected a string for type '{expected_type}'.")

    if expected_type == "bool":
        if value == "true":
            return True
        if value == "false":
            return False
        var_data = get_var(value)
        if var_data:
            result = var_data["value"]
            if not isinstance(result, bool):
                raise TypeError(f"Variable '{value}' is not a boolean.")
            return result
        raise ValueError(f"Expected 'true' or 'false' for type '{expected_type}'.")

    if expected_type == "list":
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
                else:
                    item_data = get_var(item)
                    if item_data:
                        parsed_items.append(item_data["value"])
                    else:
                        parsed_items.append(item)
            return parsed_items

        var_data = get_var(value)
        if var_data:
            result = var_data["value"]
            if not isinstance(result, list):
                raise TypeError(f"Variable '{value}' is not a list.")
            return list(result)

        raise ValueError(f"Expected a list literal or list variable for type '{expected_type}'.")

    var_data = get_var(value)
    if var_data:
        result = var_data["value"]
        actual_type = var_data["type"]
        if actual_type != expected_type:
            raise TypeError(f"Variable '{value}' is type '{actual_type}', not '{expected_type}'.")
        return result

    if expected_type == "int":
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid integer.")

    if expected_type == "float":
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"'{value}' is not a valid float.")


def arith(operation, a, b=None):
    var_a = get_var(a)
    is_list_a = False
    
    if var_a:
        a_val = var_a["value"]
        if var_a["type"] == "list":
            is_list_a = True
            a = a_val
        else:
            a = a_val
    else:
        try:
            a = float(a) if '.' in str(a) else int(a)
        except ValueError:
            pass

    # Handle operations that operate on a single list first
    if is_list_a:
        if operation == "sum":
            return sum(a)
        elif operation == "max":
            return max(a)
        elif operation == "min":
            return min(a)
        else:
            raise TypeError(f"Operation '{operation}' does not support list arguments.")

    # Now we know 'a' must be a number
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise TypeError(f"Arithmetic requires numbers. Got '{a}' instead.")

    # Single-operand numeric operations
    if operation == "abs": 
        return abs(a)
    elif operation == "round":
        return round(a)

    # For everything else, a second operand (b) is required
    if b is None:
        raise ValueError(f"Operation '{operation}' requires a second operand.")

    var_b = get_var(b)
    if var_b:
        b = var_b["value"]
    else:
        try:
            b = float(b) if '.' in str(b) else int(b)
        except ValueError:
            pass

    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise TypeError("Arithmetic requires numbers.")

    # Two-operand numeric operations
    if operation == "add": return a + b
    elif operation == "sub": return a - b
    elif operation == "mul": return a * b
    elif operation == "div":
        if b == 0: raise ZeroDivisionError("Cannot divide by zero.")
        return a / b
    elif operation == "mod":
        if b == 0: raise ZeroDivisionError("Cannot modulo by zero.")
        return a % b
    elif operation == "max": return max(a, b)
    elif operation == "min": return min(a, b)
    else:
        raise ValueError(f"Unknown arithmetic operation: {operation}")


def evaluate_condition(cond_str):
    cond_str = cond_str.strip()
    if cond_str == "true": return True
    if cond_str == "false": return False
    var_data = get_var(cond_str)
    if var_data:
        return bool(var_data["value"])
    return False


def interpret(line):
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
        if len(parts) != 6 or parts[1] != "var" or not parts[2].endswith(":") or parts[4] != "=":
            raise SyntaxError("Usage: define var <name>: <type> = <value>")
        
        name = parts[2][:-1]
        variable_type = parts[3]
        if variable_type not in TYPES:
            raise ValueError(f"Unknown type: {variable_type}")

        value = parts[5]
        parsed_value = parse_value(value, variable_type)
        define_var(name, variable_type, parsed_value)

    # --------------------------------
    # convert
    # --------------------------------
    elif parts[0] == "convert":
        if len(parts) == 4 and parts[2] == "to":
            var_name, target_type = parts[1], parts[3]
        elif len(parts) == 3:
            var_name, target_type = parts[1], parts[2]
        else:
            raise SyntaxError("Usage: convert <variable> to <type>")

        var_data = get_var(var_name)
        if not var_data:
            raise ValueError(f"Variable '{var_name}' is not defined.")
        if target_type not in TYPES:
            raise ValueError(f"Unknown type: {target_type}")

        val = var_data["value"]
        
        try:
            if target_type == "int":
                val = int(float(val)) if isinstance(val, (str, float)) else int(val)
            elif target_type == "float":
                val = float(val)
            elif target_type == "string":
                val = "true" if val is True else "false" if val is False else str(val)
            elif target_type == "bool":
                if isinstance(val, str):
                    if val.lower() not in ["true", "false"]:
                        raise ValueError("String must be 'true' or 'false' to convert to bool.")
                    val = (val.lower() == "true")
                else:
                    val = bool(val)
            elif target_type == "list":
                if isinstance(val, (str, tuple)):
                    val = list(val)
                elif not isinstance(val, list):
                    val = [val]
        except Exception as e:
            raise ValueError(f"Cannot convert '{var_name}' to {target_type}: {e}")

        update_var(var_name, target_type, val)

    # --------------------------------
    # arith
    # --------------------------------
    elif parts[0] == "arith":
        single_ops = ["abs", "round", "sum"]
        
        # 'max' and 'min' can take 1 argument (a list) or 2 arguments (two numbers)
        if len(parts) == 3 and parts[1] in single_ops + ["max", "min"]:
            result = arith(parts[1], parts[2])
        elif len(parts) == 4 and parts[1] not in single_ops:
            result = arith(parts[1], parts[2], parts[3])
        else:
            raise SyntaxError("Usage: arith <abs|round|sum> <val> OR arith <op> <val1> <val2>")
        
        print(result)

    # --------------------------------
    # compare
    # --------------------------------
    elif parts[0] == "compare":
        if len(parts) != 5:
            raise SyntaxError("Usage: compare <val1> <op> <val2> <dest_bool_var>")
        
        v1_str, op, v2_str, dest_var = parts[1], parts[2], parts[3], parts[4]

        var_v1 = get_var(v1_str)
        if var_v1:
            v1 = var_v1["value"]
        else:
            try: v1 = float(v1_str) if '.' in v1_str else int(v1_str)
            except ValueError: v1 = v1_str.strip("\"'")

        var_v2 = get_var(v2_str)
        if var_v2:
            v2 = var_v2["value"]
        else:
            try: v2 = float(v2_str) if '.' in v2_str else int(v2_str)
            except ValueError: v2 = v2_str.strip("\"'")

        dest_data = get_var(dest_var)
        if not dest_data:
            raise ValueError(f"Destination variable '{dest_var}' is not defined.")
        if dest_data["type"] != "bool":
            raise TypeError(f"Destination variable '{dest_var}' must be a bool.")

        ops = {"==": lambda a,b: a==b, "!=": lambda a,b: a!=b, "<": lambda a,b: a<b,
               ">": lambda a,b: a>b, "<=": lambda a,b: a<=b, ">=": lambda a,b: a>=b}
        if op not in ops:
            raise SyntaxError(f"Unknown comparison operator: {op}")
        
        update_var(dest_var, "bool", ops[op](v1, v2))

    # --------------------------------
    # list
    # --------------------------------
    elif parts[0] == "list":
        if len(parts) < 3:
            raise SyntaxError("Usage: list <append|get|len> <list_var> [args]")

        action, target_var = parts[1], parts[2]
        var_data = get_var(target_var)
        
        if not var_data:
            raise ValueError(f"Variable '{target_var}' is not defined.")
        if var_data["type"] != "list":
            raise TypeError(f"Variable '{target_var}' is not a list.")

        lst = var_data["value"]

        if action == "append":
            if len(parts) != 4:
                raise SyntaxError("Usage: list append <list_var> <value>")
            val = parts[3]
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            else:
                val_data = get_var(val)
                if val_data: val = val_data["value"]
                elif val.isdigit(): val = int(val)
            lst.append(val)

        elif action == "get":
            if len(parts) != 5:
                raise SyntaxError("Usage: list get <list_var> <index> <dest_var>")
            index_str, dest_var = parts[3], parts[4]

            idx_data = get_var(index_str)
            if idx_data: index = idx_data["value"]
            else:
                try: index = int(index_str)
                except ValueError: raise ValueError(f"Index '{index_str}' must be an integer.")

            if not get_var(dest_var):
                raise ValueError(f"Destination variable '{dest_var}' is not defined.")

            try:
                # Update existing variable type implicitly or assume string for simplicity in basic tests
                update_var(dest_var, get_var(dest_var)["type"], lst[index])
            except IndexError:
                raise IndexError(f"Index {index} out of range for list '{target_var}'.")

        elif action == "len":
            if len(parts) != 4:
                raise SyntaxError("Usage: list len <list_var> <dest_var>")
            dest_var = parts[3]
            if not get_var(dest_var):
                raise ValueError(f"Destination variable '{dest_var}' is not defined.")
            update_var(dest_var, "int", len(lst))

        else:
            raise SyntaxError(f"Unknown list operation: {action}")

    # --------------------------------
    # text
    # --------------------------------
    elif parts[0] == "text":
        if len(parts) < 3:
            raise SyntaxError("Usage: text <input/output> <value>")

        action = parts[1]
        if action == "output":
            value = " ".join(parts[2:])
            if (len(value) >= 2 and value[0] == '"' and value[-1] == '"') or \
               (len(value) >= 2 and value[0] == "'" and value[-1] == "'"):
                value = value[1:-1]
            else:
                var_data = get_var(value)
                if var_data:
                    value = var_data["value"]
                else:
                    raise ValueError(f"Variable '{value}' is not defined.")
            print(value)

        elif action == "input":
            if len(parts) != 3:
                raise SyntaxError("Usage: text input <variable>")
            name = parts[2]
            var_data = get_var(name)
            if not var_data:
                raise ValueError(f"Variable '{name}' is not defined.")
            if var_data["type"] != "string":
                raise TypeError(f"Variable '{name}' must be a string for text input.")
            update_var(name, "string", input())
        else:
            raise SyntaxError(f"Unknown text operation: {action}")

    else:
        raise SyntaxError(f"Unknown command: {parts[0]}")


def execute_lines(lines):
    i = 0
    while i < len(lines):
        raw_line = lines[i].strip()

        if not raw_line or raw_line.startswith("#"):
            i += 1
            continue
            
        if raw_line == "return":
            raise ReturnException()

        elif raw_line.startswith("if "):
            parts = shlex.split(raw_line, posix=False)
            if len(parts) != 2:
                print(f"Error: Usage: if <condition>")
                raise SystemExit(1)
            
            branches = [{"condition": parts[1], "body": []}]
            depth = 1 
            i += 1
            
            while i < len(lines):
                line_str = lines[i].strip()
                if line_str.startswith("if "):
                    depth += 1
                    branches[-1]["body"].append(lines[i])
                elif line_str == "endif":
                    depth -= 1
                    if depth == 0: break
                    else: branches[-1]["body"].append(lines[i])
                elif line_str.startswith("elseif ") and depth == 1:
                    parts = shlex.split(line_str, posix=False)
                    if len(parts) != 2:
                        print(f"Error: Usage: elseif <condition>")
                        raise SystemExit(1)
                    branches.append({"condition": parts[1], "body": []})
                elif line_str == "else" and depth == 1:
                    branches.append({"condition": "true", "body": []})
                else:
                    branches[-1]["body"].append(lines[i])
                i += 1
                
            if depth > 0:
                print("Error: Missing 'endif' for if block.")
                raise SystemExit(1)
                
            for branch in branches:
                if evaluate_condition(branch["condition"]):
                    execute_lines(branch["body"])
                    break 

        elif raw_line.startswith("func define "):
            parts = shlex.split(raw_line, posix=False)
            if len(parts) != 3:
                print(f"Error on block evaluation: Usage: func define <func_name>")
                raise SystemExit(1)
            
            func_name = parts[2]
            body = []
            i += 1
            
            while i < len(lines) and lines[i].strip() != "endfunc":
                body.append(lines[i])
                i += 1
                
            if i >= len(lines):
                print(f"Error: Missing 'endfunc' for function block '{func_name}'.")
                raise SystemExit(1)
                
            functions[func_name] = body

        elif raw_line.startswith("func call "):
            parts = shlex.split(raw_line, posix=False)
            if len(parts) != 3:
                print(f"Error on block evaluation: Usage: func call <func_name>")
                raise SystemExit(1)
                
            func_name = parts[2]
            if func_name not in functions:
                print(f"Error: Function '{func_name}' is not defined.")
                raise SystemExit(1)
                
            # Push a new local scope
            call_stack.append({})
            try:
                execute_lines(functions[func_name])
            except ReturnException:
                pass
            finally:
                # Pop the local scope when done
                call_stack.pop()

        elif raw_line.startswith("loop for ") or raw_line.startswith("loop while "):
            parts = shlex.split(raw_line, posix=False)
            loop_type = parts[1]
            condition_val = parts[2]

            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != "endloop":
                body.append(lines[i])
                i += 1

            if i >= len(lines):
                print(f"Error: Missing 'endloop' for loop block.")
                raise SystemExit(1)

            try:
                if loop_type == "for":
                    cond_data = get_var(condition_val)
                    count = cond_data["value"] if cond_data else int(condition_val)
                    for _ in range(count):
                        execute_lines(body)
                elif loop_type == "while":
                    while evaluate_condition(condition_val):
                        execute_lines(body)
            except (SyntaxError, ValueError, TypeError, ZeroDivisionError, IndexError) as error:
                print(f"Error executing loop: {error}")
                raise SystemExit(1)
                
        else:
            try:
                interpret(lines[i])
            except (SyntaxError, ValueError, TypeError, ZeroDivisionError, IndexError) as error:
                print(f"Error processing command: {error}")
                raise SystemExit(1)
        i += 1

def run_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()
    try:
        execute_lines(lines)
    except ReturnException:
        pass 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Usage: py hyperlang.py <path_to_file.hl>")