
from uuid import uuid4

from agent.graph import run_agent


def main():
    print("Testing LangGraph SLA tool execution...")

    question = (
        "Show me the November 2026 SLA metrics "
        "for Platform Support. Include total tickets, "
        "resolved tickets, breached tickets, and average "
        "resolution time."
    )

    thread_id = f"agent-sla-test-{uuid4().hex[:12]}"

    print(f"\nQuestion: {question}")
    print(f"Fresh thread ID: {thread_id}")

    result = run_agent(
        question=question,
        thread_id=thread_id,
        user_id="sla-execution-test-user",
    )

    print("\nAgent execution result:")
    print("Success:", result.get("success"))
    print("Answer:", result.get("answer", result.get("error")))
    print("Tool steps:", result.get("tool_steps"))
    print("Selected tools:", result.get("selected_tools"))

    if result.get("success"):
        assert "sla_lookup" in result["selected_tools"]
        assert result["tool_steps"] >= 1
        assert "120" in result["answer"]
        print("\nACTUAL SLA TOOL EXECUTION PASSED!")
    else:
        raise AssertionError("SLA agent execution failed!")


if __name__ == "__main__":
    main()
