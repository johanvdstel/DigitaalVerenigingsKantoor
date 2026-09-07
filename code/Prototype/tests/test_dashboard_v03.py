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
    return cases, service, teams, matches, decisions, assessments, priorities


def test_i02_dashboard_lists_only_members_with_open_duty_and_meaningful_hours():
    cases, service, teams, matches, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, matches=matches)
    rows = {row.person_id: row for row in dashboard.duty_rows}
    assert rows["W08P"].name == "Senior Grote E"
    assert rows["W08P"].remaining_hours == 8
    assert rows["W08P"].required_hours == 10
    assert rows["W08P"].completed_hours == 1
    assert rows["W08P"].scheduled_hours == 1


def test_i02_dashboard_lists_only_services_that_still_need_people():
    cases, service, teams, matches, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, {"S-DASH": 1}, matches)
    assert dashboard.service_rows[0].remaining_staff == 1
    full = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, {"S-DASH": 2}, matches)
    assert full.service_rows == ()


def test_i02_dashboard_recommends_one_best_candidate_with_name_and_match_time():
    cases, service, teams, matches, decisions, assessments, priorities = _dashboard_fixture()
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, matches=matches)
    assert len(dashboard.candidate_rows) == 1
    row = dashboard.candidate_rows[0]
    assert row.person_id == "W08P"
    assert row.name == "Senior Grote E"
    assert row.remaining_hours == 8
    assert row.team_id == "SEN-8"
    assert row.home_away == "home"
    assert row.match_starts_at == datetime(2026, 9, 12, 14, 30)
    assert row.shared_first_choice is False


def test_i02_dashboard_shows_multiple_candidates_only_for_equal_first_choice():
    cases, service, teams, matches, decisions, assessments, priorities = _dashboard_fixture()
    equal = priorities[0].__class__(
        "W07P", "S-DASH", 2, priorities[0].remaining_hours,
        priorities[0].previous_season_backlog, priorities[0].previous_season_considered,
        priorities[0].match_preference, priorities[0].explanation,
    )
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, (priorities[0], equal), matches=matches)
    assert {row.person_id for row in dashboard.candidate_rows} == {"W08P", "W07P"}
    assert all(row.shared_first_choice for row in dashboard.candidate_rows)


def test_i02_dashboard_does_not_propose_same_person_twice_on_same_day_if_alternative_exists():
    cases, service, teams, matches, decisions, assessments, priorities = _dashboard_fixture()
    later = DutyService("S-LATER", "bardienst", datetime(2026, 9, 12, 17), datetime(2026, 9, 12, 20), "kantine", 1)
    later_assessments = tuple(assess_candidate(case, later, teams, matches, TODAY) for case in cases)
    later_priorities = prioritize_candidates(later_assessments, cases, date(2026, 9, 12))
    dashboard = build_dashboard(
        cases, decisions, (service, later), teams,
        assessments + later_assessments, priorities + later_priorities, matches=matches,
    )
    proposed = {row.service_id: row.person_id for row in dashboard.candidate_rows}
    assert proposed["S-DASH"] == "W08P"
    assert proposed["S-LATER"] == "W07P"
    jan_later = next(row for row in dashboard.not_proposed_rows if row.service_id == "S-LATER" and row.person_id == "W08P")
    assert "al voorgesteld voor een andere Ledendienst op deze dag" in jan_later.reason
