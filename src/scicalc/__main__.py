"""Command-line interface for the scientific calculator."""

from .core import evaluate


def main() -> None:
    """Run the interactive calculator REPL."""
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
