from __future__ import annotations

from dataclasses import replace

from .model import PrototypeCase, SportlinkDutyRegistration
from .workstream_model import AssignmentProposal, DutyAssignment, DutyService, HumanDecision


def create_duty_assignment(
    assignment_id: str,
    proposal: AssignmentProposal,
    decision: HumanDecision,
    service: DutyService,
) -> DutyAssignment | None:
    """Turn an approved proposal into a factual scheduled duty.

    A rejected proposal deliberately yields no assignment. The assignment records
    scheduled hours; applying those hours to the administrative duty position is
    a separate explicit operation.
    """
    if decision.proposal_id != proposal.proposal_id:
        raise ValueError("human decision does not belong to proposal")
    if service.service_id != proposal.service_id:
        raise ValueError("service does not belong to proposal")
    if decision.decision == "rejected":
        return None
    if decision.decision != "approved":
        raise ValueError("DutyAssignment requires an approved proposal")

    duration = service.duration_hours
    if duration <= 0 or not duration.is_integer():
        raise ValueError("prototype requires a positive whole-hour duty duration")
    scheduled_hours = int(duration)
    if scheduled_hours > proposal.E:
        raise ValueError("duty duration exceeds remaining unscheduled hours")

    return DutyAssignment(
        assignment_id=assignment_id,
        proposal_id=proposal.proposal_id,
        service_id=proposal.service_id,
        person_id=proposal.person_id,
        executor_category=proposal.executor_category,
        scheduled_hours=scheduled_hours,
        approved_by=decision.decided_by,
    )


def apply_assignment_to_case(case: PrototypeCase, assignment: DutyAssignment) -> PrototypeCase:
    """Return a new case with D increased; A/B/C remain unchanged."""
    if case.person.person_id != assignment.person_id:
        raise ValueError("assignment does not belong to case person")
    registration = case.sportlink_duty
    if registration is None or registration.required_hours is None:
        raise ValueError("complete duty registration required to apply assignment")

    updated = SportlinkDutyRegistration(
        person_id=registration.person_id,
        required_hours=registration.required_hours,
        correction_hours=registration.correction_hours,
        completed_hours=registration.completed_hours,
        scheduled_hours=registration.scheduled_hours + assignment.scheduled_hours,
    )
    return replace(case, sportlink_duty=updated)
