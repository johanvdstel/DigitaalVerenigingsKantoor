"""Minimal local diagnostic presentation; never repair or re-import source rows."""
from dataclasses import dataclass
from .sportlink_exports import EXPORT_FILENAMES


@dataclass(frozen=True)
class SourceDiagnostic:
    code: str
    filename: str
    description: str
    person_id: str
    name: str
    row_number: int | None
    values: tuple[tuple[str, str], ...]


def source_diagnostics(source, program=None):
    names = {person.person_id: person.name for person in source.persons}
    result = []
    for signal in source.signals:
        key = signal.record_key or ""
        records = tuple(record for record in source.diagnostic_records if record.dataset == signal.dataset
                        and (str(record.row_number) == key if signal.code == "UNMATCHED_PERSON_REFERENCE"
                             else record.person_id == key.split(":", 1)[0]))
        for record in records or (None,):
            values = dict(record.values) if record else {}
            pid = record.person_id if record else key.split(":", 1)[0]
            # Birth date is necessary only to explain an identity/date conflict.
            if signal.code not in {"CONFLICTING_DUPLICATE_IDENTITY", "INVALID_BIRTH_DATE"}:
                values.pop("Geb.dat.", None)
                values.pop("Geboortedatum", None)
            result.append(SourceDiagnostic(signal.code, EXPORT_FILENAMES.get(signal.dataset, signal.dataset),
                signal.message, pid, values.get("Naam", names.get(pid, "")),
                record.row_number if record else None, tuple(values.items())))
    if program is not None:
        for signal in program.signals:
            links = tuple(link for link in program.links if link.record_key == signal.record_key)
            values = tuple((field, value) for link in links for field, value in (
                ("Oorspronkelijke teamnaam", link.original_team_name or ""),
                ("Competitie", link.competition), ("Competitiesoort", link.competition_type)))
            result.append(SourceDiagnostic(signal.code, "Programma API", signal.message, "", "", None, values))
    return tuple(result)
