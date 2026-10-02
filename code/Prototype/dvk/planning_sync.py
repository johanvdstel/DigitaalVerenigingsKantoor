"""Ledendienst Planning lifecycle; source imports remain independent facts."""
from dataclasses import asdict, dataclass, replace
from datetime import date, datetime, timedelta
import json
from uuid import uuid4

from .import_management import ImportBatch, ImportStatus, SnapshotRecord
from .import_workflow import BLOCKING_SEVERITIES, confirm_import
from .planning import PlanningPeriod
from .real_data_import import SportlinkRealDataAdapter
from .security import Authorizer, Permission
from .vrijwilligers_adapter import SportlinkVrijwilligersAdapter, VolunteerBooking, TZ


def sportlink_period(*, today: date, weekoffset: int, days: int) -> PlanningPeriod:
    """CKC-verified: -1=current Monday, 0=next Monday, N inclusive days."""
    if type(weekoffset) is not int or type(days) is not int or days < 1:
        raise ValueError("Kies een geheel aantal weken en minimaal één kalenderdag.")
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=weekoffset + 1)
    return PlanningPeriod(start, start + timedelta(days=days - 1))


def sportlink_parameters(period: PlanningPeriod, *, today: date):
    monday = today - timedelta(days=today.weekday())
    if period.start.weekday() != 0:
        raise ValueError("De Sportlink-planningsperiode moet op maandag beginnen.")
    return {"weekoffset": (period.start - monday).days // 7 - 1,
            "days": (period.end - period.start).days + 1}


@dataclass(frozen=True)
class PlanningState:
    period: PlanningPeriod | None
    revision: int
    sync_id: str | None
    roster_snapshot_id: str | None
    duty_snapshot_id: str | None


def _json(value):
    return json.dumps(value, default=lambda v: v.isoformat(), sort_keys=True)


def require_service_in_period(uow, service):
    state = uow.planning_state.get()
    if state.period is None:
        raise ValueError("Kies eerst expliciet een actieve planningsperiode.")
    if not state.period.contains(service.starts_at) or not state.period.contains(service.ends_at):
        raise ValueError("De dienst valt buiten de actieve planningsperiode.")


class PlanningSyncApplicationService:
    def __init__(self, uow, identity, authorizer=None, *, clock=None):
        self.clock = clock or (lambda: datetime.now(TZ))
        self.uow = uow
        self.identity = identity
        self.authorizer = authorizer or Authorizer()

    def state(self):
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        return self.uow.planning_state.get()

    def select_period(self, period):
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        sportlink_parameters(period, today=self.clock().date())
        self.uow.begin_planning_write()
        try:
            state = self.uow.planning_state.get()
            if state.period != period:
                active = self.uow.temporary_planning.all()
                if active and state.period is not None:
                    raise ValueError("Synchroniseer of gooi de tijdelijke planning weg voordat u de periode wijzigt.")
                if any(not period.contains(e.service.starts_at) or not period.contains(e.service.ends_at) for e in active):
                    raise ValueError("De gekozen periode bevat niet de volledige bestaande werkvoorraad.")
                self.uow.planning_state.select(period)
            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise
        return self.uow.planning_state.get()

    def discard(self):
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        self.uow.begin_planning_write()
        try:
            self.uow.temporary_planning.clear()
            self.uow.planning_state.discard()
            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise

    def _confirm_source(self, sync_id, dataset, records, source_period=None):
        now = datetime.now(TZ)
        batch = ImportBatch(f"{sync_id}:{dataset}", "Sportlink", dataset,
                            source_period, now, self.identity.subject_id,
                            ImportStatus.AWAITING_CONFIRMATION)
        self.uow.import_batches.add(batch)
        return confirm_import(self.uow, batch, records, snapshot_id=str(uuid4()),
                              confirmed_at=now, confirmed_by=self.identity.subject_id)

    def synchronize(self, *, csv_content: bytes, current_export_confirmed: bool,
                    client, client_id, bindings, persons):
        """Each call requires a newly offered export and makes fresh API requests.

        No snapshot IDs or cached import results can be supplied as evidence.
        The user's explicit declaration establishes export freshness, not a hash
        or timestamp (unchanged fresh exports may contain identical bytes).
        """
        self.authorizer.require(self.identity, Permission.DECIDE_PROPOSAL)
        self.authorizer.require(self.identity, Permission.CONFIRM_IMPORT)
        if current_export_confirmed is not True or not isinstance(csv_content, bytes) or not csv_content:
            raise ValueError("Bied voor deze synchronisatie de actuele Sportlink CSV aan en bevestig dit.")
        initial = self.state()
        if initial.period is None:
            raise ValueError("Kies eerst een actieve planningsperiode.")
        params = sportlink_parameters(initial.period, today=self.clock().date())
        bindings = tuple(replace(b, service=replace(b.service, starts_at=_local(b.service.starts_at),
                                                   ends_at=_local(b.service.ends_at))) for b in bindings)
        if not bindings or any(not b.task_code.strip() for b in bindings):
            raise ValueError("Sportlink-taakcodes voor de actieve diensten ontbreken.")
        for binding in bindings:
            require_service_in_period(self.uow, binding.service)
        active = self.uow.temporary_planning.all()
        if any(not any(e.service.service_id == b.service.service_id
                       and _local(e.service.starts_at) == _local(b.service.starts_at)
                       and _local(e.service.ends_at) == _local(b.service.ends_at) for b in bindings)
               for e in active):
            raise ValueError("De roosteropvraag dekt niet de volledige tijdelijke planning.")
        persons = tuple(persons)
        person_ids = {p.person_id for p in persons}
        if not person_ids or len(person_ids) != len(persons) or any(e.assignment.person_id not in person_ids for e in active):
            raise ValueError("De relevante leden ontbreken of zijn niet eenduidig.")
        sync_id = str(uuid4())
        try:
            roster_records = []
            adapter = SportlinkVrijwilligersAdapter()
            for task_code in sorted({b.task_code for b in bindings}):
                if sportlink_parameters(initial.period, today=self.clock().date()) != params:
                    raise ValueError("De API-periode veranderde tijdens de synchronisatie; probeer opnieuw.")
                fetched = client.fetch_rows(client_id=client_id, task_code=task_code, **params)
                if sportlink_parameters(initial.period, today=self.clock().date()) != params:
                    raise ValueError("De kalenderweek veranderde tijdens de opvraag; synchroniseer opnieuw.")
                if fetched.task_code != task_code:
                    raise ValueError("Sportlink-resultaat hoort niet bij de opgevraagde taak.")
                result = adapter.import_rows(task_code=task_code, rows=fetched.rows,
                                             services=bindings, imported_at=datetime.now(TZ))
                if any(s.severity in BLOCKING_SEVERITIES for s in result.signals):
                    raise ValueError("Roosterimport geblokkeerd: " + "; ".join(s.message for s in result.signals))
                for row, booking, provenance in zip(fetched.rows, result.bookings, result.provenance):
                    roster_records.append(SnapshotRecord("", provenance.source_record_key,
                        _json(row), _json(asdict(booking)), _json(asdict(provenance))))
            roster = self._confirm_source(sync_id, "vrijwilligers_rooster", tuple(roster_records),
                                         f"{initial.period.start.isoformat()}/{initial.period.end.isoformat()}")

            adapter = SportlinkRealDataAdapter()
            rows = adapter.parse_csv(csv_content.decode("utf-8-sig"), "vrijwilligers_periode")
            duties, provenance, signals = adapter.import_duty_rows(
                rows, person_ids=person_ids, imported_at=datetime.now(TZ))
            if any(s.severity in BLOCKING_SEVERITIES for s in signals):
                raise ValueError("CSV-import geblokkeerd: " + "; ".join(s.message for s in signals))
            ids = [d.registration.person_id for d in duties]
            if len(ids) != len(set(ids)) or set(ids) != person_ids:
                raise ValueError("De CSV moet voor ieder relevant lid precies één urenpositie bevatten.")
            records = tuple(SnapshotRecord("", d.registration.person_id, _json(row),
                                           _json(asdict(d.registration)), _json(asdict(p)))
                            for row, d, p in zip(rows, duties, provenance))
            duty = self._confirm_source(sync_id, "vrijwilligers_periode", records)
            self._complete(sync_id, initial, roster, duty)
            return self.state()
        except Exception:
            self.uow.rollback()
            raise

    def _complete(self, sync_id, initial, roster, duty):
        self.uow.begin_planning_write()
        try:
            if self.uow.planning_state.get() != initial:
                raise ValueError("De planning is tijdens synchronisatie gewijzigd; synchroniseer opnieuw.")
            for snapshot, dataset in ((roster, "vrijwilligers_rooster"), (duty, "vrijwilligers_periode")):
                stored = self.uow.snapshots.get(snapshot.snapshot_id)
                batch = self.uow.import_batches.get(snapshot.import_batch_id)
                if (stored != snapshot or snapshot.import_batch_id != f"{sync_id}:{dataset}"
                        or snapshot.dataset_type != dataset or batch is None
                        or batch.status is not ImportStatus.CONFIRMED):
                    raise ValueError("Beide verse bronnen van deze synchronisatie zijn vereist.")
            self.uow.planning_state.complete(sync_id, roster.snapshot_id, duty.snapshot_id)
            self.uow.temporary_planning.clear()
            self.uow.commit()
        except Exception:
            self.uow.rollback()
            raise

    def bookings(self):
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        return read_bookings(self.uow)

    def current_cases(self, cases):
        from .model import SportlinkDutyRegistration
        state = self.state()
        if state.duty_snapshot_id is None:
            return tuple(cases)
        registrations = {r.record_key: SportlinkDutyRegistration(**json.loads(r.canonical_payload))
                         for r in self.uow.snapshots.records(state.duty_snapshot_id)}
        cases = tuple(cases)
        if any(case.person.person_id not in registrations for case in cases):
            raise ValueError("Een relevant lid ontbreekt in de actuele Sportlink Vrijwilligers-snapshot.")
        return tuple(replace(case, sportlink_duty=registrations[case.person.person_id]) for case in cases)


def _local(moment):
    return moment.replace(tzinfo=TZ) if moment.tzinfo is None else moment.astimezone(TZ)


def source_staffing(service, need, bookings):
    if bookings is None:
        return need
    occupancy = sum(b.service_id == service.service_id and b.starts_at == _local(service.starts_at)
                    and b.ends_at == _local(service.ends_at) for b in bookings)
    return replace(need, confirmed_occupancy=occupancy)


def source_availability(assessment, case, cases, service, bookings):
    # Exact visible names only; privacy placeholders never supply identity.
    matching = tuple(b for b in bookings if b.volunteer_name != "Afgeschermd"
                     and b.volunteer_name == case.person.name
                     and sum(c.person.name == b.volunteer_name for c in cases) == 1)
    start, end = _local(service.starts_at), _local(service.ends_at)
    if assessment.eligible and any(b.starts_at < end and b.ends_at > start for b in matching):
        return replace(assessment, eligible=False, preference="none",
                       exclusion_reason="Overlapt met een feitelijke Sportlink-inroostering")
    if assessment.eligible and any(b.starts_at.date() == start.date() for b in matching):
        return replace(assessment, preference="avoid", planning_relation="same_day_emergency")
    return assessment


def read_bookings(uow):
    state = uow.planning_state.get()
    if state.roster_snapshot_id is None:
        return None
    snapshot = uow.snapshots.get(state.roster_snapshot_id)
    if state.period is None or snapshot.source_period != f"{state.period.start.isoformat()}/{state.period.end.isoformat()}":
        return None
    records = uow.snapshots.records(state.roster_snapshot_id)
    result = []
    for record in records:
        values = json.loads(record.canonical_payload)
        for field in ("starts_at", "ends_at"):
            values[field] = datetime.fromisoformat(values[field])
        result.append(VolunteerBooking(**values))
    return tuple(result)



def validate_source_selection(uow, selections, service, bookings):
    """A proposal from before synchronization cannot override new source facts."""
    state = uow.planning_state.get()
    if state.duty_snapshot_id is None:
        return
    registrations = {r.record_key: json.loads(r.canonical_payload)
                     for r in uow.snapshots.records(state.duty_snapshot_id)}
    for proposal, case, _ in selections:
        registration = registrations.get(proposal.person_id)
        if registration is None or tuple(registration[k] for k in (
                "required_hours", "correction_hours", "completed_hours", "scheduled_hours")) != (
                proposal.A, proposal.B, proposal.C, proposal.D):
            raise ValueError("De Sportlink-urenpositie is gewijzigd; beoordeel de kandidaat opnieuw.")
        matching = tuple(b for b in bookings or () if b.volunteer_name != "Afgeschermd"
                         and b.volunteer_name == case.person.name)
        if any(b.starts_at < _local(service.ends_at) and b.ends_at > _local(service.starts_at) for b in matching):
            raise ValueError("De kandidaat heeft een overlappende Sportlink-inroostering.")
        if any(b.starts_at.date() == _local(service.starts_at).date() for b in matching) and proposal.suitability != "emergency":
            raise ValueError("Beoordeel deze kandidaat opnieuw als nood-/uitwijkkandidaat.")
