
from uuid import uuid4

from agent.graph import run_agent


def main():
    question = (
        "According to the company leave policy, "
        "how many paid annual leave days are available "
        "to full-time employees? Use the operations "
        "documents to verify the answer."
    )

    thread_id = f"agent-rag-test-{uuid4().hex[:12]}"

    print("Testing LangGraph RAG tool execution...")
    print(f"\nQuestion: {question}")
    print(f"Fresh thread ID: {thread_id}")

    result = run_agent(
        question=question,
        thread_id=thread_id,
        user_id="rag-execution-test-user",
    )

    print("\nAgent execution result:")
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {result['selected_tools']}")

    if result["success"]:
        assert "search_operations_documents" in result["selected_tools"]
        assert "20" in result["answer"]
        assert result["tool_steps"] >= 1
        print("\nACTUAL RAG TOOL EXECUTION PASSED!")
    else:
        raise AssertionError("RAG tool execution failed!")


if __name__ == "__main__":
    main()
