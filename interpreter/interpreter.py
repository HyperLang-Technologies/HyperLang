# HyperLang Interpreter
# Copyleft 🄯 2026 HyperLang Technologies

import shlex
import sys
import time

# Call stack for variable scoping. Index 0 is global.
call_stack = [{}]
functions = {}

TYPES = {
    "int": int,
    "float": float,
    "string": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "set": set,
    "tuple": tuple,
    "bytes": bytes,
    "bytearray": bytearray,
    "file": object
}

# --- Control Flow Exceptions ---
class ReturnException(Exception): pass
class BreakException(Exception): pass
class ContinueException(Exception): pass

# --- Scope Helpers ---

def get_var(name):
    if name in call_stack[-1]:
        return call_stack[-1][name]
    if name in call_stack[0]:
        return call_stack[0][name]
    return None

def define_var(name, var_type, value):
    call_stack[-1][name] = {"type": var_type, "value": value}

def update_var(name, var_type, value):
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
        if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
            return value[1:-1]
        var_data = get_var(value)
        if var_data:
            result = var_data["value"]
            if not isinstance(result, str):
                raise TypeError(f"Variable '{value}' is not a string.")
            return result
        raise ValueError(f"Expected a string for type '{expected_type}'.")

    if expected_type == "bool":
        if value == "true": return True
        if value == "false": return False
        var_data = get_var(value)
        if var_data:
            result = var_data["value"]
            if not isinstance(result, bool):
                raise TypeError(f"Variable '{value}' is not a boolean.")
            return result
        raise ValueError(f"Expected 'true' or 'false' for type '{expected_type}'.")

    if expected_type in ("list", "tuple", "set"):
        if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))):
            value = value[1:-1]

        if len(value) >= 2 and (value.startswith("[") or value.startswith("(")) and (value.endswith("]") or value.endswith(")")):
            content = value[1:-1].strip()
            if not content:
                parsed = []
            else:
                raw_items = [item.strip() for item in content.split(",")]
                parsed = []
                for item in raw_items:
                    if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                        parsed.append(item[1:-1])
                    elif item.isdigit():
                        parsed.append(int(item))
                    else:
                        item_data = get_var(item)
                        parsed.append(item_data["value"] if item_data else item)
            if expected_type == "list": return parsed
            if expected_type == "tuple": return tuple(parsed)
            if expected_type == "set": return set(parsed)

        var_data = get_var(value)
        if var_data:
            return TYPES[expected_type](var_data["value"])
        raise ValueError(f"Expected a literal or variable for type '{expected_type}'.")

    if expected_type == "dict":
        if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))):
            value = value[1:-1]
        if len(value) >= 2 and value.startswith("{") and value.endswith("}"):
            content = value[1:-1].strip()
            if not content: return {}
            pairs = [p.strip() for p in content.split(",")]
            res_dict = {}
            for pair in pairs:
                k, v = pair.split(":", 1)
                k, v = k.strip().strip("\"'"), v.strip().strip("\"'")
                v_data = get_var(v)
                res_dict[k] = v_data["value"] if v_data else (int(v) if v.isdigit() else v)
            return res_dict
        var_data = get_var(value)
        if var_data and isinstance(var_data["value"], dict):
            return dict(var_data["value"])
        raise ValueError("Expected a dict literal '{key: val}' or dict variable.")

    if expected_type in ("bytes", "bytearray"):
        if len(value) >= 2 and ((value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'"))):
            val_str = value[1:-1]
        else:
            var_data = get_var(value)
            val_str = str(var_data["value"]) if var_data else value
        b_data = val_str.encode("utf-8")
        return bytes(b_data) if expected_type == "bytes" else bytearray(b_data)

    var_data = get_var(value)
    if var_data:
        result = var_data["value"]
        actual_type = var_data["type"]
        if actual_type != expected_type and expected_type != "file":
            raise TypeError(f"Variable '{value}' is type '{actual_type}', not '{expected_type}'.")
        return result

    if expected_type == "int":
        try: return int(value)
        except ValueError: raise ValueError(f"'{value}' is not a valid integer.")

    if expected_type == "float":
        try: return float(value)
        except ValueError: raise ValueError(f"'{value}' is not a valid float.")

    raise ValueError(f"Unable to parse value '{value}' for type '{expected_type}'.")


def arith(operation, a, b=None):
    var_a = get_var(a)
    is_coll_a = False
    
    if var_a:
        a_val = var_a["value"]
        if var_a["type"] in ("list", "tuple", "set"):
            is_coll_a = True
            a = a_val
        else:
            a = a_val
    else:
        try: a = float(a) if '.' in str(a) else int(a)
        except ValueError: pass

    if is_coll_a:
        if operation == "sum": return sum(a)
        elif operation == "max": return max(a)
        elif operation == "min": return min(a)
        else: raise TypeError(f"Operation '{operation}' does not support collection arguments.")

    if not isinstance(a, (int, float)) or isinstance(a, bool):
        raise TypeError(f"Arithmetic requires numbers. Got '{a}' instead.")

    if operation == "abs": return abs(a)
    elif operation == "round": return round(a)
    elif operation == "bin":
        if not isinstance(a, int): raise TypeError("bin() requires an integer.")
        return bin(a)
    elif operation == "hex":
        if not isinstance(a, int): raise TypeError("hex() requires an integer.")
        return hex(a)
    elif operation == "oct":
        if not isinstance(a, int): raise TypeError("oct() requires an integer.")
        return oct(a)

    if b is None: raise ValueError(f"Operation '{operation}' requires a second operand.")

    var_b = get_var(b)
    if var_b: b = var_b["value"]
    else:
        try: b = float(b) if '.' in str(b) else int(b)
        except ValueError: pass

    if not isinstance(b, (int, float)) or isinstance(b, bool):
        raise TypeError("Arithmetic requires numbers.")

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
    elif operation == "pow": return pow(a, b)
    elif operation == "divmod":
        if b == 0: raise ZeroDivisionError("Cannot divide by zero.")
        return list(divmod(a, b))
    else:
        raise ValueError(f"Unknown arithmetic operation: {operation}")


def evaluate_condition(cond_str):
    cond_str = cond_str.strip()
    if cond_str == "true": return True
    if cond_str == "false": return False
    var_data = get_var(cond_str)
    if var_data: return bool(var_data["value"])
    return False


def interpret(line):
    line = line.strip()
    if not line or line.startswith("#"): return

    if "#" in line: line = line.split("#", 1)[0].rstrip()

    parts = shlex.split(line, posix=False)
    if not parts: return

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
        if len(parts) == 4 and parts[2] == "to": var_name, target_type = parts[1], parts[3]
        elif len(parts) == 3: var_name, target_type = parts[1], parts[2]
        else: raise SyntaxError("Usage: convert <variable> to <type>")

        var_data = get_var(var_name)
        if not var_data: raise ValueError(f"Variable '{var_name}' is not defined.")
        if target_type not in TYPES: raise ValueError(f"Unknown type: {target_type}")

        val = var_data["value"]
        
        try:
            if target_type == "int": val = int(float(val)) if isinstance(val, (str, float)) else int(val)
            elif target_type == "float": val = float(val)
            elif target_type == "string": val = "true" if val is True else "false" if val is False else str(val)
            elif target_type == "bool":
                if isinstance(val, str):
                    if val.lower() not in ["true", "false"]: raise ValueError("String must be 'true' or 'false'.")
                    val = (val.lower() == "true")
                else: val = bool(val)
            elif target_type == "list": val = list(val) if isinstance(val, (str, tuple, set)) else [val]
            elif target_type == "tuple": val = tuple(val) if isinstance(val, (str, list, set)) else (val,)
            elif target_type == "set": val = set(val) if isinstance(val, (str, list, tuple)) else {val}
            elif target_type == "bytes": val = bytes(str(val).encode("utf-8")) if not isinstance(val, bytes) else val
            elif target_type == "bytearray": val = bytearray(str(val).encode("utf-8")) if not isinstance(val, bytearray) else val
        except Exception as e:
            raise ValueError(f"Cannot convert '{var_name}' to {target_type}: {e}")

        update_var(var_name, target_type, val)

    # --------------------------------
    # arith
    # --------------------------------
    elif parts[0] == "arith":
        single_ops = ["abs", "round", "sum", "bin", "hex", "oct"]
        if len(parts) == 3 and parts[1] in single_ops + ["max", "min"]:
            result = arith(parts[1], parts[2])
        elif len(parts) == 4 and parts[1] not in single_ops:
            result = arith(parts[1], parts[2], parts[3])
        else:
            raise SyntaxError("Usage: arith <abs|round|sum|bin|hex|oct> <val> OR arith <op> <val1> <val2>")
        print(result)

    # --------------------------------
    # compare
    # --------------------------------
    elif parts[0] == "compare":
        if len(parts) != 5:
            raise SyntaxError("Usage: compare <val1> <op> <val2> <dest_bool_var>")
        
        v1_str, op, v2_str, dest_var = parts[1], parts[2], parts[3], parts[4]

        var_v1 = get_var(v1_str)
        v1 = var_v1["value"] if var_v1 else (float(v1_str) if '.' in v1_str else int(v1_str) if v1_str.isdigit() else v1_str.strip("\"'"))

        var_v2 = get_var(v2_str)
        v2 = var_v2["value"] if var_v2 else (float(v2_str) if '.' in v2_str else int(v2_str) if v2_str.isdigit() else v2_str.strip("\"'"))

        dest_data = get_var(dest_var)
        if not dest_data or dest_data["type"] != "bool":
            raise TypeError(f"Destination variable '{dest_var}' must be a defined boolean.")

        ops = {"==": lambda a,b: a==b, "!=": lambda a,b: a!=b, "<": lambda a,b: a<b,
               ">": lambda a,b: a>b, "<=": lambda a,b: a<=b, ">=": lambda a,b: a>=b}
        if op not in ops: raise SyntaxError(f"Unknown comparison operator: {op}")
        
        update_var(dest_var, "bool", ops[op](v1, v2))

    # --------------------------------
    # Collection Operations (list, dict, set, tuple)
    # --------------------------------
    elif parts[0] in ("list", "dict", "set", "tuple"):
        coll_type = parts[0]
        if len(parts) < 3:
            raise SyntaxError(f"Usage: {coll_type} <op> <var> [args]")

        action, target_var = parts[1], parts[2]
        var_data = get_var(target_var)
        if not var_data or var_data["type"] != coll_type:
            raise TypeError(f"Variable '{target_var}' is not of type '{coll_type}'.")

        coll = var_data["value"]

        if coll_type == "list":
            if action == "append":
                val = parts[3].strip("\"'") if len(parts) == 4 else ""
                v_data = get_var(parts[3])
                coll.append(v_data["value"] if v_data else val)
            elif action == "get":
                idx, dest = int(parts[3]), parts[4]
                update_var(dest, get_var(dest)["type"], coll[idx])
            elif action == "len":
                update_var(parts[3], "int", len(coll))

        elif coll_type == "dict":
            if action == "set":
                k, v = parts[3].strip("\"'"), parts[4].strip("\"'")
                v_data = get_var(parts[4])
                coll[k] = v_data["value"] if v_data else v
            elif action == "get":
                k, dest = parts[3].strip("\"'"), parts[4]
                update_var(dest, get_var(dest)["type"], coll[k])

        elif coll_type == "set":
            if action == "add":
                val = parts[3].strip("\"'")
                v_data = get_var(parts[3])
                coll.add(v_data["value"] if v_data else val)
            elif action == "remove":
                val = parts[3].strip("\"'")
                v_data = get_var(parts[3])
                coll.remove(v_data["value"] if v_data else val)

        elif coll_type == "tuple":
            if action == "get":
                idx, dest = int(parts[3]), parts[4]
                update_var(dest, get_var(dest)["type"], coll[idx])

    # --------------------------------
    # Input / Output & File I/O
    # --------------------------------
    elif parts[0] == "text":
        if len(parts) < 3: raise SyntaxError("Usage: text <input/output> <value>")
        action = parts[1]
        if action == "output":
            value = " ".join(parts[2:])
            if (len(value) >= 2 and value[0] == '"' and value[-1] == '"') or (len(value) >= 2 and value[0] == "'" and value[-1] == "'"):
                value = value[1:-1]
            else:
                var_data = get_var(value)
                value = var_data["value"] if var_data else value
            print(value)
        elif action == "input":
            name = parts[2]
            var_data = get_var(name)
            if not var_data or var_data["type"] != "string":
                raise TypeError(f"Variable '{name}' must be a string for text input.")
            update_var(name, "string", input())

    elif parts[0] == "open":
        if len(parts) != 4:
            raise SyntaxError("Usage: open <path> <mode> <dest_file_var>")
        path, mode, dest_var = parts[1].strip("\"'"), parts[2].strip("\"'"), parts[3]
        file_obj = open(path, mode, encoding="utf-8" if "b" not in mode else None)
        if not get_var(dest_var):
            define_var(dest_var, "file", file_obj)
        else:
            update_var(dest_var, "file", file_obj)

    # --------------------------------
    # Built-in Object & Attribute Utilities
    # --------------------------------
    elif parts[0] == "getattr":
        if len(parts) != 4:
            raise SyntaxError("Usage: getattr <var_or_obj> <attr_name> <dest_var>")
        obj_name, attr_name, dest_var = parts[1], parts[2].strip("\"'"), parts[3]
        var_data = get_var(obj_name)
        obj = var_data["value"] if var_data else obj_name
        
        # Check dictionary dynamic key lookup or standard object attribute
        if isinstance(obj, dict) and attr_name in obj:
            val = obj[attr_name]
        else:
            val = getattr(obj, attr_name)

        dest_data = get_var(dest_var)
        if not dest_data: raise ValueError(f"Destination variable '{dest_var}' is not defined.")
        update_var(dest_var, dest_data["type"], val)

    elif parts[0] == "hasattr":
        if len(parts) != 4:
            raise SyntaxError("Usage: hasattr <var_or_obj> <attr_name> <dest_bool_var>")
        obj_name, attr_name, dest_var = parts[1], parts[2].strip("\"'"), parts[3]
        var_data = get_var(obj_name)
        obj = var_data["value"] if var_data else obj_name

        has_att = (attr_name in obj) if isinstance(obj, dict) else hasattr(obj, attr_name)
        update_var(dest_var, "bool", has_att)

    elif parts[0] == "setattr":
        if len(parts) != 4:
            raise SyntaxError("Usage: setattr <var_or_obj> <attr_name> <value>")
        obj_name, attr_name, val_str = parts[1], parts[2].strip("\"'"), parts[3].strip("\"'")
        var_data = get_var(obj_name)
        if not var_data: raise ValueError(f"Variable '{obj_name}' is not defined.")
        obj = var_data["value"]
        
        val_data = get_var(val_str)
        val = val_data["value"] if val_data else val_str

        if isinstance(obj, dict):
            obj[attr_name] = val
        else:
            setattr(obj, attr_name, val)

    # --------------------------------
    # Bytes & Bytearray Built-ins
    # --------------------------------
    elif parts[0] in ("bytes", "bytearray"):
        if len(parts) != 3:
            raise SyntaxError(f"Usage: {parts[0]} <string_or_var> <dest_var>")
        src_str, dest_var = parts[1].strip("\"'"), parts[2]
        var_data = get_var(src_str)
        raw_val = var_data["value"] if var_data else src_str
        b_data = bytes(str(raw_val).encode("utf-8")) if parts[0] == "bytes" else bytearray(str(raw_val).encode("utf-8"))
        update_var(dest_var, parts[0], b_data)

    # --------------------------------
    # Built-in Inspection & Utility Functions
    # --------------------------------
    elif parts[0] in ("all", "any"):
        if len(parts) != 3: raise SyntaxError(f"Usage: {parts[0]} <coll_var> <dest_bool_var>")
        lst_data = get_var(parts[1])
        if not lst_data or lst_data["type"] not in ("list", "tuple", "set", "dict"):
            raise TypeError(f"Variable '{parts[1]}' must be a defined collection.")
        res = all(lst_data["value"]) if parts[0] == "all" else any(lst_data["value"])
        update_var(parts[2], "bool", res)

    elif parts[0] == "bool":
        if len(parts) != 3: raise SyntaxError("Usage: bool <val_or_var> <dest_bool_var>")
        var_data = get_var(parts[1])
        val = var_data["value"] if var_data else evaluate_condition(parts[1])
        update_var(parts[2], "bool", bool(val))

    elif parts[0] == "callable":
        if len(parts) != 3: raise SyntaxError("Usage: callable <func_name> <dest_bool_var>")
        update_var(parts[2], "bool", parts[1] in functions)

    elif parts[0] == "id":
        if len(parts) != 3: raise SyntaxError("Usage: id <var_name> <dest_int_var>")
        var_data = get_var(parts[1])
        if not var_data: raise ValueError(f"Variable '{parts[1]}' is not defined.")
        update_var(parts[2], "int", id(var_data["value"]))

    elif parts[0] == "len":
        if len(parts) != 3: raise SyntaxError("Usage: len <var_name> <dest_int_var>")
        var_data = get_var(parts[1])
        if not var_data: raise ValueError(f"Variable '{parts[1]}' is not defined.")
        update_var(parts[2], "int", len(var_data["value"]))

    elif parts[0] == "type":
        if len(parts) != 3: raise SyntaxError("Usage: type <var_name> <dest_string_var>")
        var_data = get_var(parts[1])
        if not var_data: raise ValueError(f"Variable '{parts[1]}' is not defined.")
        update_var(parts[2], "string", var_data["type"])

    elif parts[0] == "vars":
        merged_vars = {}
        for scope in call_stack: merged_vars.update(scope)
        print("--- Active Scope Variables ---")
        for k, v in merged_vars.items(): print(f"{k}: {v['type']} = {v['value']}")
        print("--- Defined Functions ---")
        for fn in functions: print(f"func {fn}")

    elif parts[0] == "wait":
        if len(parts) != 2: raise SyntaxError("Usage: wait <seconds>")
        var_sec = get_var(parts[1])
        sec = var_sec["value"] if var_sec else float(parts[1])
        time.sleep(sec)

    else:
        raise SyntaxError(f"Unknown command: {parts[0]}")


def execute_lines(lines):
    i = 0
    while i < len(lines):
        raw_line = lines[i].strip()
        if not raw_line or raw_line.startswith("#"):
            i += 1
            continue
            
        if raw_line == "return": raise ReturnException()
        elif raw_line == "break": raise BreakException()
        elif raw_line == "continue": raise ContinueException()

        elif raw_line.startswith("if "):
            parts = shlex.split(raw_line, posix=False)
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
                    branches.append({"condition": parts[1], "body": []})
                elif line_str == "else" and depth == 1:
                    branches.append({"condition": "true", "body": []})
                else:
                    branches[-1]["body"].append(lines[i])
                i += 1
                
            for branch in branches:
                if evaluate_condition(branch["condition"]):
                    execute_lines(branch["body"])
                    break 

        elif raw_line.startswith("func define "):
            parts = shlex.split(raw_line, posix=False)
            func_name = parts[2]
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != "endfunc":
                body.append(lines[i])
                i += 1
            functions[func_name] = body

        elif raw_line.startswith("func call "):
            parts = shlex.split(raw_line, posix=False)
            func_name = parts[2]
            call_stack.append({})
            try:
                execute_lines(functions[func_name])
            except ReturnException: pass
            finally: call_stack.pop()

        elif raw_line.startswith("loop for ") or raw_line.startswith("loop while "):
            parts = shlex.split(raw_line, posix=False)
            loop_type, condition_val = parts[1], parts[2]
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != "endloop":
                body.append(lines[i])
                i += 1

            try:
                if loop_type == "for":
                    cond_data = get_var(condition_val)
                    count = cond_data["value"] if cond_data else int(condition_val)
                    for _ in range(count):
                        try: execute_lines(body)
                        except ContinueException: continue
                        except BreakException: break
                elif loop_type == "while":
                    while evaluate_condition(condition_val):
                        try: execute_lines(body)
                        except ContinueException: continue
                        except BreakException: break
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
    except ReturnException: pass 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        print("Usage: py hyperlang.py <path_to_file.hl>")