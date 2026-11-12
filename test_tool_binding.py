
from langchain_groq import ChatGroq
from langchain_core.tools import tool

from config import settings


@tool
def calculator(expression: str) -> str:
    """Perform a mathematical calculation."""
    return f"Calculation requested: {expression}"


@tool
def ticket_lookup(ticket_id: str) -> str:
    """Look up an operations ticket by its ID."""
    return f"Ticket lookup requested: {ticket_id}"


@tool
def sla_lookup(reporting_period: str) -> str:
    """Retrieve SLA metrics for a reporting period."""
    return f"SLA lookup requested: {reporting_period}"


@tool
def live_web_search(query: str) -> str:
    """Search the live web for current information."""
    return f"Web search requested: {query}"


def main():
    print("Testing Groq tool binding...")

    model = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0,
        max_retries=2,
        timeout=30,
    )

    tools = [
        calculator,
        ticket_lookup,
        sla_lookup,
        live_web_search,
    ]

    model_with_tools = model.bind_tools(tools)

    print("Groq model:", settings.groq_model)
    print("Tools registered:", len(tools))
    print("Tool binding successful!")

    response = model_with_tools.invoke(
        "Look up ticket TCK-1001 using the ticket lookup tool."
    )

    print("\nModel response received!")
    print("Tool calls:", response.tool_calls)

    assert response is not None
    assert len(response.tool_calls) > 0
    assert response.tool_calls[0]["name"] == "ticket_lookup"

    print("\nGroq function calling test PASSED!")


if __name__ == "__main__":
    main()
