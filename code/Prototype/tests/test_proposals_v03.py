from datetime import date, datetime

import pytest

from dvk.candidate_selection import assess_candidate
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _proposal_fixture():
    case = W_CASE_BY_ID["W08"]
    service = DutyService("S-PROP", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-PROP", "SEN-8", datetime(2026, 9, 12, 14, 30), "home"),)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal("P-001", service, case, assessment, priority, matches)
    return case, service, proposal


def test_step7_assignment_proposal_contains_complete_explainable_context():
    case, service, proposal = _proposal_fixture()
    assert proposal.status == "proposed"
    assert proposal.service_id == service.service_id
    assert proposal.person_id == case.person.person_id
    assert (proposal.A, proposal.B, proposal.C, proposal.D, proposal.E) == (10, 0, 1, 1, 8)
    assert proposal.team_id == "SEN-8"
    assert proposal.home_away == "home"
    assert proposal.match_starts_at == datetime(2026, 9, 12, 14, 30)
    assert proposal.suitability == "suitable"
    assert proposal.priority_rank == 1
    assert proposal.applied_priority_rules


def test_step7_approval_records_human_decision_but_does_not_change_duty_position():
    case, _, proposal = _proposal_fixture()
    before = case.sportlink_duty
    decision = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    assert decision.decision == "approved"
    assert decision.proposal_id == proposal.proposal_id
    assert case.sportlink_duty == before
    assert proposal.status == "proposed"


def test_step7_rejection_requires_category_and_reason():
    _, _, proposal = _proposal_fixture()
    with pytest.raises(ValueError, match="reason category"):
        assess_proposal(proposal, "rejected", "Vrijwilligerscommissie", reason="Kan deze datum niet")
    with pytest.raises(ValueError, match="rejection reason"):
        assess_proposal(proposal, "rejected", "Vrijwilligerscommissie", "personal_circumstance")


def test_step7_rejection_records_reason_without_removing_obligation():
    case, _, proposal = _proposal_fixture()
    before = case.sportlink_duty
    decision = assess_proposal(
        proposal, "rejected", "Vrijwilligerscommissie",
        "personal_circumstance", "Kan deze datum niet",
    )
    assert decision.decision == "rejected"
    assert decision.reason_category == "personal_circumstance"
    assert decision.reason == "Kan deze datum niet"
    assert case.sportlink_duty == before
    assert proposal.E == 8
