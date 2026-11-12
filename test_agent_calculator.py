
import re
import unicodedata
from uuid import uuid4

from agent.graph import run_agent


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return value.casefold()


def test_agent_calculator_percentage():
    question = (
        "Use the calculator tool to calculate 15% of 2400. "
        "Tell me the result."
    )

    result = run_agent(
        question=question,
        thread_id=f"agent-calculator-test-{uuid4().hex[:12]}",
    )

    assert result["success"] is True, result

    selected_tools = result["selected_tools"]
    answer = normalize_text(result["answer"])

    assert selected_tools.count("calculator") == 1, selected_tools
    assert result["tool_steps"] == 1, result
    assert re.search(r"\b360(?:\.0+)?\b", answer), result["answer"]

    print("\nAgent calculator integration test passed.")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {selected_tools}")
