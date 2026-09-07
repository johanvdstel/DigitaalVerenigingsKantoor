from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.duty import evaluate_duty_foundation
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _wedstrijdtekst(row) -> str:
    if row.match_starts_at is None:
        return "geen relevante wedstrijd op deze dag"
    soort = "thuiswedstrijd" if row.home_away == "home" else "uitwedstrijd"
    return f"{soort} om {row.match_starts_at:%H:%M}"


def main() -> None:
    cases = (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"])
    service = DutyService("S-DASH", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 2)
    teams = (
        TeamMembership("W08P", "SEN-8", date(2026, 7, 1), date(2027, 6, 30)),
        TeamMembership("W07P", "SEN-7", date(2026, 7, 1), date(2027, 6, 30)),
    )
    matches = (
        Match("M-8", "SEN-8", datetime(2026, 9, 12, 14, 30), "home"),
        Match("M-7", "SEN-7", datetime(2026, 9, 12, 14, 30), "home"),
    )
    decisions = tuple(evaluate_duty_foundation(case, TODAY) for case in cases)
    assessments = tuple(assess_candidate(case, service, teams, matches, TODAY) for case in cases)
    priorities = prioritize_candidates(assessments, cases, date(2026, 9, 12))
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, {"S-DASH": 1}, matches)

    print("DVK Ledendiensten — werkoverzicht Vrijwilligerscommissie")
    print("=" * 62)

    print("\n1. Leden met nog openstaande Ledendiensturen")
    print("   Dit zijn taakplichtige leden waarvoor nog uren moeten worden ingepland.")
    for row in dashboard.duty_rows:
        print(f"\n   {row.name} — team {row.team_id}")
        print(f"   Nog in te plannen: {row.remaining_hours} uur")
        print(
            f"   Toelichting: verplicht {row.required_hours} uur; "
            f"uitgevoerd {row.completed_hours} uur; al ingepland {row.scheduled_hours} uur"
            + (f"; correctie {row.correction_hours} uur" if row.correction_hours else "")
            + "."
        )
        if row.sportlink_mismatch:
            print("   Let op: de Sportlink-registratie wijkt af van de DVK-afleiding.")

    print("\n2. Ledendiensten waarvoor nog iemand nodig is")
    for row in dashboard.service_rows:
        plek = "plek" if row.remaining_staff == 1 else "plekken"
        print(
            f"   {row.service_type.capitalize()} op {row.starts_at:%d-%m-%Y} "
            f"van {row.starts_at:%H:%M} tot {row.ends_at:%H:%M} — "
            f"nog {row.remaining_staff} {plek} te bezetten."
        )

    print("\n3. Geadviseerde kandidaat per openstaande dienst")
    for row in dashboard.candidate_rows:
        label = "Gedeelde eerste keuze" if row.shared_first_choice else "Advies"
        print(f"\n   {label}: {row.name} — team {row.team_id}")
        print(f"   Nog {row.remaining_hours} Ledendiensturen in te plannen; {_wedstrijdtekst(row)}.")
        print("   Waarom dit advies: " + "; ".join(row.explanation) + ".")


if __name__ == "__main__":
    main()
