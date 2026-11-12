
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

from config import settings


class LongTermMemoryStore:
    """User-scoped long-term memory backed by Qdrant."""

    def __init__(self):
        if not settings.qdrant_url or not settings.qdrant_api_key:
            raise ValueError("Qdrant credentials are missing.")

        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30,
        )

        self.collection_name = settings.memory_collection
        self.embedding_model = SentenceTransformer(
            settings.embedding_model
        )
        self.vector_size = 384

        self.ensure_collection()

    def ensure_collection(self) -> None:
        """Create the memory collection only if it does not exist."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )

        self.client.create_payload_index(
            collection_name=self.collection_name,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )

    def save_memory(
        self,
        user_id: str,
        memory: str,
        category: str = "context",
    ) -> dict[str, Any]:
        """Save a non-sensitive memory for a specific user."""
        user_id = user_id.strip() if user_id else ""
        memory = memory.strip() if memory else ""
        category = category.strip() if category else "context"

        if not user_id or len(user_id) > 128:
            return {"success": False, "error": "Invalid user ID."}

        if not memory or len(memory) > 2000:
            return {"success": False, "error": "Invalid memory content."}

        if len(category) > 64:
            return {"success": False, "error": "Invalid memory category."}

        vector = self.embedding_model.encode(
            memory,
            normalize_embeddings=True,
        ).tolist()

        point_id = str(uuid4())

        payload = {
            "user_id": user_id,
            "memory": memory,
            "category": category,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload,
                )
            ],
            wait=True,
        )

        return {
            "success": True,
            "memory_id": point_id,
            "message": "Memory saved successfully.",
        }

    def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve only memories belonging to the requested user."""
        user_id = user_id.strip() if user_id else ""
        query = query.strip() if query else ""

        if not user_id or not query or len(user_id) > 128:
            return []

        if not isinstance(limit, int) or not 1 <= limit <= 20:
            return []

        vector = self.embedding_model.encode(
            query,
            normalize_embeddings=True,
        ).tolist()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
        ).points

        return [
            {
                "memory_id": str(point.id),
                "memory": point.payload.get("memory", ""),
                "category": point.payload.get("category", "context"),
                "created_at": point.payload.get("created_at"),
                "score": point.score,
            }
            for point in results
        ]

    def list_memories(
        self,
        user_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Inspect saved memories for one user."""
        user_id = user_id.strip() if user_id else ""

        if not user_id or len(user_id) > 128:
            return []

        if not isinstance(limit, int) or not 1 <= limit <= 500:
            return []

        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id),
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return [
            {
                "memory_id": str(point.id),
                "memory": point.payload.get("memory", ""),
                "category": point.payload.get("category", "context"),
                "created_at": point.payload.get("created_at"),
            }
            for point in results
        ]

    def delete_memory(
        self,
        user_id: str,
        memory_id: str,
    ) -> dict[str, Any]:
        """Delete a memory only when it belongs to the requesting user."""
        user_id = user_id.strip() if user_id else ""
        memory_id = memory_id.strip() if memory_id else ""

        if not user_id or not memory_id or len(user_id) > 128:
            return {"success": False, "error": "Invalid input."}

        points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[memory_id],
            with_payload=True,
            with_vectors=False,
        )

        if not points or points[0].payload.get("user_id") != user_id:
            return {
                "success": False,
                "error": "Memory not found for this user.",
            }

        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=[memory_id]
            ),
            wait=True,
        )

        return {
            "success": True,
            "message": "Memory deleted successfully.",
        }

    def close(self) -> None:
        """Close the Qdrant client."""
        self.client.close()
