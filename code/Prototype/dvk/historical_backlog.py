"""Optional previous-season Sportlink facts; no season inference or persistence."""
import csv
from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .real_data_import import DataQualitySignal, DutyImportRecord, SportlinkRealDataAdapter

HISTORICAL_FILENAME = "Overzicht per periode vorig seizoen.csv"
DATASET = "historical_duty"


@dataclass(frozen=True)
class HistoricalBacklogSource:
    available: bool
    records: tuple[DutyImportRecord, ...] = ()
    signals: tuple[DataQualitySignal, ...] = ()
    message: str = ""
    loaded_at: datetime | None = None

    @property
    def values(self) -> dict[str, int]:
        """Only unambiguous validated facts; negative source values remain intact."""
        invalid = {s.record_key for s in self.signals}
        return {r.registration.person_id: r.source_remaining_hours for r in self.records
                if r.registration.person_id not in invalid}


def unavailable_history(message: str) -> HistoricalBacklogSource:
    return HistoricalBacklogSource(False, message=message +
        " Historische achterstanden zijn niet meegewogen; planning blijft bruikbaar.")


def import_historical_backlog(text: str, person_ids) -> HistoricalBacklogSource:
    """Reuse CSV and number parsing; never match names or repair mismatched E."""
    try:
        rows = SportlinkRealDataAdapter.read_rows_text(
            text.lstrip("\ufeff"), "vrijwilligers_periode", name=HISTORICAL_FILENAME, strict=True)
        if any(None in row or any(value is None for value in row.values()) for row in rows):
            raise ValueError("invalid row shape")
    except (ValueError, csv.Error):
        return unavailable_history("Historische urenbron is structureel ongeldig. Controleer de CSV-kolommen en regels.")
    counts = Counter(SportlinkRealDataAdapter.value(row, "Relatiecode") for row in rows)
    people = set(person_ids)
    records, signals = [], []
    for row in rows:
        pid = SportlinkRealDataAdapter.value(row, "Relatiecode")
        def signal(code, message):
            signals.append(DataQualitySignal(code, "WARNING", DATASET, pid, message))
        if not pid or pid not in people:
            signal("HISTORICAL_UNMATCHED_PERSON", "Historische bronregel kan niet aan een actueel lid worden gekoppeld.")
        if counts[pid] > 1:
            signal("HISTORICAL_DUPLICATE_PERSON", "Meerdere historische bronregels voor hetzelfde lid; achterstand niet gebruikt.")
        try:
            record = SportlinkRealDataAdapter.parse_duty_record(row)
        except ValueError:
            signal("HISTORICAL_INVALID_HOURS", "Historische urenregel bevat een ongeldig of ontbrekend getal; achterstand niet gebruikt.")
            continue
        records.append(record)
        if not record.source_formula_matches:
            signal("HISTORICAL_FORMULA_MISMATCH", "Historische bronwaarde Niet ingedeeld wijkt af van A − B − C − D; achterstand niet gebruikt.")
    return HistoricalBacklogSource(True, tuple(records), tuple(signals),
                                   "Historische urenbron geladen. De planner is verantwoordelijk voor het juiste vorige seizoen.")
