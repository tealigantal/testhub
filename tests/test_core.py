from scicalc import evaluate


def test_addition():
    assert evaluate("2 + 2") == 4


def test_trigonometry():
    assert round(evaluate("sin(pi / 2)"), 8) == 1.0
