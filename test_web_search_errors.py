
from unittest.mock import MagicMock, patch

import pytest

from agent.tools import (
    WEB_SEARCH_TIMEOUT_SECONDS,
    web_search,
)


@patch("agent.tools.TavilyClient")
def test_web_search_timeout(mock_client_class):
    mock_client = MagicMock()
    mock_client.search.side_effect = TimeoutError("Simulated timeout")
    mock_client_class.return_value = mock_client

    result = web_search("Test timeout handling")

    assert result["success"] is False
    assert "timed out" in result["error"].lower()

    mock_client.search.assert_called_once()

    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["timeout"] == WEB_SEARCH_TIMEOUT_SECONDS

    print("Web search timeout handling: PASSED")


@patch("agent.tools.TavilyClient")
def test_web_search_connection_failure(mock_client_class):
    mock_client = MagicMock()
    mock_client.search.side_effect = ConnectionError(
        "Simulated connection failure"
    )
    mock_client_class.return_value = mock_client

    result = web_search("Test connection failure")

    assert result["success"] is False
    assert "connection failed" in result["error"].lower()

    print("Web search connection failure handling: PASSED")


@patch("agent.tools.TavilyClient")
def test_web_search_api_failure(mock_client_class):
    mock_client = MagicMock()
    mock_client.search.side_effect = RuntimeError(
        "Simulated API failure"
    )
    mock_client_class.return_value = mock_client

    result = web_search("Test API failure")

    assert result["success"] is False
    assert "Live web search failed" in result["error"]

    print("Web search API failure handling: PASSED")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
