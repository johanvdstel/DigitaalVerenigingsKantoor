"""Source-based hours controls; a difference asks for human reassessment."""
from dataclasses import dataclass
from datetime import date

from .member_duty import MemberDutyExpectation
from .model import DutyPolicy
from .real_data_import import DataQualitySignal, DutyImportRecord, Provenance, RealDataImportResult


@dataclass(frozen=True)
class RequiredHoursControl:
    person_id: str
    status: str
    expected_required_hours: int | None
    registered_required_hours: int | float | None
    expectation: MemberDutyExpectation
    duty_records: tuple[DutyImportRecord, ...]
    signals: tuple[DataQualitySignal, ...]
    provenance: tuple[Provenance, ...]
    kind: str = "DERIVED"


def compare_required_hours(source: RealDataImportResult, as_of: date,
                           policy: DutyPolicy | None = None) -> tuple[RequiredHoursControl, ...]:
    records_by_person, provenance_by_person = {}, {}
    general_signals, member_signals, hours_signals = [], {}, {}
    for record in source.duty_records:
        records_by_person.setdefault(record.registration.person_id, []).append(record)
    for fact in source.provenance:
        if fact.source_dataset == "vrijwilligers_periode":
            provenance_by_person.setdefault(fact.source_record_key.split(":", 1)[0], []).append(fact)
    for index, signal in enumerate(source.signals):
        if signal.record_key is None:
            general_signals.append((index, signal))
        else:
            target = hours_signals if signal.dataset == "vrijwilligers_periode" else member_signals
            target.setdefault(signal.record_key.split(":", 1)[0], []).append((index, signal))
    results = []
    for expectation in source.derive_member_duties(as_of, policy):
        pid = expectation.person_id
        records = tuple(records_by_person.get(pid, ()))
        support_ids = {getattr(f, "person_id", pid) for f in expectation.source_facts}
        # Another household/function subject can supply exemption evidence,
        # but that subject's hours never determine this person's A/B/C/D/E.
        selected_signals = general_signals + hours_signals.get(pid, [])
        selected_signals += [entry for sid in support_ids for entry in member_signals.get(sid, ())]
        signals = tuple(signal for _, signal in sorted(selected_signals, key=lambda entry: entry[0]))
        additional = []
        if not records:
            additional.append(DataQualitySignal("MISSING_DUTY_POSITION", "ERROR", "vrijwilligers_periode", pid,
                                                "Geen betrouwbaar gekoppelde urenpositie beschikbaar"))
        elif len(records) > 1:
            additional.append(DataQualitySignal("AMBIGUOUS_DUTY_POSITION", "ERROR", "vrijwilligers_periode", pid,
                                                "Meerdere urenposities; geen regel gekozen"))
        registered = records[0].registration.required_hours if len(records) == 1 else None
        if (expectation.expected_required_hours is None or additional
                or any(s.severity == "ERROR" for s in signals)):
            status = "niet betrouwbaar beoordeelbaar"
        elif registered == expectation.expected_required_hours:
            status = "overeenkomst"
        else:
            status = "afwijking"
            additional.append(DataQualitySignal("REQUIRED_HOURS_REASSESSMENT", "WARNING", "vrijwilligers_periode", pid,
                                                "DVK verwachte A verschilt van menselijk vastgestelde Sportlink A; herbeoordeling nodig"))
        provenance = tuple(provenance_by_person.get(pid, ()))
        results.append(RequiredHoursControl(pid, status, expectation.expected_required_hours, registered,
                                            expectation, records, signals + tuple(additional), provenance))
    return tuple(results)
