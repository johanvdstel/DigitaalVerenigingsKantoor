from dvk.duty import derive_duty_qualification, evaluate_duty_foundation, expected_required_hours
from dvk.workstream_cases import TODAY, W_CASE_BY_ID, W_CASES


def test_v03_step1_case_set_is_separate_from_c_masterset():
    assert [case.case_id for case in W_CASES] == ["W01", "W02", "W07"]


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


def test_w07_duty_position_uses_a_minus_b_minus_c_minus_d():
    decision = evaluate_duty_foundation(W_CASE_BY_ID["W07"], TODAY)
    assert decision.status == "ok"
    assert decision.facts["duty_position"] == {"A": 10, "B": 0, "C": 4, "D": 3, "E": 3}
