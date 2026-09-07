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


def _match_start_overlaps_service(match: Match, service: DutyService) -> bool:
    """Known overlap based only on source facts available in v0.3: match start time."""
    return service.starts_at <= match.starts_at < service.ends_at


def assess_candidate(
    case: PrototypeCase,
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
    matches: tuple[Match, ...],
    today: date,
) -> CandidateAssessment:
    """Assess step-4 candidate eligibility and practical match context.

    No ranking on remaining hours or historic backlog is performed here.
    """
    qualification = derive_duty_qualification(case, today)
    executor_category = derive_executor_category(case, today)
    person_id = case.person.person_id

    if not qualification.duty_required:
        return CandidateAssessment(
            person_id, service.service_id, False, executor_category,
            None, None, "not_assessed", "none", qualification.reason,
        )

    team = _active_team_membership(person_id, service, team_memberships)
    if team is None:
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            None, None, "no_match_context", "neutral",
        )

    match = _match_for_team_on_service_date(team.team_id, service, matches)
    if match is None:
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            team.team_id, None, "no_match_that_day", "neutral",
        )

    overlap = _match_start_overlaps_service(match, service)

    if match.home_away == "away":
        if overlap:
            return CandidateAssessment(
                person_id, service.service_id, False, executor_category,
                team.team_id, "away", "away_match_overlaps_service", "none",
                "dienst overlapt met de uitwedstrijd",
            )
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            team.team_id, "away", "away_match_same_day_no_overlap", "avoid",
        )

    if match.home_away == "home":
        if executor_category == "parent_guardian":
            relation = "home_match_overlaps_service" if overlap else "home_match_same_day_no_overlap"
            preference = "preferred" if overlap else "neutral"
        else:
            relation = "home_match_before_or_after_service" if not overlap else "home_match_overlaps_service"
            preference = "preferred" if not overlap else "neutral"
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            team.team_id, "home", relation, preference,
        )

    raise ValueError(f"Unknown home_away value for match {match.match_id}: {match.home_away!r}")


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
