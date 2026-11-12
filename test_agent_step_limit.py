
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

import agent.graph as graph_module


def make_tool_calls(count):
    """Create deterministic mock tool calls."""
    return [
        {
            "name": "limit_test_tool",
            "args": {"value": str(index + 1)},
            "id": f"call-{index + 1}",
            "type": "tool_call",
        }
        for index in range(count)
    ]


def build_test_graph(monkeypatch, response_batches, executed):
    """Build the real agent graph with a mock LLM and harmless test tool."""

    @tool
    def limit_test_tool(value: str) -> str:
        """Record a harmless test tool execution."""
        executed.append(value)
        return f"Executed test call {value}"

    class FakeBoundModel:
        def __init__(self):
            self.call_index = 0

        def invoke(self, messages):
            if self.call_index >= len(response_batches):
                return AIMessage(content="Test model finished.")

            response = response_batches[self.call_index]
            self.call_index += 1
            return response

    class FakeChatGroq:
        def __init__(self, **kwargs):
            pass

        def bind_tools(self, tools):
            return FakeBoundModel()

    monkeypatch.setattr(
        graph_module,
        "AVAILABLE_TOOLS",
        [limit_test_tool],
    )

    monkeypatch.setattr(
        graph_module,
        "settings",
        SimpleNamespace(
            groq_api_key="mock-key",
            groq_model="mock-model",
            max_agent_steps=4,
        ),
    )

    monkeypatch.setattr(
        graph_module,
        "ChatGroq",
        FakeChatGroq,
    )

    return graph_module.build_agent_graph(checkpointer=None)


def test_four_calls_allowed_and_fifth_blocked(monkeypatch):
    """Verify four calls execute and the fifth call is blocked."""

    executed = []

    responses = [
        AIMessage(content="", tool_calls=make_tool_calls(4)),
        AIMessage(content="", tool_calls=make_tool_calls(1)),
    ]

    graph = build_test_graph(monkeypatch, responses, executed)

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="Test the four-step execution limit.")
            ],
            "tool_steps": 0,
            "selected_tools": [],
            "user_id": "step-limit-test-user",
        }
    )

    assert len(executed) == 4
    assert result["tool_steps"] == 4
    assert len(result["selected_tools"]) == 4

    final_answer = result["messages"][-1].content.lower()
    assert "limit" in final_answer

    print("\nTEST 1 PASSED")
    print("Four tool calls executed:", len(executed))
    print("Total tool steps:", result["tool_steps"])
    print("Fifth tool call blocked successfully.")


def test_five_calls_blocked_before_execution(monkeypatch):
    """Verify a batch of five calls is rejected before execution."""

    executed = []

    responses = [
        AIMessage(content="", tool_calls=make_tool_calls(5)),
    ]

    graph = build_test_graph(monkeypatch, responses, executed)

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content="Try to execute five tool calls.")
            ],
            "tool_steps": 0,
            "selected_tools": [],
            "user_id": "step-limit-test-user",
        }
    )

    assert len(executed) == 0
    assert result["tool_steps"] == 0
    assert len(result["selected_tools"]) == 0

    final_answer = result["messages"][-1].content.lower()
    assert "limit" in final_answer

    print("\nTEST 2 PASSED")
    print("Five-call batch executed: No")
    print("Tool steps:", result["tool_steps"])
    print("Over-limit batch blocked successfully.")


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([__file__, "-v", "-s"])
    )
