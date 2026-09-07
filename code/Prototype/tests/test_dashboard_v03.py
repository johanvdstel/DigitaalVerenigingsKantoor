from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.duty import evaluate_duty_foundation
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _dashboard_fixture():
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"])
    service = DutyService("S-DASH", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 2)
    teams = (
        TeamMembership("W08P", "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),
        TeamMembership("W07P", "SEN-7", date(2026, 7, 1), date(2027, 6, 30)),
    )
    matches = (
        Match("M-8", "SEN-8", datetime(2026, 9, 12, 14, 30), "home"),
        Match("M-7", "SEN-7", datetime(2026, 9, 12, 14, 30), "home"),
    )
    decisions = tuple(evaluate_duty_foundation(case, TODAY) for case in cases)
    assessments = tuple(assess_candidate(case, service, teams, matches, TODAY) for case in cases)
    priorities = prioritize_candidates(assessments, cases, date(2026, 9, 12))
    return cases, service, teams, decisions, assessments, priorities


def test_i02_dashboard_shows_duty_position_and_source_mismatch_state():
    cases, service, teams, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities)
    rows = {row.person_id: row for row in dashboard.duty_rows}
    assert rows["W08P"].E == 8
    assert rows["W07P"].E == 3
    assert rows["W08P"].duty_required is True
    assert rows["W08P"].sportlink_mismatch is False


def test_i02_dashboard_shows_open_service_capacity_without_selection_policy():
    cases, service, teams, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, {"S-DASH": 1})
    row = dashboard.service_rows[0]
    assert row.required_staff == 2
    assert row.remaining_staff == 1


def test_i02_dashboard_preserves_engine_candidate_ranking_and_explanation():
    cases, service, teams, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities)
    assert [row.person_id for row in dashboard.candidate_rows] == ["W08P", "W07P"]
    assert [row.remaining_hours for row in dashboard.candidate_rows] == [8, 3]
    assert dashboard.candidate_rows[0].rank == priorities[0].rank
    assert dashboard.candidate_rows[0].explanation == priorities[0].explanation
    assert dashboard.candidate_rows[0].preference == "preferred"


def test_i02_dashboard_does_not_re_rank_supplied_engine_outcomes():
    cases, service, teams, decisions, assessments, priorities = _dashboard_fixture()
    deliberately_reversed_ranks = (priorities[1], priorities[0])
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, deliberately_reversed_ranks)
    # Dashboard orders only by the supplied rank field; it does not recalculate E or policy.
    assert [row.rank for row in dashboard.candidate_rows] == [1, 2]
    assert [row.person_id for row in dashboard.candidate_rows] == ["W08P", "W07P"]
