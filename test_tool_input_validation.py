
import pytest

from agent.tools import (
    calculate,
    get_sla_metrics,
    lookup_ticket,
    web_search,
)


def test_ticket_input_validation():
    assert lookup_ticket("")["success"] is False
    assert lookup_ticket("   ")["success"] is False
    assert lookup_ticket("T" * 31)["success"] is False

    # SQL injection attempt must remain a harmless lookup.
    result = lookup_ticket("' OR 1=1 --")
    assert result["success"] is False

    print("Ticket input validation: PASSED")


def test_sla_input_validation():
    invalid_periods = [
        "",
        "2026",
        "2026-13",
        "2026-00",
        "26-11",
        "2026/11",
    ]

    for period in invalid_periods:
        result = get_sla_metrics(period)
        assert result["success"] is False

    assert get_sla_metrics("2026-11", "T" * 101)["success"] is False

    print("SLA input validation: PASSED")


def test_calculator_input_validation():
    invalid_expressions = [
        "",
        "   ",
        "__import__('os').system('whoami')",
        "10 / 0",
        "2 ** 100",
        "True + 1",
        "10 + unknown",
    ]

    for expression in invalid_expressions:
        result = calculate(expression)
        assert result["success"] is False

    assert calculate("10 + 5")["result"] == 15

    print("Calculator input validation: PASSED")


def test_web_search_input_validation():
    assert web_search("")["success"] is False
    assert web_search("   ")["success"] is False

    assert web_search("test query", max_results=0)["success"] is False
    assert web_search("test query", max_results=10)["success"] is False
    assert web_search("test query", max_results=True)["success"] is False
    assert web_search("test query", max_results=1.5)["success"] is False

    assert web_search("x" * 501)["success"] is False

    print("Web search input validation: PASSED")


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([__file__, "-v", "-s"])
    )
