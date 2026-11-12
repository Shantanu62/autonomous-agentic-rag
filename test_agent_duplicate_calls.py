
import pytest

from agent.graph import create_tool_fingerprint


def test_same_tool_and_arguments_have_same_fingerprint():
    first = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1001"},
    )
    second = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1001"},
    )
    assert first == second


def test_string_arguments_are_normalized():
    first = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": " TCK-1001 "},
    )
    second = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "tck-1001"},
    )
    assert first == second


def test_different_ticket_ids_have_different_fingerprints():
    first = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1001"},
    )
    second = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1002"},
    )
    assert first != second


def test_different_tools_have_different_fingerprints():
    first = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1001"},
    )
    second = create_tool_fingerprint(
        "search_operations_documents",
        {"question": "TCK-1001"},
    )
    assert first != second


def test_fingerprint_is_stable_when_argument_order_changes():
    first = create_tool_fingerprint(
        "sla_lookup",
        {
            "reporting_period": "2026-11",
            "assigned_team": "Platform Support",
        },
    )
    second = create_tool_fingerprint(
        "sla_lookup",
        {
            "assigned_team": "Platform Support",
            "reporting_period": "2026-11",
        },
    )
    assert first == second
