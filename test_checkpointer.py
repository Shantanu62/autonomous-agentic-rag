
import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


def main():
    database_path = Path("data/checkpointer_test.sqlite3")
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(database_path),
        check_same_thread=False,
    )

    try:
        checkpointer = SqliteSaver(connection)
        checkpointer.setup()

        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        print("SQLite checkpoint initialized successfully!")
        print("Database:", database_path)
        print("Tables:", [table[0] for table in tables])

    finally:
        connection.close()


if __name__ == "__main__":
    main()
