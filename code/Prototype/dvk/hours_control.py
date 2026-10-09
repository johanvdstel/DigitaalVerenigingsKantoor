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
    results = []
    for expectation in source.derive_member_duties(as_of, policy):
        pid = expectation.person_id
        records = tuple(r for r in source.duty_records if r.registration.person_id == pid)
        support_ids = {getattr(f, "person_id", pid) for f in expectation.source_facts}
        signals = tuple(s for s in source.signals if s.record_key is None
                        or s.record_key.split(":", 1)[0] in support_ids)
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
        provenance = tuple(p for p in source.provenance if p.source_dataset == "vrijwilligers_periode"
                           and p.source_record_key.split(":", 1)[0] == pid)
        results.append(RequiredHoursControl(pid, status, expectation.expected_required_hours, registered,
                                            expectation, records, signals + tuple(additional), provenance))
    return tuple(results)
