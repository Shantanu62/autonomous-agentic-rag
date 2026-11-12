
from rag.retriever import OperationsRetriever


def test_retriever_removes_duplicate_chunks(monkeypatch):
    """Verify identical document chunks are returned only once."""

    fake_results = [
        {
            "point_id": "point-1",
            "text": "Employees receive 20 annual leave days.",
            "metadata": {
                "source": "company_sop.txt",
                "page": None,
                "chunk": 1,
            },
            "score": 0.91,
        },
        {
            "point_id": "point-2",
            "text": "Employees receive 20 annual leave days.",
            "metadata": {
                "source": "company_sop.txt",
                "page": None,
                "chunk": 1,
            },
            "score": 0.89,
        },
        {
            "point_id": "point-3",
            "text": "Sick leave entitlement is 10 days.",
            "metadata": {
                "source": "company_sop.txt",
                "page": None,
                "chunk": 2,
            },
            "score": 0.85,
        },
    ]

    class FakeVectorStore:
        def search(self, query, limit):
            return fake_results

    retriever = OperationsRetriever.__new__(OperationsRetriever)
    retriever.vector_store = FakeVectorStore()

    results = retriever.retrieve(
        question="What is the leave entitlement?",
        limit=5,
        min_score=0.45,
    )

    assert len(results) == 2
    assert results[0]["source_id"] == "point-1"
    assert results[1]["source_id"] == "point-3"


def test_retriever_filters_low_similarity_results():
    """Verify weak matches are excluded."""

    class FakeVectorStore:
        def search(self, query, limit):
            return [
                {
                    "point_id": "point-1",
                    "text": "Unrelated content.",
                    "metadata": {"source": "other.txt"},
                    "score": 0.20,
                }
            ]

    retriever = OperationsRetriever.__new__(OperationsRetriever)
    retriever.vector_store = FakeVectorStore()

    results = retriever.retrieve(
        question="Annual leave policy?",
        limit=5,
        min_score=0.45,
    )

    assert results == []
