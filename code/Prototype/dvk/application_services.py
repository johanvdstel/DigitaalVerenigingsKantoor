from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import PrototypeCase
from .run_context import EngineRun
from .workstream_model import AssignmentProposal, DutyService


@dataclass(frozen=True)
class ImportPreviewResult:
    batch: ImportBatch
    differences: tuple[SnapshotDifference, ...]


class ImportApplicationService:
    """Application boundary for previewing and confirming validated source imports."""

    def __init__(self, uow):
        self.uow = uow

    def preview(self, batch: ImportBatch, records: tuple[SnapshotRecord, ...]) -> ImportPreviewResult:
        return ImportPreviewResult(batch, tuple(preview_differences(self.uow, batch, records)))

    def confirm(
        self,
        batch: ImportBatch,
        records: tuple[SnapshotRecord, ...],
        *,
        snapshot_id: str,
        confirmed_at: datetime,
        confirmed_by: str,
    ) -> SourceSnapshot:
        return confirm_import(
            self.uow, batch, records, snapshot_id=snapshot_id,
            confirmed_at=confirmed_at, confirmed_by=confirmed_by,
        )


class EngineRunApplicationService:
    """Application boundary for persisting an already-computed engine run context."""

    def __init__(self, uow):
        self.uow = uow

    def record(self, run: EngineRun) -> EngineRun:
        self.uow.engine_runs.add(run)
        self.uow.commit()
        return run


class ProposalDecisionApplicationService:
    """Application orchestration for human proposal decisions; domain rules remain outside the UI."""

    def approve(
        self,
        proposal: AssignmentProposal,
        service: DutyService,
        case: PrototypeCase,
        *,
        decided_by: str,
        assignment_id: str,
    ) -> DashboardActionResult:
        return approve_from_dashboard(proposal, service, case, decided_by, assignment_id)

    def reject(
        self,
        proposal: AssignmentProposal,
        case: PrototypeCase,
        *,
        decided_by: str,
        reason_category: str,
        reason: str,
    ) -> DashboardActionResult:
        return reject_from_dashboard(proposal, case, decided_by, reason_category, reason)
