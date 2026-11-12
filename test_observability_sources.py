
import json

from observability.logger import extract_sources, extract_tool_error


def test_extract_rag_sources_from_json():
    tool_result = {
        "answer": "Employees receive 20 annual leave days.",
        "grounded": True,
        "sources": [
            {
                "source_id": "qdrant-point-123",
                "source": "company_sop.txt",
                "page": None,
                "chunk": 1,
                "score": 0.82,
                "citation": "[Source 1: company_sop.txt, Page not available]",
            }
        ],
    }

    extracted = extract_sources(json.dumps(tool_result))

    assert len(extracted) == 1
    assert extracted[0]["source_id"] == "qdrant-point-123"
    assert extracted[0]["source"] == "company_sop.txt"
    assert extracted[0]["chunk"] == 1
    assert extracted[0]["score"] == 0.82

    print("RAG source ID extraction: PASSED")


def test_extract_multiple_sources():
    tool_result = {
        "sources": [
            {
                "source_id": "point-001",
                "source": "policy.pdf",
                "page": 2,
                "chunk": 1,
                "score": 0.91,
                "citation": "[Source 1: policy.pdf, Page 2]",
            },
            {
                "source_id": "point-002",
                "source": "operations.docx",
                "page": None,
                "chunk": 3,
                "score": 0.78,
                "citation": "[Source 2: operations.docx, Page not available]",
            },
        ]
    }

    extracted = extract_sources(tool_result)

    assert len(extracted) == 2
    assert extracted[0]["source_id"] == "point-001"
    assert extracted[0]["page"] == 2
    assert extracted[1]["source_id"] == "point-002"
    assert extracted[1]["source"] == "operations.docx"

    print("Multiple source extraction: PASSED")


def test_extract_sources_from_invalid_response():
    assert extract_sources("invalid JSON") == []
    assert extract_sources({"sources": "invalid"}) == []
    assert extract_sources(None) == []

    print("Invalid source response handling: PASSED")


def test_extract_tool_error():
    result = {
        "success": False,
        "error": "Simulated tool failure.",
    }

    error = extract_tool_error(json.dumps(result))

    assert error == "Simulated tool failure."

    print("Tool error extraction: PASSED")


def test_successful_tool_has_no_error():
    result = {
        "success": True,
        "ticket": {"ticket_id": "TCK-1001"},
    }

    assert extract_tool_error(result) is None

    print("Successful tool error handling: PASSED")


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
