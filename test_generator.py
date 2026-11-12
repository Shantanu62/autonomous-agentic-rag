
from rag.generator import RAGAnswerGenerator


def main():
    generator = RAGAnswerGenerator()

    question = "How many annual paid leave days does an employee receive?"

    print("Question:", question)
    print("\nGenerating grounded answer...\n")

    result = generator.answer(question)

    print("=" * 60)
    print("RAG ANSWER")
    print("=" * 60)
    print(result["answer"])

    print("\n" + "=" * 60)
    print("SOURCE DOCUMENTS")
    print("=" * 60)

    for source in result["sources"]:
        print("Source:", source["source"])
        print("Page:", source["page"])
        print("Chunk:", source["chunk"])
        print("Similarity:", source["score"])
        print("Citation:", source["citation"])
        print("-" * 40)

    print("Grounded:", result["grounded"])


if __name__ == "__main__":
    main()
