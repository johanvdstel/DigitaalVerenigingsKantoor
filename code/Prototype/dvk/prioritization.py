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
    """Rank by group, youth home kickoff preference, E, positive backlog and person key.

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
        other_weekend = assessment.person_id in other_weekend_person_ids
        group = "other_weekend" if other_weekend else assessment.preference
        preference = PREFERENCE_ORDER.get(group, 0)
        kickoff_preference = group == "youth_home" and assessment.youth_home_kickoff_in_service
        sort_key = (other_weekend, -preference, -kickoff_preference,
                    -remaining, -previous, assessment.person_id)
        rows.append((sort_key, assessment, remaining, previous, group, kickoff_preference))

    rows.sort(key=lambda row: row[0])

    result = []
    for rank, (_, assessment, remaining, previous, group, kickoff_preference) in enumerate(rows, start=1):
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
        if group == "youth_home":
            explanation.append("jeugdthuisaftrap binnen dienst" if kickoff_preference
                               else "jeugdthuisaftrap vóór dienst")
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
                group,
                tuple(explanation),
                youth_home_kickoff_in_service=kickoff_preference,
            )
        )
    return tuple(result)
