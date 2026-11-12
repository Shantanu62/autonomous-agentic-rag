
import json

from observability.logger import (
    ExecutionTimer,
    build_run_details,
    create_run_id,
    log_event,
)


def test_run_id_generation():
    first_id = create_run_id()
    second_id = create_run_id()

    assert first_id
    assert first_id != second_id

    print("Unique run ID generation: PASSED")


def test_execution_timer():
    timer = ExecutionTimer()

    elapsed = timer.elapsed_ms()

    assert isinstance(elapsed, float)
    assert elapsed >= 0

    print("Execution timer: PASSED")


def test_run_details():
    details = build_run_details(
        run_id="test-run-001",
        thread_id="test-thread-001",
        tool_steps=2,
        selected_tools=["ticket_lookup", "calculator"],
        sources=[
            {
                "source": "company_sop.txt",
                "page": None,
            }
        ],
        errors=[],
        latency_ms=125.50,
    )

    assert details["run_id"] == "test-run-001"
    assert details["tool_steps"] == 2
    assert len(details["selected_tools"]) == 2
    assert details["sources"][0]["source"] == "company_sop.txt"
    assert details["latency_ms"] == 125.50

    print("Run details generation: PASSED")


def test_structured_logging():
    test_run_id = create_run_id()

    log_event(
        event_type="test_event",
        run_id=test_run_id,
        details={
            "tool": "ticket_lookup",
            "status": "success",
        },
    )

    from observability.logger import LOG_FILE

    assert LOG_FILE.exists()

    matching_events = []

    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            event = json.loads(line)

            if event["run_id"] == test_run_id:
                matching_events.append(event)

    assert len(matching_events) == 1
    assert matching_events[0]["event_type"] == "test_event"
    assert matching_events[0]["details"]["tool"] == "ticket_lookup"

    print("Structured JSON logging: PASSED")


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
