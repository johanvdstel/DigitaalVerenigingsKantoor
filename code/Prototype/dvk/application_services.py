from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import PrototypeCase
from .no_show import NoShowEvent, SanctionAssessment, assess_sanction, season_id
from .planning import PlanningOverview, PlanningPeriod, PlanningSourceStatus, build_planning_overview
from .real_data_import import DataQualitySignal
from .run_context import EngineRun
from .replacement_duty import ActiveSanctionState, ReplacementDuty, active_sanction_state
from .security import Authorizer, Identity, Permission
from .staffing import StaffingNeed
from .workstream_model import AssignmentProposal, DutyService, Match


class NoShowApplicationService:
    """Authorized Gate 9 boundary for registering and correcting no-shows."""

    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def available_assignments(self, limit: int = 50):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        return self.uow.assignments.recent(limit)

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
