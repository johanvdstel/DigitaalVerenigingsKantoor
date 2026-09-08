from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.dashboard_actions import approve_from_dashboard, reject_from_dashboard
from dvk.duty import duty_position_from_registration, evaluate_duty_foundation
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.recommendation_planner import plan_recommendations
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _integrated_fixture():
    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    service = DutyService("S-E2E", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-E2E", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)
    decision = evaluate_duty_foundation(case, TODAY)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priorities = prioritize_candidates((assessment,), (case,), service.starts_at.date())
    plan = plan_recommendations(priorities, (service,))
    dashboard = build_dashboard(
        (case,), (decision,), (service,), teams, (assessment,), priorities, plan, matches=matches
    )
    proposal = create_assignment_proposal("P-E2E", service, case, assessment, priorities[0], matches)
    return case, service, decision, assessment, priorities, plan, dashboard, proposal


def test_v03_integrated_approved_chain_is_reproducible_end_to_end():
    case, service, decision, assessment, priorities, plan, dashboard, proposal = _integrated_fixture()
    before = duty_position_from_registration(case.sportlink_duty)

    assert decision.facts["duty_required"] is True
    assert before.E == 7
    assert assessment.eligible is True
    assert assessment.preference == "preferred"
    assert priorities[0].person_id == "W08P"
    assert plan.recommended[0].person_id == "W08P"
    assert dashboard.candidate_rows[0].name == "Jan Smit"
    assert proposal.status == "proposed"

    result = approve_from_dashboard(proposal, service, case, "Vrijwilligerscommissie", "A-E2E")
    after = duty_position_from_registration(result.updated_case.sportlink_duty)
    assert result.decision.decision == "approved"
    assert result.assignment is not None
    assert (before.C, before.D, before.E) == (2, 1, 7)
    assert (after.C, after.D, after.E) == (2, 4, 4)


def test_v03_integrated_rejection_stops_before_assignment_and_preserves_hours():
    case, service, _, _, _, _, _, proposal = _integrated_fixture()
    before = duty_position_from_registration(case.sportlink_duty)
    result = reject_from_dashboard(
        proposal, case, "Vrijwilligerscommissie", "planning", "Past niet in de planning"
    )
    after = duty_position_from_registration(result.updated_case.sportlink_duty)
    assert result.decision.decision == "rejected"
    assert result.assignment is None
    assert after == before


def test_i02_dashboard_source_contains_no_recommendation_selection_policy():
    source = Path(__file__).parents[1] / "dvk" / "dashboard.py"
    text = source.read_text(encoding="utf-8")
    assert "plan_recommendations(" not in text
    assert "proposed_by_day" not in text
    assert "_same_priority" not in text
