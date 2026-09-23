from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import Person, PrototypeCase
from .no_show import NoShowEvent, SanctionAssessment, assess_sanction, season_id
from .planning import PlanningOverview, PlanningPeriod, PlanningSourceStatus, build_planning_overview
from .real_data_import import DataQualitySignal
from .run_context import EngineRun
from .replacement_duty import ActiveSanctionState, ReplacementDuty, active_sanction_state
from .security import Authorizer, Identity, Permission
from .staffing import StaffingNeed
from .workstream_model import AssignmentProposal, DutyAssignment, DutyService, Match


@dataclass(frozen=True)
class AssignmentContext:
    assignment: DutyAssignment
    service: DutyService | None
    person_name: str | None


def _assignment_context(assignment, services, persons) -> AssignmentContext:
    # Only an exact, unique identifier match supplies human context.
    matching_services = tuple(s for s in services if s.service_id == assignment.service_id)
    matching_persons = tuple(p for p in persons if p.person_id == assignment.person_id)
    return AssignmentContext(
        assignment,
        matching_services[0] if len(matching_services) == 1 else None,
        matching_persons[0].name if len(matching_persons) == 1 else None,
    )


@dataclass(frozen=True)
class ReplacementLinkContext:
    no_show: NoShowEvent
    original_assignment: AssignmentContext
    available_assignments: tuple[AssignmentContext, ...]


@dataclass(frozen=True)
class ReplacementStatusContext:
    replacement: ReplacementDuty
    assignment: AssignmentContext


@dataclass(frozen=True)
class ReplacementOverview:
    link_options: tuple[ReplacementLinkContext, ...]
    pending: tuple[ReplacementStatusContext, ...]
    with_no_show: tuple[ReplacementStatusContext, ...]


class NoShowApplicationService:
    """Authorized Gate 9 boundary for registering and correcting no-shows."""

    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def available_assignments(self, limit: int = 50):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        return self.uow.assignments.recent(limit)

    def assignment_contexts(self, *, services: tuple[DutyService, ...] = (), persons: tuple[Person, ...] = (), limit: int = 50) -> tuple[AssignmentContext, ...]:
        return tuple(_assignment_context(a, services, persons) for a in self.available_assignments(limit))

    def register(self, event: NoShowEvent) -> SanctionAssessment:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        if event.recorded_by != self.identity.subject_id:
            raise ValueError("no-show recorded_by must match authenticated identity")
        assignment = self.uow.assignments.get(event.assignment_id)
        if assignment is None:
            raise ValueError("no-show must reference an existing inroostering")
        if assignment.person_id != event.person_id:
            raise ValueError("no-show person must match inroostering")
        if self.uow.no_shows.for_assignment(event.assignment_id) is not None:
            raise ValueError("voor deze inroostering is al een no-show geregistreerd")
        prior = self.uow.no_shows.for_person_season(event.person_id, event.season)
        assessment = assess_sanction(event, prior)
        self.uow.no_shows.add(event)
        self.uow.sanctions.add(assessment)
        self.uow.commit()
        return assessment

    def revoke(self, no_show_id: str, *, reason: str, corrected_at: datetime) -> NoShowEvent:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        if not reason.strip():
            raise ValueError("correction reason is required")
        current = self.uow.no_shows.get(no_show_id)
        if current is None:
            raise ValueError("unknown no-show")
        if current.status == "revoked":
            raise ValueError("no-show is already revoked")
        revoked = NoShowEvent(
            current.no_show_id, current.assignment_id, current.person_id,
            current.occurred_at, current.recorded_at, current.recorded_by,
            current.season, "revoked", reason.strip(), corrected_at,
            self.identity.subject_id,
        )
        self.uow.no_shows.update(revoked)
        self.uow.commit()
        return revoked



class ReplacementDutyApplicationService:
    """Authorized VC boundary for linking and confirming replacement duties."""

    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def overview(self, *, services: tuple[DutyService, ...] = (), persons: tuple[Person, ...] = (), limit: int = 50) -> ReplacementOverview:
        """Read the existing recent-assignment scope without changing sanctions.

        A valid no-show on the replacement is a separate presentation state,
        including when completion has already been recorded. Command validation
        and chronological sanction derivation remain independent of this query.
        """
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        assignments = self.uow.assignments.recent(limit)
        contexts = tuple(_assignment_context(a, services, persons) for a in assignments)
        link_options = []
        pending = []
        with_no_show = []
        for context in contexts:
            assignment = context.assignment
            no_show = self.uow.no_shows.for_assignment(assignment.assignment_id)
            if no_show is None:
                continue
            replacement = self.uow.replacements.for_no_show(no_show.no_show_id)
            if replacement is None:
                if no_show.status != "valid":
                    continue
                state = self._state(no_show.person_id, no_show.season)
                if state.counter == 1 and state.assessment and state.assessment.no_show_id == no_show.no_show_id:
                    choices = tuple(c for c in contexts if c.assignment.person_id == no_show.person_id and c.assignment.assignment_id != no_show.assignment_id)
                    link_options.append(ReplacementLinkContext(no_show, context, choices))
                continue
            replacement_assignment = self.uow.assignments.get(replacement.assignment_id)
            if replacement_assignment is None:
                raise ValueError("replacement references an unknown inroostering")
            row = ReplacementStatusContext(replacement, _assignment_context(replacement_assignment, services, persons))
            replacement_no_show = self.uow.no_shows.for_assignment(replacement.assignment_id)
            if replacement_no_show is not None and replacement_no_show.status == "valid":
                with_no_show.append(row)
            elif not replacement.completed:
                pending.append(row)
        return ReplacementOverview(tuple(link_options), tuple(pending), tuple(with_no_show))

    def register_replacement(self, replacement: ReplacementDuty) -> ActiveSanctionState:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        if replacement.registered_by != self.identity.subject_id:
            raise ValueError("replacement registered_by must match authenticated identity")
        if replacement.completed:
            raise ValueError("replacement must be registered before it can be confirmed completed")
        no_show = self.uow.no_shows.get(replacement.no_show_id)
        if no_show is None or no_show.status != "valid":
            raise ValueError("replacement must reference a valid no-show")
        assignment = self.uow.assignments.get(replacement.assignment_id)
        if assignment is None:
            raise ValueError("replacement must reference an existing inroostering")
        if no_show.person_id != replacement.person_id or assignment.person_id != replacement.person_id:
            raise ValueError("replacement person must match no-show and inroostering")
        if no_show.season != replacement.season:
            raise ValueError("replacement season must match no-show season")
        state_before = self._state(replacement.person_id, replacement.season)
        if state_before.counter != 1 or state_before.assessment is None or state_before.assessment.no_show_id != no_show.no_show_id:
            raise ValueError("only the active first no-show can receive a replacement duty")
        self.uow.replacements.add(replacement)
        self.uow.commit()
        return self._state(replacement.person_id, replacement.season)

    def complete_replacement(self, replacement_id: str, *, completed_at: datetime) -> ActiveSanctionState:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        current = self.uow.replacements.get(replacement_id)
        if current is None:
            raise ValueError("unknown replacement duty")
        if current.completed:
            raise ValueError("replacement duty is already completed")
        completed = ReplacementDuty(
            current.replacement_id, current.no_show_id, current.assignment_id,
            current.person_id, current.season, current.registered_at, current.registered_by,
            completed_at, self.identity.subject_id,
        )
        self.uow.replacements.update(completed)
        self.uow.commit()
        return self._state(completed.person_id, completed.season)

    def _state(self, person_id: str, season: str) -> ActiveSanctionState:
        return active_sanction_state(
            person_id, season,
            self.uow.no_shows.for_person_season(person_id, season),
            self.uow.replacements.for_person_season(person_id, season),
        )


@dataclass(frozen=True)
class ImportPreviewResult:
    batch: ImportBatch
    differences: tuple[SnapshotDifference, ...]


class ImportApplicationService:
    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def preview(self, batch: ImportBatch, records: tuple[SnapshotRecord, ...]) -> ImportPreviewResult:
        self.authorizer.require(self.identity, Permission.PREVIEW_IMPORT)
        return ImportPreviewResult(batch, tuple(preview_differences(self.uow, batch, records)))

    def confirm(self, batch: ImportBatch, records: tuple[SnapshotRecord, ...], *, snapshot_id: str, confirmed_at: datetime) -> SourceSnapshot:
        self.authorizer.require(self.identity, Permission.CONFIRM_IMPORT)
        return confirm_import(self.uow, batch, records, snapshot_id=snapshot_id, confirmed_at=confirmed_at, confirmed_by=self.identity.subject_id)


class EngineRunApplicationService:
    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def record(self, run: EngineRun) -> EngineRun:
        self.authorizer.require(self.identity, Permission.RECORD_ENGINE_RUN)
        if run.initiated_by != self.identity.subject_id:
            raise ValueError("EngineRun initiated_by must match authenticated identity")
        self.uow.engine_runs.add(run)
        self.uow.commit()
        return run


class PlanningApplicationService:
    def __init__(self, identity: Identity, authorizer: Authorizer | None = None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def build_overview(self, *, period: PlanningPeriod, services: tuple[DutyService, ...], staffing_needs: tuple[StaffingNeed, ...], matches: tuple[Match, ...] = (), source_statuses: tuple[PlanningSourceStatus, ...] = (), data_quality_signals: tuple[DataQualitySignal, ...] = ()) -> PlanningOverview:
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        return build_planning_overview(period=period, services=services, staffing_needs=staffing_needs, matches=matches, source_statuses=source_statuses, data_quality_signals=data_quality_signals)


class ProposalDecisionApplicationService:
    """Authorized persistence boundary for human proposal decisions."""

    def __init__(self, identity: Identity, authorizer: Authorizer | None = None, uow=None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()
        self.uow = uow

    def _add_without_commit(self, proposal: AssignmentProposal, result: DashboardActionResult) -> None:
        if self.uow is None:
            return
        self.uow.proposals.add(proposal)
        self.uow.decisions.add(result.decision)
        if result.assignment is not None:
            self.uow.assignments.add(result.assignment)

    def _persist(self, proposal: AssignmentProposal, result: DashboardActionResult) -> None:
        self._add_without_commit(proposal, result)
        if self.uow is not None:
            self.uow.commit()

    def approve(self, proposal: AssignmentProposal, service: DutyService, case: PrototypeCase, *, assignment_id: str) -> DashboardActionResult:
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        result = approve_from_dashboard(proposal, service, case, self.identity.subject_id, assignment_id)
        self._persist(proposal, result)
        return result

    def approve_many(self, selections: tuple[tuple[AssignmentProposal, PrototypeCase, str], ...], service: DutyService, staffing_need: StaffingNeed) -> tuple[DashboardActionResult, ...]:
        """Confirm one planner selection as a single transaction, bounded by remaining capacity."""
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        if not selections:
            raise ValueError("at least one candidate must be selected")
        if len(selections) > staffing_need.remaining_capacity:
            raise ValueError("selection exceeds remaining service capacity")
        if staffing_need.service_id != service.service_id:
            raise ValueError("staffing need does not belong to service")
        if any(proposal.service_id != service.service_id for proposal, _, _ in selections):
            raise ValueError("all proposals must belong to the selected service")
        proposal_ids = [proposal.proposal_id for proposal, _, _ in selections]
        if len(set(proposal_ids)) != len(proposal_ids):
            raise ValueError("a proposal can only be selected once")

        results = tuple(
            approve_from_dashboard(proposal, service, case, self.identity.subject_id, assignment_id)
            for proposal, case, assignment_id in selections
        )
        for (proposal, _, _), result in zip(selections, results):
            self._add_without_commit(proposal, result)
        if self.uow is not None:
            self.uow.commit()
        return results

    def reject(self, proposal: AssignmentProposal, case: PrototypeCase, *, reason_category: str, reason: str) -> DashboardActionResult:
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        result = reject_from_dashboard(proposal, case, self.identity.subject_id, reason_category, reason)
        self._persist(proposal, result)
        return result
