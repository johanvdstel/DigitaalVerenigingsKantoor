from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import uuid4

from .candidate_selection import assess_candidate
from .team_matchday import validate_emergency_selection
from .planning_workqueue import TemporaryPlanning, planning_conflict, planning_staffing, validate_planning_selection
from .dashboard_actions import DashboardActionResult, approve_from_dashboard, reject_from_dashboard
from .import_management import ImportBatch, SnapshotDifference, SnapshotRecord, SourceSnapshot
from .import_workflow import confirm_import, preview_differences
from .model import Person, PrototypeCase
from .no_show import (
    CurrentSanctionState, NoShowEvent, NoShowRevocation, SanctionAssessment,
    assess_sanction, current_sanction_state, season_id, ManualServiceContext,
    validate_registration_time, duplicate_events, MANUAL_DECLARATION,
)
from .planning_session import TZ, active_source, booking_in_period
from .planning import PlanningOverview, PlanningPeriod, PlanningSourceStatus, build_planning_overview
from .real_data_import import DataQualitySignal
from .run_context import EngineRun
from .security import Authorizer, Identity, Permission
from .staffing import StaffingNeed
from .workstream_model import AssignmentProposal, DutyAssignment, DutyService, Match
from .vrijwilligers_adapter import VolunteerBooking, SportlinkVrijwilligersAdapter, booking_identity_report


@dataclass(frozen=True)
class AssignmentContext:
    assignment: DutyAssignment | VolunteerBooking | ManualServiceContext
    service: DutyService | None
    person_name: str | None
    source_revision: str | None = field(default=None, compare=False)


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

    def __init__(self, uow, identity: Identity, authorizer: Authorizer | None = None, *, clock=None):
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()
        self.clock = clock or (lambda: datetime.now(TZ))

    def available_assignments(self, limit: int | None = None, *, period=None):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        session = active_source(self.uow, period)
        if session is None:
            return ()
        bookings = (b for b in self.uow.sportlink_bookings.recent(None)
                    if b.can_register_no_show and booking_in_period(b, session.period))
        return tuple(sorted(bookings, key=lambda b: (
            b.starts_at.astimezone(TZ).date(), b.starts_at.astimezone(TZ).time(),
            b.service.service_type if b.service else "", b.volunteer_name, b.assignment_id,
        )))[:limit]

    def assignment_contexts(self, *, services: tuple[DutyService, ...] = (), persons: tuple[Person, ...] = (), limit: int | None = None, period=None) -> tuple[AssignmentContext, ...]:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        session = active_source(self.uow, period)
        if session is None:
            return ()
        assignments = self.available_assignments(limit, period=period)
        if active_source(self.uow, period) != session:
            return ()
        return tuple(AssignmentContext(a, a.service, a.person_name, session.source_revision) for a in assignments)

    def synchronize(self, *, client, client_id, bindings, persons, imported_at, days=60, weekoffset=-1,
                    task_codes=None, period=None, refresh_state=None, catalog_overlap=False, confirmed=False, source_revision=None, planning_definitions=(), planning_catalog=None):
        """Fetch through the accepted client/adapter; publish only a valid full refresh."""
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        session = self.uow.planning_sessions.get()
        if session is None or (period is not None and period != session.period):
            raise ValueError("Kies eerst de actieve planningsperiode.")
        if (session.source_revision or self.uow.temporary_planning.all()) and (not confirmed or source_revision != session.source_revision):
            raise ValueError("Bevestig vervanging van de actieve Sportlink-bron en tijdelijke indelingen.")
        bindings = tuple(bindings)
        persons = tuple(persons)
        if (not bindings and task_codes is None) or any(not b.task_code.strip() for b in bindings):
            raise ValueError("Sportlink-synchronisatie vereist concrete diensten en taakcodes")
        bookings, signals = [], []
        codes = sorted({b.task_code for b in bindings}) if task_codes is None else tuple(task_codes)
        if not codes or len(set(codes)) != len(codes) or any(not c.strip() for c in codes):
            raise ValueError("Sportlink-synchronisatie vereist unieke taakcodes")
        for task_code in codes:
            fetched = client.fetch_rows(client_id=client_id, task_code=task_code, days=days, weekoffset=weekoffset)
            result = SportlinkVrijwilligersAdapter().import_rows(task_code=task_code, rows=fetched.rows,
                services=bindings, imported_at=imported_at, persons=persons, period=period, catalog_overlap=catalog_overlap, planning_definitions=planning_definitions)
            bookings.extend(result.bookings)
            signals.extend(result.signals)
        if any(s.severity == "ERROR" for s in signals):
            return tuple(signals)
        self.uow.begin_planning_write()
        if self.uow.planning_sessions.get() != session:
            raise ValueError("De planning of bron is gewijzigd; synchroniseer opnieuw na bevestiging.")
        if self.uow.temporary_planning.all() and not confirmed:
            raise ValueError("Bevestig het vervallen van tijdelijke indelingen.")
        try:
            revision = str(uuid4())
            self.uow.sportlink_bookings.replace_all(bookings)
            for entry in self.uow.temporary_planning.all():
                self.uow.temporary_planning.remove(entry.assignment.assignment_id)
            if refresh_state is None:
                refresh_state = dict(start=session.period.start.isoformat(), end=session.period.end.isoformat(),
                    fetched_at=imported_at.isoformat(), codes=list(codes),
                    tasks=[dict(task_code=code) for code in codes])
            if refresh_state is not None:
                refresh_state = dict(refresh_state, session_id=session.session_id, source_revision=revision)
                refresh_state["tasks"] = [dict(row, bookings=sum(b.task_code == row["task_code"] for b in bookings))
                                          for row in refresh_state["tasks"]]
                refresh_state["identity"] = booking_identity_report(bookings)
                refresh_state["status"] = "Geslaagd, met aandachtspunten" if any(s.severity == "WARNING" for s in signals) else "Geslaagd"
                self.uow.sportlink_bookings.save_refresh_state(refresh_state)
                self.uow.sportlink_bookings.save_refresh_state(dict(
                    start=refresh_state["start"], end=refresh_state["end"], at=refresh_state["fetched_at"],
                    status=refresh_state["status"], message="", codes=refresh_state["codes"],
                    tasks=refresh_state["tasks"], session_id=session.session_id), "attempt")
            self.uow.planning_sessions.save(replace(session, source_revision=revision, catalog=session.catalog or planning_catalog))
            self.uow.commit()
        except BaseException:
            self.uow.rollback()
            raise
        return tuple(signals)

    def register(self, event: NoShowEvent, *, source_revision=None, period=None, acknowledged_possible=()) -> SanctionAssessment:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        if event.recorded_by != self.identity.subject_id:
            raise ValueError("no-show recorded_by must match authenticated identity")
        self.uow.begin_planning_write()
        session = active_source(self.uow, period)
        if session is None or source_revision is None or session.source_revision != source_revision:
            raise ValueError("De actieve gevalideerde bron is gewijzigd of ontbreekt; selecteer de inroostering opnieuw.")
        assignment = self.uow.sportlink_bookings.get(event.assignment_id)
        if assignment is None:
            raise ValueError("no-show must reference an existing inroostering")
        if not booking_in_period(assignment, session.period):
            raise ValueError("Inroostering valt buiten de actieve planningsperiode")
        if not assignment.can_register_no_show:
            raise ValueError("No-show vereist een betrouwbare, unieke persoonskoppeling")
        if assignment.person_id != event.person_id:
            raise ValueError("no-show person must match inroostering")
        if assignment.service is None or assignment.provenance is None or assignment.provenance.source_system != "Sportlink" or assignment.provenance.kind != "SOURCE_FACT":
            raise ValueError("no-show requires Sportlink source provenance")
        if event.occurred_at != assignment.starts_at:
            raise ValueError("no-show occurrence must match Sportlink service start")
        event = replace(event, booking=assignment)
        return self._save_event(event, acknowledged_possible=acknowledged_possible)

    def _save_event(self, event, *, acknowledged_possible=()):
        # All registration routes share the same transaction, clock and duplicate rules.
        self.uow.begin_planning_write()
        now = self.clock()
        context = event.context
        validate_registration_time(context.starts_at, context.ends_at, now)
        event = replace(event, recorded_at=now)
        events = self.uow.no_shows.all()
        revocations = tuple(r for e in events
                            if (r := self.uow.no_show_revocations.for_no_show(e.no_show_id)) is not None)
        exact, possible = duplicate_events(context, events, revocations)
        if exact:
            raise ValueError("voor deze inroostering is al een no-show geregistreerd")
        if {e.no_show_id for e in possible} - set(acknowledged_possible):
            raise ValueError("Mogelijk duplicaat: controleer de bestaande registraties en bevestig expliciet doorgaan")
        prior = self.uow.no_shows.for_person_season(event.person_id, event.season)
        revoked = self.uow.no_show_revocations.for_person_season(event.person_id, event.season)
        assessment = assess_sanction(event, prior, revoked)
        self.uow.no_shows.add(event)
        self.uow.sanctions.add(assessment)
        self.uow.commit()
        return assessment

    def registration_choices(self, bookings):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        choices = []
        for booking in bookings:
            if not booking.can_register_no_show:
                continue
            try:
                validate_registration_time(booking.starts_at, booking.ends_at, self.clock())
            except ValueError:
                continue
            choices.append(booking)
        return tuple(sorted(choices, key=lambda b: (b.starts_at, b.person_name or "", b.assignment_id)))

    def duplicate_check(self, context):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        events = self.uow.no_shows.all()
        revocations = tuple(r for e in events
                            if (r := self.uow.no_show_revocations.for_no_show(e.no_show_id)) is not None)
        return duplicate_events(context, events, revocations)

    def manual_context(self, *, person_id, persons, catalog, task_code, description,
                       start_day, start_time, end_day, end_time, other=False,
                       location="", explanation="", confirmed=False):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        from .shift_catalog import local_moment
        matches = tuple(p for p in persons if p.person_id == person_id)
        if not matches or any(p.volunteer_identity_conflicting or p != matches[0] for p in matches):
            raise ValueError("Selecteer een betrouwbaar geïdentificeerd lid uit Leden.csv")
        person = matches[0]
        if not person.name.strip():
            raise ValueError("Leesbare persoonsnaam ontbreekt in Leden.csv")
        if not confirmed:
            raise ValueError("De bevestigingsverklaring is verplicht")
        if other:
            if not description.strip():
                raise ValueError("Een omschrijving voor Andere dienst is verplicht")
            # Explicit CKC decision: entered historical codes remain unverified.
            task_code = task_code.strip() or None
        else:
            definition = next((d for d in catalog.definitions if d.task_code == task_code), None)
            if definition is None:
                raise ValueError("Selecteer een dienst uit de actuele catalogus")
            description = definition.service_type
        start, end = local_moment(start_day, start_time), local_moment(end_day, end_time)
        validate_registration_time(start, end, self.clock())
        return ManualServiceContext(person.person_id, person.name, task_code, not other,
                                    description.strip(), start, end, location.strip(), explanation.strip(),
                                    MANUAL_DECLARATION, True)

    def register_manual(self, *, acknowledged_possible=(), **inputs):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        # Caller supplies freshly loaded source persons/catalog, never a claimed booking.
        context = self.manual_context(**inputs)
        event = NoShowEvent(str(uuid4()), "MANUAL-" + str(uuid4()), context.person_id,
                            context.starts_at, self.clock(), self.identity.subject_id,
                            season_id(context.starts_at.astimezone(TZ).date()), manual=context)
        return self._save_event(event, acknowledged_possible=acknowledged_possible)

    def register_booking(self, selected, *, source, acknowledged_possible=()):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        booking = source.verify(selected, self.clock())
        if (not booking.can_register_no_show or booking.service is None or booking.provenance is None
                or booking.provenance.source_system != "Sportlink" or booking.provenance.kind != "SOURCE_FACT"):
            raise ValueError("No-show vereist een betrouwbare Sportlink-inroostering met provenance")
        event = NoShowEvent(str(uuid4()), booking.assignment_id, booking.person_id,
                            booking.starts_at.astimezone(TZ), self.clock(), self.identity.subject_id,
                            season_id(booking.starts_at.astimezone(TZ).date()), booking)
        return self._save_event(event, acknowledged_possible=acknowledged_possible)

    def history(self, *, season=None, person_id=None, status=None):
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        result = []
        for event in self.uow.no_shows.all():
            revocation = self.uow.no_show_revocations.for_no_show(event.no_show_id)
            if season is not None and event.season != season:
                continue
            if person_id is not None and event.person_id != person_id:
                continue
            if status is not None and status != ("Ingetrokken" if revocation else "Actief"):
                continue
            result.append((event, revocation))
        return tuple(result)

    def revocable_no_shows(self, *, services: tuple[DutyService, ...] = (), persons: tuple[Person, ...] = ()) -> tuple[NoShowContext, ...]:
        self.authorizer.require(self.identity, Permission.MANAGE_NO_SHOWS)
        rows = []
        for event in self.uow.no_shows.all():
            if self.uow.no_show_revocations.for_no_show(event.no_show_id) is not None:
                continue
            assignment = event.context
            if assignment is None:
                raise ValueError("no-show references an unknown inroostering")
            rows.append(NoShowContext(event, AssignmentContext(assignment, assignment.service, assignment.person_name)))
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
        self.uow.begin_planning_write()
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

    def assess_candidates(self, *, cases, service, team_memberships, matches, today, duty_qualifications=None):
        active = self.active_planning()
        return tuple(assess_candidate(case, service, team_memberships, matches, today,
                                      active_planning=active,
                                      qualification=(None if duty_qualifications is None else
                                                     duty_qualifications[case.person.person_id])) for case in cases)

    def selection_problem(self, *, person_ids, service, staffing_need):
        """Present the existing selection guard; approval rechecks atomically."""
        try:
            validate_planning_selection(tuple(person_ids), service, staffing_need, self.active_planning())
        except ValueError as exc:
            messages = {
                "selection exceeds remaining service capacity": "U heeft meer kandidaten geselecteerd dan er plaatsen beschikbaar zijn.",
                "a person can only be selected once for the same service": "Een kandidaat kan maar één keer voor dezelfde dienst worden geselecteerd.",
            }
            return messages.get(str(exc), str(exc))
        return None

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
            validate_emergency_selection(tuple(p for p, _, _ in selections),
                                         planning_staffing(service, staffing_need, active))
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
