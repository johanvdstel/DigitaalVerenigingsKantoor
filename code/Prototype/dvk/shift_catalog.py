from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, time
import csv
from pathlib import Path
from zoneinfo import ZoneInfo
from typing import Iterable

from .real_data_import import DataQualitySignal, Provenance
from .workstream_model import DutyService


@dataclass(frozen=True)
class StaffingRule:
    condition: str
    minimum_staff: int
    maximum_staff: int


@dataclass(frozen=True)
class ShiftDefinition:
    task_code: str
    service_type: str
    duration_hours: float
    minimum_staff: int
    maximum_staff: int
    staffing_rules: tuple[StaffingRule, ...] = ()

    def staffing_for(self, condition: str | None = None) -> tuple[int, int]:
        if condition:
            for rule in self.staffing_rules:
                if rule.condition == condition:
                    return rule.minimum_staff, rule.maximum_staff
        return self.minimum_staff, self.maximum_staff

    def candidate_target(self, condition: str | None = None) -> int:
        return self.staffing_for(condition)[1]


@dataclass(frozen=True)
class ShiftCatalogImportResult:
    definitions: tuple[ShiftDefinition, ...]
    provenance: tuple[Provenance, ...]
    signals: tuple[DataQualitySignal, ...]


class ShiftCatalogAdapter:
    REQUIRED_FIELDS = (
        "task_code", "service_type", "duration_hours", "minimum_staff", "maximum_staff",
    )

    def import_rows(self, rows: Iterable[dict[str, object]], *, imported_at: datetime) -> ShiftCatalogImportResult:
        definitions: list[ShiftDefinition] = []
        provenance: list[Provenance] = []
        signals: list[DataQualitySignal] = []
        seen_codes: set[str] = set()

        for index, row in enumerate(rows, 1):
            code = self._value(row, "task_code")
            key = code or str(index)
            missing = [field for field in self.REQUIRED_FIELDS if self._value(row, field) == ""]
            if missing:
                signals.append(DataQualitySignal("INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", key, f"Verplichte ShiftCatalog-velden ontbreken: {', '.join(missing)}"))
                continue
            if code in seen_codes:
                signals.append(DataQualitySignal("DUPLICATE_SHIFT_CODE", "ERROR", "shift_catalog", code, "Taakcode komt meer dan eenmaal voor in ShiftCatalog"))
                continue
            try:
                duration = float(self._value(row, "duration_hours").replace(",", "."))
                minimum = int(self._value(row, "minimum_staff"))
                maximum = int(self._value(row, "maximum_staff"))
                rules = self._rules(row.get("staffing_rules"))
            except (TypeError, ValueError, KeyError):
                signals.append(DataQualitySignal("INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", code, "Ongeldige duur, bezetting of conditionele bezettingsregel"))
                continue
            if duration <= 0 or not self._valid(minimum, maximum) or any(not self._valid(r.minimum_staff, r.maximum_staff) for r in rules):
                signals.append(DataQualitySignal("INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", code, "ShiftCatalog vereist duur > 0 en 0 <= minimum_staff <= maximum_staff"))
                continue
            conditions = [r.condition for r in rules]
            if len(conditions) != len(set(conditions)):
                signals.append(DataQualitySignal("DUPLICATE_STAFFING_RULE", "ERROR", "shift_catalog", code, "Een conditionele bezettingsregel mag per taakcode maar eenmaal voorkomen"))
                continue
            definition = ShiftDefinition(code, self._value(row, "service_type"), duration, minimum, maximum, rules)
            definitions.append(definition)
            seen_codes.add(code)
            provenance.append(Provenance("CKC", "ShiftCatalog", code, imported_at, kind="CONFIGURATION", source_value=str(dict(row)), normalized_value=str(definition)))

        return ShiftCatalogImportResult(tuple(definitions), tuple(provenance), tuple(signals))

    @staticmethod
    def create_service(definition: ShiftDefinition, *, service_id: str, starts_at: datetime, location: str, condition: str | None = None) -> DutyService:
        minimum, _ = definition.staffing_for(condition)
        return DutyService(service_id=service_id, service_type=definition.service_type, starts_at=starts_at, ends_at=starts_at + timedelta(hours=definition.duration_hours), location=location, required_staff=minimum)

    @staticmethod
    def _rules(value: object) -> tuple[StaffingRule, ...]:
        if value in (None, ""):
            return ()
        if not isinstance(value, (list, tuple)):
            raise TypeError
        return tuple(StaffingRule(str(item["condition"]).strip(), int(item["minimum_staff"]), int(item["maximum_staff"])) for item in value)

    @staticmethod
    def _valid(minimum: int, maximum: int) -> bool:
        return minimum >= 0 and maximum >= minimum

    @staticmethod
    def _value(row: dict[str, object], field: str) -> str:
        return str(row.get(field) or "").strip()


@dataclass(frozen=True)
class WeeklySlot:
    weekday: int
    starts_at: time
    ends_at: time
    task_code: str


@dataclass(frozen=True)
class ShiftCatalog:
    definitions: tuple[ShiftDefinition, ...]
    slots: tuple[WeeklySlot, ...]

    def __post_init__(self):
        codes = [d.task_code for d in self.definitions]
        if not codes or len(set(codes)) != len(codes):
            raise ValueError("Dienstencatalogus vereist unieke actieve taakcodes")
        if len(set(self.slots)) != len(self.slots):
            raise ValueError("Dubbel weekpatroon in dienstencatalogus")
        for slot in self.slots:
            definition = next((d for d in self.definitions if d.task_code == slot.task_code), None)
            if definition is None or not 0 <= slot.weekday <= 6 or slot.ends_at <= slot.starts_at:
                raise ValueError("Ongeldig weekpatroon in dienstencatalogus")
            duration = (datetime.combine(datetime.min.date(), slot.ends_at) -
                        datetime.combine(datetime.min.date(), slot.starts_at)).total_seconds() / 3600
            if duration != definition.duration_hours:
                raise ValueError("Weekpatroon wijkt af van de catalogusduur")

    @property
    def task_codes(self):
        return tuple(d.task_code for d in self.definitions)

    def bindings(self, period):
        from .vrijwilligers_adapter import ServiceBinding
        result = []
        day = period.start
        by_code = {d.task_code: d for d in self.definitions}
        while day <= period.end:
            for slot in self.slots:
                if slot.weekday != day.weekday():
                    continue
                definition = by_code[slot.task_code]
                start = datetime.combine(day, slot.starts_at, ZoneInfo("Europe/Amsterdam"))
                service = ShiftCatalogAdapter.create_service(
                    definition, service_id=f"CKC-{slot.task_code}-{day.isoformat()}-{slot.starts_at:%H%M}",
                    starts_at=start, location="Kantine CKC",
                    condition="vrijdag" if day.weekday() == 4 else None)
                result.append(ServiceBinding(slot.task_code, service))
            day += timedelta(days=1)
        return tuple(result)


def load_shift_catalog() -> ShiftCatalog:
    """Configuration transcribed from CKC Shift Catalog.xlsx (Diensten/Rooster).

    Code 721 is explicitly unused. Friday staffing is an existing catalog rule.
    No personal data or runtime Excel dependency is involved.
    """
    folder = Path(__file__).with_name("configuration")
    with (folder / "shift_definitions.csv").open() as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        if row["friday_minimum"]:
            row["staffing_rules"] = [{"condition": "vrijdag", "minimum_staff": int(row["friday_minimum"]),
                                      "maximum_staff": int(row["friday_maximum"])}]
    imported = ShiftCatalogAdapter().import_rows(rows, imported_at=datetime(2026, 10, 21, tzinfo=ZoneInfo("Europe/Amsterdam")))
    if imported.signals:
        raise ValueError("Ongeldige CKC-dienstencatalogus")
    with (folder / "shift_week_pattern.csv").open() as handle:
        slots = tuple(WeeklySlot(int(r["weekday"]), time.fromisoformat(r["starts_at"]),
                                 time.fromisoformat(r["ends_at"]), r["task_code"]) for r in csv.DictReader(handle))
    return ShiftCatalog(imported.definitions, slots)
