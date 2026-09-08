from __future__ import annotations

from .model import Decision, PrototypeCase
from .recommendation_planner import RecommendationPlan
from .workstream_model import (
    CandidateAssessment, CandidatePriority, DashboardCandidateRow, DashboardDutyRow,
    DashboardNotProposedRow, DashboardServiceRow, DashboardViewModel, DutyService,
    Match, TeamMembership,
)


def _team_for_person(person_id: str, team_memberships: tuple[TeamMembership, ...]) -> str | None:
    membership = next((item for item in team_memberships if item.person_id == person_id), None)
    return membership.team_id if membership else None


def _match_for_team(team_id: str | None, service: DutyService, matches: tuple[Match, ...]) -> Match | None:
    if team_id is None:
        return None
    return next((m for m in matches if m.team_id == team_id and m.starts_at.date() == service.starts_at.date()), None)


def build_dashboard(
    cases: tuple[PrototypeCase, ...], duty_decisions: tuple[Decision, ...],
    services: tuple[DutyService, ...], team_memberships: tuple[TeamMembership, ...],
    candidate_assessments: tuple[CandidateAssessment, ...], priorities: tuple[CandidatePriority, ...],
    recommendation_plan: RecommendationPlan,
    assigned_staff: dict[str, int] | None = None, matches: tuple[Match, ...] = (),
) -> DashboardViewModel:
    """Build presentation rows only from already-computed domain/engine outcomes."""
    decisions_by_person = {d.facts["administrative_subject"]: d for d in duty_decisions}
    cases_by_person = {c.person.person_id: c for c in cases}
    assessments_by_key = {(a.service_id, a.person_id): a for a in candidate_assessments}
    services_by_id = {s.service_id: s for s in services}
    assigned = assigned_staff or {}

    duty_rows = []
    for person_id, decision in decisions_by_person.items():
        case = cases_by_person[person_id]
        registration = case.sportlink_duty
        position = decision.facts.get("duty_position")
        remaining = position["E"] if position else None
        if not decision.facts["duty_required"] or remaining is None or remaining <= 0:
            continue
        duty_rows.append(DashboardDutyRow(
            person_id, case.person.name, _team_for_person(person_id, team_memberships), True,
            decision.facts["qualification_reason"], registration.required_hours if registration else None,
            registration.correction_hours if registration else None, registration.completed_hours if registration else None,
            registration.scheduled_hours if registration else None, remaining,
            any(s.code == "sportlink_required_hours_mismatch" for s in decision.signals),
        ))

    service_rows = tuple(DashboardServiceRow(
        s.service_id, s.service_type, s.starts_at, s.ends_at, s.required_staff,
        max(0, s.required_staff - assigned.get(s.service_id, 0)),
    ) for s in services if max(0, s.required_staff - assigned.get(s.service_id, 0)) > 0)

    recommended = recommendation_plan.recommended
    candidate_rows = []
    for priority in recommended:
        assessment = assessments_by_key[(priority.service_id, priority.person_id)]
        service = services_by_id[priority.service_id]
        match = _match_for_team(assessment.team_id, service, matches)
        equal_count = sum(1 for row in recommended if row.service_id == priority.service_id)
        candidate_rows.append(DashboardCandidateRow(
            priority.service_id, priority.person_id, cases_by_person[priority.person_id].person.name,
            priority.rank, assessment.team_id, priority.remaining_hours, assessment.executor_category,
            assessment.home_away, match.starts_at if match else None, assessment.match_relation,
            priority.match_preference, priority.explanation, equal_count > 1, assessment.exclusion_reason,
        ))

    not_proposed = []
    recommended_keys = {(r.service_id, r.person_id) for r in recommended}
    priority_by_key = {(p.service_id, p.person_id): p for p in priorities}
    for assessment in candidate_assessments:
        key = (assessment.service_id, assessment.person_id)
        if key in recommended_keys or assessment.person_id not in cases_by_person:
            continue
        service = services_by_id[assessment.service_id]
        match = _match_for_team(assessment.team_id, service, matches)
        if not assessment.eligible:
            reason = assessment.exclusion_reason or "voldoet niet aan de kandidaatvoorwaarden"
        elif key in recommendation_plan.skipped_same_day:
            reason = "al voorgesteld voor een andere Ledendienst op deze dag; beschikbaar als alternatief"
        elif key in priority_by_key:
            rank = priority_by_key[key].rank
            reason = f"wel geschikt, maar staat lager in de rangorde (plaats {rank}); beschikbaar als alternatief"
        else:
            reason = "niet opgenomen in de prioritering"
        not_proposed.append(DashboardNotProposedRow(
            assessment.service_id, assessment.person_id, cases_by_person[assessment.person_id].person.name,
            assessment.team_id, assessment.home_away, match.starts_at if match else None, reason,
        ))

    return DashboardViewModel(
        tuple(sorted(duty_rows, key=lambda r: (-r.remaining_hours, r.name))),
        tuple(sorted(service_rows, key=lambda r: r.starts_at)),
        tuple(sorted(candidate_rows, key=lambda r: (services_by_id[r.service_id].starts_at, r.name))),
        tuple(sorted(not_proposed, key=lambda r: (services_by_id[r.service_id].starts_at, r.name))),
    )
