
from dotenv import load_dotenv
from pathlib import Path
import os

from qdrant_client import QdrantClient, models

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

client = QdrantClient(
    url=os.environ["QDRANT_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
    timeout=30,
)

COLLECTIONS = [
    "operations_documents",
    "user_long_term_memory",
]

for collection_name in COLLECTIONS:
    if client.collection_exists(collection_name):
        print(f"Already exists: {collection_name}")
        continue

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=384,
            distance=models.Distance.COSINE,
        ),
    )

    print(f"Created successfully: {collection_name}")

print("\nProject Qdrant collections:")
for collection in client.get_collections().collections:
    print("-", collection.name)
