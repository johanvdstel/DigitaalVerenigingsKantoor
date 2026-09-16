from __future__ import annotations

import sqlite3
from collections.abc import Callable

Migration = Callable[[sqlite3.Connection], None]


def _migration_001(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS dvk_records (
            record_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """
    )


MIGRATIONS: tuple[Migration, ...] = (_migration_001,)


def migrate(connection: sqlite3.Connection) -> int:
    """Bring a database to the latest known schema and return its version."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
        """
    )
    row = connection.execute("SELECT MAX(version) FROM schema_version").fetchone()
    current = int(row[0] or 0)

    for version, migration in enumerate(MIGRATIONS, start=1):
        if version <= current:
            continue
        migration(connection)
        connection.execute(
            "INSERT INTO schema_version(version) VALUES (?)", (version,)
        )
    return len(MIGRATIONS)
