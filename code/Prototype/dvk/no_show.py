from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


def season_id(day: date) -> str:
    """CKC/KNVB/Sportlink season: 1 July through 30 June."""
    start_year = day.year if day.month >= 7 else day.year - 1
    return f"{start_year}/{start_year + 1}"


@dataclass(frozen=True)
class NoShowEvent:
    no_show_id: str
    assignment_id: str
    person_id: str
    occurred_at: datetime
    recorded_at: datetime
    recorded_by: str
    season: str

    def __post_init__(self) -> None:
        if self.season != season_id(self.occurred_at.date()):
            raise ValueError("no-show season must match occurrence date")


@dataclass(frozen=True)
class NoShowRevocation:
    revocation_id: str
    no_show_id: str
    reason: str
    revoked_at: datetime
    revoked_by: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("revocation reason is required")


@dataclass(frozen=True)
class SanctionAssessment:
    no_show_id: str
    person_id: str
    season: str
    counter: int
    card: str | None
    fine_eur: int
    suspension_matches: int
    replacement_service_required: bool
    board_follow_up: bool
    communication_required: bool = True


def assess_sanction(
    event: NoShowEvent, prior_events: tuple[NoShowEvent, ...],
    revocations: tuple[NoShowRevocation, ...] = (),
) -> SanctionAssessment:
    revoked_ids = {revocation.no_show_id for revocation in revocations}
    if event.no_show_id in revoked_ids:
        raise ValueError("a revoked no-show cannot produce a sanction")
    prior_count = sum(
        1 for prior in prior_events
        if prior.person_id == event.person_id and prior.season == event.season
        and prior.no_show_id not in revoked_ids and prior.occurred_at < event.occurred_at
    )
    return _sanction_at_counter(event, prior_count + 1)


def _sanction_at_counter(event: NoShowEvent, counter: int) -> SanctionAssessment:
    if counter == 1:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, None, 0, 0, True, False)
    if counter == 2:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 1, False, False)
    if counter == 3:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 2, False, False)
    return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "red", 100, 3, False, True)


@dataclass(frozen=True)
class CurrentSanctionState:
    person_id: str
    season: str
    counter: int
    assessment: SanctionAssessment | None


def current_sanction_state(
    person_id: str, season: str, no_shows: tuple[NoShowEvent, ...],
    revocations: tuple[NoShowRevocation, ...] = (),
) -> CurrentSanctionState:
    """Current season state, independent of historical registration assessments."""
    revoked_ids = {revocation.no_show_id for revocation in revocations}
    valid = tuple(event for event in no_shows
                  if event.person_id == person_id and event.season == season
                  and event.no_show_id not in revoked_ids)
    latest = max(valid, key=lambda event: (event.occurred_at, event.no_show_id)) if valid else None
    assessment = _sanction_at_counter(latest, len(valid)) if latest else None
    return CurrentSanctionState(person_id, season, len(valid), assessment)
