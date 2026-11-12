
from typing import Any

from langchain_groq import ChatGroq

from config import settings
from rag.retriever import OperationsRetriever


INSUFFICIENT_EVIDENCE = (
    "I don't have enough information in the available operations "
    "documents to answer that question reliably."
)

MIN_RETRIEVAL_SCORE = 0.60


class RAGAnswerGenerator:
    """Generate answers grounded in retrieved operations documents."""

    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is missing from configuration.")

        if not settings.groq_model:
            raise ValueError("GROQ_MODEL is missing from configuration.")

        self.retriever = OperationsRetriever()

        self.llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,
            max_tokens=700,
            timeout=30,
            max_retries=2,
        )

    def answer(self, question: str) -> dict[str, Any]:
        """Answer a question using retrieved document evidence."""

        if not question or not question.strip():
            return {
                "answer": "Please enter a question.",
                "sources": [],
                "grounded": False,
            }

        retrieved_chunks = self.retriever.retrieve(
            question=question.strip(),
            limit=settings.retrieval_limit,
            min_score=MIN_RETRIEVAL_SCORE,
        )

        if not retrieved_chunks:
            return {
                "answer": INSUFFICIENT_EVIDENCE,
                "sources": [],
                "grounded": False,
            }

        selected_chunks = retrieved_chunks[:settings.final_source_limit]

        context_parts = []
        sources = []

        for index, chunk in enumerate(selected_chunks, start=1):
            source_id = chunk.get("source_id")
            source_name = chunk.get("source", "Unknown source")
            page_number = chunk.get("page")
            chunk_number = chunk.get("chunk", "Unknown")

            location = (
                f"Page {page_number}"
                if page_number is not None
                else "Page not available"
            )

            citation = f"[Source {index}: {source_name}, {location}]"

            context_parts.append(
                f"{citation}\n"
                f"Chunk: {chunk_number}\n"
                f"Content:\n{chunk.get('content', '')}"
            )

            sources.append({
                "source_id": source_id,
                "source": source_name,
                "page": page_number,
                "chunk": chunk_number,
                "score": chunk.get("score"),
                "citation": citation,
            })

        context = "\n\n".join(context_parts)

        messages = [
            (
                "system",
                """
You are an enterprise operations assistant.

Answer using ONLY the supplied document context.

Rules:
1. Never invent facts, numbers, policies, or dates.
2. Do not use outside knowledge.
3. If the context does not contain sufficient evidence,
   respond with exactly this sentence:

I don't have enough information in the available operations documents to answer that question reliably.

4. Do not write source citations in your answer.
   Source metadata is returned separately.
5. If sources conflict, explain the conflict.
6. Keep the answer clear and professional.
7. Do not claim that an action was performed.
                """.strip(),
            ),
            (
                "human",
                f"""
Document context:

{context}

User question:
{question}

Provide a concise answer based only on the context.
                """.strip(),
            ),
        ]

        response = self.llm.invoke(messages)
        answer_text = str(response.content).strip()

        if not answer_text:
            answer_text = INSUFFICIENT_EVIDENCE

        if INSUFFICIENT_EVIDENCE.lower() in answer_text.lower():
            return {
                "answer": INSUFFICIENT_EVIDENCE,
                "sources": [],
                "grounded": False,
            }

        return {
            "answer": answer_text,
            "sources": sources,
            "grounded": True,
        }
