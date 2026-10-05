from dataclasses import replace
from datetime import datetime, timedelta
from io import BytesIO
import json

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.model import Person
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.planning_workqueue import TemporaryPlanning
from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.security import Identity, Permission
from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient, VrijwilligersFetchError
from dvk.workstream_model import DutyAssignment
from sportlink_fixtures import booking, seed_bookings

IDENTITY = Identity("planner", "Planner", frozenset({Permission.MANAGE_NO_SHOWS}))
SOURCE = booking("TEST001", name="Alex de Voorbeeld")
NAME_PARTS = {"Rel. code": "TEST001", "Achternaam": "Voorbeeld", "Voorletter(s)": "A.B.",
              "Tussenvoegsel(s)": "de", "Roepnaam": "Alex"}


def rows(name="Voorbeeld, A.B. de (Alex)"):
    return [{"naam": name, "datumvanaf": SOURCE.starts_at.isoformat(),
             "datumtot": SOURCE.ends_at.isoformat(), "lokatie": "CKC"}]


def import_rows(values, persons):
    return SportlinkVrijwilligersAdapter().import_rows(task_code="741", rows=values,
        persons=persons, services=(ServiceBinding("741", SOURCE.service),), imported_at=SOURCE.starts_at)


def event(source=SOURCE, identifier="N1"):
    return NoShowEvent(identifier, source.assignment_id, source.person_id, source.starts_at,
                       source.starts_at, "planner", "2026/2027")


@pytest.mark.parametrize("date_value, start_value, end_value, offset", [
    ("2026-10-10T00:00:00+0200", "2026-10-10T10:00:00+02:00", "2026-10-10T12:30:00+02:00", 2),
    ("2026-11-07T00:00:00+0100", "2026-11-07T10:00:00+01:00", "2026-11-07T12:30:00+01:00", 1),
])
def test_actual_sportlink_date_and_separate_time_reach_durable_no_show(
        tmp_path, date_value, start_value, end_value, offset):
    start, end = datetime.fromisoformat(start_value), datetime.fromisoformat(end_value)
    concrete = replace(SOURCE.service, starts_at=start, ends_at=end)
    raw = {"naam": "Voorbeeld, A.B. de (Alex)", "datumvanaf": date_value,
           "tijdvanaf": "10:00", "datumtot": date_value, "tijdtot": "12:30", "lokatie": "CKC"}
    result = SportlinkVrijwilligersAdapter().import_rows(task_code="741", rows=[raw],
        services=[ServiceBinding("741", concrete)], imported_at=start,
        persons=[Person("TEST001", "Alex", sportlink_name=raw["naam"])])
    assert not result.signals
    source, = result.bookings
    assert source.starts_at.isoformat() == start_value
    assert source.ends_at.isoformat() == end_value
    assert source.starts_at.utcoffset() == source.ends_at.utcoffset() == timedelta(hours=offset)
    assert source.assignment_id == replace(SOURCE, starts_at=start, ends_at=end).assignment_id
    db = SQLiteDatabase(tmp_path / "actual-source.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        uow.sportlink_bookings.replace_all([source]); uow.commit()
        service = NoShowApplicationService(uow, IDENTITY)
        service.register(event(source))
        stored = uow.no_shows.get("N1")
        assert stored.occurred_at == start
        assert stored.booking.starts_at.isoformat() == start_value
        assert stored.booking.ends_at.isoformat() == end_value


@pytest.mark.parametrize("date_value, time_value, expected", [
    ("2026-10-10", "10:00", "2026-10-10T10:00:00+02:00"),
    ("10-10-2026", "10:00:30", "2026-10-10T10:00:30+02:00"),
    ("10/10/2026", "", "2026-10-10T00:00:00+02:00"),
    ("2026-10-10T10:00:00+0200", "", "2026-10-10T10:00:00+02:00"),
    ("2026-11-07T10:00:00+0100", "", "2026-11-07T10:00:00+01:00"),
    ("2026-10-10T08:00:00Z", "", "2026-10-10T10:00:00+02:00"),
    ("2026-10-10T10:00:00", "", "2026-10-10T10:00:00+02:00"),
])
def test_existing_volunteer_datetime_forms_keep_their_behavior(date_value, time_value, expected):
    assert SportlinkVrijwilligersAdapter._parse_datetime(date_value, time_value).isoformat() == expected


def test_exact_confirmed_name_build_and_members_csv_route(tmp_path):
    assert SportlinkRealDataAdapter.sportlink_name(NAME_PARTS) == "Voorbeeld, A.B. de (Alex)"
    row = NAME_PARTS | {"Naam": "Alex de Voorbeeld", "Geb.dat.": "01-01-2000", "Lidstatus": "Definitief",
                        "Lidsoort": "Verenigingslid", "Status lidmaatschap": "spelend lid"}
    text = ";".join(row) + "\n" + ";".join(row.values())
    persons = SportlinkRealDataAdapter.read_volunteer_persons(text)
    imported = import_rows(rows(), persons)
    assert not imported.signals
    assert imported.bookings[0].person_id == "TEST001"
    assert imported.bookings[0].person_name == "Alex de Voorbeeld"
    assert imported.bookings[0].volunteer_name == "Voorbeeld, A.B. de (Alex)"


@pytest.mark.parametrize("missing", ["Achternaam", "Voorletter(s)", "Tussenvoegsel(s)", "Roepnaam"])
def test_missing_name_part_is_not_formatted_by_an_unapproved_rule(missing):
    name = SportlinkRealDataAdapter.sportlink_name(NAME_PARTS | {missing: ""})
    assert name is None
    result = import_rows(rows(), [Person("TEST001", "Alex", sportlink_name=name)])
    assert not result.bookings
    assert result.signals[0].code == "VOLUNTEER_PERSON_NOT_FOUND"


def test_ambiguous_name_never_selects_a_person():
    result = import_rows(rows(), [Person(pid, "Alex", sportlink_name="Voorbeeld, A.B. de (Alex)") for pid in ("A", "B")])
    assert not result.bookings
    assert result.signals[0].code == "VOLUNTEER_PERSON_AMBIGUOUS"


def test_logical_key_and_source_provenance_survive_api_reordering():
    people = [Person("TEST001", "Alex", sportlink_name="Voorbeeld, A.B. de (Alex)"),
              Person("TEST002", "Bob", sportlink_name="Voorbeeld, C.D. de (Bob)")]
    forward = import_rows(rows() + rows("Voorbeeld, C.D. de (Bob)"), people)
    reverse = import_rows(list(reversed(rows() + rows("Voorbeeld, C.D. de (Bob)"))), people)
    assert {b.assignment_id for b in forward.bookings} == {b.assignment_id for b in reverse.bookings}
    for source in forward.bookings:
        assert source.provenance.source_record_key == source.assignment_id
        assert source.provenance.source_system == "Sportlink"
        assert source.provenance.source_value
    assert replace(SOURCE, location="Andere locatie", volunteer_name="Andere weergave").assignment_id == SOURCE.assignment_id
    for changed in (replace(SOURCE, person_id="OTHER"), replace(SOURCE, task_code="742"),
                    replace(SOURCE, starts_at=SOURCE.starts_at+timedelta(minutes=1)),
                    replace(SOURCE, ends_at=SOURCE.ends_at+timedelta(minutes=1))):
        assert changed.assignment_id != SOURCE.assignment_id


def test_duplicate_source_is_signalled_without_second_booking():
    result = import_rows(rows()*2, [Person("TEST001", "Alex", sportlink_name="Voorbeeld, A.B. de (Alex)")])
    assert len(result.bookings) == 1
    assert result.signals[0].code == "DUPLICATE_VOLUNTEER_BOOKING"


def test_no_show_on_only_temporary_dvk_planning_is_rejected(tmp_path):
    db = SQLiteDatabase(tmp_path / "temporary.sqlite"); db.initialize()
    assignment = DutyAssignment(SOURCE.assignment_id, "P1", SOURCE.service_id, SOURCE.person_id, "member", 4, "planner")
    with db.unit_of_work() as uow:
        uow.temporary_planning.add(TemporaryPlanning(assignment, SOURCE.service)); uow.commit()
        service = NoShowApplicationService(uow, IDENTITY)
        assert service.available_assignments() == ()
        with pytest.raises(ValueError, match="existing inroostering"):
            service.register(event())
        assert uow.no_shows.all() == ()


def test_legacy_dvk_assignment_and_snapshotless_durable_fact_are_rejected(tmp_path):
    from dvk.workstream_model import AssignmentProposal
    db = SQLiteDatabase(tmp_path / "legacy.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        uow.proposals.add(AssignmentProposal("P1", SOURCE.service_id, SOURCE.person_id, "member", 10, 0, 0, 0,
                          10, 0, False, None, None, None, "no_match_context", "normal", 1, ()))
        uow.assignments.add(DutyAssignment(SOURCE.assignment_id, "P1", SOURCE.service_id, SOURCE.person_id, "member", 4, "planner"))
        uow.commit()
        with pytest.raises(ValueError, match="existing inroostering"):
            NoShowApplicationService(uow, IDENTITY).register(event())
        with pytest.raises(ValueError, match="snapshot"):
            uow.no_shows.add(event())


def test_logical_key_requires_explicit_timezones():
    with pytest.raises(ValueError, match="timezones"):
        replace(SOURCE, starts_at=SOURCE.starts_at.replace(tzinfo=None)).assignment_id


def test_ui_never_offers_only_temporary_planning(tmp_path):
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    source_path = Path(__file__).parents[1] / "streamlit_app.py"
    script = tmp_path / "streamlit_app.py"
    script.write_text(source_path.read_text())
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        assignment = DutyAssignment("TEMP", "P1", SOURCE.service_id, SOURCE.person_id, "member", 4, "planner")
        uow.temporary_planning.add(TemporaryPlanning(assignment, SOURCE.service)); uow.commit()
    app = AppTest.from_file(str(script)).run()
    assert not app.exception
    assert not any(widget.label == "Inroostering" for widget in app.selectbox)


def test_snapshot_revocation_and_sanction_survive_source_refresh_and_reopen(tmp_path):
    db = SQLiteDatabase(tmp_path / "snapshot.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        seed_bookings(uow, [SOURCE])
        service = NoShowApplicationService(uow, IDENTITY)
        service.register(event())
        original = uow.no_shows.get("N1")
        assert original.booking == SOURCE
        uow.sportlink_bookings.replace_all([]); uow.commit()
        contexts = service.revocable_no_shows()
        assert contexts[0].assignment.service == SOURCE.service
        assert contexts[0].assignment.person_name == SOURCE.person_name
        service.revoke("N1", reason="Expliciet besluit", revoked_at=SOURCE.ends_at)
        assert service.current_state("TEST001", "2026/2027").counter == 0
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") == original
        assert uow.no_show_revocations.for_no_show("N1").reason == "Expliciet besluit"
        assert uow.sanctions.get("N1") is None
        seed_bookings(uow, [replace(SOURCE, volunteer_name="gewijzigde presentatie")])
        with pytest.raises(ValueError, match="al een no-show"):
            NoShowApplicationService(uow, IDENTITY).register(event(identifier="N2"))


def client(payload):
    return SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=lambda request, timeout: BytesIO(json.dumps(payload).encode()))


@pytest.mark.parametrize("mode", ["success", "unknown", "transport"])
def test_synchronization_uses_existing_client_and_is_atomic(tmp_path, mode):
    db = SQLiteDatabase(tmp_path / "sync.sqlite"); db.initialize()
    assignment = DutyAssignment("TEMP", "P1", SOURCE.service_id, "OTHER", "member", 4, "planner")
    with db.unit_of_work() as uow:
        seed_bookings(uow, [SOURCE])
        uow.temporary_planning.add(TemporaryPlanning(assignment, SOURCE.service)); uow.commit()
        instance = client(rows("unknown") if mode == "unknown" else rows())
        if mode == "transport":
            def fail(request, timeout):
                raise TimeoutError("synthetic")
            instance = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=fail)
        app = NoShowApplicationService(uow, IDENTITY)
        kwargs = dict(client=instance, client_id="synthetic", bindings=[ServiceBinding("741", SOURCE.service)],
                      persons=[Person("TEST001", "Alex", sportlink_name="Voorbeeld, A.B. de (Alex)")], imported_at=SOURCE.ends_at)
        if mode == "transport":
            with pytest.raises(VrijwilligersFetchError):
                app.synchronize(**kwargs)
        else:
            signals = app.synchronize(**kwargs)
            assert bool(signals) is (mode == "unknown")
        assert len(uow.temporary_planning.all()) == (0 if mode == "success" else 1)
        assert len(uow.sportlink_bookings.recent()) == 1
