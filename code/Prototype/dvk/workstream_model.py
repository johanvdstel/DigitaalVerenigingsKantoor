from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class TeamMembership:
    person_id: str
    team_id: str
    start_date: date | None = None
    end_date: date | None = None


@dataclass(frozen=True)
class Match:
    match_id: str
    team_id: str
    starts_at: datetime
    home_away: str


@dataclass(frozen=True)
class DutyService:
    service_id: str
    service_type: str
    starts_at: datetime
    ends_at: datetime
    location: str
    required_staff: int

    @property
    def duration_hours(self) -> float:
        return (self.ends_at - self.starts_at).total_seconds() / 3600


@dataclass(frozen=True)
class CandidateAssessment:
    """Step-4 assessment for one member/service combination.

    This records eligibility and practical match context only. Ranking based on
    remaining hours or previous-season backlog belongs to step 5.
    """

    person_id: str
    service_id: str
    eligible: bool
    executor_category: str | None
    team_id: str | None
    home_away: str | None
    match_relation: str
    preference: str
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class CandidatePriority:
    person_id: str
    service_id: str
    rank: int
    remaining_hours: int
    previous_season_backlog: int
    previous_season_considered: bool
    match_preference: str
    explanation: tuple[str, ...]


@dataclass(frozen=True)
class DashboardDutyRow:
    person_id: str
    name: str
    team_id: str | None
    duty_required: bool
    qualification_reason: str
    A: int | None
    B: int | None
    C: int | None
    D: int | None
    E: int | None
    sportlink_mismatch: bool


@dataclass(frozen=True)
class DashboardServiceRow:
    service_id: str
    service_type: str
    starts_at: datetime
    ends_at: datetime
    required_staff: int
    remaining_staff: int


@dataclass(frozen=True)
class DashboardCandidateRow:
    service_id: str
    person_id: str
    rank: int
    team_id: str | None
    remaining_hours: int
    executor_category: str | None
    home_away: str | None
    match_relation: str
    preference: str
    explanation: tuple[str, ...]
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class DashboardViewModel:
    duty_rows: tuple[DashboardDutyRow, ...]
    service_rows: tuple[DashboardServiceRow, ...]
    candidate_rows: tuple[DashboardCandidateRow, ...]
