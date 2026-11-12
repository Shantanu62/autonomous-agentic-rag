
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "agent_runs.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("operations_agent")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)


def create_run_id() -> str:
    """Generate a unique identifier for an agent execution."""
    return str(uuid4())


def current_timestamp() -> str:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def log_event(
    event_type: str,
    run_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Write a structured JSON event to the agent log."""
    event = {
        "timestamp": current_timestamp(),
        "run_id": run_id,
        "event_type": event_type,
        "details": details or {},
    }

    logger.info(
        json.dumps(
            event,
            ensure_ascii=False,
            default=str,
        )
    )


class ExecutionTimer:
    """Measure elapsed execution time."""

    def __init__(self):
        self.start_time = time.perf_counter()

    def elapsed_ms(self) -> float:
        """Return elapsed time in milliseconds."""
        return round(
            (time.perf_counter() - self.start_time) * 1000,
            2,
        )


def extract_sources(tool_result: Any) -> list[dict[str, Any]]:
    """Extract source IDs and safe citation metadata from a RAG response."""
    if isinstance(tool_result, str):
        try:
            tool_result = json.loads(tool_result)
        except (json.JSONDecodeError, TypeError):
            return []

    if not isinstance(tool_result, dict):
        return []

    sources = tool_result.get("sources", [])

    if not isinstance(sources, list):
        return []

    extracted = []

    for source in sources:
        if not isinstance(source, dict):
            continue

        extracted.append(
            {
                "source_id": source.get("source_id"),
                "source": source.get("source", "Unknown source"),
                "page": source.get("page"),
                "chunk": source.get("chunk"),
                "score": source.get("score"),
                "citation": source.get("citation", ""),
            }
        )

    return extracted


def extract_tool_error(tool_result: Any) -> str | None:
    """Extract a tool failure message from its structured response."""
    if isinstance(tool_result, str):
        try:
            tool_result = json.loads(tool_result)
        except (json.JSONDecodeError, TypeError):
            return None

    if not isinstance(tool_result, dict):
        return None

    if tool_result.get("success") is False:
        error = tool_result.get("error")

        if isinstance(error, str) and error.strip():
            return error.strip()[:300]

        return "Tool execution failed."

    return None


def build_run_details(
    run_id: str,
    thread_id: str,
    tool_steps: int,
    selected_tools: list[str],
    sources: list[dict[str, Any]] | None = None,
    errors: list[str] | None = None,
    latency_ms: float = 0,
) -> dict[str, Any]:
    """Build a structured, UI-friendly execution summary."""
    return {
        "run_id": run_id,
        "thread_id": thread_id,
        "tool_steps": tool_steps,
        "selected_tools": selected_tools,
        "sources": sources or [],
        "errors": errors or [],
        "latency_ms": round(latency_ms, 2),
    }
