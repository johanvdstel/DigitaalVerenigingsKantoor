from dataclasses import replace
from datetime import date, datetime

from dvk.assignments import apply_assignment_to_case, create_duty_assignment
from dvk.candidate_selection import assess_candidate
from dvk.duty import duty_position_from_registration
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _fixture():
    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    service = DutyService("S-W11", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-W11", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal("P-W11", service, case, assessment, priority, matches)
    return case, service, proposal


def test_w11_approved_proposal_creates_assignment_and_changes_d_and_e_only():
    case, service, proposal = _fixture()
    decision = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    assignment = create_duty_assignment("A-W11", proposal, decision, service)
    assert assignment is not None
    assert assignment.scheduled_hours == 3

    before = duty_position_from_registration(case.sportlink_duty)
    updated_case = apply_assignment_to_case(case, assignment)
    after = duty_position_from_registration(updated_case.sportlink_duty)

    assert (before.A, before.B, before.C, before.D, before.E) == (10, 0, 2, 1, 7)
    assert (after.A, after.B, after.C, after.D, after.E) == (10, 0, 2, 4, 4)
    assert after.C == before.C


def test_w12_rejected_proposal_creates_no_assignment_and_changes_nothing():
    case, service, proposal = _fixture()
    decision = assess_proposal(
        proposal, "rejected", "Vrijwilligerscommissie",
        "personal_circumstance", "Kan deze datum niet",
    )
    assignment = create_duty_assignment("A-W12", proposal, decision, service)
    assert assignment is None
    assert duty_position_from_registration(case.sportlink_duty).E == 7


def test_step8_assignment_requires_decision_for_same_proposal():
    _, service, proposal = _fixture()
    decision = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    wrong = replace(decision, proposal_id="P-OTHER")
    try:
        create_duty_assignment("A-X", proposal, wrong, service)
    except ValueError as exc:
        assert "does not belong" in str(exc)
    else:
        raise AssertionError("mismatched human decision should fail")
