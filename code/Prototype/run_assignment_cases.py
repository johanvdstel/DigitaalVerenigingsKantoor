from dataclasses import replace
from datetime import date, datetime

from dvk.assignments import apply_assignment_to_case, create_duty_assignment
from dvk.candidate_selection import assess_candidate
from dvk.duty import duty_position_from_registration
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def main() -> None:
    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    service = DutyService("S-W11", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-W11", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal("P-W11", service, case, assessment, priority, matches)

    print("DVK v0.3 — Step 8: daadwerkelijke Ledendienstindeling")
    print("=" * 62)
    before = duty_position_from_registration(case.sportlink_duty)
    print(f"Uitgangspositie {case.person.name}: uitgevoerd {before.C} uur, ingepland {before.D} uur, nog {before.E} uur in te plannen.")

    approved = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    assignment = create_duty_assignment("A-W11", proposal, approved, service)
    updated = apply_assignment_to_case(case, assignment)
    after = duty_position_from_registration(updated.sportlink_duty)
    print("\nW11 — voorstel goedgekeurd")
    print(f"Indeling aangemaakt: {case.person.name} — {service.service_type} {service.starts_at:%d-%m-%Y %H:%M}-{service.ends_at:%H:%M}.")
    print(f"Ingeplande uren: {before.D} → {after.D}; nog in te plannen: {before.E} → {after.E}; uitgevoerd blijft {after.C} uur.")

    rejected = assess_proposal(
        proposal, "rejected", "Vrijwilligerscommissie",
        "personal_circumstance", "Kan deze datum niet",
    )
    rejected_assignment = create_duty_assignment("A-W12", proposal, rejected, service)
    unchanged = duty_position_from_registration(case.sportlink_duty)
    print("\nW12 — voorstel afgewezen")
    print(f"Reden: {rejected.reason}.")
    print(f"Geen indeling aangemaakt: {rejected_assignment is None}.")
    print(f"Urenpositie blijft ongewijzigd: ingepland {unchanged.D} uur, nog {unchanged.E} uur in te plannen.")
    print("De dienst blijft open; DVK kan een volgende kandidaat voorstellen.")


if __name__ == "__main__":
    main()
