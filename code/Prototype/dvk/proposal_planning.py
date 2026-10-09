from __future__ import annotations

from dataclasses import dataclass

from .staffing import StaffingNeed
from .workstream_model import AssignmentProposal


@dataclass(frozen=True)
class PlannedProposal:
    """A candidate proposal with its staffing purpose made explicit."""

    proposal: AssignmentProposal
    staffing_purpose: str


def plan_proposals(
    proposals: tuple[AssignmentProposal, ...],
    staffing_need: StaffingNeed,
) -> tuple[PlannedProposal, ...]:
    """Offer ranked proposals up to maximum capacity, distinguishing V06 purpose.

    Candidate selection is independent of match availability. Matches may have
    influenced the already-derived ranking, but an empty match set is never a
    reason to suppress otherwise suitable proposals.
    """
    if any(proposal.service_id != staffing_need.service_id for proposal in proposals):
        raise ValueError("all proposals must belong to the StaffingNeed service")

    ranked = sorted(proposals, key=lambda proposal: (proposal.priority_rank, proposal.proposal_id))
    selected = ranked[:staffing_need.candidate_slots]
    return tuple(
        PlannedProposal(
            proposal=proposal,
            staffing_purpose=(
                "minimum_coverage"
                if index < staffing_need.minimum_coverage_slots
                else "optional_capacity"
            ),
        )
        for index, proposal in enumerate(selected)
    )
