from datetime import date, datetime

from dvk.candidate_selection import assess_candidate, select_candidates
from dvk.duty import (
    derive_duty_qualification,
    derive_executor_category,
    evaluate_duty_foundation,
    expected_required_hours,
)
from dvk.workstream_cases import TODAY, W_CASE_BY_ID, W_CASES
from dvk.workstream_model import DutyService, Match, TeamMembership


def test_v03_workstream_case_set_remains_separate_from_c_masterset():
    assert [case.case_id for case in W_CASES] == ["W01", "W02", "W03", "W04", "W05", "W06", "W07", "W10", "W13"]


def test_w01_duty_is_derived_and_policy_norm_applied():
    case = W_CASE_BY_ID["W01"]
    qualification = derive_duty_qualification(case, TODAY)
    assert qualification.duty_required is True
    assert qualification.reason == "playing_member"
    assert qualification.administrative_subject_id == "W01P"
    assert expected_required_hours(qualification) == 10

    decision = evaluate_duty_foundation(case, TODAY)
    assert decision.status == "ok"
    assert decision.facts["expected_required_hours"] == 10
    assert decision.facts["sportlink_comparison_performed"] is False
    assert not decision.signals


def test_w02_missing_sportlink_required_hours_is_signalled_not_corrected():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W02"], TODAY)
    assert decision.status == "attention"
    assert decision.facts["expected_required_hours"] == 10
    assert decision.facts["sportlink_required_hours"] is None
    assert decision.facts["sportlink_comparison_performed"] is True
    assert {signal.code for signal in decision.signals} == {"sportlink_required_hours_mismatch"}


def test_w03_home_match_same_day_is_preferred_candidate_context():
    service = DutyService("S-W03", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W03P", "SEN-3", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-W03", "SEN-3", datetime(2026, 9, 12, 14, 30), "home"),)

    assessment = assess_candidate(W_CASE_BY_ID["W03"], service, teams, matches, TODAY)
    assert assessment.eligible is True
    assert assessment.match_relation == "home_match_same_day"
    assert assessment.preference == "preferred"
    assert assessment.home_away == "home"


def test_w04_minor_keeps_child_as_subject_and_parent_guardian_as_executor_category():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W04"], TODAY)
    assert decision.facts["duty_required"] is True
    assert decision.facts["administrative_subject"] == "W04P"
    assert decision.facts["executor_category"] == "parent_guardian"


def test_w05_fifteen_year_old_uses_parent_guardian_category():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W05"], TODAY)
    assert decision.facts["administrative_subject"] == "W05P"
    assert decision.facts["executor_category"] == "parent_guardian"


def test_w06_seventeen_year_old_switches_category_only_at_eighteen():
    case = W_CASE_BY_ID["W06"]
    assert derive_executor_category(case, date(2026, 9, 30)) == "parent_guardian"
    assert derive_executor_category(case, date(2026, 10, 1)) == "member"
    assert derive_duty_qualification(case, date(2026, 10, 1)).administrative_subject_id == "W06P"


def test_w07_duty_position_uses_a_minus_b_minus_c_minus_d():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W07"], TODAY)
    assert decision.status == "ok"
    assert decision.facts["duty_position"] == {"A": 10, "B": 0, "C": 4, "D": 3, "E": 3}


def test_w10_away_match_same_day_is_eligible_but_avoided():
    service = DutyService("S-W10", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W10P", "SEN-10", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-W10", "SEN-10", datetime(2026, 9, 12, 14, 30), "away"),)

    assessment = assess_candidate(W_CASE_BY_ID["W10"], service, teams, matches, TODAY)
    assert assessment.eligible is True
    assert assessment.match_relation == "away_match_same_day"
    assert assessment.preference == "avoid"
    assert assessment.home_away == "away"


def test_step4_selection_filters_non_duty_member_without_ranking_candidates():
    service = DutyService("S-SEL", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    selected = select_candidates((W_CASE_BY_ID["W03"], W_CASE_BY_ID["W13"]), service, (), (), TODAY)
    assert [candidate.person_id for candidate in selected] == ["W03P"]
    assert selected[0].preference == "neutral"


def test_w13_younger_minor_does_not_create_second_family_obligation():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W13"], TODAY)
    assert decision.facts["duty_required"] is False
    assert decision.facts["qualification_reason"] == "family_duty:W13E"
    assert decision.facts["expected_required_hours"] == 0
    assert decision.facts["administrative_subject"] == "W13Y"
