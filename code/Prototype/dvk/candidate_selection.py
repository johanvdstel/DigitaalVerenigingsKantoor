from __future__ import annotations

from datetime import date, time, timedelta

from .duty import derive_duty_qualification, derive_executor_category
from .model import PrototypeCase
from .workstream_model import CandidateAssessment, DutyService, Match, TeamMembership

# v0.5 planning assumption: a match occupies two hours from kick-off
# (2x45 minutes, 15 minutes half-time, 15 minutes run-out).
MATCH_PLANNING_DURATION = timedelta(hours=2)


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


def _match_overlaps_service(match: Match, service: DutyService) -> bool:
    """True when the service and the v0.5 two-hour match window share time."""
    match_ends_at = match.starts_at + MATCH_PLANNING_DURATION
    return service.starts_at < match_ends_at and service.ends_at > match.starts_at


def _youth_service_window_allowed(service: DutyService) -> bool:
    """Parents of youth members are candidates on weekdays and weekend services starting <= 12:30."""
    if service.starts_at.weekday() < 5:
        return True
    return service.starts_at.time() <= time(12, 30)


def assess_candidate(
    case: PrototypeCase,
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
    matches: tuple[Match, ...],
    today: date,
) -> CandidateAssessment:
    """Assess candidate eligibility using the Gate-8 youth/senior match decision tree."""
    qualification = derive_duty_qualification(case, today)
    executor_category = derive_executor_category(case, today)
    person_id = case.person.person_id

    if not qualification.duty_required:
        return CandidateAssessment(
            person_id, service.service_id, False, executor_category,
            None, None, "not_assessed", "none", qualification.reason,
        )

    if executor_category == "parent_guardian" and not _youth_service_window_allowed(service):
        return CandidateAssessment(
            person_id, service.service_id, False, executor_category,
            None, None, "youth_weekend_after_1230", "none",
            "jeugdlid alleen beschikbaar voor doordeweekse diensten of weekenddiensten die uiterlijk om 12:30 beginnen",
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

    overlap = _match_overlaps_service(match, service)
    home_away = match.home_away.lower()

    if home_away == "away":
        if overlap:
            return CandidateAssessment(
                person_id, service.service_id, False, executor_category,
                team.team_id, "away", "away_match_overlaps_service", "none",
                "dienst overlapt met de uitwedstrijd",
            )
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            team.team_id, "away", "away_match_same_day", "avoid",
        )

    if home_away == "home":
        if overlap:
            if executor_category == "parent_guardian":
                return CandidateAssessment(
                    person_id, service.service_id, True, executor_category,
                    team.team_id, "home", "home_match_overlaps_service", "preferred",
                )
            return CandidateAssessment(
                person_id, service.service_id, False, executor_category,
                team.team_id, "home", "home_match_overlaps_service", "none",
                "dienst overlapt met de thuiswedstrijd",
            )
        return CandidateAssessment(
            person_id, service.service_id, True, executor_category,
            team.team_id, "home", "home_match_same_day", "preferred",
        )

    raise ValueError(f"Unknown home_away value for match {match.match_id}: {match.home_away!r}")


def select_candidates(
    cases: tuple[PrototypeCase, ...],
    service: DutyService,
    team_memberships: tuple[TeamMembership, ...],
    matches: tuple[Match, ...],
    today: date,
) -> tuple[CandidateAssessment, ...]:
    assessments = tuple(
        assess_candidate(case, service, team_memberships, matches, today) for case in cases
    )
    return tuple(assessment for assessment in assessments if assessment.eligible)
