from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .real_data_import import Provenance
from .shift_catalog import ShiftDefinition
from .vrijwilligers_adapter import VolunteerBooking
from .workstream_model import DutyService


@dataclass(frozen=True)
class StaffingNeed:
    service_id: str
    minimum_staff: int
    maximum_staff: int
    confirmed_occupancy: int
    open_need: int
    remaining_capacity: int


def calculate_staffing_need(
    *,
    service: DutyService,
    definition: ShiftDefinition,
    bookings: Iterable[VolunteerBooking],
    condition: str | None = None,
) -> StaffingNeed:
    """Derive required staffing and capacity for one concrete DutyService.

    Open need is based only on the applicable minimum staffing and confirmed
    Sportlink occupancy. Maximum staffing is retained separately as planning /
    registration capacity and never increases the required open need.
    """
    minimum, maximum = definition.staffing_for(condition)
    if service.required_staff != minimum:
        raise ValueError(
            "DutyService.required_staff must equal the applicable ShiftCatalog minimum_staff"
        )

    confirmed = sum(1 for booking in bookings if booking.service_id == service.service_id)
    return StaffingNeed(
        service_id=service.service_id,
        minimum_staff=minimum,
        maximum_staff=maximum,
        confirmed_occupancy=confirmed,
        open_need=max(0, minimum - confirmed),
        remaining_capacity=max(0, maximum - confirmed),
    )


def staffing_provenance(need: StaffingNeed, *, derived_at: datetime) -> Provenance:
    """Mark a staffing result explicitly as a DVK derivation, never as a source fact."""
    return Provenance(
        source_system="DVK",
        source_dataset="staffing",
        source_record_key=need.service_id,
        imported_at=derived_at,
        kind="DERIVED",
        source_value=None,
        normalized_value=str(need),
    )
