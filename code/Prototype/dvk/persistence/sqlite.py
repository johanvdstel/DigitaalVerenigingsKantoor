from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from ..import_management import ImportBatch, ImportStatus, SnapshotRecord, SourceSnapshot
from .migrations import migrate


class SQLiteRecordRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, record_id: str, payload: str) -> None:
        self._connection.execute("INSERT INTO dvk_records(record_id, payload) VALUES (?, ?)", (record_id, payload))
    def get(self, record_id: str) -> dict[str, Any] | None:
        row = self._connection.execute("SELECT record_id, payload FROM dvk_records WHERE record_id = ?", (record_id,)).fetchone()
        return None if row is None else {"record_id": row[0], "payload": row[1]}


class SQLiteImportBatchRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, batch: ImportBatch) -> None:
        self._connection.execute(
            "INSERT INTO import_batches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (batch.import_batch_id, batch.source_system, batch.dataset_type, batch.source_period,
             batch.uploaded_at.isoformat(), batch.uploaded_by, batch.status.value,
             batch.validation_summary, _iso(batch.confirmed_at), batch.confirmed_by))
    def update(self, batch: ImportBatch) -> None:
        self._connection.execute(
            "UPDATE import_batches SET status=?, validation_summary=?, confirmed_at=?, confirmed_by=? WHERE import_batch_id=?",
            (batch.status.value, batch.validation_summary, _iso(batch.confirmed_at), batch.confirmed_by, batch.import_batch_id))
    def get(self, import_batch_id: str) -> ImportBatch | None:
        row = self._connection.execute("SELECT * FROM import_batches WHERE import_batch_id=?", (import_batch_id,)).fetchone()
        return None if row is None else _batch(row)


class SQLiteSnapshotRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, snapshot: SourceSnapshot, records: tuple[SnapshotRecord, ...]) -> None:
        self._connection.execute(
            "INSERT INTO source_snapshots VALUES (?, ?, ?, ?, ?, ?, ?)",
            (snapshot.snapshot_id, snapshot.import_batch_id, snapshot.source_system, snapshot.dataset_type,
             snapshot.source_period, snapshot.created_at.isoformat(), snapshot.supersedes_snapshot_id))
        self._connection.executemany(
            "INSERT INTO snapshot_records VALUES (?, ?, ?, ?, ?)",
            [(r.snapshot_id, r.record_key, r.source_payload, r.canonical_payload, r.provenance_payload) for r in records])
    def get(self, snapshot_id: str) -> SourceSnapshot | None:
        row = self._connection.execute("SELECT * FROM source_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone()
        return None if row is None else _snapshot(row)
    def records(self, snapshot_id: str) -> tuple[SnapshotRecord, ...]:
        rows = self._connection.execute(
            "SELECT snapshot_id, record_key, source_payload, canonical_payload, provenance_payload FROM snapshot_records WHERE snapshot_id=? ORDER BY record_key",
            (snapshot_id,)).fetchall()
        return tuple(SnapshotRecord(*row) for row in rows)
    def latest(self, source_system: str, dataset_type: str, source_period: str | None) -> SourceSnapshot | None:
        row = self._connection.execute(
            "SELECT * FROM source_snapshots WHERE source_system=? AND dataset_type=? AND source_period IS ? ORDER BY created_at DESC, rowid DESC LIMIT 1",
            (source_system, dataset_type, source_period)).fetchone()
        return None if row is None else _snapshot(row)


class SQLiteUnitOfWork:
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path); self._connection = None; self._committed = False
    def __enter__(self):
        self._connection = sqlite3.connect(self._database_path)
        # Schema setup is infrastructure state and must survive rollback of a business UoW.
        migrate(self._connection)
        self._connection.commit()
        self.records = SQLiteRecordRepository(self._connection)
        self.import_batches = SQLiteImportBatchRepository(self._connection)
        self.snapshots = SQLiteSnapshotRepository(self._connection)
        self._committed = False; return self
    def commit(self) -> None:
        if self._connection is None: raise RuntimeError("Unit of work is not active")
        self._connection.commit(); self._committed = True
    def rollback(self) -> None:
        if self._connection is not None: self._connection.rollback()
    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._connection is None: return False
        try:
            if exc_type is not None or not self._committed: self._connection.rollback()
        finally:
            self._connection.close(); self._connection = None
        return False


class SQLiteDatabase:
    def __init__(self, path: str | Path) -> None: self.path = Path(path)
    def initialize(self) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection: return migrate(connection)
    def unit_of_work(self) -> SQLiteUnitOfWork:
        self.path.parent.mkdir(parents=True, exist_ok=True); return SQLiteUnitOfWork(self.path)


def _iso(value): return None if value is None else value.isoformat()
def _dt(value): return None if value is None else datetime.fromisoformat(value)
def _batch(row):
    return ImportBatch(row[0], row[1], row[2], row[3], _dt(row[4]), row[5], ImportStatus(row[6]), row[7], _dt(row[8]), row[9])
def _snapshot(row):
    return SourceSnapshot(row[0], row[1], row[2], row[3], row[4], _dt(row[5]), row[6])
