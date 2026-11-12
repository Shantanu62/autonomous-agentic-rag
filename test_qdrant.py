
from dotenv import load_dotenv
from pathlib import Path
import os

from qdrant_client import QdrantClient

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

if not qdrant_url or not qdrant_api_key:
    raise ValueError(
        "QDRANT_URL or QDRANT_API_KEY is missing from .env"
    )

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key,
    timeout=30,
)

# Verify connection by retrieving existing collection names.
collections = client.get_collections()

print("Qdrant connection successful!")
print("Connection status: Connected")
print("Existing collection count:", len(collections.collections))

for collection in collections.collections:
    print("Collection:", collection.name)

