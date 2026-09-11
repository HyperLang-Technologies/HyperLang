# HyperLang Interpreter
# Copyleft 🄯 2026 HyperLang Tecnhologies

def arith(operation, a, b):
    a = float(a)
    b = float(b)

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
        raise ValueError(f"Unknown arithmetic operation: {operation}")


def interpret(line):
    parts = line.split()

    if not parts:
        return

    if parts[0] == "arith":
        if len(parts) != 4:
            raise SyntaxError(
                "Usage: arith <operation> <number> <number>"
            )

        operation = parts[1]
        a = parts[2]
        b = parts[3]

        result = arith(operation, a, b)

        print(result)

    else:
        raise SyntaxError(f"Unknown command: {parts[0]}")


def run_file(filename):
    with open(filename, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                interpret(line)

            except (SyntaxError, ValueError, ZeroDivisionError) as error:
                print(f"Error on line {line_number}: {error}")