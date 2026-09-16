from __future__ import annotations

from typing import Protocol

from .repositories import ImportBatchRepository, RecordRepository, SnapshotRepository


class UnitOfWork(Protocol):
    """Transaction boundary exposed to application services."""

    records: RecordRepository
    import_batches: ImportBatchRepository
    snapshots: SnapshotRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc_value, traceback) -> bool | None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
