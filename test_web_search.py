
from agent.tools import web_search


def main():
    print("TEST 1: Live web search")

    result = web_search(
        query="Latest developments in enterprise AI agents in 2026",
        max_results=3,
    )

    print("Success:", result["success"])

    if not result["success"]:
        print("Error:", result["error"])
        raise SystemExit(1)

    print("Query:", result["query"])
    print("Total results:", result["total_results"])

    for index, item in enumerate(result["results"], start=1):
        print(f"\nResult {index}")
        print("Title:", item["title"])
        print("URL:", item["url"])
        print("Content:", item["content"][:300])
        print("Score:", item["score"])

    assert result["total_results"] > 0
    assert all(item["url"] for item in result["results"])

    print("\nTEST 2: Empty search query")

    result = web_search("")
    print(result)

    assert result["success"] is False

    print("\nTEST 3: Invalid maximum results")

    result = web_search(
        query="Enterprise AI",
        max_results=10,
    )
    print(result)

    assert result["success"] is False

    print("\nAll web search tests passed!")


if __name__ == "__main__":
    main()
