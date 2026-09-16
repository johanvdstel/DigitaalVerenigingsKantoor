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

    @property
    def candidate_slots(self) -> int:
        """v0.5: candidates may be proposed until maximum capacity is reached."""
        return self.remaining_capacity

    @property
    def minimum_coverage_slots(self) -> int:
        """Slots still required to reach the minimum staffing level."""
        return self.open_need

    @property
    def optional_capacity_slots(self) -> int:
        """Capacity above the minimum is human planning discretion, not open need."""
        return max(0, self.remaining_capacity - self.open_need)


def calculate_staffing_need(*, service: DutyService, definition: ShiftDefinition, bookings: Iterable[VolunteerBooking], condition: str | None = None) -> StaffingNeed:
    minimum, maximum = definition.staffing_for(condition)
    if service.required_staff != minimum: raise ValueError("DutyService.required_staff must equal the applicable ShiftCatalog minimum_staff")
    confirmed = sum(1 for booking in bookings if booking.service_id == service.service_id)
    return StaffingNeed(service.service_id, minimum, maximum, confirmed, max(0, minimum - confirmed), max(0, maximum - confirmed))


def staffing_provenance(need: StaffingNeed, *, derived_at: datetime) -> Provenance:
    return Provenance(source_system="DVK", source_dataset="staffing", source_record_key=need.service_id, imported_at=derived_at, kind="DERIVED", source_value=None, normalized_value=str(need))
