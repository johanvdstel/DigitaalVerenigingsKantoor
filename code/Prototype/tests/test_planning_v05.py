from datetime import date, datetime

import pytest

from dvk.application_services import PlanningApplicationService
from dvk.planning import PlanningPeriod, PlanningSourceStatus
from dvk.security import AuthorizationError, Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_model import DutyService, Match


def _service(service_id, service_type, starts, required, location="CKC"):
    return DutyService(service_id, service_type, starts, starts.replace(hour=starts.hour + 2), location, required)


def _planner():
    return Identity("planner", "Planner", frozenset({Permission.VIEW_PLANNING}))


def test_planning_period_includes_weekday_and_weekend_services():
    services = (
        _service("WED", "Bardienst", datetime(2026, 9, 16, 19), 2),
        _service("SAT", "Bardienst", datetime(2026, 9, 19, 9), 3),
        _service("OUT", "Bardienst", datetime(2026, 9, 23, 19), 2),
    )
    needs = (
        StaffingNeed("WED", 2, 3, 1, 1, 2),
        StaffingNeed("SAT", 3, 5, 3, 0, 2),
        StaffingNeed("OUT", 2, 3, 0, 2, 3),
    )
    overview = PlanningApplicationService(_planner()).build_overview(
        period=PlanningPeriod(date(2026, 9, 14), date(2026, 9, 20)),
        services=services,
        staffing_needs=needs,
    )
    assert [row.service_id for row in overview.services] == ["WED", "SAT"]
    assert overview.services[0].open_need == 1
    assert overview.services[1].open_need == 0
    assert overview.services[1].remaining_capacity == 2


def test_planning_exposes_matches_source_status_and_quality():
    from dvk.real_data_import import DataQualitySignal

    service = _service("CK", "Gastvrouw/heer", datetime(2026, 9, 19, 12), 1, "Commissiekamer")
    need = StaffingNeed("CK", 1, 2, 0, 1, 2)
    match = Match("M1", "Senioren 1", datetime(2026, 9, 19, 14, 30), "home")
    outside = Match("M2", "Senioren 2", datetime(2026, 9, 20, 14, 30), "away")
    status = PlanningSourceStatus("Sportlink Programma", datetime(2026, 9, 17, 12), "actueel")
    signal = DataQualitySignal("TEST", "WARNING", "planning", "CK", "Controle nodig")
    overview = PlanningApplicationService(_planner()).build_overview(
        period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
        services=(service,), staffing_needs=(need,), matches=(match, outside),
        source_statuses=(status,), data_quality_signals=(signal,),
    )
    row = overview.services[0]
    assert row.match_id == "M1"
    assert row.match_team_id == "Senioren 1"
    assert overview.matches == (match,)
    assert overview.source_statuses == (status,)
    assert overview.data_quality_signals == (signal,)


def test_commissiekamer_context_never_links_away_match():
    service = _service("CK", "Gastvrouw/heer", datetime(2026, 9, 19, 12), 1, "Commissiekamer")
    need = StaffingNeed("CK", 1, 2, 0, 1, 2)
    away = Match("AWAY", "Senioren 2", datetime(2026, 9, 19, 13), "away")
    home = Match("HOME", "Senioren 1", datetime(2026, 9, 19, 14, 30), "home")
    overview = PlanningApplicationService(_planner()).build_overview(
        period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
        services=(service,), staffing_needs=(need,), matches=(away, home),
    )
    assert overview.services[0].match_id == "HOME"
    assert [match.match_id for match in overview.matches] == ["AWAY", "HOME"]


def test_only_away_match_leaves_commissiekamer_context_empty():
    service = _service("CK", "Gastvrouw/heer", datetime(2026, 9, 19, 12), 1, "Commissiekamer")
    need = StaffingNeed("CK", 1, 2, 0, 1, 2)
    away = Match("AWAY", "Senioren 2", datetime(2026, 9, 19, 14), "away")
    overview = PlanningApplicationService(_planner()).build_overview(
        period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
        services=(service,), staffing_needs=(need,), matches=(away,),
    )
    assert overview.services[0].match_id is None
    assert overview.matches == (away,)


def test_planning_requires_view_permission():
    identity = Identity("member", "Member", frozenset())
    with pytest.raises(AuthorizationError):
        PlanningApplicationService(identity).build_overview(
            period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
            services=(), staffing_needs=(),
        )


def test_planning_requires_staffing_for_each_visible_service():
    service = _service("BAR", "Bardienst", datetime(2026, 9, 19, 9), 2)
    with pytest.raises(ValueError, match="missing staffing need"):
        PlanningApplicationService(_planner()).build_overview(
            period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
            services=(service,), staffing_needs=(),
        )
