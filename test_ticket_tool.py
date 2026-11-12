
from agent.tools import lookup_ticket


def main():
    print("TEST 1: Existing ticket")
    result = lookup_ticket("TCK-1001")
    print(result)

    assert result["success"] is True
    assert result["ticket"]["ticket_id"] == "TCK-1001"
    assert result["ticket"]["priority"] == "Critical"

    print("\nTEST 2: Ticket ID with lowercase")
    result = lookup_ticket("tck-1002")
    print(result)

    assert result["success"] is True
    assert result["ticket"]["ticket_id"] == "TCK-1002"

    print("\nTEST 3: Non-existing ticket")
    result = lookup_ticket("TCK-9999")
    print(result)

    assert result["success"] is False

    print("\nTEST 4: Empty ticket ID")
    result = lookup_ticket("")
    print(result)

    assert result["success"] is False

    print("\nAll ticket lookup tests passed!")


if __name__ == "__main__":
    main()
