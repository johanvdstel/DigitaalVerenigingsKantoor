from datetime import date

from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import W_CASE_BY_ID
from dvk.workstream_model import CandidateAssessment


def assessment(person_id: str, preference: str = "neutral") -> CandidateAssessment:
    return CandidateAssessment(person_id, "S-PRIO", True, "member", None, None, "demo", preference)


def show(title: str, rows) -> None:
    print(title)
    for row in rows:
        print(
            f"  {row.rank}. {row.person_id}: E={row.remaining_hours}, "
            f"vorig seizoen={row.previous_season_backlog}, context={row.match_preference}"
        )
        print("     verklaring: " + "; ".join(row.explanation))
    print()


def main() -> None:
    print("DVK Prototype v0.3 - Stap 5 prioritering")
    print("=" * 48)

    w08 = prioritize_candidates(
        (assessment("W08P"), assessment("W07P")),
        (W_CASE_BY_ID["W08"], W_CASE_BY_ID["W07"]),
        date(2026, 9, 15),
    )
    show("W08 — grotere actuele E heeft hogere prioriteit", w08)

    w09 = prioritize_candidates(
        (assessment("W09P"), assessment("W07P")),
        (W_CASE_BY_ID["W09"], W_CASE_BY_ID["W07"]),
        date(2026, 11, 30),
        {"W09P": 6, "W07P": 0},
    )
    show("W09 — gelijke E: vóór 1 december telt oude achterstand mee", w09)

    december = prioritize_candidates(
        (assessment("W09P"), assessment("W07P")),
        (W_CASE_BY_ID["W09"], W_CASE_BY_ID["W07"]),
        date(2026, 12, 1),
        {"W09P": 6, "W07P": 0},
    )
    show("W09 grenscontrole — vanaf 1 december telt oude achterstand niet mee", december)


if __name__ == "__main__":
    main()
