from __future__ import annotations

from datetime import date

from .duty import derive_duty_qualification, derive_executor_category
from .model import PrototypeCase
from .workstream_model import CandidateAssessment, DutyService, Match, TeamMembership


def _active_team_membership(
    person_id: str,
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
) -> TeamMembership | None:
    service_date = service.starts_at.date()
    return next(
        (
            membership
            for membership in team_memberships
            if membership.person_id == person_id
            and (membership.start_date is None or membership.start_date <= service_date)
            and (membership.end_date is None or membership.end_date >= service_date)
        ),
        None,
    )


def _match_for_team_on_service_date(
    team_id: str,
    service: DutyService,
    matches: tuple[Match, ...],
) -> Match | None:
    service_date = service.starts_at.date()
    return next(
        (match for match in matches if match.team_id == team_id and match.starts_at.date() == service_date),
        None,
    )


def assess_candidate(
    case: PrototypeCase,
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
    matches: tuple[Match, ...],
    today: date,
) -> CandidateAssessment:
    """Assess step-4 candidate eligibility and match context.

    No ranking on remaining hours or historic backlog is performed here.
    """
    qualification = derive_duty_qualification(case, today)
    executor_category = derive_executor_category(case, today)
    person_id = case.person.person_id

    if not qualification.duty_required:
        return CandidateAssessment(
            person_id,
            service.service_id,
            False,
            executor_category,
            None,
            None,
            "not_assessed",
            "none",
            qualification.reason,
        )

    team = _active_team_membership(person_id, service, team_memberships)
    if team is None:
        return CandidateAssessment(
            person_id,
            service.service_id,
            True,
            executor_category,
            None,
            None,
            "no_match_context",
            "neutral",
        )

    match = _match_for_team_on_service_date(team.team_id, service, matches)
    if match is None:
        return CandidateAssessment(
            person_id,
            service.service_id,
            True,
            executor_category,
            team.team_id,
            None,
            "no_match_that_day",
            "neutral",
        )

    if match.home_away == "home":
        return CandidateAssessment(
            person_id,
            service.service_id,
            True,
            executor_category,
            team.team_id,
            "home",
            "home_match_same_day",
            "preferred",
        )

    return CandidateAssessment(
        person_id,
        service.service_id,
        True,
        executor_category,
        team.team_id,
        match.home_away,
        "away_match_same_day",
        "avoid",
    )


def select_candidates(
    cases: tuple[PrototypeCase, ...],
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
    matches: tuple[Match, ...],
    today: date,
) -> tuple[CandidateAssessment, ...]:
    """Return eligible candidates; ordering/prioritisation belongs to step 5."""
    assessments = tuple(
        assess_candidate(case, service, team_memberships, matches, today) for case in cases
    )
    return tuple(assessment for assessment in assessments if assessment.eligible)
