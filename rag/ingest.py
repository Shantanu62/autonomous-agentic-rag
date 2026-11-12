
from pathlib import Path
from typing import Any

from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_document_text(file_path: str | Path) -> list[dict[str, Any]]:
    """Extract text while preserving source filename and page metadata."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document format: {extension}")

    pages = []

    if extension == ".pdf":
        reader = PdfReader(str(path))

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            if text.strip():
                pages.append({
                    "text": text,
                    "metadata": {
                        "source": path.name,
                        "page": page_number,
                        "file_type": "pdf",
                    },
                })

    elif extension == ".docx":
        document = Document(str(path))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        )

        if text.strip():
            pages.append({
                "text": text,
                "metadata": {
                    "source": path.name,
                    "page": None,
                    "file_type": "docx",
                },
            })

    elif extension == ".txt":
        text = path.read_text(encoding="utf-8")

        if text.strip():
            pages.append({
                "text": text,
                "metadata": {
                    "source": path.name,
                    "page": None,
                    "file_type": "txt",
                },
            })

    return pages


def split_document_into_chunks(
    pages: list[dict[str, Any]],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> list[dict[str, Any]]:
    """Split extracted document text into overlapping chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be between zero and chunk_size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []

    for page in pages:
        page_chunks = splitter.split_text(page["text"])

        for chunk_number, chunk_text in enumerate(page_chunks, start=1):
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **page["metadata"],
                    "chunk": chunk_number,
                },
            })

    return chunks
