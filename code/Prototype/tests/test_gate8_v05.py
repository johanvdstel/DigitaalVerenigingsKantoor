from datetime import date, datetime

import pytest

from dvk.assignments import create_duty_assignment
from dvk.candidate_selection import assess_candidate
from dvk.proposal_planning import plan_proposals
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.run_context import EngineRun, EngineRunStatus
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, TeamMembership


def _engine_run():
    return EngineRun(
        engine_run_id="RUN-G8",
        started_at=datetime(2026, 9, 16, 8),
        initiated_by="planner-1",
        period_start=date(2026, 9, 16),
        period_end=date(2026, 9, 16),
        status=EngineRunStatus.COMPLETED,
        snapshot_ids=("SNAP-LEDEN-G8", "SNAP-VRIJW-G8"),
        source_fetch_ids=("FETCH-WED-G8", "FETCH-DIENST-G8"),
        policy_version="policy-g8",
        config_version="config-g8",
        engine_version="software-g8",
        completed_at=datetime(2026, 9, 16, 8, 1),
    )


def _proposal(proposal_id: str = "P-G8", *, with_run_context: bool = False):
    case = W_CASE_BY_ID["W08"]
    service = DutyService(
        "BAR-WO-G8", "bardienst",
        datetime(2026, 9, 16, 19), datetime(2026, 9, 16, 22),
        "Clubhuis", 1,
    )
    teams = (TeamMembership(case.person.person_id, "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),)
    assessment = assess_candidate(case, service, teams, (), TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    return case, service, create_assignment_proposal(
        proposal_id, service, case, assessment, priority, (),
        engine_run=_engine_run() if with_run_context else None,
    )


def test_v06_service_without_matches_still_yields_candidate_proposal():
    _, service, proposal = _proposal()
    need = StaffingNeed(service.service_id, 1, 2, 0, 1, 2)
    planned = plan_proposals((proposal,), need)
    assert len(planned) == 1
    assert planned[0].proposal.person_id == proposal.person_id
    assert planned[0].staffing_purpose == "minimum_coverage"
    assert proposal.match_starts_at is None


def test_v06_distinguishes_minimum_coverage_from_optional_capacity():
    _, service, proposal1 = _proposal("P-G8-1")
    _, _, proposal2 = _proposal("P-G8-2")
    proposal2 = proposal2.__class__(**{**proposal2.__dict__, "priority_rank": 2})
    need = StaffingNeed(service.service_id, 1, 2, 0, 1, 2)
    planned = plan_proposals((proposal2, proposal1), need)
    assert [item.staffing_purpose for item in planned] == [
        "minimum_coverage", "optional_capacity"
    ]


def test_v06_when_minimum_is_met_candidate_is_optional_capacity():
    _, service, proposal = _proposal()
    need = StaffingNeed(service.service_id, 1, 2, 1, 0, 1)
    planned = plan_proposals((proposal,), need)
    assert len(planned) == 1
    assert planned[0].staffing_purpose == "optional_capacity"


def test_v07_approval_creates_decision_and_assignment():
    case, service, proposal = _proposal()
    decision = assess_proposal(proposal, "approved", "planner-1")
    assignment = create_duty_assignment("A-G8", proposal, decision, service)
    assert decision.decision == "approved"
    assert decision.decided_by == "planner-1"
    assert assignment is not None
    assert assignment.proposal_id == proposal.proposal_id
    assert assignment.approved_by == "planner-1"
    assert case.sportlink_duty.scheduled_hours == 1


def test_v07_approval_retains_engine_snapshot_policy_and_time_context():
    _, service, proposal = _proposal(with_run_context=True)
    decided_at = datetime(2026, 9, 16, 9, 30)
    decision = assess_proposal(
        proposal, "approved", "planner-1", decided_at=decided_at
    )
    assignment = create_duty_assignment("A-G8-CONTEXT", proposal, decision, service)

    assert proposal.engine_run_id == "RUN-G8"
    assert proposal.snapshot_ids == ("SNAP-LEDEN-G8", "SNAP-VRIJW-G8")
    assert proposal.policy_version == "policy-g8"
    assert proposal.config_version == "config-g8"
    assert proposal.software_version == "software-g8"
    assert decision.decided_at == decided_at
    assert assignment is not None
    assert assignment.engine_run_id == proposal.engine_run_id
    assert assignment.snapshot_ids == proposal.snapshot_ids
    assert assignment.policy_version == proposal.policy_version
    assert assignment.config_version == proposal.config_version
    assert assignment.software_version == proposal.software_version
    assert assignment.decided_at == decided_at


def test_v08_rejection_is_auditable_and_creates_no_assignment():
    _, service, proposal = _proposal()
    decision = assess_proposal(
        proposal, "rejected", "planner-1",
        "personal_circumstance", "Kan deze avond niet",
    )
    assignment = create_duty_assignment("A-NOT-CREATED", proposal, decision, service)
    assert decision.reason_category == "personal_circumstance"
    assert decision.reason == "Kan deze avond niet"
    assert assignment is None


def test_v08_rejection_requires_reason():
    _, _, proposal = _proposal()
    with pytest.raises(ValueError, match="rejection reason"):
        assess_proposal(
            proposal, "rejected", "planner-1", "personal_circumstance", ""
        )
