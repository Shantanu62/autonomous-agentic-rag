
from agent.tools import calculate


def main():
    print("TEST 1: Addition")
    result = calculate("100 + 50")
    print(result)
    assert result["success"] is True
    assert result["result"] == 150

    print("\nTEST 2: Multiple operations")
    result = calculate("(100 + 50) * 2 - 25")
    print(result)
    assert result["success"] is True
    assert result["result"] == 275

    print("\nTEST 3: Division")
    result = calculate("100 / 4")
    print(result)
    assert result["success"] is True
    assert result["result"] == 25

    print("\nTEST 4: Power")
    result = calculate("2 ** 5")
    print(result)
    assert result["success"] is True
    assert result["result"] == 32

    print("\nTEST 5: Division by zero")
    result = calculate("100 / 0")
    print(result)
    assert result["success"] is False

    print("\nTEST 6: Invalid Python expression")
    result = calculate("__import__('os').system('whoami')")
    print(result)
    assert result["success"] is False

    print("\nTEST 7: Empty expression")
    result = calculate("")
    print(result)
    assert result["success"] is False

    print("\nTEST 8: Unsupported operator")
    result = calculate("10 > 5")
    print(result)
    assert result["success"] is False

    print("\nAll calculator tests passed!")


if __name__ == "__main__":
    main()
