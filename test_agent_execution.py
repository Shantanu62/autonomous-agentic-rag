
from uuid import uuid4

from agent.graph import run_agent


def main():
    thread_id = f"agent-ticket-test-{uuid4().hex[:12]}"

    print("Testing actual LangGraph agent execution...")
    print("Question: Look up ticket TCK-1001.")
    print("Fresh thread ID:", thread_id)

    result = run_agent(
        question=(
            "Look up ticket TCK-1001 and tell me "
            "its current status and priority."
        ),
        thread_id=thread_id,
        user_id="ticket-execution-test-user",
    )

    print("\nAgent execution result:")
    print("Success:", result.get("success"))
    print("Answer:", result.get("answer", result.get("error")))
    print("Tool steps:", result.get("tool_steps"))
    print("Selected tools:", result.get("selected_tools"))

    assert result.get("success"), (
        f"Agent execution failed: {result.get('error')}"
    )

    assert "ticket_lookup" in result.get("selected_tools", []), (
        "Agent did not execute ticket_lookup."
    )

    assert result.get("tool_steps", 0) >= 1, (
        "Expected at least one tool execution."
    )

    print("\nACTUAL TICKET TOOL EXECUTION PASSED!")


if __name__ == "__main__":
    main()
