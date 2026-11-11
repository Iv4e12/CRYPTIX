
import sqlite3

from pathlib import Path
from datetime import datetime, timezone


DATABASE = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "history.db"
)


def get_connection():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    return connection


def add_record(operation, description):
    timestamp = datetime.now(timezone.utc).isoformat(
        timespec="seconds"
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO history (
                operation, description, timestamp
            )
            VALUES (?, ?, ?)
            """,
            (operation, description, timestamp)
        )


def get_records(limit=100):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, operation, description, timestamp
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return rows


def clear_history():
    with get_connection() as connection:
        connection.execute("DELETE FROM history")
