from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_VERSION = 1


def initialize_database(database_file: Path) -> None:
    """Create the SQLite file and baseline migration ledger."""
    database_file.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_file)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "version INTEGER PRIMARY KEY, "
            "applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)",
            (SCHEMA_VERSION,),
        )
        connection.commit()
    finally:
        connection.close()
