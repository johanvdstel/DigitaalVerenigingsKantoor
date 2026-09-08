from dataclasses import replace
from datetime import date, datetime

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


def main() -> None:
    case, service, proposal = _fixture()
    before = duty_position_from_registration(case.sportlink_duty)
    print("DVK v0.3 — Step 9: beslissen vanuit het dashboard")
    print("=" * 58)
    print(f"Advies: {case.person.name} uit Senioren 8 voor {service.service_type} {service.starts_at:%d-%m-%Y %H:%M}-{service.ends_at:%H:%M}.")
    print(f"Huidige urenpositie: {before.D} uur ingepland, nog {before.E} uur in te plannen.")
    print("Beschikbare acties: [Goedkeuren] [Afwijzen]")

    approved = approve_from_dashboard(proposal, service, case, "Vrijwilligerscommissie", "A-DASH")
    after = duty_position_from_registration(approved.updated_case.sportlink_duty)
    print("\nNa keuze Goedkeuren:")
    print(f"{approved.message} Ingepland {before.D} → {after.D} uur; nog in te plannen {before.E} → {after.E} uur.")

    rejected = reject_from_dashboard(
        proposal, case, "Vrijwilligerscommissie", "planning", "Lid is deze dag al elders ingezet"
    )
    unchanged = duty_position_from_registration(rejected.updated_case.sportlink_duty)
    print("\nNa keuze Afwijzen:")
    print("Redencategorie: planning")
    print(f"Reden: {rejected.decision.reason}.")
    print(f"{rejected.message} Nog in te plannen: {unchanged.E} uur.")
    print("Een afwijzing zonder reden wordt niet geaccepteerd.")


if __name__ == "__main__":
    main()
