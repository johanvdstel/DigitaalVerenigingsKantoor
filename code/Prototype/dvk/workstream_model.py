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
