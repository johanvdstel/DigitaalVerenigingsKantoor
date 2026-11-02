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
    from uuid import uuid4
    from dvk.planning import PlanningPeriod
    from dvk.planning_session import PlanningSession
    bookings = tuple(bookings)
    if bookings:
        period = PlanningPeriod(min(b.starts_at.date() for b in bookings), max(b.starts_at.date() for b in bookings))
        session = PlanningSession(str(uuid4()), period, str(uuid4()))
        uow.planning_sessions.save(session)
        uow.sportlink_bookings.save_refresh_state(dict(session_id=session.session_id,
            source_revision=session.source_revision, start=period.start.isoformat(), end=period.end.isoformat(),
            codes=list(dict.fromkeys(b.task_code for b in bookings)), status="Geslaagd", fetched_at=bookings[0].starts_at.isoformat(),
            tasks=[dict(task_code=code, description="Synthetic duty", services=1, bookings=sum(b.task_code==code for b in bookings), status="Geslaagd")
                   for code in dict.fromkeys(b.task_code for b in bookings)]))
    uow.sportlink_bookings.replace_all(bookings)
    uow.commit()


def source_revision(uow):
    session = uow.planning_sessions.get()
    return session.source_revision if session else None


def open_no_show_ui(app, db, monkeypatch, *, navigate=True):
    """UI relocation harness: synthetic external snapshot, independent of sessions.

    The dedicated BL-19 source tests exercise HTTP-client/adapter confirmation;
    these historical UI tests reuse their original known source fixtures.
    """
    from dvk.application_services import NoShowApplicationService
    from dvk.local_csv_sources import LocalCsvSourceApplicationService
    from dvk.no_show import registration_period
    from dvk.no_show_source import NoShowSource, NoShowSourceApplicationService
    from dvk.model import Person
    def bookings():
        with db.unit_of_work() as u:
            return u.sportlink_bookings.all()
    def now():
        with db.unit_of_work() as u:
            moments = [b.starts_at for b in u.sportlink_bookings.all()]
            moments += [e.occurred_at for e in u.no_shows.all()]
        from dvk.no_show import TZ
        return max(moments) + timedelta(hours=1) if moments else datetime(2026,10,25,12,tzinfo=TZ)
    original_init = NoShowApplicationService.__init__
    def init(self, *args, **kwargs):
        kwargs.setdefault("clock", now)
        original_init(self, *args, **kwargs)
    monkeypatch.setattr(NoShowApplicationService, "__init__", init)
    monkeypatch.setattr(NoShowSourceApplicationService, "consult", lambda self, moment, **kw:
        NoShowSource(bookings(), (), registration_period(now()), now()))
    monkeypatch.setattr(LocalCsvSourceApplicationService, "volunteer_persons", lambda self:
        tuple(Person(b.person_id, b.person_name, sportlink_name=b.volunteer_name)
              for b in bookings() if b.person_id))
    if navigate:
        app.button(key="nav-no-shows").click().run()
        app.button[ next(i for i,b in enumerate(app.button) if b.label == "Sportlink-diensten raadplegen") ].click().run()
    return app
