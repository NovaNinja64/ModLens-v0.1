import sqlite3

from modlens.storage.database import initialize_database


def test_database_initialization_creates_migration_ledger(tmp_path):
    db_file = tmp_path / "nested" / "modlens.sqlite3"
    initialize_database(db_file)
    with sqlite3.connect(db_file) as connection:
        row = connection.execute("SELECT version FROM schema_migrations").fetchone()
    assert row == (1,)
