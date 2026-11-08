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
    *, offer_all: bool = False,
) -> tuple[PlannedProposal, ...]:
    """Rank proposals with V06 purpose; offer_all preserves the planner's choice.

    Default capacity truncation is retained for historical callers. Operation/UI
    callers offer all suitable choices; existing approval guards limit selection.

    Candidate selection is independent of match availability. Matches may have
    influenced the already-derived ranking, but an empty match set is never a
    reason to suppress otherwise suitable proposals.
    """
    if any(proposal.service_id != staffing_need.service_id for proposal in proposals):
        raise ValueError("all proposals must belong to the StaffingNeed service")

    ranked = sorted(proposals, key=lambda proposal: (proposal.priority_rank, proposal.proposal_id))
    selected = ranked if offer_all else ranked[:staffing_need.candidate_slots]
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
