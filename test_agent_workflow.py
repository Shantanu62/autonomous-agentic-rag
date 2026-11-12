
from uuid import uuid4

import re
import unicodedata

from agent.graph import run_agent


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = value.casefold()
    value = re.sub(r"[\u2010-\u2015\u2212\u00ad]", "-", value)
    return value


def test_combined_multi_tool_workflow():
    question = (
        "I need a combined operations report. "
        "Use the operations documents to find how many "
        "paid annual leave days full-time employees receive "
        "per calendar year. Also look up ticket TCK-1001 "
        "and report its current status and priority. "
        "Use both tools, clearly separate the two sections, "
        "and cite the policy source."
    )

    thread_id = f"agent-workflow-test-{uuid4().hex[:12]}"

    result = run_agent(
        question=question,
        thread_id=thread_id,
        user_id="workflow-execution-test-user",
    )

    assert result["success"] is True, result

    selected = result["selected_tools"]
    answer = normalize_text(result["answer"])

    assert selected.count("search_operations_documents") == 1
    assert selected.count("ticket_lookup") == 1
    assert result["tool_steps"] == 2

    assert "20" in answer
    assert "tck-1001" in answer
    assert "open" in answer
    assert "critical" in answer

    sources = result.get("sources", [])

    assert any(
        source.get("source") == "company_sop.txt"
        for source in sources
    ), sources

    print("\nCombined workflow passed!")
    print(f"Answer: {result['answer']}")
    print(f"Tool steps: {result['tool_steps']}")
    print(f"Selected tools: {selected}")
    print(f"Sources: {sources}")
