
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "demo_ops.db"


def initialize_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                  description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                requester TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sla_metrics (
                metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporting_period TEXT NOT NULL,
                assigned_team TEXT NOT NULL,
                total_tickets INTEGER NOT NULL,
                resolved_tickets INTEGER NOT NULL,
                breached_tickets INTEGER NOT NULL,
                target_resolution_hours REAL NOT NULL,
                average_resolution_hours REAL NOT NULL,
                UNIQUE(reporting_period, assigned_team)
            )
        """)

        tickets = [
            (
                "TCK-1001",
                "Production login failure",
                "Employees cannot log in to the operations portal.",
                "Open",
                "Critical",
                "Alex Morgan",
                "Platform Support",
                "2026-11-10 09:15:00",
                "2026-11-12 08:30:00",
            ),
            (
                "TCK-1002",
                "Invoice export issue",
                "Monthly invoice export produces an incomplete CSV file.",
                "In Progress",
                "High",
                "Jordan Lee",
                "Application Support",
                "2026-11-10 11:00:00",
                "2026-11-11 16:45:00",
            ),
            (
                "TCK-1003",
                "Employee access request",
                "New employee requires access to the reporting dashboard.",
                "Resolved",
                "Medium",
                "Taylor Smith",
                "Platform Support",
                "2026-11-08 10:00:00",
                "2026-11-08 13:30:00",
            ),
            (
                "TCK-1004",
                "Delayed customer notification",
                "Automated email notifications are delayed.",
                "Open",
                "High",
                "Casey Brown",
                "Infrastructure",
                "2026-11-09 14:20:00",
                "2026-11-12 07:10:00",
            ),
            (
                "TCK-1005",
                "Dashboard loading slowly",
                "Operations dashboard takes more than 20 seconds to load.",
                "Resolved",
                "Low",
                "Riley Wilson",
                "Application Support",
                "2026-11-07 08:00:00",
                "2026-11-07 12:00:00",
            ),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO tickets (
                ticket_id, title, description, status, priority,
                requester, assigned_team, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tickets)

        sla_records = [
            ("2026-11", "Platform Support", 120, 114, 8, 24.0, 18.5),
            ("2026-11", "Application Support", 95, 90, 12, 24.0, 21.3),
            ("2026-11", "Infrastructure", 80, 76, 5, 12.0, 9.8),
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO sla_metrics (
                reporting_period, assigned_team, total_tickets,
                resolved_tickets, breached_tickets,
                target_resolution_hours, average_resolution_hours
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sla_records)

        connection.commit()

        ticket_count = cursor.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

        sla_count = cursor.execute(
            "SELECT COUNT(*) FROM sla_metrics"
        ).fetchone()[0]

    print("Operations database initialized successfully!")
    print("Database:", DATABASE_PATH)
    print("Synthetic tickets:", ticket_count)
    print("SLA metric records:", sla_count)


if __name__ == "__main__":
    initialize_database()
