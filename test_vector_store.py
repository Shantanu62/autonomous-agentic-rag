
from rag.ingest import (
    extract_document_text,
    split_document_into_chunks,
)
from rag.vector_store import OperationsVectorStore

DOCUMENT_PATH = "data/sample_docs/company_sop.txt"

# Extract and split the sample document
pages = extract_document_text(DOCUMENT_PATH)
chunks = split_document_into_chunks(pages)

print("Extracted chunks:", len(chunks))

# Initialize the vector store
store = OperationsVectorStore()

# Store document embeddings in Qdrant
stored_count = store.add_documents(chunks)

print("Documents stored in Qdrant:", stored_count)

# Search the document collection
query = "How many annual paid leave days does an employee receive?"

results = store.search(query, limit=3)

print("\nSemantic search results:")

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("Similarity score:", round(result["score"], 4))
    print("Source:", result["metadata"].get("source"))
    print("Content:", result["text"])
