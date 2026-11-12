
import pytest

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


@tool
def failing_test_tool(value: str) -> str:
    """Simulate a controlled tool failure."""
    raise ValueError("Simulated tool failure")


def test_tool_node_handles_tool_exception():
    """Verify ToolNode handles tool exceptions inside a graph."""

    tool_node = ToolNode(
        [failing_test_tool],
        handle_tool_errors=True,
    )

    builder = StateGraph(MessagesState)
    builder.add_node("tools", tool_node)
    builder.add_edge(START, "tools")
    builder.add_edge("tools", END)

    graph = builder.compile()

    message = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "failing_test_tool",
                "args": {"value": "test"},
                "id": "error-test-call-1",
                "type": "tool_call",
            }
        ],
    )

    result = graph.invoke(
        {"messages": [message]}
    )

    tool_messages = [
        item
        for item in result["messages"]
        if isinstance(item, ToolMessage)
    ]

    assert len(tool_messages) == 1

    error_content = tool_messages[0].content

    assert "Error" in error_content
    assert "Simulated tool failure" in error_content

    print("\nTOOL ERROR HANDLING TEST PASSED!")
    print("Exception converted into a ToolMessage.")
    print("Error details:", error_content)


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([__file__, "-v", "-s"])
    )
