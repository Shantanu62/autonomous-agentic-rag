
from typing import Any

from rag.vector_store import OperationsVectorStore


class OperationsRetriever:
    """Retrieve relevant operations knowledge with source metadata."""

    def __init__(self) -> None:
        self.vector_store = OperationsVectorStore()

    def retrieve(
        self,
        question: str,
        limit: int = 5,
        min_score: float = 0.25,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant chunks and remove duplicate content."""

        if not question or not question.strip():
            return []

        results = self.vector_store.search(
            query=question.strip(),
            limit=limit,
        )

        relevant_results = []
        seen_chunks = set()

        for result in results:
            if result["score"] < min_score:
                continue

            metadata = result["metadata"]
            content = result["text"].strip()

            source = metadata.get("source", "Unknown")
            page = metadata.get("page")
            chunk = metadata.get("chunk")

            deduplication_key = (
                source,
                page,
                chunk,
                content,
            )

            if deduplication_key in seen_chunks:
                continue

            seen_chunks.add(deduplication_key)

            relevant_results.append({
                "source_id": result["point_id"],
                "content": content,
                "source": source,
                "page": page,
                "chunk": chunk,
                "score": result["score"],
            })

        return relevant_results
