
import sqlite3

import pytest

from modlens.core.exceptions import DatabaseError, MigrationError
from modlens.storage import database
from modlens.storage.database import DatabaseManager, Migration, initialize_database


def test_database_initialization_creates_migration_ledger(tmp_path):
    db_file = tmp_path / "nested" / "modlens.sqlite3"

    initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        row = connection.execute(
            "SELECT version FROM schema_migrations"
        ).fetchone()

    assert row == (1,)


def test_database_enables_foreign_keys_on_every_connection(tmp_path):
    manager = DatabaseManager(tmp_path / "modlens.sqlite3")
    manager.initialize()

    with manager.connection() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)

    with manager.connection() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone() == (1,)


def test_transaction_commits_successful_operations(tmp_path):
    manager = DatabaseManager(tmp_path / "modlens.sqlite3")
    manager.initialize()

    with manager.transaction() as connection:
        connection.execute(
            "CREATE TABLE example (value TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO example(value) VALUES (?)",
            ("saved",),
        )

    with manager.connection() as connection:
        row = connection.execute(
            "SELECT value FROM example"
        ).fetchone()

    assert row == ("saved",)


def test_transaction_rolls_back_failed_operations(tmp_path):
    manager = DatabaseManager(tmp_path / "modlens.sqlite3")
    manager.initialize()

    with pytest.raises(RuntimeError, match="force rollback"), manager.transaction() as connection:
        connection.execute(
            "CREATE TABLE example (value TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO example(value) VALUES (?)",
            ("not saved",),
        )
        raise RuntimeError("force rollback")

    with manager.connection() as connection:
        row = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name = 'example'"
        ).fetchone()

    assert row is None


def test_migrations_are_applied_in_version_order(tmp_path):
    applied = []

    def migration_two(connection):
        applied.append(2)
        connection.execute(
            "CREATE TABLE first_migration (value TEXT)"
        )

    def migration_three(connection):
        applied.append(3)
        connection.execute(
            "CREATE TABLE second_migration (value TEXT)"
        )

    manager = DatabaseManager(
        tmp_path / "modlens.sqlite3",
        migrations=(
            Migration(3, migration_three),
            Migration(2, migration_two),
        ),
    )

    manager.initialize()

    assert applied == [2, 3]

    with manager.connection() as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()

    assert versions == [(1,), (2,), (3,)]


def test_failed_migration_rolls_back_schema_and_version(tmp_path):
    def failing_migration(connection):
        connection.execute(
            "CREATE TABLE incomplete (value TEXT)"
        )
        raise RuntimeError("migration failure")

    manager = DatabaseManager(
        tmp_path / "modlens.sqlite3",
        migrations=(Migration(2, failing_migration),),
    )

    with pytest.raises(MigrationError, match="Migration 2 failed"):
        manager.initialize()

    with manager.connection() as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()
        table = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name = 'incomplete'"
        ).fetchone()

    assert versions == [(1,)]
    assert table is None


def test_newer_database_schema_is_rejected(tmp_path):
    db_file = tmp_path / "modlens.sqlite3"
    initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        connection.execute(
            "INSERT INTO schema_migrations(version) VALUES (2)"
        )

    manager = DatabaseManager(db_file)

    with pytest.raises(MigrationError, match="newer than"):
        manager.initialize()


def test_migration_history_with_a_gap_is_rejected(tmp_path):
    db_file = tmp_path / "modlens.sqlite3"
    initialize_database(db_file)

    with sqlite3.connect(db_file) as connection:
        connection.execute(
            "INSERT INTO schema_migrations(version) VALUES (3)"
        )

    manager = DatabaseManager(
        db_file,
        migrations=(Migration(2, lambda connection: None),),
    )

    with pytest.raises(MigrationError, match="contains a gap"):
        manager.initialize()


def test_duplicate_migration_versions_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="must be unique"):
        DatabaseManager(
            tmp_path / "modlens.sqlite3",
            migrations=(
                Migration(2, lambda connection: None),
                Migration(2, lambda connection: None),
            ),
        )


def test_migration_versions_must_start_after_baseline(tmp_path):
    with pytest.raises(ValueError, match="greater than 1"):
        DatabaseManager(
            tmp_path / "modlens.sqlite3",
            migrations=(Migration(1, lambda connection: None),),
        )


def test_invalid_timeout_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="greater than zero"):
        DatabaseManager(tmp_path / "modlens.sqlite3", timeout=0)


def test_connection_failure_uses_database_error(tmp_path):
    manager = DatabaseManager(tmp_path / "missing" / "modlens.sqlite3")
    manager.database_file.parent.mkdir(parents=True)

    # Replace the database path with a directory, which SQLite cannot open.
    manager.database_file.mkdir()

    with pytest.raises(DatabaseError, match="Could not connect"), manager.connection():
        pass


def test_connection_is_closed_if_configuration_fails(tmp_path, monkeypatch):
    class FakeConnection:
        closed = False

        def execute(self, statement):
            raise sqlite3.OperationalError("configuration failure")

        def close(self):
            self.closed = True

    fake_connection = FakeConnection()

    monkeypatch.setattr(
        database.sqlite3,
        "connect",
        lambda *args, **kwargs: fake_connection,
    )

    manager = DatabaseManager(tmp_path / "modlens.sqlite3")

    with pytest.raises(DatabaseError, match="Could not connect"), manager.connection():
        pass

    assert fake_connection.closed is True
    

def test_missing_registered_migration_version_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="consecutive starting at 2"):
        DatabaseManager(
            tmp_path / "modlens.sqlite3",
            migrations=(
                Migration(2, lambda connection: None),
                Migration(4, lambda connection: None),
            ),
        )

        
def test_database_initialization_is_idempotent(tmp_path):
    db_file = tmp_path / "modlens.sqlite3"
    manager = DatabaseManager(db_file)

    manager.initialize()
    manager.initialize()

    with manager.connection() as connection:
        versions = connection.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()

    assert versions == [(1,)]


def test_sqlite_errors_in_transaction_are_wrapped(tmp_path):
    manager = DatabaseManager(tmp_path / "modlens.sqlite3")
    manager.initialize()

    with pytest.raises(DatabaseError, match="transaction failed"), manager.transaction() as connection:
            connection.execute(
                "INSERT INTO nonexistent_table(value) VALUES (?)",
                ("test",),
            )
            
