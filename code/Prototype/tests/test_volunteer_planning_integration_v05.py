"""Synthetic source responses only. CKC catalog configuration contains no people."""
from dataclasses import replace
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
import json
from pathlib import Path
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import NoShowApplicationService, PlanningApplicationService
from dvk.model import Person
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod
from dvk.planning_workqueue import TemporaryPlanning
from dvk.security import Identity, Permission
from dvk.shift_catalog import ShiftCatalog, ShiftDefinition, WeeklySlot, load_shift_catalog
from dvk.volunteer_planning import VolunteerPlanningApplicationService, request_window
from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
from dvk.workstream_model import DutyAssignment

PERIOD = PlanningPeriod(date(2026, 10, 19), date(2026, 10, 25))
NOW = datetime(2026, 10, 21, 12, tzinfo=timezone.utc)
IDENTITY = Identity("synthetic-planner", "Planner", frozenset(Permission))


@pytest.fixture
def db(tmp_path):
    result = SQLiteDatabase(tmp_path / "synthetic.sqlite")
    result.initialize()
    return result


@pytest.fixture
def catalog():
    # Synthetic task codes; do not derive test people from any CKC source.
    return ShiftCatalog((ShiftDefinition("A", "Synthetic bar", 1, 1, 100),
                         ShiftDefinition("B", "Synthetic other", 1, 1, 2)),
                        (WeeklySlot(0, time(18), time(19), "A"),
                         WeeklySlot(1, time(18), time(19), "B")))


def people(count=1):
    return tuple(Person(f"P{i}", f"Synthetic {i}", sportlink_name=f"Example, A. van (Test{i})")
                 for i in range(count))


def row(service, person):
    return dict(naam=person.sportlink_name, datumvanaf=service.starts_at.isoformat(),
                datumtot=service.ends_at.isoformat(), lokatie="Synthetic source")


def client(payloads, seen):
    def opener(request, timeout):
        query = parse_qs(urlparse(request.full_url).query)
        code = query["vrijwilligerstaakcode"][0]
        seen.append(query)
        payload = payloads.get(code, [])
        if isinstance(payload, Exception):
            raise payload
        return BytesIO(payload if isinstance(payload, bytes) else json.dumps(payload).encode())
    return SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=opener)


def sync(db, catalog, payloads, persons=None, period=PERIOD):
    seen = []
    with db.unit_of_work() as uow:
        error = VolunteerPlanningApplicationService(uow, IDENTITY, catalog).synchronize(
            period=period, client=client(payloads, seen), client_id="synthetic-secret",
            persons=people() if persons is None else persons, imported_at=NOW)
    return error, seen


def snapshot(db):
    with db.unit_of_work() as uow:
        return (uow.sportlink_bookings.all(), uow.temporary_planning.all(),
                uow.sportlink_bookings.refresh_state())


def seed_work(db, service):
    with db.unit_of_work() as uow:
        uow.temporary_planning.add(TemporaryPlanning(
            DutyAssignment("TEMP", "PROPOSAL", service.service_id, "P0", "member", 1, "planner"), service))
        uow.commit()


def test_catalog_transcription_has_29_services_and_friday_exception():
    catalog = load_shift_catalog()
    bindings = catalog.bindings(PERIOD)
    assert set(catalog.task_codes) == {"701", "741", "761", "442"}
    assert len(bindings) == 29
    assert [sum(b.service.starts_at.weekday() == d for b in bindings) for d in range(7)] == [3, 3, 4, 3, 2, 12, 2]
    assert len({b.service.service_id for b in bindings}) == 29
    friday = [b for b in bindings if b.service.starts_at.weekday() == 4]
    assert len(friday) == 2 and all(b.service.required_staff == 1 for b in friday)
    assert next(d for d in catalog.definitions if d.task_code == "741").staffing_for("vrijdag") == (1, 2)
    assert all(b.service.location == "Kantine CKC" for b in bindings)
    assert len(catalog.bindings(PlanningPeriod(PERIOD.start, PERIOD.end + timedelta(days=7)))) == 58


@pytest.mark.parametrize("start,end,today", [
    (date(2026,10,19),date(2026,10,25),date(2026,10,21)),
    (date(2026,9,1),date(2026,12,1),date(2026,10,21)),
    (date(2027,1,1),date(2027,1,31),date(2026,10,21)),
    (date(2025,12,29),date(2026,1,4),date(2026,1,1)),
])
def test_request_window_covers_period_for_day_and_week_anchors(start,end,today):
    window = request_window(PlanningPeriod(start,end), today)
    assert window.weekoffset <= -1 and window.days >= 60
    monday = today - timedelta(days=today.weekday())
    for anchor in (today, monday):
        first = anchor + timedelta(weeks=window.weekoffset)
        assert first <= start and first + timedelta(days=window.days-1) >= end


def test_all_codes_once_and_empty_success_is_known_zero(db, catalog):
    service = catalog.bindings(PERIOD)[0].service
    seed_work(db, service)
    error, seen = sync(db,catalog,{})
    assert error is None
    assert [q["vrijwilligerstaakcode"][0] for q in seen] == list(catalog.task_codes)
    window = request_window(PERIOD, NOW.date())
    assert all(q["aantaldagen"] == [str(window.days)] and q["weekoffset"] == [str(window.weekoffset)] for q in seen)
    assert snapshot(db)[0:2] == ((), ())
    with db.unit_of_work() as uow:
        app = VolunteerPlanningApplicationService(uow, IDENTITY, catalog)
        success, attempt, matching = app.source(PERIOD)
        assert matching and attempt["status"] == "Geslaagd"
        assert [t["bookings"] for t in success["tasks"]] == [0,0]
        services, needs, _, statuses = app.planning_data(PERIOD)
        assert len(services) == 2 and [n.confirmed_occupancy for n in needs] == [0,0]
        assert statuses[0].fetched_at == NOW


@pytest.mark.parametrize("bad", [b'{"error":"synthetic"}', b'', URLError("URL with synthetic-secret"), TimeoutError("synthetic-secret")])
def test_second_code_failure_keeps_every_booking_and_work(db,catalog,bad):
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{"A":[row(service,people()[0])]})[0] is None
    seed_work(db,service)
    before = snapshot(db)
    error, seen = sync(db,catalog,{"B":bad})
    assert error and "synthetic-secret" not in error
    assert len(seen) == 2 and snapshot(db) == before
    with db.unit_of_work() as uow:
        assert uow.sportlink_bookings.refresh_state("attempt")["status"] == "Mislukt"


def test_more_than_50_people_correct_week_and_zero_other_service(db,catalog):
    extended = PlanningPeriod(PERIOD.start, PERIOD.end + timedelta(days=7))
    bindings = catalog.bindings(extended)
    ps = people(61)
    assert sync(db,catalog,{"A":[row(bindings[0].service,p) for p in ps]},ps,extended)[0] is None
    with db.unit_of_work() as uow:
        app = VolunteerPlanningApplicationService(uow,IDENTITY,catalog)
        services, needs, _, _ = app.planning_data(extended)
        assert len(uow.sportlink_bookings.all()) == 61
        assert [n.confirmed_occupancy for n in needs] == [61,0,0,0]
        assert len({s.service_id for s in services}) == 4
        # A different selected period cannot reinterpret the saved full refresh.
        assert not app.source(PERIOD)[2]


@pytest.mark.parametrize("mode", ["missing","ambiguous","service","interval"])
def test_invalid_identity_or_service_never_publishes(db,catalog,mode):
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{})[0] is None
    seed_work(db,service)
    before = snapshot(db)
    ps = people()
    value = row(service,ps[0])
    if mode == "missing": ps = (replace(ps[0],sportlink_name=None),)
    if mode == "ambiguous": ps = (ps[0],replace(ps[0],person_id="P2"))
    if mode == "service": value["datumvanaf"] = (service.starts_at + timedelta(minutes=1)).isoformat()
    if mode == "interval": value["datumtot"] = service.starts_at.isoformat()
    assert sync(db,catalog,{"A":[value]},ps)[0]
    assert snapshot(db) == before


def test_no_show_and_revocation_survive_refresh_and_timezone_match(db,catalog):
    service = catalog.bindings(PERIOD)[0].service
    value = row(service,people()[0])
    value["datumvanaf"] = service.starts_at.astimezone(timezone.utc).isoformat()
    value["datumtot"] = service.ends_at.astimezone(timezone.utc).isoformat()
    assert sync(db,catalog,{"A":[value]})[0] is None
    with db.unit_of_work() as uow:
        booking = uow.sportlink_bookings.all()[0]
        app = NoShowApplicationService(uow,IDENTITY)
        app.register(NoShowEvent("N",booking.assignment_id,booking.person_id,booking.starts_at,NOW,IDENTITY.subject_id,"2026/2027"))
        app.revoke("N",reason="Synthetic reason",revoked_at=NOW)
    assert sync(db,catalog,{})[0] is None
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N").booking == booking
        assert uow.no_show_revocations.for_no_show("N").reason == "Synthetic reason"


def test_live_dashboard_no_fake_actuality_and_no_request_knobs(tmp_path):
    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1]/"streamlit_app.py").read_text().replace("value=date.today()","value=date(2026, 10, 19)"))
    app = AppTest.from_file(str(script),default_timeout=20).run()
    app.button(key="nav-planning").click().run()
    assert not app.exception
    assert app.metric[0].value == "29"
    assert app.dataframe[0].value["Sportlink"].tolist() == ["Onbekend"]*29
    assert not app.number_input
    assert not any(x.key and x.key.startswith("sportlink-task") for x in app.text_input)
    db = SQLiteDatabase(tmp_path/"dvk_v05.sqlite")
    error, seen = sync(db,load_shift_catalog(),{},period=PERIOD)
    assert error is None
    assert [q["vrijwilligerstaakcode"][0] for q in seen] == list(load_shift_catalog().task_codes)
    app.run()
    assert not app.exception
    assert app.dataframe[0].value["Sportlink"].tolist() == [0]*29
    task_table = next(x.value for x in app.dataframe if "Sportlink-taakcode" in x.value.columns)
    assert task_table["Aantal geplande diensten"].sum() == 29
    assert task_table["Aantal Sportlink-inroosteringen"].sum() == 0
    assert len(task_table) == 4
    error, _ = sync(db,load_shift_catalog(),{"442":TimeoutError("synthetic-secret")},period=PERIOD)
    assert error
    app.run()
    assert not app.exception and app.error
    assert "synthetic-secret" not in " ".join(x.value for x in app.error)
    retained = next(x.value for x in app.dataframe if "Sportlink-taakcode" in x.value.columns)
    assert retained.equals(task_table)
    assert app.dataframe[0].value["Sportlink"].tolist() == [0]*29


def test_publication_and_planning_removal_rollback_together(db,catalog,monkeypatch):
    from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{"A":[row(service,people()[0])]})[0] is None
    seed_work(db,service)
    before = snapshot(db)
    def fail(self, identifier):
        raise RuntimeError("synthetic delete failure")
    monkeypatch.setattr(SQLiteTemporaryPlanningRepository,"remove",fail)
    with pytest.raises(RuntimeError,match="synthetic delete failure"):
        sync(db,catalog,{})
    assert snapshot(db) == before


def test_minimum_maximum_source_and_temporary_occupancy(db,catalog):
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{"A":[row(service,people()[0])]})[0] is None
    seed_work(db,service)
    with db.unit_of_work() as uow:
        services, needs, _, _ = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)
        final = PlanningApplicationService(IDENTITY,uow=uow).staffing_needs(services=services,source_needs=needs)
        assert (final[0].confirmed_occupancy,final[0].temporary_occupancy,final[0].planning_occupancy) == (1,1,2)
        assert (final[0].open_need,final[0].remaining_capacity) == (0,98)


def test_no_access_does_not_fetch_or_change_source(db,catalog):
    unauthorized = Identity("none","None",frozenset())
    seen = []
    with db.unit_of_work() as uow:
        app = VolunteerPlanningApplicationService(uow,unauthorized,catalog)
        with pytest.raises(PermissionError):
            app.synchronize(period=PERIOD,client=client({},seen),client_id="synthetic",persons=(),imported_at=NOW)
    assert seen == []
