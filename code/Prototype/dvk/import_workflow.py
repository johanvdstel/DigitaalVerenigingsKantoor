from __future__ import annotations

from dataclasses import replace
from datetime import datetime

from .import_management import ImportBatch, ImportStatus, SnapshotRecord, SourceSnapshot, compare_snapshot_records

BLOCKING_SEVERITIES = {"ERROR", "BLOCKING"}


def mark_validated(batch: ImportBatch, *, validation_summary: str, has_blocking_signals: bool) -> ImportBatch:
    return replace(
        batch,
        status=ImportStatus.INVALID if has_blocking_signals else ImportStatus.AWAITING_CONFIRMATION,
        validation_summary=validation_summary,
    )


def preview_differences(uow, batch: ImportBatch, records: tuple[SnapshotRecord, ...]):
    latest = uow.snapshots.latest(batch.source_system, batch.dataset_type, batch.source_period)
    old_records = () if latest is None else uow.snapshots.records(latest.snapshot_id)
    return compare_snapshot_records(old_records, records)


def confirm_import(
    uow,
    batch: ImportBatch,
    records: tuple[SnapshotRecord, ...],
    *,
    snapshot_id: str,
    confirmed_at: datetime,
    confirmed_by: str,
) -> SourceSnapshot:
    if batch.status is not ImportStatus.AWAITING_CONFIRMATION:
        raise ValueError("Only a validated import awaiting confirmation can create a snapshot")
    latest = uow.snapshots.latest(batch.source_system, batch.dataset_type, batch.source_period)
    snapshot = SourceSnapshot(
        snapshot_id, batch.import_batch_id, batch.source_system, batch.dataset_type,
        batch.source_period, confirmed_at, None if latest is None else latest.snapshot_id,
    )
    persisted_records = tuple(replace(record, snapshot_id=snapshot_id) for record in records)
    uow.snapshots.add(snapshot, persisted_records)
    uow.import_batches.update(replace(batch, status=ImportStatus.CONFIRMED,
                                      confirmed_at=confirmed_at, confirmed_by=confirmed_by))
    uow.commit()
    return snapshot
