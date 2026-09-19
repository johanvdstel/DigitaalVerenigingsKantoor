from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .real_data_import import DataQualitySignal
from .staffing import StaffingNeed
from .workstream_model import DutyService, Match


@dataclass(frozen=True)
class PlanningPeriod:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("planning period end must be on or after start")

    def contains(self, moment: datetime) -> bool:
        return self.start <= moment.date() <= self.end


@dataclass(frozen=True)
class PlanningSourceStatus:
    source: str
    fetched_at: datetime | None
    status: str


@dataclass(frozen=True)
class PlanningServiceRow:
    service_id: str
    service_type: str
    starts_at: datetime
    ends_at: datetime
    location: str
    minimum_staff: int
    maximum_staff: int
    confirmed_occupancy: int
    open_need: int
    remaining_capacity: int
    match_id: str | None = None
    match_team_id: str | None = None
    match_starts_at: datetime | None = None


@dataclass(frozen=True)
class PlanningOverview:
    period: PlanningPeriod
    services: tuple[PlanningServiceRow, ...]
    matches: tuple[Match, ...] = ()
    source_statuses: tuple[PlanningSourceStatus, ...] = ()
    data_quality_signals: tuple[DataQualitySignal, ...] = ()


def build_planning_overview(
    *,
    period: PlanningPeriod,
    services: tuple[DutyService, ...],
    staffing_needs: tuple[StaffingNeed, ...],
    matches: tuple[Match, ...] = (),
    source_statuses: tuple[PlanningSourceStatus, ...] = (),
    data_quality_signals: tuple[DataQualitySignal, ...] = (),
) -> PlanningOverview:
    """Build a read-only planning view from already-derived DVK facts."""
    needs = {need.service_id: need for need in staffing_needs}
    visible_matches = tuple(sorted(
        (match for match in matches if period.contains(match.starts_at)),
        key=lambda match: (match.starts_at, match.match_id),
    ))
    rows: list[PlanningServiceRow] = []
    for service in services:
        if not period.contains(service.starts_at):
            continue
        need = needs.get(service.service_id)
        if need is None:
            raise ValueError(f"missing staffing need for {service.service_id}")

        # Commissiekamer is a location. A service there may show a home match as
        # context, but an away match must never be linked to that service.
        linked_match = next(
            (
                match for match in visible_matches
                if match.starts_at.date() == service.starts_at.date()
                and service.location.strip().lower() == "commissiekamer"
                and match.home_away.strip().lower() == "home"
            ),
            None,
        )
        rows.append(PlanningServiceRow(
            service.service_id, service.service_type, service.starts_at, service.ends_at,
            service.location, need.minimum_staff, need.maximum_staff,
            need.confirmed_occupancy, need.open_need, need.remaining_capacity,
            linked_match.match_id if linked_match else None,
            linked_match.team_id if linked_match else None,
            linked_match.starts_at if linked_match else None,
        ))
    return PlanningOverview(
        period,
        tuple(sorted(rows, key=lambda row: (row.starts_at, row.service_id))),
        visible_matches,
        source_statuses,
        data_quality_signals,
    )
