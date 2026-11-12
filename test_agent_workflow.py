
from uuid import uuid4

from agent.graph import run_agent


def main():
    question = (
        "I need a combined operations report. "
        "First, use the operations documents to find "
        "how many paid annual leave days full-time "
        "employees receive per calendar year. "
        "Then look up ticket TCK-1001 and report "
        "its current status and priority. "
        "Clearly separate the policy information "
        "from the ticket information and cite their sources."
    )

    thread_id = f"agent-workflow-test-{uuid4().hex[:12]}"

    print("Testing combined multi-tool agent workflow...")
    print(f"\nQuestion: {question}")
    print(f"Fresh thread ID: {thread_id}")

    result = run_agent(
        question=question,
        thread_id=thread_id,
        user_id="workflow-execution-test-user",
    )

    print("\nAgent execution result:")
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {result['selected_tools']}")

    if result["success"]:
        selected = result["selected_tools"]

        assert "search_operations_documents" in selected
        assert "ticket_lookup" in selected
        assert result["tool_steps"] >= 2
        assert result["tool_steps"] <= 4

        print("\nCOMBINED MULTI-TOOL WORKFLOW PASSED!")
    else:
        raise AssertionError("Multi-tool workflow failed!")


if __name__ == "__main__":
    main()
