from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest

from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.workstream_model import DutyService


IMPORTED_AT = datetime(2026, 9, 13, 20, 0, tzinfo=timezone.utc)
TZ = ZoneInfo("Europe/Amsterdam")


def service(service_id="S741", start_hour=10):
    return DutyService(
        service_id=service_id,
        service_type="Bar weekend",
        starts_at=datetime(2026, 9, 19, start_hour, 0, tzinfo=timezone.utc),
        ends_at=datetime(2026, 9, 19, start_hour + 2, 30, tzinfo=timezone.utc),
        location="CKC",
        required_staff=2,
    )


def volunteer_row(**overrides):
    row = {
        "naam": "Jan Smit",
        "datumvanaf": "2026-09-19",
        "datumtot": "2026-09-19",
        "tijdvanaf": "12:00",
        "tijdtot": "14:30",
        "lokatie": "CKC",
        "heledag": "Nee",
    }
    row.update(overrides)
    return row


def test_r13_links_volunteer_to_service_by_task_code_and_exact_time():
    adapter = SportlinkVrijwilligersAdapter()
    result = adapter.import_rows(
        task_code="741", rows=[volunteer_row()], services=[ServiceBinding("741", service())], imported_at=IMPORTED_AT
    )
    assert len(result.bookings) == 1
    assert result.bookings[0].service_id == "S741"
    assert result.bookings[0].volunteer_name == "Jan Smit"
    assert result.bookings[0].task_code == "741"
    assert not result.signals


def test_r13_does_not_link_same_time_to_wrong_task_code():
    adapter = SportlinkVrijwilligersAdapter()
    result = adapter.import_rows(
        task_code="442", rows=[volunteer_row()], services=[ServiceBinding("741", service())], imported_at=IMPORTED_AT
    )
    assert not result.bookings
    assert result.signals[0].code == "VOLUNTEER_SERVICE_NOT_FOUND"


def test_r13_signals_ambiguous_service_instead_of_guessing():
    adapter = SportlinkVrijwilligersAdapter()
    bindings = [ServiceBinding("741", service("A")), ServiceBinding("741", service("B"))]
    result = adapter.import_rows(task_code="741", rows=[volunteer_row()], services=bindings, imported_at=IMPORTED_AT)
    assert not result.bookings
    assert result.signals[0].code == "VOLUNTEER_SERVICE_AMBIGUOUS"


def test_r13_signals_missing_service_instead_of_guessing_nearest_slot():
    adapter = SportlinkVrijwilligersAdapter()
    result = adapter.import_rows(
        task_code="741", rows=[volunteer_row(tijdvanaf="12:15", tijdtot="14:45")],
        services=[ServiceBinding("741", service())], imported_at=IMPORTED_AT
    )
    assert not result.bookings
    assert result.signals[0].code == "VOLUNTEER_SERVICE_NOT_FOUND"


def test_r13_records_source_provenance_without_credentials():
    adapter = SportlinkVrijwilligersAdapter()
    result = adapter.import_rows(
        task_code="741", rows=[volunteer_row()], services=[ServiceBinding("741", service())], imported_at=IMPORTED_AT
    )
    provenance = result.provenance[0]
    assert provenance.source_system == "Sportlink"
    assert provenance.source_dataset == "Vrijwilligers"
    assert provenance.kind == "SOURCE_FACT"
    assert provenance.source_record_key == "741:1"


def local_dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 9, 15, hour, minute, tzinfo=TZ)  # Tuesday


def test_r13b_preserves_full_sportlink_period_and_derives_catalog_segments():
    adapter = SportlinkVrijwilligersAdapter()
    operational = adapter.derive_operational_service(
        task_code="741",
        starts_at=local_dt(17),
        ends_at=local_dt(22, 30),
        location="CKC",
        catalog_boundaries=(local_dt(18), local_dt(19), local_dt(20), local_dt(22, 30)),
    )

    assert operational.starts_at == local_dt(17)
    assert operational.ends_at == local_dt(22, 30)
    assert operational.segments == (
        (local_dt(17), local_dt(18)),
        (local_dt(18), local_dt(19)),
        (local_dt(19), local_dt(20)),
        (local_dt(20), local_dt(22, 30)),
    )
    assert operational.deviates_from_catalog is True


def test_r13b_exact_catalog_period_is_not_marked_as_deviation():
    adapter = SportlinkVrijwilligersAdapter()
    operational = adapter.derive_operational_service(
        task_code="741",
        starts_at=local_dt(18),
        ends_at=local_dt(22, 30),
        location="CKC",
        catalog_boundaries=(local_dt(18), local_dt(19), local_dt(20), local_dt(22, 30)),
    )
    assert operational.segments == (
        (local_dt(18), local_dt(19)),
        (local_dt(19), local_dt(20)),
        (local_dt(20), local_dt(22, 30)),
    )
    assert operational.deviates_from_catalog is False


def test_r13b_rejects_empty_or_reversed_period():
    adapter = SportlinkVrijwilligersAdapter()
    with pytest.raises(ValueError):
        adapter.derive_operational_service(
            task_code="741",
            starts_at=local_dt(18),
            ends_at=local_dt(18),
            location="CKC",
            catalog_boundaries=(),
        )
