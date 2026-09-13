from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
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
