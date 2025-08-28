#!/usr/bin/env python3
"""Interactive scientific calculator."""
import math

# Build a dictionary of allowed names from the math module
ALLOWED_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
ALLOWED_NAMES.update({"abs": abs, "round": round})


def evaluate(expression: str) -> float:
    """Safely evaluate a math expression using only allowed names."""
    expression = expression.replace("^", "**")  # allow ^ for exponent
    return eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)


def main() -> None:
    print("Scientific Calculator. Type 'exit' or 'quit' to exit.")
    while True:
        try:
            expression = input(">>> ").strip()
            if not expression:
                continue
            if expression.lower() in {"exit", "quit"}:
                print("Goodbye!")
                break
            result = evaluate(expression)
            print(result)
        except Exception as exc:  # catch evaluation errors
            print(f"Error: {exc}")


if __name__ == "__main__":
    main()
