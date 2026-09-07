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
    TeamMembership,
)


def _team_for_person(person_id: str, team_memberships: tuple[TeamMembership, ...]) -> str | None:
    membership = next((item for item in team_memberships if item.person_id == person_id), None)
    return membership.team_id if membership else None


def build_dashboard(
    cases: tuple[PrototypeCase, ...],
    duty_decisions: tuple[Decision, ...],
    services: tuple[DutyService, ...],
    team_memberships: tuple[TeamMembership, ...],
    candidate_assessments: tuple[CandidateAssessment, ...],
    priorities: tuple[CandidatePriority, ...],
    assigned_staff: dict[str, int] | None = None,
) -> DashboardViewModel:
    """Assemble a dashboard exclusively from source objects and engine outcomes.

    This module deliberately does not derive duty, select candidates or rank
    them. Those outcomes must already have been produced by the domain engine.
    """
    decisions_by_person = {
        decision.facts["administrative_subject"]: decision for decision in duty_decisions
    }
    cases_by_person = {case.person.person_id: case for case in cases}
    assessments_by_key = {
        (assessment.service_id, assessment.person_id): assessment
        for assessment in candidate_assessments
    }
    assigned = assigned_staff or {}

    duty_rows = []
    for person_id, decision in decisions_by_person.items():
        case = cases_by_person[person_id]
        registration = case.sportlink_duty
        position = decision.facts.get("duty_position")
        duty_rows.append(
            DashboardDutyRow(
                person_id,
                case.person.name,
                _team_for_person(person_id, team_memberships),
                decision.facts["duty_required"],
                decision.facts["qualification_reason"],
                registration.required_hours if registration else None,
                registration.correction_hours if registration else None,
                registration.completed_hours if registration else None,
                registration.scheduled_hours if registration else None,
                position["E"] if position else None,
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
    )

    candidate_rows = []
    for priority in priorities:
        assessment = assessments_by_key[(priority.service_id, priority.person_id)]
        candidate_rows.append(
            DashboardCandidateRow(
                priority.service_id,
                priority.person_id,
                priority.rank,
                assessment.team_id,
                priority.remaining_hours,
                assessment.executor_category,
                assessment.home_away,
                assessment.match_relation,
                priority.match_preference,
                priority.explanation,
                assessment.exclusion_reason,
            )
        )

    return DashboardViewModel(
        tuple(sorted(duty_rows, key=lambda row: row.name)),
        service_rows,
        tuple(sorted(candidate_rows, key=lambda row: (row.service_id, row.rank))),
    )
