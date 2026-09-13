from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable

from .real_data_import import DataQualitySignal, Provenance
from .workstream_model import DutyService


@dataclass(frozen=True)
class ShiftDefinition:
    task_code: str
    pattern: str
    service_type: str
    duration_hours: float
    minimum_staff: int
    maximum_staff: int


@dataclass(frozen=True)
class ShiftCatalogImportResult:
    definitions: tuple[ShiftDefinition, ...]
    provenance: tuple[Provenance, ...]
    signals: tuple[DataQualitySignal, ...]


class ShiftCatalogAdapter:
    """Read CKC shift definitions as configuration, separate from duty occupancy."""

    REQUIRED_FIELDS = (
        "task_code",
        "pattern",
        "service_type",
        "duration_hours",
        "minimum_staff",
        "maximum_staff",
    )

    def import_rows(
        self,
        rows: Iterable[dict[str, object]],
        *,
        imported_at: datetime,
    ) -> ShiftCatalogImportResult:
        definitions: list[ShiftDefinition] = []
        provenance: list[Provenance] = []
        signals: list[DataQualitySignal] = []
        seen_keys: set[tuple[str, str]] = set()

        for index, row in enumerate(rows, 1):
            raw_code = self._value(row, "task_code")
            raw_pattern = self._value(row, "pattern")
            key = f"{raw_code}:{raw_pattern}" if raw_code or raw_pattern else str(index)
            missing = [field for field in self.REQUIRED_FIELDS if self._value(row, field) == ""]
            if missing:
                signals.append(DataQualitySignal(
                    "INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", key,
                    f"Verplichte ShiftCatalog-velden ontbreken: {', '.join(missing)}",
                ))
                continue

            code = raw_code
            pattern = raw_pattern
            natural_key = (code, pattern)
            if natural_key in seen_keys:
                signals.append(DataQualitySignal(
                    "DUPLICATE_SHIFT_DEFINITION", "ERROR", "shift_catalog", key,
                    "Combinatie taakcode en patroon komt meer dan eenmaal voor in ShiftCatalog",
                ))
                continue

            try:
                duration = float(self._value(row, "duration_hours").replace(",", "."))
                minimum = int(self._value(row, "minimum_staff"))
                maximum = int(self._value(row, "maximum_staff"))
            except ValueError:
                signals.append(DataQualitySignal(
                    "INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", key,
                    "Duur en bezettingsgrenzen moeten numeriek zijn",
                ))
                continue

            if duration <= 0 or minimum < 0 or maximum < minimum:
                signals.append(DataQualitySignal(
                    "INVALID_SHIFT_DEFINITION", "ERROR", "shift_catalog", key,
                    "ShiftCatalog vereist duur > 0 en 0 <= minimum_staff <= maximum_staff",
                ))
                continue

            definition = ShiftDefinition(
                task_code=code,
                pattern=pattern,
                service_type=self._value(row, "service_type"),
                duration_hours=duration,
                minimum_staff=minimum,
                maximum_staff=maximum,
            )
            definitions.append(definition)
            seen_keys.add(natural_key)
            provenance.append(Provenance(
                "CKC", "ShiftCatalog", key, imported_at,
                kind="CONFIGURATION",
                source_value=str(dict(row)),
                normalized_value=str(definition),
            ))

        return ShiftCatalogImportResult(tuple(definitions), tuple(provenance), tuple(signals))

    @staticmethod
    def create_service(
        definition: ShiftDefinition,
        *,
        service_id: str,
        starts_at: datetime,
        location: str,
    ) -> DutyService:
        """Create a service using minimum staffing as the operational requirement."""
        return DutyService(
            service_id=service_id,
            service_type=definition.service_type,
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=definition.duration_hours),
            location=location,
            required_staff=definition.minimum_staff,
        )

    @staticmethod
    def _value(row: dict[str, object], field: str) -> str:
        return str(row.get(field) or "").strip()
