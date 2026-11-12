
from unittest.mock import patch

from rag.generator import RAGAnswerGenerator


def test_rag_source_id_is_preserved():
    retrieved_chunks = [
        {
            "source_id": "qdrant-point-123",
            "content": "Employees receive 20 annual leave days.",
            "source": "company_sop.txt",
            "page": None,
            "chunk": 1,
            "score": 0.82,
        }
    ]

    with (
        patch(
            "rag.generator.OperationsRetriever.retrieve",
            return_value=retrieved_chunks,
        ),
        patch(
            "rag.generator.ChatGroq.invoke",
        ) as mock_invoke,
    ):
        from langchain_core.messages import AIMessage

        mock_invoke.return_value = AIMessage(
            content="Employees receive 20 annual leave days."
        )

        generator = RAGAnswerGenerator()
        result = generator.answer("How many annual leave days?")

    assert result["grounded"] is True
    assert len(result["sources"]) == 1

    source = result["sources"][0]

    assert source["source_id"] == "qdrant-point-123"
    assert source["source"] == "company_sop.txt"
    assert source["chunk"] == 1
    assert source["score"] == 0.82
    assert "company_sop.txt" in source["citation"]

    print("RAG source ID propagation: PASSED")
    print("Source metadata preservation: PASSED")


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-v", "-s"]))
