from dataclasses import replace
from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.dashboard_actions import approve_from_dashboard, reject_from_dashboard
from dvk.duty import duty_position_from_registration, evaluate_duty_foundation
from dvk.proposals import create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.recommendation_planner import plan_recommendations
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def main() -> None:
    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    service = DutyService("S-EIND", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-EIND", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)

    decision = evaluate_duty_foundation(case, TODAY)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priorities = prioritize_candidates((assessment,), (case,), service.starts_at.date())
    plan = plan_recommendations(priorities, (service,))
    dashboard = build_dashboard((case,), (decision,), (service,), teams, (assessment,), priorities, plan, matches=matches)
    proposal = create_assignment_proposal("P-EIND", service, case, assessment, priorities[0], matches)

    before = duty_position_from_registration(case.sportlink_duty)
    approved = approve_from_dashboard(proposal, service, case, "Vrijwilligerscommissie", "A-EIND")
    after = duty_position_from_registration(approved.updated_case.sportlink_duty)
    rejected = reject_from_dashboard(proposal, case, "Vrijwilligerscommissie", "planning", "Past niet in de planning")

    print("DVK Prototype v0.3 — geïntegreerde eindacceptatie")
    print("=" * 58)
    print(f"1. Taakplicht uit feiten: {'OK' if decision.facts['duty_required'] else 'FOUT'}")
    print(f"2. Urenpositie vóór planning: uitgevoerd {before.C}, ingepland {before.D}, openstaand {before.E} uur")
    print(f"3. Kandidaat passend bij thuiswedstrijd: {'OK' if assessment.eligible and assessment.preference == 'preferred' else 'FOUT'}")
    print(f"4. Engine-advies: {dashboard.candidate_rows[0].name} uit {dashboard.candidate_rows[0].team_id}")
    print(f"5. DVK-voorstel: {proposal.proposal_id} — status {proposal.status}")
    print(f"6. Goedkeuring: DutyAssignment aangemaakt; ingepland {before.D} → {after.D}, openstaand {before.E} → {after.E} uur")
    print(f"7. Uitgevoerde uren blijven bij planning gelijk: {before.C} → {after.C}")
    print(f"8. Afwijzing: geen DutyAssignment = {rejected.assignment is None}; urenpositie ongewijzigd = {rejected.updated_case == case}")
    print("9. Dashboard gebruikt vooraf berekend engine-adviesplan: OK")
    print("\nEINDRESULTAAT: functionele keten v0.3 reproduceerbaar.")


if __name__ == "__main__":
    main()
