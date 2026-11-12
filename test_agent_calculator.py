
from agent.graph import run_agent


def main():
    question = (
        "Use the calculator tool to calculate "
        "(120 - 114) / 120 * 100. "
        "Tell me the result as a percentage."
    )

    print("Testing LangGraph calculator tool execution...")
    print(f"\nQuestion: {question}")

    result = run_agent(
        question=question,
        thread_id="agent-calculator-test-001",
    )

    print("\nAgent execution result:")
    print(f"Success: {result['success']}")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {result['selected_tools']}")

    if result["success"]:
        assert "calculator" in result["selected_tools"]
        print("\nACTUAL CALCULATOR TOOL EXECUTION PASSED!")
    else:
        print("\nCALCULATOR TOOL EXECUTION FAILED!")


if __name__ == "__main__":
    main()
