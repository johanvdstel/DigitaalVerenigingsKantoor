from __future__ import annotations

from .duty import duty_position_from_registration
from .model import PrototypeCase
from .workstream_model import (
    AssignmentProposal, CandidateAssessment, CandidatePriority, DutyService,
    HumanDecision, Match,
)

REJECTION_CATEGORIES = frozenset({
    "personal_circumstance",
    "unsuitable_for_service",
    "planning",
    "source_data_incorrect",
    "other",
})


def _match_for_assessment(
    assessment: CandidateAssessment,
    service: DutyService,
    matches: tuple[Match, ...],
) -> Match | None:
    if assessment.team_id is None:
        return None
    return next(
        (m for m in matches if m.team_id == assessment.team_id and m.starts_at.date() == service.starts_at.date()),
        None,
    )


def create_assignment_proposal(
    proposal_id: str,
    service: DutyService,
    case: PrototypeCase,
    assessment: CandidateAssessment,
    priority: CandidatePriority,
    matches: tuple[Match, ...] = (),
) -> AssignmentProposal:
    """Create an auditable DVK proposal from already-derived engine outcomes."""
    if assessment.service_id != service.service_id or priority.service_id != service.service_id:
        raise ValueError("service mismatch between proposal inputs")
    if assessment.person_id != case.person.person_id or priority.person_id != case.person.person_id:
        raise ValueError("person mismatch between proposal inputs")
    if not assessment.eligible:
        raise ValueError("cannot create a proposal for an ineligible candidate")

    registration = case.sportlink_duty
    if registration is None or registration.required_hours is None:
        raise ValueError("complete A/B/C/D duty position required for proposal")
    position = duty_position_from_registration(registration)
    match = _match_for_assessment(assessment, service, matches)

    uncertainties = []
    if assessment.team_id is None:
        uncertainties.append("team_unknown")
    if assessment.match_relation in {"no_match_context", "no_match_that_day"}:
        uncertainties.append("match_context_incomplete")

    return AssignmentProposal(
        proposal_id=proposal_id,
        service_id=service.service_id,
        person_id=case.person.person_id,
        executor_category=assessment.executor_category,
        A=position.A, B=position.B, C=position.C, D=position.D, E=position.E,
        previous_season_backlog=priority.previous_season_backlog,
        previous_season_considered=priority.previous_season_considered,
        team_id=assessment.team_id,
        home_away=assessment.home_away,
        match_starts_at=match.starts_at if match else None,
        match_relation=assessment.match_relation,
        suitability="suitable",
        priority_rank=priority.rank,
        applied_priority_rules=priority.explanation,
        uncertainties=tuple(uncertainties),
        status="proposed",
    )


def assess_proposal(
    proposal: AssignmentProposal,
    decision: str,
    decided_by: str,
    reason_category: str | None = None,
    reason: str | None = None,
) -> HumanDecision:
    """Record the human decision; does not create a DutyAssignment or mutate D."""
    if proposal.status != "proposed":
        raise ValueError("only a proposed AssignmentProposal can be assessed")
    if decision not in {"approved", "rejected"}:
        raise ValueError("decision must be approved or rejected")
    if not decided_by.strip():
        raise ValueError("decided_by is required")

    if decision == "rejected":
        if reason_category not in REJECTION_CATEGORIES:
            raise ValueError("valid rejection reason category is required")
        if not reason or not reason.strip():
            raise ValueError("rejection reason is required")
    elif reason_category is not None:
        raise ValueError("reason_category only applies to rejected proposals")

    return HumanDecision(
        proposal_id=proposal.proposal_id,
        decision=decision,
        decided_by=decided_by,
        reason_category=reason_category,
        reason=reason,
    )
