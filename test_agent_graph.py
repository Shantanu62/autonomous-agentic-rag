
import pytest

from agent.graph import AVAILABLE_TOOLS, get_agent_graph


def test_agent_graph_initialization():
    expected_tools = {
        "search_operations_documents",
        "ticket_lookup",
        "sla_lookup",
        "calculator",
        "live_web_search",
        "search_long_term_memory",
        "save_long_term_memory",
        "inspect_long_term_memory",
        "delete_long_term_memory",
    }

    actual_tools = {
        tool.name for tool in AVAILABLE_TOOLS
    }

    assert len(AVAILABLE_TOOLS) == 9
    assert actual_tools == expected_tools

    graph = get_agent_graph()

    graph_nodes = set(graph.get_graph().nodes.keys())

    expected_nodes = {
        "__start__",
        "agent",
        "tools",
        "limit",
        "__end__",
    }

    assert expected_nodes.issubset(graph_nodes)
