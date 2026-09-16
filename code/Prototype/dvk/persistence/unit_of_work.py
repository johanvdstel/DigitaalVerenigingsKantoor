from __future__ import annotations

from typing import Protocol

from .repositories import EngineRunRepository, ImportBatchRepository, RecordRepository, SnapshotRepository, SourceFetchRepository


class UnitOfWork(Protocol):
    """Transaction boundary exposed to application services."""

    records: RecordRepository
    import_batches: ImportBatchRepository
    snapshots: SnapshotRepository
    source_fetches: SourceFetchRepository
    engine_runs: EngineRunRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc_value, traceback) -> bool | None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
