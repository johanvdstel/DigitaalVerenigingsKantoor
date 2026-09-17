from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _service(start: datetime, end: datetime) -> DutyService:
    return DutyService("S-G8-TREE", "bardienst", start, end, "Clubhuis", 1)


def _assessment(case_id: str, service: DutyService, match: Match):
    case = W_CASE_BY_ID[case_id]
    memberships = (TeamMembership(case.person.person_id, match.team_id, date(2026, 7, 1), date(2027, 6, 30)),)
    return assess_candidate(case, service, memberships, (match,), TODAY)


def test_senior_away_overlap_is_ineligible():
    service = _service(datetime(2026, 9, 19, 9), datetime(2026, 9, 19, 13))
    match = Match("M1", "SEN-8", datetime(2026, 9, 19, 12, 15), "away")
    result = _assessment("W08", service, match)
    assert result.eligible is False
    assert result.match_relation == "away_match_overlaps_service"


def test_senior_away_same_day_is_emergency_candidate():
    service = _service(datetime(2026, 9, 19, 12, 30), datetime(2026, 9, 19, 17))
    match = Match("M2", "SEN-8", datetime(2026, 9, 19, 12, 15), "away")
    result = _assessment("W08", service, match)
    assert result.eligible is True
    assert result.match_relation == "away_match_same_day"
    assert result.preference == "avoid"


def test_senior_home_overlap_is_ineligible():
    service = _service(datetime(2026, 9, 19, 12), datetime(2026, 9, 19, 16))
    match = Match("M3", "SEN-8", datetime(2026, 9, 19, 14, 30), "home")
    result = _assessment("W08", service, match)
    assert result.eligible is False
    assert result.match_relation == "home_match_overlaps_service"


def test_senior_home_same_day_without_overlap_is_eligible():
    service = _service(datetime(2026, 9, 19, 9), datetime(2026, 9, 19, 12))
    match = Match("M4", "SEN-8", datetime(2026, 9, 19, 14, 30), "home")
    result = _assessment("W08", service, match)
    assert result.eligible is True
    assert result.match_relation == "home_match_same_day"


def test_youth_home_overlap_is_eligible_via_parent():
    service = _service(datetime(2026, 9, 19, 9), datetime(2026, 9, 19, 13))
    match = Match("M5", "JO14-1", datetime(2026, 9, 19, 11), "home")
    result = _assessment("W04", service, match)
    assert result.executor_category == "parent_guardian"
    assert result.eligible is True
    assert result.match_relation == "home_match_overlaps_service"


def test_youth_weekend_service_starting_at_1230_is_allowed():
    service = _service(datetime(2026, 9, 19, 12, 30), datetime(2026, 9, 19, 17))
    match = Match("M6", "JO14-1", datetime(2026, 9, 19, 10), "home")
    result = _assessment("W04", service, match)
    assert result.eligible is True


def test_youth_weekend_service_starting_after_1230_is_ineligible():
    service = _service(datetime(2026, 9, 19, 12, 31), datetime(2026, 9, 19, 17))
    match = Match("M7", "JO14-1", datetime(2026, 9, 19, 10), "home")
    result = _assessment("W04", service, match)
    assert result.eligible is False
    assert result.match_relation == "youth_weekend_after_1230"


def test_youth_weekday_evening_service_is_allowed():
    service = _service(datetime(2026, 9, 16, 19), datetime(2026, 9, 16, 22))
    match = Match("M8", "JO14-1", datetime(2026, 9, 16, 18), "home")
    result = _assessment("W04", service, match)
    assert result.eligible is True
