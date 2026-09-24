from __future__ import annotations

import sqlite3
from collections.abc import Callable

Migration = Callable[[sqlite3.Connection], None]


def _migration_001(connection: sqlite3.Connection) -> None:
    connection.execute("CREATE TABLE dvk_records (record_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")


def _migration_002(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE import_batches (
        import_batch_id TEXT PRIMARY KEY, source_system TEXT NOT NULL, dataset_type TEXT NOT NULL,
        source_period TEXT, uploaded_at TEXT NOT NULL, uploaded_by TEXT NOT NULL, status TEXT NOT NULL,
        validation_summary TEXT, confirmed_at TEXT, confirmed_by TEXT)""")
    connection.execute("""CREATE TABLE source_snapshots (
        snapshot_id TEXT PRIMARY KEY, import_batch_id TEXT NOT NULL UNIQUE REFERENCES import_batches(import_batch_id),
        source_system TEXT NOT NULL, dataset_type TEXT NOT NULL, source_period TEXT, created_at TEXT NOT NULL,
        supersedes_snapshot_id TEXT REFERENCES source_snapshots(snapshot_id))""")
    connection.execute("""CREATE TABLE snapshot_records (
        snapshot_id TEXT NOT NULL REFERENCES source_snapshots(snapshot_id), record_key TEXT NOT NULL,
        source_payload TEXT NOT NULL, canonical_payload TEXT NOT NULL, provenance_payload TEXT NOT NULL,
        PRIMARY KEY (snapshot_id, record_key))""")
    connection.execute("CREATE INDEX idx_snapshot_dataset ON source_snapshots(source_system, dataset_type, source_period, created_at)")


def _migration_003(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE source_fetches (
        source_fetch_id TEXT PRIMARY KEY, source_system TEXT NOT NULL, dataset_type TEXT NOT NULL,
        requested_at TEXT NOT NULL, completed_at TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL,
        status TEXT NOT NULL, record_count INTEGER, error_category TEXT)""")
    connection.execute("""CREATE TABLE engine_runs (
        engine_run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, completed_at TEXT, initiated_by TEXT NOT NULL,
        period_start TEXT NOT NULL, period_end TEXT NOT NULL, status TEXT NOT NULL, policy_version TEXT NOT NULL,
        engine_version TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE engine_run_snapshots (
        engine_run_id TEXT NOT NULL REFERENCES engine_runs(engine_run_id), snapshot_id TEXT NOT NULL REFERENCES source_snapshots(snapshot_id), PRIMARY KEY (engine_run_id, snapshot_id))""")
    connection.execute("""CREATE TABLE engine_run_fetches (
        engine_run_id TEXT NOT NULL REFERENCES engine_runs(engine_run_id), source_fetch_id TEXT NOT NULL REFERENCES source_fetches(source_fetch_id), PRIMARY KEY (engine_run_id, source_fetch_id))""")


def _migration_004(connection: sqlite3.Connection) -> None:
    connection.execute("ALTER TABLE engine_runs ADD COLUMN config_version TEXT NOT NULL DEFAULT 'unspecified'")


def _migration_005(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE policy_versions (
        version_id TEXT PRIMARY KEY, content_json TEXT NOT NULL, content_hash TEXT NOT NULL,
        created_at TEXT NOT NULL, created_by TEXT NOT NULL, effective_from TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE config_versions (
        version_id TEXT PRIMARY KEY, content_json TEXT NOT NULL, content_hash TEXT NOT NULL,
        created_at TEXT NOT NULL, created_by TEXT NOT NULL, effective_from TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE software_versions (
        version_id TEXT PRIMARY KEY, release_label TEXT NOT NULL, git_commit_sha TEXT NOT NULL,
        created_at TEXT NOT NULL)""")


def _migration_006(connection: sqlite3.Connection) -> None:
    """Persist the V07 chain: proposal -> human decision -> inroostering."""
    connection.execute("""CREATE TABLE assignment_proposals (
        proposal_id TEXT PRIMARY KEY,
        engine_run_id TEXT REFERENCES engine_runs(engine_run_id),
        payload TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE human_decisions (
        proposal_id TEXT PRIMARY KEY REFERENCES assignment_proposals(proposal_id),
        payload TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE duty_assignments (
        assignment_id TEXT PRIMARY KEY,
        proposal_id TEXT NOT NULL REFERENCES assignment_proposals(proposal_id),
        engine_run_id TEXT REFERENCES engine_runs(engine_run_id),
        payload TEXT NOT NULL)""")
    connection.execute("CREATE INDEX idx_assignment_proposal ON duty_assignments(proposal_id)")


def _migration_007(connection: sqlite3.Connection) -> None:
    """Persist Gate 9 no-show facts and derived sanction assessments."""
    connection.execute("""CREATE TABLE no_show_events (
        no_show_id TEXT PRIMARY KEY,
        assignment_id TEXT NOT NULL REFERENCES duty_assignments(assignment_id),
        person_id TEXT NOT NULL,
        season TEXT NOT NULL,
        occurred_at TEXT NOT NULL,
        status TEXT NOT NULL,
        payload TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE sanction_assessments (
        no_show_id TEXT PRIMARY KEY REFERENCES no_show_events(no_show_id),
        person_id TEXT NOT NULL,
        season TEXT NOT NULL,
        counter INTEGER NOT NULL,
        payload TEXT NOT NULL)""")
    connection.execute("CREATE INDEX idx_no_show_person_season ON no_show_events(person_id, season, occurred_at)")


def _migration_008(connection: sqlite3.Connection) -> None:
    """Harden Gate 9: one no-show fact per concrete inroostering."""
    duplicates = connection.execute(
        "SELECT assignment_id FROM no_show_events GROUP BY assignment_id HAVING COUNT(*) > 1 LIMIT 1"
    ).fetchone()
    if duplicates is not None:
        raise ValueError("cannot enforce one no-show per inroostering: duplicate historical records exist")
    connection.execute("CREATE UNIQUE INDEX idx_no_show_assignment ON no_show_events(assignment_id)")


def _migration_009(connection: sqlite3.Connection) -> None:
    """Persist Gate 10 replacement duties with one repair path per first no-show."""
    connection.execute("""CREATE TABLE replacement_duties (
        replacement_id TEXT PRIMARY KEY,
        no_show_id TEXT NOT NULL UNIQUE REFERENCES no_show_events(no_show_id),
        assignment_id TEXT NOT NULL UNIQUE REFERENCES duty_assignments(assignment_id),
        person_id TEXT NOT NULL,
        season TEXT NOT NULL,
        completed_at TEXT,
        payload TEXT NOT NULL)""")
    connection.execute("CREATE INDEX idx_replacement_person_season ON replacement_duties(person_id, season)")


def _migration_010(connection: sqlite3.Connection) -> None:
    """Replace the abandoned repair model with separate immutable revocations.

    Explicit CKC decision: discard legacy revoked prototype facts and only their
    assessments; keep valid facts/payloads and all assignments/decisions intact.
    Never infer revocations from legacy corrections or replacement duties.
    """
    if not connection.in_transaction:
        connection.execute("BEGIN")
    connection.execute("SAVEPOINT no_show_revocation_migration")
    try:
        connection.execute("DROP TABLE replacement_duties")
        connection.execute("""DELETE FROM sanction_assessments WHERE no_show_id IN (
            SELECT no_show_id FROM no_show_events WHERE status='revoked')""")
        connection.execute("DELETE FROM no_show_events WHERE status='revoked'")
        connection.execute("ALTER TABLE no_show_events DROP COLUMN status")
        connection.execute("""CREATE TABLE no_show_revocations (
            revocation_id TEXT PRIMARY KEY,
            no_show_id TEXT NOT NULL UNIQUE REFERENCES no_show_events(no_show_id),
            reason TEXT NOT NULL,
            revoked_at TEXT NOT NULL,
            revoked_by TEXT NOT NULL)""")
        for table in ("no_show_events", "no_show_revocations"):
            for operation in ("UPDATE", "DELETE"):
                connection.execute(f"""CREATE TRIGGER {table}_no_{operation.lower()}
                    BEFORE {operation} ON {table} BEGIN
                    SELECT RAISE(ABORT, 'no-show facts are immutable'); END""")
    except Exception:
        connection.execute("ROLLBACK TO no_show_revocation_migration")
        connection.execute("RELEASE no_show_revocation_migration")
        raise
    connection.execute("RELEASE no_show_revocation_migration")


MIGRATIONS: tuple[Migration, ...] = (_migration_001, _migration_002, _migration_003, _migration_004, _migration_005, _migration_006, _migration_007, _migration_008, _migration_009, _migration_010)


def migrate(connection: sqlite3.Connection) -> int:
    """Bring a database to the latest known schema and return its version."""
    connection.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)")
    row = connection.execute("SELECT MAX(version) FROM schema_version").fetchone()
    current = int(row[0] or 0)
    for version, migration in enumerate(MIGRATIONS, start=1):
        if version <= current:
            continue
        migration(connection)
        connection.execute("INSERT INTO schema_version(version) VALUES (?)", (version,))
    return len(MIGRATIONS)
