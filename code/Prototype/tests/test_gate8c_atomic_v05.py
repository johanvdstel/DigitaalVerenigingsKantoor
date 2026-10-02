from datetime import date, datetime

import pytest

from dvk.application_services import ProposalDecisionApplicationService
from dvk.candidate_selection import assess_candidate
from dvk.persistence import SQLiteDatabase
from dvk.prioritization import prioritize_candidates
from dvk.proposals import create_assignment_proposal
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, TeamMembership


def _proposal(proposal_id, case_id="W08"):
    case = W_CASE_BY_ID[case_id]
    service = DutyService("BAR-G8C", "bardienst", datetime(2026, 9, 19, 9), datetime(2026, 9, 19, 13), "Clubhuis", 1)
    teams = (TeamMembership(case.person.person_id, "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),)
    assessment = assess_candidate(case, service, teams, (), TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    return case, service, create_assignment_proposal(proposal_id, service, case, assessment, priority)


def _identity():
    return Identity("planner-1", "Planner", frozenset({Permission.DECIDE_PROPOSAL}))


def test_batch_selection_above_remaining_capacity_is_rejected_before_persistence(tmp_path):
    case1, service, proposal1 = _proposal("P-G8C-1", "W08")
    case2, _, proposal2 = _proposal("P-G8C-2", "W07")
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    with db.unit_of_work() as uow:
        app = ProposalDecisionApplicationService(_identity(), uow=uow)
        with pytest.raises(ValueError, match="remaining service capacity"):
            app.approve_many(((proposal1, case1, "A-G8C-1"), (proposal2, case2, "A-G8C-2")), service, StaffingNeed(service.service_id, 1, 1, 0, 1, 1))
    with db.unit_of_work() as uow:
        assert uow.proposals.get("P-G8C-1") is None
        assert uow.proposals.get("P-G8C-2") is None
        assert uow.assignments.get("A-G8C-1") is None
        assert uow.assignments.get("A-G8C-2") is None


def test_batch_persistence_rolls_back_when_second_assignment_fails(tmp_path):
    case1, service, proposal1 = _proposal("P-G8C-R1", "W08")
    case2, _, proposal2 = _proposal("P-G8C-R2", "W07")
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    with pytest.raises(Exception):
        with db.unit_of_work() as uow:
            ProposalDecisionApplicationService(_identity(), uow=uow).approve_many(((proposal1, case1, "A-DUP"), (proposal2, case2, "A-DUP")), service, StaffingNeed(service.service_id, 1, 2, 0, 1, 2))
    with db.unit_of_work() as uow:
        assert uow.proposals.get("P-G8C-R1") is None
        assert uow.proposals.get("P-G8C-R2") is None
        assert uow.assignments.get("A-DUP") is None


def test_v08_exception_is_durable_without_assignment(tmp_path):
    case, _, proposal = _proposal("P-G8C-EX")
    path = tmp_path / "dvk.sqlite"
    db = SQLiteDatabase(path)
    with db.unit_of_work() as uow:
        result = ProposalDecisionApplicationService(_identity(), uow=uow).reject(proposal, case, reason_category="personal_circumstance", reason="Kan deze dienst niet")
        assert result.assignment is None
        assert result.decision.decided_at is not None
    reopened = SQLiteDatabase(path)
    with reopened.unit_of_work() as uow:
        stored_proposal = uow.proposals.get("P-G8C-EX")
        decision = uow.decisions.get("P-G8C-EX")
        assert stored_proposal is not None
        assert decision is not None
        assert decision.decision == "rejected"
        assert decision.reason_category == "personal_circumstance"
        assert decision.reason == "Kan deze dienst niet"
        assert decision.decided_at is not None
        count = uow._connection.execute("SELECT COUNT(*) FROM duty_assignments WHERE proposal_id=?", ("P-G8C-EX",)).fetchone()[0]
        assert count == 0
