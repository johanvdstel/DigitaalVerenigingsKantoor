from __future__ import annotations

import sqlite3
from collections.abc import Callable

Migration = Callable[[sqlite3.Connection], None]


def _migration_001(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE dvk_records (
            record_id TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """
    )


def _migration_002(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE import_batches (
            import_batch_id TEXT PRIMARY KEY,
            source_system TEXT NOT NULL,
            dataset_type TEXT NOT NULL,
            source_period TEXT,
            uploaded_at TEXT NOT NULL,
            uploaded_by TEXT NOT NULL,
            status TEXT NOT NULL,
            validation_summary TEXT,
            confirmed_at TEXT,
            confirmed_by TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE source_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            import_batch_id TEXT NOT NULL UNIQUE REFERENCES import_batches(import_batch_id),
            source_system TEXT NOT NULL,
            dataset_type TEXT NOT NULL,
            source_period TEXT,
            created_at TEXT NOT NULL,
            supersedes_snapshot_id TEXT REFERENCES source_snapshots(snapshot_id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE snapshot_records (
            snapshot_id TEXT NOT NULL REFERENCES source_snapshots(snapshot_id),
            record_key TEXT NOT NULL,
            source_payload TEXT NOT NULL,
            canonical_payload TEXT NOT NULL,
            provenance_payload TEXT NOT NULL,
            PRIMARY KEY (snapshot_id, record_key)
        )
        """
    )
    connection.execute(
        """
        CREATE INDEX idx_snapshot_dataset
        ON source_snapshots(source_system, dataset_type, source_period, created_at)
        """
    )


MIGRATIONS: tuple[Migration, ...] = (_migration_001, _migration_002)


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
        connection.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    return len(MIGRATIONS)
