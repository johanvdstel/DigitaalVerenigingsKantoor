from __future__ import annotations

from typing import Protocol

from .repositories import (
    ConfigVersionRepository, EngineRunRepository, ImportBatchRepository, PolicyVersionRepository,
    RecordRepository, SnapshotRepository, SoftwareVersionRepository, SourceFetchRepository,
)


class UnitOfWork(Protocol):
    """Transaction boundary exposed to application services."""

    records: RecordRepository
    import_batches: ImportBatchRepository
    snapshots: SnapshotRepository
    source_fetches: SourceFetchRepository
    engine_runs: EngineRunRepository
    policy_versions: PolicyVersionRepository
    config_versions: ConfigVersionRepository
    software_versions: SoftwareVersionRepository

    def __enter__(self) -> "UnitOfWork": ...
    def __exit__(self, exc_type, exc_value, traceback) -> bool | None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
