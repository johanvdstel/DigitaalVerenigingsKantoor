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
class AssignmentProposal:
    proposal_id: str
    service_id: str
    person_id: str
    executor_category: str | None
    A: int
    B: int
    C: int
    D: int
    E: int
    previous_season_backlog: int
    previous_season_considered: bool
    team_id: str | None
    home_away: str | None
    match_starts_at: datetime | None
    match_relation: str
    suitability: str
    priority_rank: int
    applied_priority_rules: tuple[str, ...]
    uncertainties: tuple[str, ...] = ()
    status: str = "proposed"


@dataclass(frozen=True)
class HumanDecision:
    proposal_id: str
    decision: str
    decided_by: str
    reason_category: str | None = None
    reason: str | None = None


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

    @property
    def required_hours(self) -> int | None: return self.A
    @property
    def correction_hours(self) -> int | None: return self.B
    @property
    def completed_hours(self) -> int | None: return self.C
    @property
    def scheduled_hours(self) -> int | None: return self.D
    @property
    def remaining_hours(self) -> int | None: return self.E


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
    name: str
    rank: int
    team_id: str | None
    remaining_hours: int
    executor_category: str | None
    home_away: str | None
    match_starts_at: datetime | None
    match_relation: str
    preference: str
    explanation: tuple[str, ...]
    shared_first_choice: bool = False
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class DashboardNotProposedRow:
    service_id: str
    person_id: str
    name: str
    team_id: str | None
    home_away: str | None
    match_starts_at: datetime | None
    reason: str


@dataclass(frozen=True)
class DashboardViewModel:
    duty_rows: tuple[DashboardDutyRow, ...]
    service_rows: tuple[DashboardServiceRow, ...]
    candidate_rows: tuple[DashboardCandidateRow, ...]
    not_proposed_rows: tuple[DashboardNotProposedRow, ...] = ()
