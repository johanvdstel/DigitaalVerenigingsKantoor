from __future__ import annotations

from .model import PrototypeCase
from .workstream_model import AssignmentProposal, DutyAssignment, DutyService, HumanDecision


def create_duty_assignment(
    assignment_id: str,
    proposal: AssignmentProposal,
    decision: HumanDecision,
    service: DutyService,
) -> DutyAssignment | None:
    """Turn an approved proposal into temporary local planning.

    A rejected proposal deliberately yields no assignment. The assignment records
    the full service duration. A member may therefore be scheduled for more hours
    than remain open. Sportlink's registered hours remain source facts.
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
    if duration <= 0:
        raise ValueError("duty duration must be positive")

    return DutyAssignment(
        assignment_id=assignment_id,
        proposal_id=proposal.proposal_id,
        service_id=proposal.service_id,
        person_id=proposal.person_id,
        executor_category=proposal.executor_category,
        scheduled_hours=duration,
        approved_by=decision.decided_by,
        status="temporary",
        engine_run_id=proposal.engine_run_id,
        snapshot_ids=proposal.snapshot_ids,
        policy_version=proposal.policy_version,
        config_version=proposal.config_version,
        software_version=proposal.software_version,
        decided_at=decision.decided_at,
    )


def apply_assignment_to_case(case: PrototypeCase, assignment: DutyAssignment) -> PrototypeCase:
    """Compatibility boundary: local planning must not mutate Sportlink A/B/C/D.

    FR-02/03 replace the historical D-update. Staffing and availability are
    derived from the active planning repository, not a fabricated source case.
    """
    if case.person.person_id != assignment.person_id:
        raise ValueError("assignment does not belong to case person")
    registration = case.sportlink_duty
    if registration is None or registration.required_hours is None:
        raise ValueError("complete duty registration required to apply assignment")

    return case
