from __future__ import annotations

from .model import Decision, PrototypeCase
from .workstream_model import (
    CandidateAssessment,
    CandidatePriority,
    DashboardCandidateRow,
    DashboardDutyRow,
    DashboardServiceRow,
    DashboardViewModel,
    DutyService,
    Match,
    TeamMembership,
)


def _team_for_person(person_id: str, team_memberships: tuple[TeamMembership, ...]) -> str | None:
    membership = next((item for item in team_memberships if item.person_id == person_id), None)
    return membership.team_id if membership else None


def _match_for_team(team_id: str | None, service: DutyService, matches: tuple[Match, ...]) -> Match | None:
    if team_id is None:
        return None
    return next(
        (match for match in matches if match.team_id == team_id and match.starts_at.date() == service.starts_at.date()),
        None,
    )


def _same_priority(a: CandidatePriority, b: CandidatePriority) -> bool:
    return (
        a.remaining_hours,
        a.previous_season_backlog,
        a.previous_season_considered,
        a.match_preference,
    ) == (
        b.remaining_hours,
        b.previous_season_backlog,
        b.previous_season_considered,
        b.match_preference,
    )


def _recommended_priorities(priorities: tuple[CandidatePriority, ...]) -> tuple[CandidatePriority, ...]:
    """Show one advice per service, except genuinely equal first choices."""
    result = []
    service_ids = dict.fromkeys(priority.service_id for priority in priorities)
    for service_id in service_ids:
        rows = sorted((p for p in priorities if p.service_id == service_id), key=lambda p: p.rank)
        if not rows:
            continue
        first = rows[0]
        result.append(first)
        result.extend(row for row in rows[1:] if _same_priority(row, first))
    return tuple(result)


def build_dashboard(
    cases: tuple[PrototypeCase, ...],
    duty_decisions: tuple[Decision, ...],
    services: tuple[DutyService, ...],
    team_memberships: tuple[TeamMembership, ...],
    candidate_assessments: tuple[CandidateAssessment, ...],
    priorities: tuple[CandidatePriority, ...],
    assigned_staff: dict[str, int] | None = None,
    matches: tuple[Match, ...] = (),
) -> DashboardViewModel:
    """Assemble the user view from already calculated engine outcomes."""
    decisions_by_person = {decision.facts["administrative_subject"]: decision for decision in duty_decisions}
    cases_by_person = {case.person.person_id: case for case in cases}
    assessments_by_key = {(a.service_id, a.person_id): a for a in candidate_assessments}
    services_by_id = {service.service_id: service for service in services}
    assigned = assigned_staff or {}

    duty_rows = []
    for person_id, decision in decisions_by_person.items():
        case = cases_by_person[person_id]
        registration = case.sportlink_duty
        position = decision.facts.get("duty_position")
        remaining = position["E"] if position else None
        # This first dashboard is a work list: only obligations with hours still open.
        if not decision.facts["duty_required"] or remaining is None or remaining <= 0:
            continue
        duty_rows.append(
            DashboardDutyRow(
                person_id,
                case.person.name,
                _team_for_person(person_id, team_memberships),
                True,
                decision.facts["qualification_reason"],
                registration.required_hours if registration else None,
                registration.correction_hours if registration else None,
                registration.completed_hours if registration else None,
                registration.scheduled_hours if registration else None,
                remaining,
                any(signal.code == "sportlink_required_hours_mismatch" for signal in decision.signals),
            )
        )

    service_rows = tuple(
        DashboardServiceRow(
            service.service_id,
            service.service_type,
            service.starts_at,
            service.ends_at,
            service.required_staff,
            max(0, service.required_staff - assigned.get(service.service_id, 0)),
        )
        for service in services
        if max(0, service.required_staff - assigned.get(service.service_id, 0)) > 0
    )

    recommended = _recommended_priorities(priorities)
    candidate_rows = []
    for priority in recommended:
        assessment = assessments_by_key[(priority.service_id, priority.person_id)]
        service = services_by_id[priority.service_id]
        match = _match_for_team(assessment.team_id, service, matches)
        equal_count = sum(1 for row in recommended if row.service_id == priority.service_id)
        candidate_rows.append(
            DashboardCandidateRow(
                priority.service_id,
                priority.person_id,
                cases_by_person[priority.person_id].person.name,
                priority.rank,
                assessment.team_id,
                priority.remaining_hours,
                assessment.executor_category,
                assessment.home_away,
                match.starts_at if match else None,
                assessment.match_relation,
                priority.match_preference,
                priority.explanation,
                shared_first_choice=equal_count > 1,
                exclusion_reason=assessment.exclusion_reason,
            )
        )

    return DashboardViewModel(
        tuple(sorted(duty_rows, key=lambda row: (-row.remaining_hours, row.name))),
        tuple(sorted(service_rows, key=lambda row: row.starts_at)),
        tuple(sorted(candidate_rows, key=lambda row: (row.service_id, row.name))),
    )
