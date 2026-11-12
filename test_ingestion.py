
from rag.ingest import (
    extract_document_text,
    split_document_into_chunks,
)

document_path = "data/sample_docs/company_sop.txt"

# Extract document text
pages = extract_document_text(document_path)

print("Document extraction successful!")
print("Extracted sections:", len(pages))

# Split extracted text into chunks
chunks = split_document_into_chunks(pages)

print("\nChunking successful!")
print("Total chunks:", len(chunks))

# Display chunk metadata and content
for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print("Source:", chunk["metadata"]["source"])
    print("Page:", chunk["metadata"]["page"])
    print("Chunk number:", chunk["metadata"]["chunk"])
    print("Content:", chunk["text"])
