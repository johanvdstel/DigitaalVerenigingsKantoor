from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.dashboard import build_dashboard
from dvk.duty import evaluate_duty_foundation
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


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
    dashboard = build_dashboard(cases, decisions, (service,), teams, assessments, priorities, {"S-DASH": 1})

    print("DVK Prototype v0.3 - Eerste dashboard (I02)")
    print("=" * 52)
    print("\nTaakplichtigen en urenpositie")
    for row in dashboard.duty_rows:
        print(
            f"  {row.name} [{row.team_id}]: taakplicht={row.duty_required} "
            f"A/B/C/D/E={row.A}/{row.B}/{row.C}/{row.D}/{row.E} "
            f"Sportlink-afwijking={row.sportlink_mismatch}"
        )

    print("\nOpenstaande diensten")
    for row in dashboard.service_rows:
        print(
            f"  {row.service_id} {row.service_type} {row.starts_at:%Y-%m-%d %H:%M}-{row.ends_at:%H:%M}: "
            f"bezetting nodig={row.required_staff}, resterend={row.remaining_staff}"
        )

    print("\nKandidaatselectie per dienst")
    for row in dashboard.candidate_rows:
        print(
            f"  {row.rank}. {row.person_id} [{row.team_id}]: E={row.remaining_hours}, "
            f"uitvoerder={row.executor_category}, wedstrijd={row.home_away}, voorkeur={row.preference}"
        )
        print("     verklaring: " + "; ".join(row.explanation))


if __name__ == "__main__":
    main()
