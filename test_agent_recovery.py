
from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

import agent.graph as graph_module


def test_agent_recovers_after_tool_failure(monkeypatch):
    """Verify the agent receives a tool error and produces a final answer."""

    executed = []

    @tool
    def failing_test_tool(value: str) -> str:
        """Simulate a controlled tool failure."""
        executed.append(value)
        raise ValueError("Simulated recovery test failure")

    class FakeBoundModel:
        def __init__(self):
            self.call_count = 0
            self.received_error = False

        def invoke(self, messages):
            self.call_count += 1

            if self.call_count == 1:
                return AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "name": "failing_test_tool",
                            "args": {"value": "recovery-test"},
                            "id": "recovery-call-1",
                            "type": "tool_call",
                        }
                    ],
                )

            self.received_error = any(
                isinstance(message, ToolMessage)
                and "Simulated recovery test failure" in str(message.content)
                for message in messages
            )

            if not self.received_error:
                return AIMessage(
                    content="The tool error was not received.",
                )

            return AIMessage(
                content=(
                    "The tool failed, but I recovered successfully "
                    "and can explain that the requested operation "
                    "could not be completed."
                )
            )

    fake_model = FakeBoundModel()

    class FakeChatGroq:
        def __init__(self, **kwargs):
            pass

        def bind_tools(self, tools):
            return fake_model

    monkeypatch.setattr(
        graph_module,
        "AVAILABLE_TOOLS",
        [failing_test_tool],
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

    graph = graph_module.build_agent_graph(checkpointer=None)

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Run the recovery test."
                )
            ],
            "tool_steps": 0,
            "selected_tools": [],
            "user_id": "recovery-test-user",
        }
    )

    final_answer = result["messages"][-1].content

    assert len(executed) == 1
    assert fake_model.call_count == 2
    assert fake_model.received_error is True
    assert "recovered successfully" in final_answer.lower()
    assert result["tool_steps"] == 1
    assert result["selected_tools"] == ["failing_test_tool"]

    print("\nAGENT RECOVERY TEST PASSED!")
    print("Failed tool execution:", len(executed))
    print("LLM invocation count:", fake_model.call_count)
    print("Error received by LLM:", fake_model.received_error)
    print("Final answer:", final_answer)


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([__file__, "-v", "-s"])
    )
