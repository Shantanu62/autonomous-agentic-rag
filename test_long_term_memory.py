
from memory.store import LongTermMemoryStore


def main():
    store = LongTermMemoryStore()

    user_id = "demo-user-001"
    other_user_id = "demo-user-002"

    try:
        print("Testing Qdrant long-term memory...")

        # 1. Save memory
        saved = store.save_memory(
            user_id=user_id,
            memory=(
                "The user prefers concise enterprise operations "
                "reports with clear source references."
            ),
            category="preference",
        )

        print("\nSAVE MEMORY:")
        print(saved)
        assert saved["success"]

        # 2. Search memory
        results = store.search_memories(
            user_id=user_id,
            query="What reporting style does the user prefer?",
            limit=5,
        )

        print("\nSEARCH MEMORY:")
        for item in results:
            print(item)

        assert results
        assert any(
            "concise enterprise operations reports" in item["memory"]
            for item in results
        )

        # 3. Verify user isolation
        other_user_results = store.search_memories(
            user_id=other_user_id,
            query="What reporting style does the user prefer?",
        )

        print("\nUSER ISOLATION:")
        print(f"Other user's results: {other_user_results}")
        assert not other_user_results

        # 4. Inspect memories
        memories = store.list_memories(user_id=user_id)

        print("\nINSPECT MEMORIES:")
        for item in memories:
            print(item)

        assert any(
            item["memory_id"] == saved["memory_id"]
            for item in memories
        )

        # 5. Delete memory
        deleted = store.delete_memory(
            user_id=user_id,
            memory_id=saved["memory_id"],
        )

        print("\nDELETE MEMORY:")
        print(deleted)
        assert deleted["success"]

        # 6. Verify deletion
        remaining = store.list_memories(user_id=user_id)

        print("\nVERIFY DELETION:")
        print(f"Remaining memories: {remaining}")

        assert not any(
            item["memory_id"] == saved["memory_id"]
            for item in remaining
        )

        print("\nLONG-TERM MEMORY TEST PASSED!")

    finally:
        store.close()


if __name__ == "__main__":
    main()
