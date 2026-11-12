
from uuid import uuid4
from typing import Any

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from config import settings


class OperationsVectorStore:
    """Store and retrieve operations document embeddings using Qdrant."""

    def __init__(self) -> None:
        if not settings.qdrant_url or not settings.qdrant_api_key:
            raise ValueError("Qdrant credentials are missing.")

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )

        self.collection_name = settings.document_collection
        self.embedding_model = SentenceTransformer(
            settings.embedding_model
        )

        self.vector_size = 384

    def ensure_collection(self) -> None:
        """Create the document collection if it does not exist."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

    def add_documents(
        self,
        chunks: list[dict[str, Any]],
    ) -> int:
        """Generate embeddings and store document chunks."""
        if not chunks:
            return 0

        self.ensure_collection()

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True,
        )

        points = []

        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk["text"],
                        **chunk["metadata"],
                    },
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )

        return len(points)

    def search(
        self,
        query: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant document chunks with their Qdrant point IDs."""
        if not query or not query.strip():
            return []

        self.ensure_collection()

        query_vector = self.embedding_model.encode(
            query.strip(),
            normalize_embeddings=True,
        ).tolist()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit or settings.retrieval_limit,
            with_payload=True,
        ).points

        return [
            {
                "point_id": str(result.id),
                "text": result.payload.get("text", ""),
                "metadata": {
                    key: value
                    for key, value in result.payload.items()
                    if key != "text"
                },
                "score": result.score,
            }
            for result in results
        ]
