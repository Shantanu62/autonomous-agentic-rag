
import pytest

from agent.tools import calculate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("100 + 50", 150),
        ("(100 + 50) * 2 - 25", 275),
        ("100 / 4", 25),
        ("2 ** 5", 32),
        ("15 % of 2400", 360),
        ("15 percent of 2400", 360),
        ("15 per cent of 2400", 360),
        ("15 / 100 * 2400", 360),
    ],
)
def test_valid_calculations(expression, expected):
    result = calculate(expression)

    assert result["success"] is True
    assert result["result"] == pytest.approx(expected)


@pytest.mark.parametrize(
    "expression",
    [
        "100 / 0",
        "__import__('os').system('whoami')",
        "",
        "10 > 5",
        "2 ** 100",
        "x + 10",
    ],
)
def test_invalid_calculations(expression):
    result = calculate(expression)

    assert result["success"] is False
    assert "error" in result


def test_empty_expression():
    result = calculate("")

    assert result["success"] is False
    assert result["error"] == "A mathematical expression is required."


def test_expression_too_long():
    result = calculate("1" * 101)

    assert result["success"] is False
    assert result["error"] == "Mathematical expression is too long."


def test_percentage_preserves_original_expression():
    result = calculate("15 % of 2400")

    assert result["success"] is True
    assert result["expression"] == "15 % of 2400"
    assert result["result"] == pytest.approx(360)
