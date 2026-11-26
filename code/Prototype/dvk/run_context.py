from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class SourceFetchStatus(str, Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class EngineRunStatus(str, Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SourceFetch:
    source_fetch_id: str
    source_system: str
    dataset_type: str
    requested_at: datetime
    completed_at: datetime
    period_start: date
    period_end: date
    status: SourceFetchStatus
    record_count: int | None = None
    error_category: str | None = None

    def __post_init__(self) -> None:
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot precede period_start")
        if self.status is SourceFetchStatus.SUCCEEDED:
            if self.record_count is None or self.record_count < 0:
                raise ValueError("successful fetch requires a non-negative record_count")
            if self.error_category is not None:
                raise ValueError("successful fetch cannot have an error_category")
        else:
            if self.record_count is not None:
                raise ValueError("failed fetch must not pretend to have a record_count")
            if not self.error_category or not self.error_category.strip():
                raise ValueError("failed fetch requires an error_category")


@dataclass(frozen=True)
class EngineRun:
    engine_run_id: str
    started_at: datetime
    initiated_by: str
    period_start: date
    period_end: date
    status: EngineRunStatus
    snapshot_ids: tuple[str, ...]
    source_fetch_ids: tuple[str, ...]
    policy_version: str
    config_version: str
    engine_version: str
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.period_end < self.period_start:
            raise ValueError("period_end cannot precede period_start")
        if not self.initiated_by.strip():
            raise ValueError("initiated_by is required")
        if not self.policy_version.strip() or not self.config_version.strip() or not self.engine_version.strip():
            raise ValueError("policy_version, config_version and engine_version are required")
        if self.status is EngineRunStatus.STARTED and self.completed_at is not None:
            raise ValueError("started run cannot already have completed_at")
        if self.status is not EngineRunStatus.STARTED and self.completed_at is None:
            raise ValueError("completed or failed run requires completed_at")
