from __future__ import annotations

from datetime import date

from .duty import duty_position_from_registration
from .model import PrototypeCase
from .workstream_model import CandidateAssessment, CandidatePriority

PREFERENCE_ORDER = {"preferred": 2, "neutral": 1, "avoid": 0}


def _remaining_hours(case: PrototypeCase) -> int:
    registration = case.sportlink_duty
    if registration is None or registration.required_hours is None:
        raise ValueError(f"{case.person.person_id}: current A/B/C/D position is incomplete")
    return duty_position_from_registration(registration).E


def _previous_backlog_is_relevant(on_date: date) -> bool:
    return 7 <= on_date.month <= 12


def prioritize_candidates(
    assessments: tuple[CandidateAssessment, ...],
    cases: tuple[PrototypeCase, ...],
    on_date: date,
    previous_season_backlog: dict[str, int] | None = None,
    *, apply_previous_season: bool = True,
) -> tuple[CandidatePriority, ...]:
    """Rank candidates: current E, positive backlog in July–December, context.

    No weighted score is invented. The sort is lexicographic so each ordering
    decision remains directly explainable from the policy rules.
    """
    cases_by_person = {case.person.person_id: case for case in cases}
    backlog = previous_season_backlog or {}
    in_season_window = _previous_backlog_is_relevant(on_date)
    consider_previous = apply_previous_season and in_season_window

    rows = []
    for assessment in assessments:
        if not assessment.eligible:
            continue
        case = cases_by_person[assessment.person_id]
        remaining = _remaining_hours(case)
        # A fully covered obligation is no longer a candidate for new planning.
        if remaining <= 0:
            continue
        previous = max(0, backlog.get(assessment.person_id, 0)) if consider_previous else 0
        preference = PREFERENCE_ORDER.get(assessment.preference, 0)
        rows.append((assessment, remaining, previous, preference))

    rows.sort(key=lambda row: (-row[1], -row[2], -row[3], row[0].person_id))

    result = []
    for rank, (assessment, remaining, previous, _) in enumerate(rows, start=1):
        explanation = [f"actuele E={remaining}"]
        known = assessment.person_id in backlog
        if not in_season_window:
            explanation.append("achterstand vorig seizoen buiten juli tot en met december")
        elif not apply_previous_season:
            explanation.append("historische bron niet beschikbaar")
        elif not known:
            explanation.append("historische achterstand onbekend")
        elif backlog.get(assessment.person_id, 0) < 0:
            explanation.append("geen positieve historische achterstand")
        else:
            explanation.append(f"achterstand vorig seizoen={previous}")
        explanation.append(f"wedstrijdvoorkeur={assessment.preference}")
        result.append(
            CandidatePriority(
                assessment.person_id,
                assessment.service_id,
                rank,
                remaining,
                previous,
                consider_previous and known,
                assessment.preference,
                tuple(explanation),
            )
        )
    return tuple(result)
