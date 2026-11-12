
import pytest

from agent.graph import create_tool_fingerprint
from agent.tool_safety import filter_duplicate_tool_calls


def make_call(name, arguments, call_id):
    return {
        "name": name,
        "args": arguments,
        "id": call_id,
        "type": "tool_call",
    }


def test_duplicate_calls_in_same_batch_are_blocked():
    calls = [
        make_call("ticket_lookup", {"ticket_id": "TCK-1001"}, "call-1"),
        make_call("ticket_lookup", {"ticket_id": "TCK-1001"}, "call-2"),
    ]

    fresh, duplicates, fingerprints = filter_duplicate_tool_calls(calls, set())

    assert len(fresh) == 1
    assert len(duplicates) == 1
    assert list(fingerprints) == ["call-1"]


def test_different_ticket_ids_are_preserved():
    calls = [
        make_call("ticket_lookup", {"ticket_id": "TCK-1001"}, "call-1"),
        make_call("ticket_lookup", {"ticket_id": "TCK-1002"}, "call-2"),
    ]

    fresh, duplicates, _ = filter_duplicate_tool_calls(calls, set())

    assert len(fresh) == 2
    assert duplicates == []


@pytest.mark.parametrize(
    "tool_name",
    ["search_operations_documents", "live_web_search"],
)
def test_single_use_tools_are_blocked_after_first_call(tool_name):
    calls = [
        make_call(tool_name, {"query": "first query"}, "call-1"),
        make_call(tool_name, {"query": "second query"}, "call-2"),
    ]

    fresh, duplicates, _ = filter_duplicate_tool_calls(calls, set())

    assert len(fresh) == 1
    assert len(duplicates) == 1


@pytest.mark.parametrize(
    "tool_name",
    ["search_operations_documents", "live_web_search"],
)
def test_single_use_tools_remain_blocked_across_batches(tool_name):
    previous_fingerprint = create_tool_fingerprint(
        tool_name,
        {"query": "previous query"},
    )

    calls = [
        make_call(tool_name, {"query": "new query"}, "call-1"),
    ]

    fresh, duplicates, _ = filter_duplicate_tool_calls(
        calls,
        {previous_fingerprint},
    )

    assert fresh == []
    assert len(duplicates) == 1


def test_identical_calls_are_blocked_across_batches():
    previous_fingerprint = create_tool_fingerprint(
        "ticket_lookup",
        {"ticket_id": "TCK-1001"},
    )

    calls = [
        make_call("ticket_lookup", {"ticket_id": "TCK-1001"}, "call-1"),
    ]

    fresh, duplicates, _ = filter_duplicate_tool_calls(
        calls,
        {previous_fingerprint},
    )

    assert fresh == []
    assert len(duplicates) == 1
