
from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from modlens.core.exceptions import DatabaseError, MigrationError

BASELINE_SCHEMA_VERSION = 1

MigrationFunction = Callable[[sqlite3.Connection], None]


@dataclass(frozen=True)
class Migration:
    """A single database schema migration."""

    version: int
    apply: MigrationFunction


class DatabaseManager:
    """Owns database connections, transactions, and schema migrations.

    A new SQLite connection is created for each operation. Connections are
    never shared between threads.
    """

    def __init__(
        self,
        database_file: Path,
        migrations: tuple[Migration, ...] = (),
        timeout: float = 5.0,
    ) -> None:
        if timeout <= 0:
            raise ValueError("Database timeout must be greater than zero.")

        self.database_file = Path(database_file)
        self.timeout = timeout
        self.migrations = self._validate_migrations(migrations)

    @staticmethod
    def _validate_migrations(
        migrations: tuple[Migration, ...],
    ) -> tuple[Migration, ...]:
        ordered = tuple(sorted(migrations, key=lambda item: item.version))
        versions = [migration.version for migration in ordered]

        if any(version <= BASELINE_SCHEMA_VERSION for version in versions):
            raise ValueError("Migration versions must be greater than 1.")

        if len(versions) != len(set(versions)):
            raise ValueError("Migration versions must be unique.")

        if versions and versions != list(
            range(BASELINE_SCHEMA_VERSION + 1, versions[-1] + 1)
        ):
            raise ValueError("Migration versions must be consecutive starting at 2.")
        
        return ordered

    def _connect(self) -> sqlite3.Connection:
        connection = None

        try:
            connection = sqlite3.connect(
                self.database_file,
                timeout=self.timeout,
            )
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                f"PRAGMA busy_timeout = {int(self.timeout * 1000)}"
            )
            return connection
        except sqlite3.Error as exc:
            if connection is not None:
                try:
                    connection.close()
                except sqlite3.Error:
                    pass

            raise DatabaseError(
                f"Could not connect to database: {self.database_file}"
            ) from exc

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        """Provide a configured connection and always close it afterward."""
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Run an operation in a transaction, committing or rolling back.

        SQLite errors are translated to DatabaseError. Other exceptions
        retain their original type after the transaction is rolled back.
        """
        with self.connection() as connection:
            try:
                connection.execute("BEGIN")
                yield connection
                connection.commit()
            except sqlite3.Error as exc:
                try:
                    connection.rollback()
                except sqlite3.Error:
                    pass

                raise DatabaseError(
                    "Database transaction failed."
                ) from exc
            except Exception:
                try:
                    connection.rollback()
                except sqlite3.Error:
                    pass

                raise

    def initialize(self) -> None:
        """Create the database and apply all pending migrations.

        Must complete before concurrent database access begins.
        Initialization itself is not thread-safe."""
        try:
            self.database_file.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise DatabaseError(
                f"Could not create database directory: "
                f"{self.database_file.parent}"
            ) from exc

        self._create_migration_ledger()
        self._apply_migrations()

    def _create_migration_ledger(self) -> None:
        try:
            with self.transaction() as connection:
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS schema_migrations ("
                    "version INTEGER PRIMARY KEY, "
                    "applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
                )
                row = connection.execute(
                    "SELECT version FROM schema_migrations "
                    "ORDER BY version DESC LIMIT 1"
                ).fetchone()

                if row is None:
                    connection.execute(
                        "INSERT INTO schema_migrations(version) VALUES (?)",
                        (BASELINE_SCHEMA_VERSION,),
                    )
        except DatabaseError as exc:
            raise DatabaseError(
                "Could not create or read the migration ledger."
            ) from exc

    def _apply_migrations(self) -> None:
        try:
            with self.connection() as connection:
                rows = connection.execute(
                    "SELECT version FROM schema_migrations ORDER BY version"
                ).fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError(
                "Could not read the database migration ledger."
            ) from exc

        applied_versions = [row[0] for row in rows]

        if not applied_versions or applied_versions[0] != BASELINE_SCHEMA_VERSION:
            raise MigrationError("Database migration history is invalid.")

        if applied_versions != list(
            range(BASELINE_SCHEMA_VERSION, applied_versions[-1] + 1)
        ):
            raise MigrationError("Database migration history contains a gap.")

        current_version = applied_versions[-1]
        latest_known_version = max(
            (migration.version for migration in self.migrations),
            default=BASELINE_SCHEMA_VERSION,
        )

        if current_version > latest_known_version:
            raise MigrationError(
                f"Database schema version {current_version} is newer than "
                f"the latest supported version {latest_known_version}."
            )

        pending = [
            migration
            for migration in self.migrations
            if migration.version > current_version
        ]

        for migration in pending:
            expected_version = current_version + 1
            if migration.version != expected_version:
                raise MigrationError(
                    f"Missing migration version {expected_version}."
                )

            try:
                with self.transaction() as connection:
                    migration.apply(connection)
                    connection.execute(
                        "INSERT INTO schema_migrations(version) VALUES (?)",
                        (migration.version,),
                    )
            except Exception as exc:
                raise MigrationError(
                    f"Migration {migration.version} failed."
                ) from exc

            current_version = migration.version


def initialize_database(database_file: Path) -> None:
    """Compatibility wrapper for the original application startup call."""
    DatabaseManager(database_file).initialize()
