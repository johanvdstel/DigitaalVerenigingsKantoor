from datetime import date, datetime, timedelta, time

from dvk.candidate_selection import assess_candidate
from dvk.prioritization import prioritize_candidates
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _context():
    monday = date(2026, 9, 14)
    services = (
        DutyService("BAR-WO-1", "Bardienst", datetime.combine(monday + timedelta(days=2), time(19)), datetime.combine(monday + timedelta(days=2), time(22)), "Clubhuis", 2),
        DutyService("BAR-ZA-1", "Bardienst", datetime.combine(monday + timedelta(days=5), time(9)), datetime.combine(monday + timedelta(days=5), time(13)), "Clubhuis", 3),
        DutyService("CK-ZA-1", "Gastvrouw/heer", datetime.combine(monday + timedelta(days=5), time(12,30)), datetime.combine(monday + timedelta(days=5), time(17)), "Commissiekamer", 1),
    )
    matches = (
        Match("W-001", "Senioren 1", datetime.combine(monday + timedelta(days=5), time(14,30)), "home"),
        Match("W-002", "SEN-8", datetime.combine(monday + timedelta(days=5), time(12,15)), "away"),
        Match("W-003", "JO17-1", datetime.combine(monday + timedelta(days=6), time(10,30)), "away"),
    )
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"], W_CASE_BY_ID["W09"])
    teams = {"W08P":"Senioren 1","W07P":"SEN-8","W09P":"JO17-1"}
    memberships = tuple(TeamMembership(c.person.person_id, teams[c.person.person_id], monday-timedelta(days=60), monday+timedelta(days=300)) for c in cases)
    return services, matches, cases, memberships


def test_representative_demo_population_exercises_three_teams():
    _, _, cases, memberships = _context()
    assert {m.team_id for m in memberships} == {"Senioren 1", "SEN-8", "JO17-1"}
    assert {c.person.name for c in cases} == {"Senior Grote E", "Senior Urenpositie", "Senior Oude Achterstand"}


def test_senioren_1_home_without_overlap_is_eligible_for_bar_service():
    services, matches, cases, memberships = _context()
    service = next(s for s in services if s.service_id == "BAR-ZA-1")
    case = W_CASE_BY_ID["W08"]
    assessment = assess_candidate(case, service, memberships, matches, TODAY)
    assert assessment.eligible
    assert assessment.team_id == "Senioren 1"
    assert assessment.home_away == "home"
    assert assessment.match_relation == "home_match_same_day"


def test_youth_candidate_is_available_on_weekday_without_match_context():
    services, matches, cases, memberships = _context()
    service = next(s for s in services if s.service_id == "BAR-WO-1")
    assessment = assess_candidate(W_CASE_BY_ID["W09"], service, memberships, matches, TODAY)
    assert assessment.eligible
    assert assessment.team_id == "JO17-1"
    assert assessment.match_relation == "no_match_that_day"


def test_previous_season_snapshot_value_is_used_before_december():
    services, matches, cases, memberships = _context()
    service = next(s for s in services if s.service_id == "BAR-WO-1")
    assessments = tuple(assess_candidate(c, service, memberships, matches, TODAY) for c in cases)
    # W03/W04 have no duty registration in their original cases, so this assertion
    # uses W07: the prioritizer must carry the supplied historical snapshot value.
    rows = prioritize_candidates(
        tuple(a for a in assessments if a.person_id == "W07P"),
        (W_CASE_BY_ID["W07"],),
        service.starts_at.date(),
        previous_season_backlog={"W07P": 2},
    )
    assert rows[0].previous_season_backlog == 2
    assert rows[0].previous_season_considered is True
