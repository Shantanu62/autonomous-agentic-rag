
from sentence_transformers import SentenceTransformer

from rag.ingest import (
    extract_document_text,
    split_document_into_chunks,
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

document_path = "data/sample_docs/company_sop.txt"

# Extract and chunk the sample document
pages = extract_document_text(document_path)
chunks = split_document_into_chunks(pages)

# Load the local embedding model
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)

# Generate embeddings
texts = [chunk["text"] for chunk in chunks]
embeddings = model.encode(texts, normalize_embeddings=True)

print("\nEmbedding generation successful!")
print("Number of embeddings:", len(embeddings))
print("Vector dimensions:", embeddings.shape[1])
print("Embedding data type:", embeddings.dtype)
