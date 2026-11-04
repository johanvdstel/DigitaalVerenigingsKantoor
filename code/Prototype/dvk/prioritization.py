from __future__ import annotations

from datetime import date

from .duty import duty_position_from_registration
from .model import PrototypeCase
from .workstream_model import CandidateAssessment, CandidatePriority

PREFERENCE_ORDER = {"youth_home": 3, "preferred": 2, "neutral": 1, "avoid": 0, "other_weekend": -1}


def _remaining_hours(case: PrototypeCase) -> int:
    registration = case.sportlink_duty
    if registration is None or registration.required_hours is None:
        raise ValueError(f"{case.person.person_id}: current A/B/C/D position is incomplete")
    return duty_position_from_registration(registration).E


def prioritize_candidates(
    assessments: tuple[CandidateAssessment, ...],
    cases: tuple[PrototypeCase, ...],
    on_date: date,
    previous_season_backlog: dict[str, int] | None = None,
    *, apply_previous_season: bool = True,
    other_weekend_person_ids: frozenset[str] = frozenset(),
) -> tuple[CandidatePriority, ...]:
    """Rank candidates: group, current E, positive previous-season backlog, person key.

    No weighted score is invented. The sort is lexicographic so each ordering
    decision remains directly explainable from the policy rules.
    """
    cases_by_person = {case.person.person_id: case for case in cases}
    backlog = previous_season_backlog or {}
    consider_previous = apply_previous_season

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

    rows.sort(key=lambda row: (row[0].person_id in other_weekend_person_ids,
                               -row[3] if row[0].person_id not in other_weekend_person_ids else 0,
                               -row[1], -row[2], row[0].person_id))

    result = []
    for rank, (assessment, remaining, previous, _) in enumerate(rows, start=1):
        explanation = [f"actuele E={remaining}"]
        known = assessment.person_id in backlog
        if not apply_previous_season:
            explanation.append("historische bron niet beschikbaar")
        elif not known:
            explanation.append("historische achterstand onbekend")
        elif backlog.get(assessment.person_id, 0) < 0:
            explanation.append("geen positieve historische achterstand")
        else:
            explanation.append(f"achterstand vorig seizoen={previous}")
        explanation.append("wedstrijdvoorkeur=" + ("same_day_emergency"
                           if assessment.planning_relation == "same_day_emergency" else assessment.preference))
        if assessment.person_id in other_weekend_person_ids:
            explanation.append("andere teamspeeldag: laatste noodgroep")
        if assessment.home_away == "home" and assessment.preference == "neutral":
            explanation.append("jeugd thuis zonder overlap: noodgroep zonder wedstrijd")
        result.append(
            CandidatePriority(
                assessment.person_id,
                assessment.service_id,
                rank,
                remaining,
                previous,
                consider_previous and known,
                "other_weekend" if assessment.person_id in other_weekend_person_ids else assessment.preference,
                tuple(explanation),
            )
        )
    return tuple(result)
