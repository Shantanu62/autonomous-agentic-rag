
from agent.graph import run_agent
from memory.store import LongTermMemoryStore


def main():
    user_id = "memory-management-test-user"
    thread_id = "memory-management-test-thread"

    memory_text = (
        "Temporary test preference: show operational summaries "
        "with clear headings."
    )

    store = LongTermMemoryStore()

    memory_id = None

    try:
        print("SETUP: Creating temporary test memory")

        saved = store.save_memory(
            user_id=user_id,
            memory=memory_text,
            category="test",
        )

        assert saved.get("success"), "Could not create test memory."

        memory_id = saved["memory_id"]

        print("Temporary memory created:", memory_id)

        print("\nTEST 1: Agent memory inspection")

        inspect_result = run_agent(
            question=(
                "Please inspect my saved long-term memories using "
                "the inspect_long_term_memory tool and tell me "
                "what you find."
            ),
            thread_id=thread_id,
            user_id=user_id,
        )

        print("Success:", inspect_result.get("success"))
        print("Answer:", inspect_result.get("answer"))
        print("Selected tools:", inspect_result.get("selected_tools"))

        assert inspect_result.get("success"), (
            f"Inspection failed: {inspect_result.get('error')}"
        )

        assert "inspect_long_term_memory" in inspect_result.get(
            "selected_tools", []
        ), "Agent did not select the inspection tool."

        assert memory_text.lower() in inspect_result.get(
            "answer", ""
        ).lower(), "Agent did not report the saved test memory."

        print("TEST 1 PASSED!")

        print("\nTEST 2: Agent memory deletion")

        delete_result = run_agent(
            question=(
                "Please delete this exact long-term memory using "
                "the delete_long_term_memory tool. "
                f"Memory ID: {memory_id}. "
                "Do not delete any other memory."
            ),
            thread_id=thread_id,
            user_id=user_id,
        )

        print("Success:", delete_result.get("success"))
        print("Answer:", delete_result.get("answer"))
        print("Selected tools:", delete_result.get("selected_tools"))

        assert delete_result.get("success"), (
            f"Deletion request failed: {delete_result.get('error')}"
        )

        assert "delete_long_term_memory" in delete_result.get(
            "selected_tools", []
        ), "Agent did not select the deletion tool."

        remaining = store.list_memories(
            user_id=user_id,
            limit=100,
        )

        assert not any(
            item["memory_id"] == memory_id
            for item in remaining
        ), "Memory still exists after agent deletion."

        print("TEST 2 PASSED!")

        print("\nMEMORY INSPECTION AND DELETION TESTS PASSED!")

    finally:
        # Ensure the temporary test record is removed even if a test fails.
        if memory_id:
            store.delete_memory(
                user_id=user_id,
                memory_id=memory_id,
            )

        store.close()

        print("Test cleanup completed.")


if __name__ == "__main__":
    main()
