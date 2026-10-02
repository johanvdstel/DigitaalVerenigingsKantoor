from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .real_data_import import DutyImportRecord


@dataclass(frozen=True)
class SeasonClosingDutyRecord:
    person_id: str
    season: str
    required_hours: int
    correction_hours: int
    completed_hours: int
    scheduled_hours: int
    remaining_hours: int
    source_remaining_hours: int
    captured_at: datetime
    source_system: str = "Sportlink"
    source_dataset: str = "vrijwilligers_periode"


def build_season_closing_records(
    duty_records: tuple[DutyImportRecord, ...],
    *,
    season: str,
    captured_at: datetime,
) -> tuple[SeasonClosingDutyRecord, ...]:
    """Freeze the Sportlink duty position at season close for later prioritisation."""
    return tuple(
        SeasonClosingDutyRecord(
            record.registration.person_id,
            season,
            record.position.A,
            record.position.B,
            record.position.C,
            record.position.D,
            record.position.E,
            record.source_remaining_hours,
            captured_at,
        )
        for record in duty_records
    )


def previous_season_backlog(
    records: tuple[SeasonClosingDutyRecord, ...],
    *,
    season: str,
) -> dict[str, int]:
    return {record.person_id: record.remaining_hours for record in records if record.season == season}
