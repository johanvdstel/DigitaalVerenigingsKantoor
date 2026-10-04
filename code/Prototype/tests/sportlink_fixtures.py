"""Synthetic source bookings for the no-show regression family."""
from datetime import datetime, timedelta
from dataclasses import replace

from dvk.model import Person
from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.workstream_model import DutyService


def booking(person="MEM1", when=None, *, name="Synthetic member", task="741", service=None):
    when = when or datetime(2026, 9, 18, 10)
    # Source timestamps are explicitly local; legacy domain fixtures may be naive.
    from dvk.vrijwilligers_adapter import TZ
    start = when.replace(tzinfo=TZ) if when.tzinfo is None else when
    service = service or DutyService("S1", "Bardienst", start, start + timedelta(hours=4), "CKC", 1)
    service = replace(service,
                      starts_at=service.starts_at.replace(tzinfo=TZ) if service.starts_at.tzinfo is None else service.starts_at,
                      ends_at=service.ends_at.replace(tzinfo=TZ) if service.ends_at.tzinfo is None else service.ends_at)
    result = SportlinkVrijwilligersAdapter().import_rows(
        task_code=task, rows=[{"naam": "Voorbeeld, A.B. de (Alex)",
                               "datumvanaf": service.starts_at.isoformat(), "datumtot": service.ends_at.isoformat(),
                               "lokatie": service.location}],
        services=[ServiceBinding(task, service)], imported_at=start,
        persons=[Person(person, name, sportlink_name="Voorbeeld, A.B. de (Alex)")])
    assert not result.signals
    return result.bookings[0]


def seed_bookings(uow, bookings):
    uow.sportlink_bookings.replace_all(tuple(bookings))
    uow.commit()
