from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, time, timezone
import csv
import math
import re
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
            if not math.isfinite(duration) or duration <= 0 or not self._valid(minimum, maximum) or any(not self._valid(r.minimum_staff, r.maximum_staff) for r in rules):
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
    date_from: date | None = None
    date_to: date | None = None


@dataclass(frozen=True)
class ShiftCatalog:
    definitions: tuple[ShiftDefinition, ...]
    slots: tuple[WeeklySlot, ...]

    def __post_init__(self):
        codes = [d.task_code for d in self.definitions]
        if not codes or len(set(codes)) != len(codes) or any(not valid_task_code(c) for c in codes):
            raise ValueError("Dienstencatalogus vereist unieke, niet-lege taakcodes zonder spaties")
        if not self.slots:
            raise ValueError("Dienstencatalogus vereist ten minste één roosterregel")
        if len(set(self.slots)) != len(self.slots):
            raise ValueError("Dubbele roosterregel in dienstencatalogus")
        for slot in self.slots:
            if slot.task_code not in codes or not 0 <= slot.weekday <= 6 or slot.ends_at == slot.starts_at:
                raise ValueError("Ongeldige roosterregel: controleer taakcode, weekdag en tijden")
            if slot.starts_at.tzinfo or slot.ends_at.tzinfo:
                raise ValueError("Roostertijden moeten lokale tijden zonder tijdzone zijn")
            if (slot.date_from is None) != (slot.date_to is None):
                raise ValueError("date_from en date_to moeten beide leeg of beide gevuld zijn")
            if slot.date_from and (slot.date_to < slot.date_from or
                    (slot.date_from == slot.date_to and slot.weekday != slot.date_from.weekday())):
                raise ValueError("Ongeldige datumperiode of weekdag in roosterregel")
        # Detect duplicates even where a dated rule overlaps a recurring rule.
        for i, left in enumerate(self.slots):
            for right in self.slots[i + 1:]:
                if (left.weekday, left.starts_at, left.ends_at, left.task_code) != (
                        right.weekday, right.starts_at, right.ends_at, right.task_code):
                    continue
                start = max(left.date_from or date.min, right.date_from or date.min)
                end = min(left.date_to or date.max, right.date_to or date.max)
                if start <= end and (left.weekday - start.weekday()) % 7 <= (end - start).days:
                    raise ValueError("Dubbel concreet dienstmoment in roosterregels")

    @property
    def task_codes(self):
        used = {s.task_code for s in self.slots}
        return tuple(d.task_code for d in self.definitions if d.task_code in used)

    def bindings(self, period):
        from .vrijwilligers_adapter import ServiceBinding
        result = []
        day = period.start
        by_code = {d.task_code: d for d in self.definitions}
        while day <= period.end:
            for slot in self.slots:
                if slot.weekday != day.weekday() or (slot.date_from and not slot.date_from <= day <= slot.date_to):
                    continue
                start = local_moment(day, slot.starts_at)
                end = local_moment(day + timedelta(days=slot.ends_at < slot.starts_at), slot.ends_at)
                service = concrete_service(by_code[slot.task_code], start, end, "Kantine CKC")
                result.append(ServiceBinding(slot.task_code, service))
            day += timedelta(days=1)
        return tuple(result)


def valid_task_code(code):
    return bool(re.fullmatch(r"[A-Za-z0-9_-]+", code))


TZ = ZoneInfo("Europe/Amsterdam")


def local_moment(day, clock):
    """Reject imaginary/ambiguous wall times rather than choosing a DST fold."""
    naive = datetime.combine(day, clock)
    candidates = {naive.replace(tzinfo=TZ, fold=fold).astimezone(timezone.utc)
                  for fold in (0, 1)
                  if naive.replace(tzinfo=TZ, fold=fold).astimezone(timezone.utc).astimezone(TZ).replace(tzinfo=None) == naive}
    if len(candidates) != 1:
        raise ValueError("Ongeldige of niet-eenduidige lokale roostertijd: " + naive.isoformat())
    return candidates.pop().astimezone(TZ)


def service_key(task_code, start, end):
    return (task_code, start.astimezone(timezone.utc), end.astimezone(timezone.utc))


def concrete_service(definition, start, end, location):
    start, end = start.astimezone(TZ), end.astimezone(TZ)
    # Include both actual boundaries; task codes remain distinct service contexts.
    import hashlib
    key = service_key(definition.task_code, start, end)
    identifier = "CKC-" + hashlib.sha256("|".join(str(v) for v in key).encode()).hexdigest()
    minimum, _ = definition.staffing_for("vrijdag" if start.astimezone(TZ).weekday() == 4 else None)
    return DutyService(identifier, definition.service_type, start, end, location, minimum)


class CatalogFileError(ValueError):
    """Local configuration cannot be used; never fall back to packaged data."""


def _rows(folder, filename, fields):
    try:
        with (folder / filename).open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or not set(fields) <= set(reader.fieldnames) or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("Verplichte kolommen ontbreken of zijn dubbel: " + ", ".join(fields))
            rows = list(reader)
            if any(None in r or any(v is None for v in r.values()) for r in rows):
                raise ValueError("Ongeldig aantal CSV-velden")
            return rows
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        reason = str(exc) if isinstance(exc, ValueError) else "bestand ontbreekt of is niet leesbaar als UTF-8 CSV"
        raise CatalogFileError(f"{filename}: {reason}. Verwachte map: {folder}") from None


def load_shift_catalog(folder=None) -> ShiftCatalog:
    from .sportlink_exports import default_export_directory
    folder = Path(folder) if folder is not None else default_export_directory()
    definition_fields = (*ShiftCatalogAdapter.REQUIRED_FIELDS, "friday_minimum", "friday_maximum")
    rows = _rows(folder, "shift_definitions.csv", definition_fields)
    try:
        for row in rows:
            if bool(row["friday_minimum"].strip()) != bool(row["friday_maximum"].strip()):
                raise ValueError("Beide vrijdagbezettingsvelden moeten gevuld of leeg zijn")
            if row["friday_minimum"].strip():
                row["staffing_rules"] = [{"condition": "vrijdag", "minimum_staff": int(row["friday_minimum"]),
                                          "maximum_staff": int(row["friday_maximum"])}]
        imported = ShiftCatalogAdapter().import_rows(rows, imported_at=datetime.now(TZ))
        if imported.signals:
            raise ValueError("; ".join(s.message for s in imported.signals))
        slot_rows = _rows(folder, "shift_week_pattern.csv", ("weekday", "starts_at", "ends_at", "task_code", "date_from", "date_to"))
        slots = tuple(WeeklySlot(int(r["weekday"]), time.fromisoformat(r["starts_at"]), time.fromisoformat(r["ends_at"]),
                                 r["task_code"].strip(), _date(r["date_from"]), _date(r["date_to"])) for r in slot_rows)
        return ShiftCatalog(imported.definitions, slots)
    except ValueError as exc:
        raise CatalogFileError("Ongeldige dienstencatalogus: " + str(exc)) from None


def _date(value):
    value = value.strip()
    if not value:
        return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Datum moet YYYY-MM-DD zijn")
    return date.fromisoformat(value)
