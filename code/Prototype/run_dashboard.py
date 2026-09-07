from dataclasses import replace
from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.duty import evaluate_duty_foundation
from dvk.model import Person, SportlinkDutyRegistration
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _wedstrijdtekst(row) -> str:
    if row.match_starts_at is None:
        return "geen wedstrijd op deze dag"
    soort = "thuiswedstrijd" if row.home_away == "home" else "uitwedstrijd"
    return f"{soort} om {row.match_starts_at:%H:%M}"


def _met_naam(case, name: str):
    return replace(case, person=replace(case.person, name=name))


def main() -> None:
    jan = _met_naam(W_CASE_BY_ID["W08"], "Jan Smit")
    piet = _met_naam(W_CASE_BY_ID["W07"], "Piet de Jong")
    away_base = _met_naam(W_CASE_BY_ID["W10"], "Kees van Dijk")
    kees = replace(
        away_base,
        case_id="DASH-AWAY",
        description="Dashboardpersoon met uitwedstrijd en complete urenpositie",
        sportlink_duty=SportlinkDutyRegistration(
            "W10P", required_hours=10, correction_hours=0, completed_hours=2, scheduled_hours=2
        ),
    )
    cases = (jan, piet, kees)
    services = (
        DutyService("BAR-OCHTEND", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 2),
        DutyService("COMM-MIDDAG", "gastheer/gastvrouw commissiekamer", datetime(2026, 9, 12, 14), datetime(2026, 9, 12, 17), "commissiekamer", 1),
        DutyService("BAR-AVOND", "bardienst", datetime(2026, 9, 12, 17), datetime(2026, 9, 12, 20), "kantine", 1),
    )
    teams = (
        TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),
        TeamMembership("W07P", "Senioren 7", date(2026, 7, 1), date(2027, 6, 30)),
        TeamMembership("W10P", "Senioren 10", date(2026, 7, 1), date(2027, 6, 30)),
    )
    matches = (
        Match("M-8", "Senioren 8", datetime(2026, 9, 12, 14, 30), "home"),
        Match("M-7", "Senioren 7", datetime(2026, 9, 12, 12, 30), "home"),
        Match("M-10", "Senioren 10", datetime(2026, 9, 12, 18, 0), "away"),
    )
    decisions = tuple(evaluate_duty_foundation(case, TODAY) for case in cases)
    assessments = tuple(
        assess_candidate(case, service, teams, matches, TODAY)
        for service in services for case in cases
    )
    priorities = tuple(
        priority
        for service in services
        for priority in prioritize_candidates(
            tuple(a for a in assessments if a.service_id == service.service_id), cases, service.starts_at.date()
        )
    )
    dashboard = build_dashboard(cases, decisions, services, teams, assessments, priorities,
                                {"BAR-OCHTEND": 1}, matches)

    print("DVK Ledendiensten — werkoverzicht Vrijwilligerscommissie")
    print("=" * 66)
    print("\n1. Leden met nog openstaande Ledendienstplicht")
    for row in dashboard.duty_rows:
        nadruk = " met veel openstaande uren" if row.remaining_hours >= 7 else ""
        print(f"   {row.name} uit {row.team_id}{nadruk}: nog {row.remaining_hours} uur in te plannen.")
        print(f"      Verplicht {row.required_hours}; uitgevoerd {row.completed_hours}; al ingepland {row.scheduled_hours} uur.")

    print("\n2. Ledendiensten waarvoor nog bezetting nodig is")
    for row in dashboard.service_rows:
        plek = "plek" if row.remaining_staff == 1 else "plekken"
        print(f"   {row.service_type.capitalize()} — {row.starts_at:%d-%m-%Y} {row.starts_at:%H:%M}-{row.ends_at:%H:%M}: nog {row.remaining_staff} {plek} te bezetten.")

    print("\n3. Advies per dienst")
    for service in dashboard.service_rows:
        print(f"\n   {service.service_type.capitalize()} {service.starts_at:%H:%M}-{service.ends_at:%H:%M}")
        advised = [r for r in dashboard.candidate_rows if r.service_id == service.service_id]
        for row in advised:
            label = "Gedeelde eerste keuze" if row.shared_first_choice else "Voorgesteld"
            print(f"   {label}: {row.name} uit {row.team_id} — nog {row.remaining_hours} uur; {_wedstrijdtekst(row)}.")
        others = [r for r in dashboard.not_proposed_rows if r.service_id == service.service_id]
        if others:
            print("   Niet voorgesteld / mogelijke alternatieven:")
            for row in others:
                print(f"      {row.name} uit {row.team_id} — {_wedstrijdtekst(row)} — {row.reason}.")


if __name__ == "__main__":
    main()
