from dataclasses import replace
from datetime import date, datetime

import pytest

from dvk.candidate_selection import assess_candidate
from dvk.dashboard_actions import approve_from_dashboard, reject_from_dashboard
from dvk.duty import duty_position_from_registration
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _fixture():
    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    service = DutyService("S-DASH-ACTION", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-DASH-ACTION", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal("P-DASH", service, case, assessment, priority, matches)
    return case, service, proposal


def test_step9_dashboard_approval_uses_domain_flow_and_updates_hours():
    case, service, proposal = _fixture()
    result = approve_from_dashboard(proposal, service, case, "Vrijwilligerscommissie", "A-DASH")
    before = duty_position_from_registration(case.sportlink_duty)
    after = duty_position_from_registration(result.updated_case.sportlink_duty)
    assert result.decision.decision == "approved"
    assert result.assignment is not None
    assert (before.D, before.E) == (1, 8)
    assert (after.D, after.E) == (4, 5)
    assert after.C == before.C == 1


def test_step9_dashboard_rejection_requires_reason_and_keeps_service_unassigned():
    case, _, proposal = _fixture()
    result = reject_from_dashboard(
        proposal, case, "Vrijwilligerscommissie", "planning", "Lid is deze dag al elders ingezet"
    )
    assert result.decision.decision == "rejected"
    assert result.assignment is None
    assert result.updated_case == case
    assert duty_position_from_registration(result.updated_case.sportlink_duty).E == 8


def test_step9_dashboard_rejection_without_reason_is_blocked_by_domain_rule():
    case, _, proposal = _fixture()
    with pytest.raises(ValueError, match="rejection reason"):
        reject_from_dashboard(proposal, case, "Vrijwilligerscommissie", "planning", "")
