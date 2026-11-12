
from agent.graph import run_agent


def main():
    thread_id = "agent-memory-test-001"

    print("Testing short-term conversation memory...")

    # First conversation turn
    first_question = (
        "Please look up ticket TCK-1001 and tell me "
        "its current status."
    )

    print("\nTURN 1:")
    print(f"Question: {first_question}")

    first_result = run_agent(
        question=first_question,
        thread_id=thread_id,
    )

    print(f"Success: {first_result['success']}")
    print(f"Answer: {first_result['answer']}")

    if not first_result["success"]:
        print("\nFirst conversation turn failed!")
        return

    # Second conversation turn using the same thread
    second_question = (
        "Which ticket did I ask you about earlier? "
        "Tell me its ticket ID."
    )

    print("\nTURN 2:")
    print(f"Question: {second_question}")

    second_result = run_agent(
        question=second_question,
        thread_id=thread_id,
    )

    print(f"Success: {second_result['success']}")
    print(f"Answer: {second_result['answer']}")

    if second_result["success"]:
        assert "TCK-1001" in second_result["answer"]
        print("\nSHORT-TERM CONVERSATION MEMORY PASSED!")
    else:
        print("\nSecond conversation turn failed!")


if __name__ == "__main__":
    main()
