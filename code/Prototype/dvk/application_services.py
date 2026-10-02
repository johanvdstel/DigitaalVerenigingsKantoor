from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .candidate_selection import assess_candidate
from .planning_workqueue import TemporaryPlanning, planning_conflict, planning_staffing, validate_planning_selection
from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import Person, PrototypeCase
from .no_show import (
    CurrentSanctionState, NoShowEvent, NoShowRevocation, SanctionAssessment,
    assess_sanction, current_sanction_state, season_id,
)
from .planning import PlanningOverview, PlanningPeriod, PlanningSourceStatus, build_planning_overview
from .real_data_import import DataQualitySignal
from .run_context import EngineRun
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
class NoShowContext:
    no_show: NoShowEvent
    assignment: AssignmentContext


class NoShowApplicationService:
    """Authorized boundary for no-show facts, revocations and current sanctions."""

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
        revocations = self.uow.no_show_revocations.for_person_season(event.person_id, event.season)
        assessment = assess_sanction(event, prior, revocations)
        self.uow.no_shows.add(event)
        self.uow.sanctions.add(assessment)
        self.uow.commit()
        return assessment

    def revocable_no_shows(self, *, services: tuple[DutyService, ...] = (), persons: tuple[Person, ...] = ()) -> tuple[NoShowContext, ...]:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        rows = []
        for event in self.uow.no_shows.all():
            if self.uow.no_show_revocations.for_no_show(event.no_show_id) is not None:
                continue
            assignment = self.uow.assignments.get(event.assignment_id)
            if assignment is None:
                raise ValueError("no-show references an unknown inroostering")
            rows.append(NoShowContext(event, _assignment_context(assignment, services, persons)))
        return tuple(rows)

    def current_state(self, person_id: str, season: str) -> CurrentSanctionState:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        return current_sanction_state(
            person_id, season,
            self.uow.no_shows.for_person_season(person_id, season),
            self.uow.no_show_revocations.for_person_season(person_id, season),
        )

    def revoke(self, no_show_id: str, *, reason: str, revoked_at: datetime) -> NoShowRevocation:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        if not reason.strip():
            raise ValueError("Een toelichting voor intrekking is verplicht.")
        if self.uow.no_shows.get(no_show_id) is None:
            raise ValueError("Onbekende no-show.")
        if self.uow.no_show_revocations.for_no_show(no_show_id) is not None:
            raise ValueError("Deze no-show is al ingetrokken.")
        revocation = NoShowRevocation(
            str(uuid4()), no_show_id, reason.strip(), revoked_at, self.identity.subject_id,
        )
        self.uow.no_show_revocations.add(revocation)
        self.uow.commit()
        return revocation


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
    def __init__(self, identity: Identity, authorizer: Authorizer | None = None, uow=None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()
        self.uow = uow

    def active_planning(self) -> tuple[TemporaryPlanning, ...]:
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        return () if self.uow is None else self.uow.temporary_planning.all()

    def staffing_needs(self, *, services, source_needs) -> tuple[StaffingNeed, ...]:
        active = self.active_planning()
        by_id = {service.service_id: service for service in services}
        return tuple(planning_staffing(by_id[need.service_id], need, active) for need in source_needs)

    def assess_candidates(self, *, cases, service, team_memberships, matches, today):
        active = self.active_planning()
        return tuple(assess_candidate(case, service, team_memberships, matches, today,
                                      active_planning=active) for case in cases)

    def temporary_assignment_contexts(self, *, persons=()) -> tuple[AssignmentContext, ...]:
        return tuple(_assignment_context(entry.assignment, (entry.service,), persons)
                     for entry in self.active_planning())

    def build_overview(self, *, period: PlanningPeriod, services: tuple[DutyService, ...], staffing_needs: tuple[StaffingNeed, ...], matches: tuple[Match, ...] = (), source_statuses: tuple[PlanningSourceStatus, ...] = (), data_quality_signals: tuple[DataQualitySignal, ...] = ()) -> PlanningOverview:
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        needs = self.staffing_needs(services=services, source_needs=staffing_needs)
        return build_planning_overview(period=period, services=services, staffing_needs=needs, matches=matches, source_statuses=source_statuses, data_quality_signals=data_quality_signals)


class ProposalDecisionApplicationService:
    """Authorized persistence boundary for human proposal decisions."""

    def __init__(self, identity: Identity, authorizer: Authorizer | None = None, uow=None):
        self.identity = identity
        self.authorizer = authorizer or Authorizer()
        self.uow = uow

    def _add_without_commit(self, proposal: AssignmentProposal, result: DashboardActionResult, service: DutyService | None = None) -> None:
        if self.uow is None:
            return
        self.uow.proposals.add(proposal)
        self.uow.decisions.add(result.decision)
        if result.assignment is not None:
            if service is None:
                raise ValueError("temporary planning requires concrete service context")
            self.uow.temporary_planning.add(TemporaryPlanning(result.assignment, service))

    def _persist(self, proposal: AssignmentProposal, result: DashboardActionResult) -> None:
        self._add_without_commit(proposal, result)
        if self.uow is not None:
            self.uow.commit()

    def approve(self, proposal: AssignmentProposal, service: DutyService, case: PrototypeCase, *, assignment_id: str, staffing_need: StaffingNeed) -> DashboardActionResult:
        return self.approve_many(((proposal, case, assignment_id),), service, staffing_need)[0]

    def approve_many(self, selections: tuple[tuple[AssignmentProposal, PrototypeCase, str], ...], service: DutyService, staffing_need: StaffingNeed) -> tuple[DashboardActionResult, ...]:
        """Confirm against the latest active queue, atomically with persistence.

        staffing_need carries source occupancy and configured bounds. Its cached
        remaining capacity (possibly from an older UI run) is never trusted.
        """
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        if self.uow is None:
            raise ValueError("persistent unit of work required for temporary planning")
        if not selections:
            raise ValueError("at least one candidate must be selected")
        if any(proposal.service_id != service.service_id for proposal, _, _ in selections):
            raise ValueError("all proposals must belong to the selected service")
        proposal_ids = [proposal.proposal_id for proposal, _, _ in selections]
        if len(set(proposal_ids)) != len(proposal_ids):
            raise ValueError("a proposal can only be selected once")

        self.uow.begin_planning_write()
        try:
            active = self.uow.temporary_planning.all()
            validate_planning_selection(tuple(p.person_id for p, _, _ in selections), service, staffing_need, active)
            for proposal, _, _ in selections:
                if planning_conflict(proposal.person_id, service, active) == "same_day" and proposal.suitability != "emergency":
                    raise ValueError("Beoordeel deze kandidaat opnieuw als nood-/uitwijkkandidaat.")
            results = tuple(
                approve_from_dashboard(proposal, service, case, self.identity.subject_id, assignment_id)
                for proposal, case, assignment_id in selections
            )
            for (proposal, _, _), result in zip(selections, results):
                self._add_without_commit(proposal, result, service)
            self.uow.commit()
            return results
        except Exception:
            self.uow.rollback()
            raise

    def undo(self, assignment_id: str) -> None:
        """Remove exactly one active position, without an audit/revocation fact."""
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        if self.uow is None:
            raise ValueError("persistent unit of work required for temporary planning")
        self.uow.begin_planning_write()
        try:
            if not self.uow.temporary_planning.remove(assignment_id):
                raise ValueError("Deze tijdelijke inroostering is niet meer actief.")
            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise

    def reject(self, proposal: AssignmentProposal, case: PrototypeCase, *, reason_category: str, reason: str) -> DashboardActionResult:
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        result = reject_from_dashboard(proposal, case, self.identity.subject_id, reason_category, reason)
        self._persist(proposal, result)
        return result
