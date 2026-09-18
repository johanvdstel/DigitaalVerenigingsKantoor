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
    status: str = "valid"
    correction_reason: str | None = None
    corrected_at: datetime | None = None
    corrected_by: str | None = None

    def __post_init__(self) -> None:
        if self.season != season_id(self.occurred_at.date()):
            raise ValueError("no-show season must match occurrence date")
        if self.status not in {"valid", "revoked"}:
            raise ValueError("invalid no-show status")


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


def assess_sanction(event: NoShowEvent, prior_events: tuple[NoShowEvent, ...]) -> SanctionAssessment:
    if event.status != "valid":
        raise ValueError("a revoked no-show cannot produce a sanction")
    prior_count = sum(
        1 for prior in prior_events
        if prior.person_id == event.person_id and prior.season == event.season
        and prior.status == "valid" and prior.occurred_at < event.occurred_at
    )
    counter = prior_count + 1
    if counter == 1:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, None, 0, 0, True, False)
    if counter == 2:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 1, False, False)
    if counter == 3:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 2, False, False)
    return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "red", 100, 3, False, True)
