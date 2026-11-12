
from rag.retriever import OperationsRetriever

retriever = OperationsRetriever()

question = "How many annual paid leave days does an employee receive?"

results = retriever.retrieve(
    question=question,
    limit=5,
    min_score=0.25,
)

print("Question:", question)
print("\nRetrieved sources:", len(results))

for index, result in enumerate(results, start=1):
    print(f"\n--- Source {index} ---")
    print("Filename:", result["source"])
    print("Page:", result["page"])
    print("Chunk:", result["chunk"])
    print("Similarity:", round(result["score"], 4))
    print("Content:", result["content"])

if results:
    print("\nRetriever test PASSED!")
else:
    print("\nNo relevant documents found.")
