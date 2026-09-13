from datetime import datetime, timezone

import pytest

from dvk.shift_catalog import ShiftDefinition, StaffingRule
from dvk.staffing import calculate_staffing_need
from dvk.vrijwilligers_adapter import VolunteerBooking
from dvk.workstream_model import DutyService


START = datetime(2026, 9, 19, 10, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 19, 12, 30, tzinfo=timezone.utc)


def service(required_staff: int = 2) -> DutyService:
    return DutyService("S1", "Bar weekend", START, END, "CKC", required_staff)


def booking(name: str, service_id: str = "S1") -> VolunteerBooking:
    return VolunteerBooking("741", service_id, name, START, END, "CKC")


def definition() -> ShiftDefinition:
    return ShiftDefinition(
        "741", "Bar weekend", 2.5, 2, 4,
        (StaffingRule("vrijdag", 1, 2),),
    )


def test_open_need_uses_minimum_not_maximum():
    need = calculate_staffing_need(
        service=service(), definition=definition(), bookings=(booking("A"),)
    )
    assert need.minimum_staff == 2
    assert need.maximum_staff == 4
    assert need.confirmed_occupancy == 1
    assert need.open_need == 1
    assert need.remaining_capacity == 3


def test_minimum_met_means_no_open_need_while_capacity_remains():
    need = calculate_staffing_need(
        service=service(), definition=definition(), bookings=(booking("A"), booking("B"))
    )
    assert need.open_need == 0
    assert need.remaining_capacity == 2


def test_overstaffing_never_creates_negative_need_or_capacity():
    bookings = tuple(booking(str(i)) for i in range(5))
    need = calculate_staffing_need(service=service(), definition=definition(), bookings=bookings)
    assert need.confirmed_occupancy == 5
    assert need.open_need == 0
    assert need.remaining_capacity == 0


def test_only_bookings_for_this_service_count_as_confirmed_occupancy():
    need = calculate_staffing_need(
        service=service(),
        definition=definition(),
        bookings=(booking("A"), booking("Other", "S2")),
    )
    assert need.confirmed_occupancy == 1
    assert need.open_need == 1


def test_condition_changes_minimum_and_maximum_together():
    friday_service = service(required_staff=1)
    need = calculate_staffing_need(
        service=friday_service,
        definition=definition(),
        bookings=(),
        condition="vrijdag",
    )
    assert need.minimum_staff == 1
    assert need.maximum_staff == 2
    assert need.open_need == 1
    assert need.remaining_capacity == 2


def test_service_minimum_must_match_catalog_minimum():
    with pytest.raises(ValueError):
        calculate_staffing_need(
            service=service(required_staff=4), definition=definition(), bookings=()
        )
