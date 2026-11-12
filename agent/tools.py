
import ast
import math
import operator
import re
import sqlite3
from pathlib import Path
from typing import Any

from tavily import TavilyClient

from config import settings


WEB_SEARCH_TIMEOUT_SECONDS = 20


def get_database_path() -> Path:
    """Resolve the configured database path relative to the project root."""
    path = Path(settings.database_path)

    if not path.is_absolute():
        path = Path(__file__).resolve().parent.parent / path

    return path


def get_readonly_connection() -> sqlite3.Connection:
    """Open the operations database in read-only mode."""
    database_path = get_database_path()

    if not database_path.exists():
        raise FileNotFoundError("Operations database was not found.")

    connection_uri = f"{database_path.resolve().as_uri()}?mode=ro"

    connection = sqlite3.connect(
        connection_uri,
        uri=True,
        timeout=5,
    )
    connection.row_factory = sqlite3.Row

    return connection


def lookup_ticket(ticket_id: str) -> dict[str, Any]:
    """Look up a ticket using a parameterized, read-only SQL query."""
    normalized_id = ticket_id.strip().upper() if ticket_id else ""

    if not normalized_id:
        return {
            "success": False,
            "error": "A ticket ID is required.",
        }

    if len(normalized_id) > 30:
        return {
            "success": False,
            "error": "Ticket ID is too long.",
        }

    try:
        with get_readonly_connection() as connection:
            row = connection.execute(
                """
                SELECT
                    ticket_id,
                    title,
                    description,
                    status,
                    priority,
                    requester,
                    assigned_team,
                    created_at,
                    updated_at
                FROM tickets
                WHERE ticket_id = ?
                """,
                (normalized_id,),
            ).fetchone()

        if row is None:
            return {
                "success": False,
                "error": f"Ticket {normalized_id} was not found.",
            }

        return {
            "success": True,
            "ticket": dict(row),
        }

    except Exception:
        return {
            "success": False,
            "error": "Ticket lookup failed. Please try again later.",
        }


def get_sla_metrics(
    reporting_period: str,
    assigned_team: str | None = None,
) -> dict[str, Any]:
    """Retrieve SLA metrics using read-only SQL queries."""
    normalized_period = reporting_period.strip() if reporting_period else ""

    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", normalized_period):
        return {
            "success": False,
            "error": "Reporting period must use YYYY-MM format.",
        }

    if assigned_team is not None:
        assigned_team = assigned_team.strip()

        if not assigned_team or len(assigned_team) > 100:
            return {
                "success": False,
                "error": "Invalid assigned team.",
            }

    try:
        with get_readonly_connection() as connection:
            if assigned_team:
                rows = connection.execute(
                    """
                    SELECT
                        reporting_period,
                        assigned_team,
                        total_tickets,
                        resolved_tickets,
                        breached_tickets,
                        target_resolution_hours,
                        average_resolution_hours
                    FROM sla_metrics
                    WHERE reporting_period = ?
                      AND assigned_team = ?
                    ORDER BY assigned_team
                    """,
                    (normalized_period, assigned_team),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT
                        reporting_period,
                        assigned_team,
                        total_tickets,
                        resolved_tickets,
                        breached_tickets,
                        target_resolution_hours,
                        average_resolution_hours
                    FROM sla_metrics
                    WHERE reporting_period = ?
                    ORDER BY assigned_team
                    """,
                    (normalized_period,),
                ).fetchall()

        return {
            "success": True,
            "reporting_period": normalized_period,
            "total_records": len(rows),
            "metrics": [dict(row) for row in rows],
        }

    except Exception:
        return {
            "success": False,
            "error": "SLA metrics lookup failed. Please try again later.",
        }


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _evaluate_math_node(node: ast.AST) -> float | int:
    """Safely evaluate an allowed arithmetic AST node."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(
            node.value,
            (int, float),
        ):
            raise ValueError("Only numeric constants are allowed.")

        return node.value

    if isinstance(node, ast.BinOp):
        operation = _ALLOWED_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported operator.")

        left = _evaluate_math_node(node.left)
        right = _evaluate_math_node(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large.")

        if abs(left) > 1e12 or abs(right) > 1e12:
            raise ValueError("Numeric input is too large.")

        result = operation(left, right)

        if not math.isfinite(result) or abs(result) > 1e15:
            raise ValueError("Result is outside the permitted range.")

        return result

    if isinstance(node, ast.UnaryOp):
        operation = _ALLOWED_UNARY_OPERATORS.get(type(node.op))

        if operation is None:
            raise ValueError("Unsupported unary operator.")

        return operation(_evaluate_math_node(node.operand))

    raise ValueError("Unsupported expression.")


def calculate(expression: str) -> dict[str, Any]:
    """Safely calculate basic arithmetic without using eval()."""
    normalized_expression = expression.strip() if expression else ""

    if not normalized_expression:
        return {
            "success": False,
            "error": "A mathematical expression is required.",
        }

    if len(normalized_expression) > 100:
        return {
            "success": False,
            "error": "Mathematical expression is too long.",
        }

    try:
        parsed = ast.parse(normalized_expression, mode="eval")

        if sum(1 for _ in ast.walk(parsed)) > 30:
            raise ValueError("Expression is too complex.")

        result = _evaluate_math_node(parsed.body)

        return {
            "success": True,
            "expression": normalized_expression,
            "result": result,
        }

    except Exception:
        return {
            "success": False,
            "error": "Invalid or unsupported mathematical expression.",
        }


def web_search(
    query: str,
    max_results: int = 5,
) -> dict[str, Any]:
    """Search the live web using Tavily with bounded execution time."""
    normalized_query = query.strip() if query else ""

    if not normalized_query:
        return {
            "success": False,
            "error": "A search query is required.",
        }

    if len(normalized_query) > 500:
        return {
            "success": False,
            "error": "Search query is too long.",
        }

    if not isinstance(max_results, int) or isinstance(max_results, bool):
        return {
            "success": False,
            "error": "Maximum results must be an integer.",
        }

    if not 1 <= max_results <= 5:
        return {
            "success": False,
            "error": "Maximum results must be between 1 and 5.",
        }

    if not settings.tavily_api_key:
        return {
            "success": False,
            "error": "Tavily API key is not configured.",
        }

    try:
        client = TavilyClient(api_key=settings.tavily_api_key)

        response = client.search(
            query=normalized_query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
            timeout=WEB_SEARCH_TIMEOUT_SECONDS,
        )

        results = []

        for item in response.get("results", []):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score"),
                }
            )

        return {
            "success": True,
            "query": normalized_query,
            "total_results": len(results),
            "results": results,
        }

    except (TimeoutError, ConnectionError):
        return {
            "success": False,
            "error": "Live web search timed out or the connection failed. Please try again later.",
        }

    except Exception:
        return {
            "success": False,
            "error": "Live web search failed. Check the API connection or try again later.",
        }
