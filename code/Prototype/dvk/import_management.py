from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ImportStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    CONFIRMED = "CONFIRMED"
    INVALID = "INVALID"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ImportBatch:
    import_batch_id: str
    source_system: str
    dataset_type: str
    source_period: str | None
    uploaded_at: datetime
    uploaded_by: str
    status: ImportStatus
    validation_summary: str | None = None
    confirmed_at: datetime | None = None
    confirmed_by: str | None = None


@dataclass(frozen=True)
class SourceSnapshot:
    snapshot_id: str
    import_batch_id: str
    source_system: str
    dataset_type: str
    source_period: str | None
    created_at: datetime
    supersedes_snapshot_id: str | None = None


@dataclass(frozen=True)
class SnapshotRecord:
    snapshot_id: str
    record_key: str
    source_payload: str
    canonical_payload: str
    provenance_payload: str


@dataclass(frozen=True)
class SnapshotDifference:
    record_key: str
    change_type: str
    before: str | None
    after: str | None


def compare_snapshot_records(
    old_records: tuple[SnapshotRecord, ...],
    new_records: tuple[SnapshotRecord, ...],
) -> tuple[SnapshotDifference, ...]:
    """Compare canonical snapshot records without depending on storage technology."""
    old = {record.record_key: record.canonical_payload for record in old_records}
    new = {record.record_key: record.canonical_payload for record in new_records}
    differences: list[SnapshotDifference] = []
    for key in sorted(old.keys() | new.keys()):
        if key not in old:
            differences.append(SnapshotDifference(key, "RECORD_ADDED", None, new[key]))
        elif key not in new:
            differences.append(SnapshotDifference(key, "RECORD_REMOVED", old[key], None))
        elif old[key] != new[key]:
            differences.append(SnapshotDifference(key, "RECORD_CHANGED", old[key], new[key]))
    return tuple(differences)
