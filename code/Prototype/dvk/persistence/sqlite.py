from __future__ import annotations

import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from ..import_management import ImportBatch, ImportStatus, SnapshotRecord, SourceSnapshot
from ..no_show import NoShowEvent, SanctionAssessment
from ..run_context import EngineRun, EngineRunStatus, SourceFetch, SourceFetchStatus
from ..versioning import ConfigVersion, PolicyVersion, SoftwareVersion
from .migrations import migrate
from .planning_records import SQLiteAssignmentProposalRepository, SQLiteDutyAssignmentRepository, SQLiteHumanDecisionRepository
from .no_show_records import SQLiteNoShowRepository, SQLiteNoShowRevocationRepository, SQLiteSanctionAssessmentRepository


class SQLiteRecordRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, record_id: str, payload: str) -> None: self._connection.execute("INSERT INTO dvk_records(record_id, payload) VALUES (?, ?)", (record_id, payload))
    def get(self, record_id: str) -> dict[str, Any] | None:
        row = self._connection.execute("SELECT record_id, payload FROM dvk_records WHERE record_id = ?", (record_id,)).fetchone(); return None if row is None else {"record_id": row[0], "payload": row[1]}


class SQLiteImportBatchRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, batch: ImportBatch) -> None:
        self._connection.execute("INSERT INTO import_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (batch.import_batch_id, batch.source_system, batch.dataset_type, batch.source_period, batch.uploaded_at.isoformat(), batch.uploaded_by, batch.status.value, batch.validation_summary, _iso(batch.confirmed_at), batch.confirmed_by))
    def update(self, batch: ImportBatch) -> None: self._connection.execute("UPDATE import_batches SET status=?, validation_summary=?, confirmed_at=?, confirmed_by=? WHERE import_batch_id=?", (batch.status.value, batch.validation_summary, _iso(batch.confirmed_at), batch.confirmed_by, batch.import_batch_id))
    def get(self, import_batch_id: str) -> ImportBatch | None:
        row = self._connection.execute("SELECT * FROM import_batches WHERE import_batch_id=?", (import_batch_id,)).fetchone(); return None if row is None else _batch(row)


class SQLiteSnapshotRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, snapshot: SourceSnapshot, records: tuple[SnapshotRecord, ...]) -> None:
        self._connection.execute("INSERT INTO source_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)", (snapshot.snapshot_id, snapshot.import_batch_id, snapshot.source_system, snapshot.dataset_type, snapshot.source_period, snapshot.created_at.isoformat(), snapshot.supersedes_snapshot_id))
        self._connection.executemany("INSERT INTO snapshot_records VALUES (?, ?, ?, ?, ?)", [(r.snapshot_id, r.record_key, r.source_payload, r.canonical_payload, r.provenance_payload) for r in records])
    def get(self, snapshot_id: str) -> SourceSnapshot | None:
        row = self._connection.execute("SELECT * FROM source_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone(); return None if row is None else _snapshot(row)
    def records(self, snapshot_id: str) -> tuple[SnapshotRecord, ...]:
        rows = self._connection.execute("SELECT snapshot_id, record_key, source_payload, canonical_payload, provenance_payload FROM snapshot_records WHERE snapshot_id=? ORDER BY record_key", (snapshot_id,)).fetchall(); return tuple(SnapshotRecord(*row) for row in rows)
    def latest(self, source_system: str, dataset_type: str, source_period: str | None) -> SourceSnapshot | None:
        row = self._connection.execute("SELECT * FROM source_snapshots WHERE source_system=? AND dataset_type=? AND source_period IS ? ORDER BY created_at DESC, rowid DESC LIMIT 1", (source_system, dataset_type, source_period)).fetchone(); return None if row is None else _snapshot(row)


class SQLiteSourceFetchRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, fetch: SourceFetch) -> None:
        self._connection.execute("INSERT INTO source_fetches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (fetch.source_fetch_id, fetch.source_system, fetch.dataset_type, fetch.requested_at.isoformat(), fetch.completed_at.isoformat(), fetch.period_start.isoformat(), fetch.period_end.isoformat(), fetch.status.value, fetch.record_count, fetch.error_category))
    def get(self, source_fetch_id: str) -> SourceFetch | None:
        row = self._connection.execute("SELECT * FROM source_fetches WHERE source_fetch_id=?", (source_fetch_id,)).fetchone(); return None if row is None else SourceFetch(row[0], row[1], row[2], _dt(row[3]), _dt(row[4]), date.fromisoformat(row[5]), date.fromisoformat(row[6]), SourceFetchStatus(row[7]), row[8], row[9])


class _ImmutableContentVersionRepository:
    model = None; table = ""
    def __init__(self, connection): self._connection = connection
    def add(self, version) -> None:
        self._connection.execute(f"INSERT INTO {self.table} VALUES (?, ?, ?, ?, ?, ?)", (version.version_id, version.content_json, version.content_hash, version.created_at.isoformat(), version.created_by, version.effective_from.isoformat()))
    def get(self, version_id):
        row = self._connection.execute(f"SELECT version_id, content_json, content_hash, created_at, created_by, effective_from FROM {self.table} WHERE version_id=?", (version_id,)).fetchone()
        return None if row is None else self.model(row[0], row[1], row[2], _dt(row[3]), row[4], date.fromisoformat(row[5]))


class SQLitePolicyVersionRepository(_ImmutableContentVersionRepository): model = PolicyVersion; table = "policy_versions"
class SQLiteConfigVersionRepository(_ImmutableContentVersionRepository): model = ConfigVersion; table = "config_versions"


class SQLiteSoftwareVersionRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, version: SoftwareVersion) -> None: self._connection.execute("INSERT INTO software_versions VALUES (?, ?, ?, ?)", (version.version_id, version.release_label, version.git_commit_sha, version.created_at.isoformat()))
    def get(self, version_id: str) -> SoftwareVersion | None:
        row = self._connection.execute("SELECT version_id, release_label, git_commit_sha, created_at FROM software_versions WHERE version_id=?", (version_id,)).fetchone(); return None if row is None else SoftwareVersion(row[0], row[1], row[2], _dt(row[3]))


class SQLiteEngineRunRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, run: EngineRun) -> None:
        required = (("policy_versions", run.policy_version), ("config_versions", run.config_version), ("software_versions", run.engine_version))
        for table, version_id in required:
            if self._connection.execute(f"SELECT 1 FROM {table} WHERE version_id=?", (version_id,)).fetchone() is None: raise ValueError(f"EngineRun references unknown version: {version_id}")
        self._connection.execute("INSERT INTO engine_runs (engine_run_id, started_at, completed_at, initiated_by, period_start, period_end, status, policy_version, engine_version, config_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (run.engine_run_id, run.started_at.isoformat(), _iso(run.completed_at), run.initiated_by, run.period_start.isoformat(), run.period_end.isoformat(), run.status.value, run.policy_version, run.engine_version, run.config_version))
        self._connection.executemany("INSERT INTO engine_run_snapshots VALUES (?, ?)", [(run.engine_run_id, value) for value in run.snapshot_ids]); self._connection.executemany("INSERT INTO engine_run_fetches VALUES (?, ?)", [(run.engine_run_id, value) for value in run.source_fetch_ids])
    def get(self, engine_run_id: str) -> EngineRun | None:
        row = self._connection.execute("SELECT engine_run_id, started_at, completed_at, initiated_by, period_start, period_end, status, policy_version, engine_version, config_version FROM engine_runs WHERE engine_run_id=?", (engine_run_id,)).fetchone()
        if row is None: return None
        snapshots = tuple(r[0] for r in self._connection.execute("SELECT snapshot_id FROM engine_run_snapshots WHERE engine_run_id=? ORDER BY snapshot_id", (engine_run_id,)).fetchall()); fetches = tuple(r[0] for r in self._connection.execute("SELECT source_fetch_id FROM engine_run_fetches WHERE engine_run_id=? ORDER BY source_fetch_id", (engine_run_id,)).fetchall())
        return EngineRun(row[0], _dt(row[1]), row[3], date.fromisoformat(row[4]), date.fromisoformat(row[5]), EngineRunStatus(row[6]), snapshots, fetches, row[7], row[9], row[8], _dt(row[2]))


class SQLiteUnitOfWork:
    def __init__(self, database_path: str | Path) -> None: self._database_path = str(database_path); self._connection = None; self._committed = False
    def __enter__(self):
        self._connection = sqlite3.connect(self._database_path); self._connection.execute("PRAGMA foreign_keys=ON"); migrate(self._connection); self._connection.commit()
        self.records = SQLiteRecordRepository(self._connection); self.import_batches = SQLiteImportBatchRepository(self._connection); self.snapshots = SQLiteSnapshotRepository(self._connection); self.source_fetches = SQLiteSourceFetchRepository(self._connection); self.engine_runs = SQLiteEngineRunRepository(self._connection)
        self.proposals = SQLiteAssignmentProposalRepository(self._connection); self.decisions = SQLiteHumanDecisionRepository(self._connection); self.assignments = SQLiteDutyAssignmentRepository(self._connection); self.no_shows = SQLiteNoShowRepository(self._connection); self.sanctions = SQLiteSanctionAssessmentRepository(self._connection); self.no_show_revocations = SQLiteNoShowRevocationRepository(self._connection)
        self.policy_versions = SQLitePolicyVersionRepository(self._connection); self.config_versions = SQLiteConfigVersionRepository(self._connection); self.software_versions = SQLiteSoftwareVersionRepository(self._connection); self._committed = False; return self
    def commit(self) -> None:
        if self._connection is None: raise RuntimeError("Unit of work is not active")
        self._connection.commit(); self._committed = True
    def rollback(self) -> None:
        if self._connection is not None: self._connection.rollback()
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._connection is None: return False
        try:
            if exc_type is not None or not self._committed: self._connection.rollback()
        finally: self._connection.close(); self._connection = None
        return False


class SQLiteDatabase:
    def __init__(self, path: str | Path) -> None: self.path = Path(path)
    def initialize(self) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection: return migrate(connection)
    def unit_of_work(self) -> SQLiteUnitOfWork: self.path.parent.mkdir(parents=True, exist_ok=True); return SQLiteUnitOfWork(self.path)


def _iso(value): return None if value is None else value.isoformat()
def _dt(value): return None if value is None else datetime.fromisoformat(value)
def _batch(row): return ImportBatch(row[0], row[1], row[2], row[3], _dt(row[4]), row[5], ImportStatus(row[6]), row[7], _dt(row[8]), row[9])
def _snapshot(row): return SourceSnapshot(row[0], row[1], row[2], row[3], row[4], _dt(row[5]), row[6])
