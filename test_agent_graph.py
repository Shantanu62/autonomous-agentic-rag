
from agent.graph import AVAILABLE_TOOLS, get_agent_graph


def main():
    print("Initializing LangGraph agent...")

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

    print("\nRegistered tools:")

    for tool in AVAILABLE_TOOLS:
        print(f"- {tool.name}")

    print(f"\nTotal registered tools: {len(AVAILABLE_TOOLS)}")

    assert len(AVAILABLE_TOOLS) == 9, (
        f"Expected 9 tools, found {len(AVAILABLE_TOOLS)}"
    )

    assert actual_tools == expected_tools, (
        "Registered tools do not match the expected tool list."
    )

    print("\nBuilding agent graph...")

    graph = get_agent_graph()

    graph_nodes = set(graph.get_graph().nodes.keys())

    expected_nodes = {
        "__start__",
        "agent",
        "tools",
        "limit",
        "__end__",
    }

    print("\nGraph nodes:")

    for node in sorted(graph_nodes):
        print(f"- {node}")

    assert expected_nodes.issubset(graph_nodes), (
        "One or more expected graph nodes are missing."
    )

    print("\nAgent graph initialization test PASSED!")


if __name__ == "__main__":
    main()
