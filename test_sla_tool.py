
from agent.tools import get_sla_metrics


def main():
    print("TEST 1: All teams for November 2026")

    result = get_sla_metrics("2026-11")
    print(result)

    assert result["success"] is True
    assert result["total_records"] == 3
    assert len(result["metrics"]) == 3

    print("\nTEST 2: Platform Support only")

    result = get_sla_metrics(
        reporting_period="2026-11",
        assigned_team="Platform Support",
    )
    print(result)

    assert result["success"] is True
    assert result["total_records"] == 1
    assert result["metrics"][0]["assigned_team"] == "Platform Support"

    print("\nTEST 3: Invalid reporting period")

    result = get_sla_metrics("November 2026")
    print(result)

    assert result["success"] is False

    print("\nTEST 4: Non-existing reporting period")

    result = get_sla_metrics("2025-01")
    print(result)

    assert result["success"] is True
    assert result["total_records"] == 0

    print("\nAll SLA metrics tests passed!")


if __name__ == "__main__":
    main()
