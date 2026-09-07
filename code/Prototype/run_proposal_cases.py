from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def main() -> None:
    case = W_CASE_BY_ID["W08"]
    service = DutyService("S-PROP", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1)
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match("M-PROP", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),)
    assessment = assess_candidate(case, service, teams, matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal("P-001", service, case, assessment, priority, matches)

    print("DVK v0.3 — Step 7: indelingsvoorstel en menselijke beoordeling")
    print("=" * 68)
    print(f"Voorstel {proposal.proposal_id}: {case.person.name} uit {proposal.team_id}")
    print(f"Dienst: {service.service_type} {service.starts_at:%d-%m-%Y %H:%M}-{service.ends_at:%H:%M}")
    print(f"Openstaand: {proposal.E} uur; uitvoerder: {proposal.executor_category}")
    print(f"Wedstrijd: {proposal.home_away} om {proposal.match_starts_at:%H:%M}")
    print(f"Status: {proposal.status} — dit is nog geen indeling")

    approved = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    print(f"Menselijke beoordeling A: {approved.decision}; D blijft {proposal.D} tot DutyAssignment in Step 8")

    rejected = assess_proposal(
        proposal, "rejected", "Vrijwilligerscommissie",
        "personal_circumstance", "Kan deze datum niet",
    )
    print(f"Menselijke beoordeling B: {rejected.decision}; reden: {rejected.reason}")
    print("Na afwijzing blijft de taakplicht bestaan en kan DVK een alternatief voorstellen.")


if __name__ == "__main__":
    main()
