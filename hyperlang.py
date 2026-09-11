# HyperLang Executable
# Copyleft 🄯 2026 HyperLang Tecnhologies\

import sys

from interpreter.interpreter import run_file


def main():
    if len(sys.argv) != 2:
        print("Usage: python hyperlang.py <file.hl>")
        sys.exit(1)

    filename = sys.argv[1]

    run_file(filename)


if __name__ == "__main__":
    main()