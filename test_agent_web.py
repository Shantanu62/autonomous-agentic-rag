
from agent.graph import run_agent


def main():
    question = (
        "Use the live web search tool to find "
        "recent developments in enterprise AI agents "
        "in 2026. Summarize the two most relevant findings "
        "and include their source URLs."
    )

    print("Testing LangGraph live web search execution...")
    print(f"\nQuestion: {question}")

    result = run_agent(
        question=question,
        thread_id="agent-web-test-001",
    )

    print("\nAgent execution result:")
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {result['selected_tools']}")

    if result["success"]:
        assert "live_web_search" in result["selected_tools"]
        print("\nACTUAL LIVE WEB SEARCH TOOL EXECUTION PASSED!")
    else:
        print("\nLIVE WEB SEARCH EXECUTION FAILED!")


if __name__ == "__main__":
    main()
