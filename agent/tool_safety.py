
import json
from typing import Any


SINGLE_USE_TOOLS = {
    "search_operations_documents",
    "live_web_search",
}


def filter_duplicate_tool_calls(
    tool_calls: list[dict[str, Any]],
    executed_tool_calls: set[str] | list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    """Filter duplicate calls while preserving distinct business lookups."""

    seen_fingerprints = set(executed_tool_calls)
    used_single_use_tools = set()

    for fingerprint in seen_fingerprints:
        try:
            payload = json.loads(fingerprint)
            tool_name = payload.get("tool")

            if tool_name in SINGLE_USE_TOOLS:
                used_single_use_tools.add(tool_name)

        except (TypeError, ValueError, AttributeError):
            continue

    fresh_calls = []
    duplicate_calls = []
    fingerprints_by_call_id = {}

    for call in tool_calls:
        tool_name = call["name"]
        arguments = call.get("args", {})

        normalized_arguments = {}

        for key, value in sorted(arguments.items()):
            if isinstance(value, str):
                value = " ".join(value.strip().lower().split())

            normalized_arguments[key] = value

        fingerprint = json.dumps(
            {
                "tool": tool_name,
                "arguments": normalized_arguments,
            },
            sort_keys=True,
            ensure_ascii=False,
            default=str,
        )

        duplicate_fingerprint = fingerprint in seen_fingerprints
        duplicate_single_use = (
            tool_name in SINGLE_USE_TOOLS
            and tool_name in used_single_use_tools
        )

        if duplicate_fingerprint or duplicate_single_use:
            duplicate_calls.append(call)
            continue

        fresh_calls.append(call)
        fingerprints_by_call_id[call["id"]] = fingerprint

        # Update immediately so duplicates in this same batch are blocked.
        seen_fingerprints.add(fingerprint)

        if tool_name in SINGLE_USE_TOOLS:
            used_single_use_tools.add(tool_name)

    return fresh_calls, duplicate_calls, fingerprints_by_call_id
