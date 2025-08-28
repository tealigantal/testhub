"""Core evaluation logic for the scientific calculator."""

from __future__ import annotations

import math

# Build a dictionary of allowed names from the math module
ALLOWED_NAMES = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
ALLOWED_NAMES.update({"abs": abs, "round": round})


def evaluate(expression: str) -> float:
    """Safely evaluate a math expression using only allowed names."""
    expression = expression.replace("^", "**")  # allow ^ for exponent
    return eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
