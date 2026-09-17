from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import PrototypeCase
from .planning import PlanningOverview, PlanningPeriod, PlanningSourceStatus, build_planning_overview
from .real_data_import import DataQualitySignal
from .run_context import EngineRun
from .security import Authorizer, Identity, Permission
from .staffing import StaffingNeed
from .workstream_model import AssignmentProposal, DutyService, Match


@dataclass(frozen=True)
class ImportPreviewResult:
    batch: ImportBatch
    differences: tuple[SnapshotDifference, ...]


class ImportApplicationService:
    """Authorized application boundary for previewing and confirming source imports."""

    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def preview(self, batch: ImportBatch, records: tuple[SnapshotRecord, ...]) -> ImportPreviewResult:
        self.authorizer.require(self.identity, Permission.PREVIEW_IMPORT)
        return ImportPreviewResult(batch, tuple(preview_differences(self.uow, batch, records)))

    def confirm(
        self,
        batch: ImportBatch,
        records: tuple[SnapshotRecord, ...],
        *,
        snapshot_id: str,
        confirmed_at: datetime,
    ) -> SourceSnapshot:
        self.authorizer.require(self.identity, Permission.CONFIRM_IMPORT)
        return confirm_import(
            self.uow, batch, records, snapshot_id=snapshot_id,
            confirmed_at=confirmed_at, confirmed_by=self.identity.subject_id,
        )


class EngineRunApplicationService:
    """Authorized application boundary for persisting an already-computed engine run context."""

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
    """Authorized read-only boundary for the Planning presentation layer."""

    def __init__(self, identity: Identity, authorizer: Authorizer | None = None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def build_overview(
        self,
        *,
        period: PlanningPeriod,
        services: tuple[DutyService, ...],
        staffing_needs: tuple[StaffingNeed, ...],
        matches: tuple[Match, ...] = (),
        source_statuses: tuple[PlanningSourceStatus, ...] = (),
        data_quality_signals: tuple[DataQualitySignal, ...] = (),
    ) -> PlanningOverview:
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        return build_planning_overview(
            period=period,
            services=services,
            staffing_needs=staffing_needs,
            matches=matches,
            source_statuses=source_statuses,
            data_quality_signals=data_quality_signals,
        )


class ProposalDecisionApplicationService:
    """Authorized orchestration for human proposal decisions; domain rules remain outside the UI."""

    def __init__(self, identity: Identity, authorizer: Authorizer | None = None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def approve(
        self,
        proposal: AssignmentProposal,
        service: DutyService,
        case: PrototypeCase,
        *,
        assignment_id: str,
    ) -> DashboardActionResult:
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        return approve_from_dashboard(
            proposal, service, case, self.identity.subject_id, assignment_id
        )

    def reject(
        self,
        proposal: AssignmentProposal,
        case: PrototypeCase,
        *,
        reason_category: str,
        reason: str,
    ) -> DashboardActionResult:
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        return reject_from_dashboard(
            proposal, case, self.identity.subject_id, reason_category, reason
        )
