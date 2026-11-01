"""Synthetic source responses only. CKC catalog configuration contains no people."""
from ui_table_events import table as ui_table
from sportlink_fixtures import source_revision
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
from dvk.real_data_import import SportlinkRealDataAdapter
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
    from dvk.planning_runtime import choose_period
    choose_period(db, period, discard=True)
    seen = []
    with db.unit_of_work() as uow:
        session = uow.planning_sessions.get()
        error = VolunteerPlanningApplicationService(uow, IDENTITY, catalog).synchronize(
            period=period, client=client(payloads, seen), client_id="synthetic-secret",
            persons=people() if persons is None else persons, imported_at=NOW,
            confirmed=True, source_revision=session.source_revision)
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


@pytest.mark.parametrize("mode", ["service","interval"])
def test_invalid_identity_or_service_never_publishes(db,catalog,mode):
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{})[0] is None
    seed_work(db,service)
    before = snapshot(db)
    ps = people()
    value = row(service,ps[0])
    if mode == "service":
        value["datumvanaf"] = service.ends_at.isoformat()  # Boundary contact has no positive overlap.
        value["datumtot"] = (service.ends_at + timedelta(hours=1)).isoformat()
    if mode == "interval": value["datumtot"] = service.starts_at.isoformat()
    error = sync(db,catalog,{"A":[value]},ps)[0]
    if mode == "interval":
        assert error and snapshot(db) == before
    else:
        # BL-14 AC-08: a valid adjacent source interval is an additional service.
        assert error is None
        with db.unit_of_work() as uow:
            services = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)[0]
            assert len(services) == 3
        assert snapshot(db)[1] == ()


def test_no_show_and_revocation_survive_refresh_and_timezone_match(db,catalog):
    service = catalog.bindings(PERIOD)[0].service
    value = row(service,people()[0])
    value["datumvanaf"] = service.starts_at.astimezone(timezone.utc).isoformat()
    value["datumtot"] = service.ends_at.astimezone(timezone.utc).isoformat()
    assert sync(db,catalog,{"A":[value]})[0] is None
    with db.unit_of_work() as uow:
        booking = uow.sportlink_bookings.all()[0]
        app = NoShowApplicationService(uow,IDENTITY)
        app.register(NoShowEvent("N",booking.assignment_id,booking.person_id,booking.starts_at,NOW,IDENTITY.subject_id,"2026/2027"), source_revision=source_revision(uow))
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
    assert ui_table(app, "services_editor-").value["Sportlink"].tolist() == ["Onbekend"]*29
    assert not app.number_input
    assert not any(x.key and x.key.startswith("sportlink-task") for x in app.text_input)
    db = SQLiteDatabase(tmp_path/"dvk_v05.sqlite")
    error, seen = sync(db,load_shift_catalog(),{},period=PERIOD)
    assert error is None
    assert [q["vrijwilligerstaakcode"][0] for q in seen] == list(load_shift_catalog().task_codes)
    app.run()
    app.button(key="resume-planning").click().run()
    assert not app.exception
    assert ui_table(app, "services_editor-").value["Sportlink"].tolist() == ["geen namen"]*29
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
    assert ui_table(app, "services_editor-").value["Sportlink"].tolist() == ["geen namen"]*29


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


@pytest.mark.parametrize("source_code", ["701", "741", "761"])
def test_wednesday_booking_spans_both_catalog_codes_without_splitting_source(db,source_code):
    catalog = load_shift_catalog()
    bindings = catalog.bindings(PERIOD)
    slot = next(b.service for b in bindings if b.service.starts_at.weekday() == 2 and b.service.starts_at.hour == 19)
    long = replace(slot, ends_at=slot.ends_at.replace(hour=22,minute=30))
    source_row = row(long,people()[0])
    assert sync(db,catalog,{source_code:[source_row]})[0] is None
    with db.unit_of_work() as uow:
        source = uow.sportlink_bookings.all()
        assert len(source) == 1
        original = source[0]
        assert original.task_code == source_code
        assert (original.starts_at,original.ends_at) == (long.starts_at,long.ends_at)
        assert original.provenance.source_value == str(source_row)
        assert original.service.starts_at == original.starts_at and original.service.ends_at == original.ends_at
        services,needs,_,_ = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)
        assert len(services) == 30  # BL-14: actual long interval remains independently visible.
        services, needs = catalog_projection(catalog, services, needs)
        occupied = [(s.starts_at.hour,s.ends_at.hour) for s,n in zip(services,needs) if n.confirmed_occupancy]
        assert occupied == [(19,20),(20,22)]
        assert len(services) == 29
        # Reading the derived occupancy does not mutate/split the source.
        assert uow.sportlink_bookings.all() == source
        app = NoShowApplicationService(uow,IDENTITY)
        app.register(NoShowEvent("N-OVERLAP",original.assignment_id,original.person_id,original.starts_at,
                                 original.ends_at,IDENTITY.subject_id,"2026/2027"), source_revision=source_revision(uow))
    assert sync(db,catalog,{})[0] is None
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N-OVERLAP").booking == original


@pytest.mark.parametrize("source_code",["701","741","761","442"])
def test_saturday_parallel_bar_and_commissiekamer_never_mix(db,source_code):
    catalog = load_shift_catalog()
    slot = next(b.service for b in catalog.bindings(PERIOD)
                if b.service.starts_at.weekday()==5 and b.task_code=="741")
    assert sync(db,catalog,{source_code:[row(slot,people()[0])]})[0] is None
    with db.unit_of_work() as uow:
        services,needs,_,_ = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)
    extra = len(services) - 29
    assert extra == (source_code in {"701", "761"})
    services, needs = catalog_projection(catalog, services, needs)
    expected = "Commissiekamer" if source_code=="442" else "Bar weekend"
    assert [s.service_type for s,n in zip(services,needs) if n.confirmed_occupancy] == [expected]


def test_one_person_counts_once_despite_multiple_original_bookings_and_codes(db):
    catalog = load_shift_catalog()
    slot = next(b.service for b in catalog.bindings(PERIOD)
                if b.service.starts_at.weekday()==2 and b.service.starts_at.hour==19)
    long = replace(slot,ends_at=slot.ends_at.replace(hour=22,minute=30))
    partial = replace(long,starts_at=long.starts_at.replace(minute=30),ends_at=long.ends_at.replace(hour=20))
    ps = people(2)
    payloads = {code:[row(long,ps[0])] for code in ("701","741","761")}
    payloads["701"] += [row(partial,ps[0]),row(long,ps[1])]
    assert sync(db,catalog,payloads,ps)[0] is None
    with db.unit_of_work() as uow:
        assert len(uow.sportlink_bookings.all()) == 5
        services,needs,_,_ = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)
        assert len(services) == 33  # Three long barcode contexts and one partial interval.
        services, needs = catalog_projection(catalog, services, needs)
        assert [n.confirmed_occupancy for n in needs if n.confirmed_occupancy] == [2,2]
        assert sum(r["bookings"] for r in uow.sportlink_bookings.refresh_state()["tasks"]) == 5
        assert len(services) == 29


@pytest.mark.parametrize("start,end,expected", [(18,20,[1,1]),(18,19,[1,0]),(19,20,[0,1]),(20,21,[0,0])])
def test_adjacent_slots_and_boundary_contact_in_published_source(db,start,end,expected):
    catalog = ShiftCatalog((ShiftDefinition("701","Synthetic bar",1,1,2),),
                           (WeeklySlot(0,time(18),time(19),"701"),WeeklySlot(0,time(19),time(20),"701")))
    slot = catalog.bindings(PERIOD)[0].service
    booking_service = replace(slot, starts_at=slot.starts_at.replace(hour=start),ends_at=slot.ends_at.replace(hour=end))
    error,_ = sync(db,catalog,{"701":[row(booking_service,people()[0])]})
    assert error is None
    with db.unit_of_work() as uow:
        services,needs,_,_ = VolunteerPlanningApplicationService(uow,IDENTITY,catalog).planning_data(PERIOD)
    assert len(services) == (3 if (start,end) in {(18,20),(20,21)} else 2)
    services,needs = catalog_projection(catalog,services,needs)
    assert [n.confirmed_occupancy for n in needs] == expected


def test_partial_overlap_with_later_failure_preserves_bookings_work_and_success(db):
    catalog = load_shift_catalog()
    slot = next(b.service for b in catalog.bindings(PERIOD) if b.task_code=="741")
    partial = replace(slot,starts_at=slot.starts_at+timedelta(minutes=15))
    assert sync(db,catalog,{"741":[row(partial,people()[0])]})[0] is None
    seed_work(db,slot)
    before = snapshot(db)
    assert sync(db,catalog,{"741":[row(partial,people()[0])],"442":TimeoutError("synthetic")})[0]
    assert snapshot(db) == before


def test_empty_prefix_person_links_in_real_planning_route(db,catalog):
    name = SportlinkRealDataAdapter.sportlink_name({"Achternaam":"Example","Voorletter(s)":"A.",
                                                  "Tussenvoegsel(s)":"","Roepnaam":"Synthetic"})
    person = Person("SYNTHETIC", "Synthetic member",sportlink_name=name)
    assert name == "Example, A. (Synthetic)"
    slot = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{"A":[row(slot,person)]},[person])[0] is None
    with db.unit_of_work() as uow:
        assert uow.sportlink_bookings.all()[0].person_id == "SYNTHETIC"


@pytest.mark.parametrize("source_code", ["701", "741", "761", "442"])
@pytest.mark.parametrize("catalog_code", ["701", "741", "761", "442"])
def test_confirmed_task_groups_through_refresh_and_planning(db, source_code, catalog_code):
    grouped = ShiftCatalog(tuple(ShiftDefinition(code, "Synthetic", 1, 1, 2)
                                for code in ("701", "741", "761", "442")),
                           (WeeklySlot(2, time(19), time(20), catalog_code),) + tuple(
                               WeeklySlot(4,time(12),time(13),code,date(2027,1,1),date(2027,1,1))
                               for code in ("701","741","761","442") if code != catalog_code))
    service = grouped.bindings(PERIOD)[0].service
    error, _ = sync(db, grouped, {source_code: [row(service, people()[0])]})
    same_group = (source_code == "442") == (catalog_code == "442")
    assert error is None  # BL-14 accepts a separate context even outside the catalog group.
    with db.unit_of_work() as uow:
        services,needs,_,_ = VolunteerPlanningApplicationService(uow, IDENTITY, grouped).planning_data(PERIOD)
        assert len(services) == (1 if source_code == catalog_code else 2)
        assert needs[0].confirmed_occupancy == int(same_group)
        assert needs[-1].confirmed_occupancy == 1
        assert uow.sportlink_bookings.all()[0].task_code == source_code


@pytest.mark.parametrize("source_code", ["701", "741", "761"])
def test_long_booking_occupies_two_catalog_slots_without_splitting_source(db, source_code):
    catalog = load_shift_catalog()
    bindings = catalog.bindings(PERIOD)
    first = next(b.service for b in bindings if b.task_code == "701"
                 and b.service.starts_at.weekday() == 2 and b.service.starts_at.hour == 19)
    second = next(b.service for b in bindings if b.task_code == "761"
                  and b.service.starts_at.weekday() == 2)
    value = row(first, people()[0]) | {"datumtot": second.ends_at.isoformat()}
    assert sync(db, catalog, {source_code: [value]})[0] is None
    before = snapshot(db)[0]
    assert len(before) == 1
    booking = before[0]
    assert (booking.task_code, booking.starts_at, booking.ends_at) == (
        source_code, first.starts_at, second.ends_at)
    assert booking.provenance.kind == "SOURCE_FACT"
    assert value["datumtot"] in booking.provenance.source_value
    with db.unit_of_work() as uow:
        services,needs,_,_ = VolunteerPlanningApplicationService(uow, IDENTITY, catalog).planning_data(PERIOD)
        assert len(services) == 30
        services,needs = catalog_projection(catalog,services,needs)
        assert {n.service_id for n in needs if n.confirmed_occupancy} == {first.service_id, second.service_id}
        assert all(n.confirmed_occupancy == 1 for n in needs if n.confirmed_occupancy)
    assert snapshot(db)[0] == before
    assert sync(db, catalog, {source_code: [value]})[0] is None
    assert snapshot(db)[0] == before  # Repeated refresh does not accumulate occupancy.


def test_multiple_source_codes_and_intervals_count_each_person_once_per_slot(db):
    catalog = load_shift_catalog()
    service = next(b.service for b in catalog.bindings(PERIOD)
                   if b.task_code == "701" and b.service.starts_at.weekday() == 2
                   and b.service.starts_at.hour == 19)
    ps = people(2)
    payloads = {code: [row(service, ps[0])] for code in ("701", "741", "761")}
    payloads["701"].append(row(service, ps[1]))
    payloads["701"].append(row(service, ps[0]) | {
        "datumvanaf": (service.starts_at + timedelta(minutes=15)).isoformat()})
    assert sync(db, catalog, payloads, ps)[0] is None
    before = snapshot(db)[0]
    assert len(before) == 5 and len({b.assignment_id for b in before}) == 5
    with db.unit_of_work() as uow:
        need = next(n for n in VolunteerPlanningApplicationService(uow, IDENTITY, catalog)
                    .planning_data(PERIOD)[1] if n.service_id == service.service_id)
        assert (need.confirmed_occupancy, need.open_need, need.remaining_capacity) == (2, 0, 0)
    assert snapshot(db)[0] == before


def catalog_projection(catalog, services, needs):
    """Keep historical slot assertions while separately asserting BL-14 additions."""
    ids = {b.service.service_id for b in catalog.bindings(PERIOD)}
    return (tuple(s for s in services if s.service_id in ids), tuple(n for n in needs if n.service_id in ids))


# Preserve historical BL-11 dates with an explicit test clock.
pytestmark = pytest.mark.usefixtures("historical_registration_context")
