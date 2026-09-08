from __future__ import annotations

from dataclasses import dataclass

from .assignments import apply_assignment_to_case, create_duty_assignment
from .model import PrototypeCase
from .proposals import assess_proposal
from .workstream_model import AssignmentProposal, DutyAssignment, DutyService, HumanDecision


@dataclass(frozen=True)
class DashboardActionResult:
    decision: HumanDecision
    assignment: DutyAssignment | None
    updated_case: PrototypeCase
    message: str


def approve_from_dashboard(
    proposal: AssignmentProposal,
    service: DutyService,
    case: PrototypeCase,
    decided_by: str,
    assignment_id: str,
) -> DashboardActionResult:
    """Dashboard orchestration only; all policy remains in Step 7/8 domain functions."""
    decision = assess_proposal(proposal, "approved", decided_by)
    assignment = create_duty_assignment(assignment_id, proposal, decision, service)
    if assignment is None:
        raise RuntimeError("approved proposal did not produce DutyAssignment")
    updated_case = apply_assignment_to_case(case, assignment)
    return DashboardActionResult(
        decision=decision,
        assignment=assignment,
        updated_case=updated_case,
        message="Voorstel goedgekeurd en Ledendienst ingepland.",
    )


def reject_from_dashboard(
    proposal: AssignmentProposal,
    case: PrototypeCase,
    decided_by: str,
    reason_category: str,
    reason: str,
) -> DashboardActionResult:
    """Reject a proposal through the dashboard without changing duty hours."""
    decision = assess_proposal(
        proposal,
        "rejected",
        decided_by,
        reason_category=reason_category,
        reason=reason,
    )
    return DashboardActionResult(
        decision=decision,
        assignment=None,
        updated_case=case,
        message="Voorstel afgewezen; urenpositie blijft ongewijzigd en de dienst blijft open.",
    )
