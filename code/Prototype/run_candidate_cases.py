from datetime import date, datetime

from dvk.candidate_selection import assess_candidate
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def _show(case_id: str, team_id: str, home_away: str) -> None:
    service = DutyService(
        f"S-{case_id}", "bardienst", datetime(2026, 9, 12, 11), datetime(2026, 9, 12, 14), "kantine", 1
    )
    teams = (TeamMembership(f"{case_id}P", team_id, date(2026, 7, 1), date(2027, 6, 30)),)
    matches = (Match(f"M-{case_id}", team_id, datetime(2026, 9, 12, 14, 30), home_away),)
    result = assess_candidate(W_CASE_BY_ID[case_id], service, teams, matches, TODAY)

    print(f"{case_id} - {W_CASE_BY_ID[case_id].description}")
    print(f"  kandidaat: {result.eligible}")
    print(f"  uitvoerdercategorie: {result.executor_category}")
    print(f"  team: {result.team_id}")
    print(f"  wedstrijd: {result.home_away}")
    print(f"  wedstrijdcontext: {result.match_relation}")
    print(f"  voorkeur: {result.preference}")
    print()


def main() -> None:
    print("DVK Prototype v0.3 - Stap 4 kandidaatselectie")
    print("=" * 50)
    _show("W03", "SEN-3", "home")
    _show("W10", "SEN-10", "away")
    print("Rangorde op E/vorig seizoen: niet toegepast (Stap 5).")


if __name__ == "__main__":
    main()
