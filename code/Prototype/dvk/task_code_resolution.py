from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .real_data_import import DataQualitySignal
from .shift_catalog import ShiftDefinition


@dataclass(frozen=True)
class TaskCodeResolution:
    definition: ShiftDefinition | None
    signals: tuple[DataQualitySignal, ...]


def resolve_task_code(
    task_code: str,
    definitions: Iterable[ShiftDefinition],
) -> TaskCodeResolution:
    """Resolve a source task code by exact equality only.

    Unknown or ambiguous codes are explicit data-quality events. DVK never
    trims, coerces, fuzzy-matches or substitutes a different task code.
    """
    matches = tuple(
        definition for definition in definitions
        if definition.task_code == task_code
    )
    if len(matches) == 1:
        return TaskCodeResolution(matches[0], ())

    if not matches:
        return TaskCodeResolution(
            None,
            (
                DataQualitySignal(
                    "UNKNOWN_TASK_CODE",
                    "ERROR",
                    "shift_catalog",
                    task_code,
                    "Taakcode komt niet voor in ShiftCatalog; geen automatische mapping toegepast",
                ),
            ),
        )

    return TaskCodeResolution(
        None,
        (
            DataQualitySignal(
                "AMBIGUOUS_TASK_CODE",
                "ERROR",
                "shift_catalog",
                task_code,
                "Taakcode heeft meer dan een ShiftCatalog-definitie; geen automatische keuze toegepast",
            ),
        ),
    )
