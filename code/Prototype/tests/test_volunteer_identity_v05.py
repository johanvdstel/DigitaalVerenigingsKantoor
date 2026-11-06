"""PR #38: occupancy is a source fact; an identity link is optional. Synthetic only."""
from sportlink_fixtures import source_revision, seed_bookings
from dataclasses import replace
from datetime import timedelta
import json

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent, season_id
from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter, booking_identity_report
from test_volunteer_planning_integration_v05 import (
    db, catalog, PERIOD, NOW, IDENTITY, people, row, sync, snapshot, seed_work, client,
)


def imported(catalog, values, persons):
    return SportlinkVrijwilligersAdapter().import_rows(
        task_code="A", rows=values, services=catalog.bindings(PERIOD), persons=persons,
        period=PERIOD, imported_at=NOW, catalog_overlap=True)


@pytest.mark.parametrize("mode,linked,issues", [
    ("exact", True, ()),
    ("shielded", False, ()),
    ("missing", False, ("VOLUNTEER_PERSON_NOT_FOUND",)),
    ("ambiguous", False, ("VOLUNTEER_PERSON_AMBIGUOUS",)),
    ("duplicate", True, ("VOLUNTEER_PERSON_DUPLICATE",)),
    ("conflict", False, ("VOLUNTEER_PERSON_DUPLICATE", "VOLUNTEER_PERSON_CONFLICT")),
])
def test_identity_never_blocks_valid_occupancy(db, catalog, mode, linked, issues):
    p = people()[0]
    ps = (p,)
    value = row(catalog.bindings(PERIOD)[0].service, p)
    if mode == "shielded":
        value["naam"] = "Afgeschermd"
        ps = (replace(p, sportlink_name="Afgeschermd"),)  # Must not match this name.
    if mode == "missing": ps = ()
    if mode == "ambiguous": ps = (p, replace(p, person_id="P2"))
    if mode == "duplicate": ps = (p, p)
    if mode == "conflict": ps = (p, replace(p, sportlink_name="Other synthetic spelling"))
    seed_work(db, catalog.bindings(PERIOD)[0].service)
    assert sync(db, catalog, {"A": [value]}, persons=ps)[0] is None
    with db.unit_of_work() as u:
        b, = u.sportlink_bookings.all()
        assert b.volunteer_name == value["naam"]
        assert bool(b.person_id) == linked
        assert b.can_register_no_show == linked
        assert b.identity_issues == issues
        assert not u.temporary_planning.all()
        app = VolunteerPlanningApplicationService(u, IDENTITY, catalog)
        assert app.source(PERIOD)[2]
        assert app.planning_data(PERIOD)[1][0].confirmed_occupancy == 1
        report = u.sportlink_bookings.refresh_state()["identity"]
        assert report["total"] == 1
        assert report["shielded"] == (mode == "shielded")
        assert report["unlinked"] == (not linked)
        assert report["problem_names"] == bool(issues)
        event = NoShowEvent("N", b.assignment_id, b.person_id or "invented", b.starts_at,
                            NOW, IDENTITY.subject_id, season_id(b.starts_at.date()))
        service = NoShowApplicationService(u, IDENTITY)
        if linked:
            service.register(event, source_revision=source_revision(u))
            assert u.no_shows.get("N").booking == b
        else:
            assert not service.available_assignments()
            with pytest.raises(ValueError, match="betrouwbare"):
                service.register(event, source_revision=source_revision(u))
            assert not u.no_shows.all()
            assert u._connection.execute('SELECT count(*) FROM sportlink_sanction_assessments').fetchone()[0] == 0


def test_distinct_shielded_bookings_same_service_and_reorder_are_preserved(db, catalog):
    slot = catalog.bindings(PERIOD)[0].service
    raw = row(slot, replace(people()[0], sportlink_name="Afgeschermd"))
    # Distinguishable source intervals, both overlap the same catalog service.
    second = dict(raw, datumvanaf=(slot.starts_at + timedelta(minutes=10)).isoformat())
    payloads = {"A": [raw, second, row(slot, people()[0])]}
    assert sync(db, catalog, payloads)[0] is None
    before = snapshot(db)
    with db.unit_of_work() as u:
        assert VolunteerPlanningApplicationService(u, IDENTITY, catalog).planning_data(PERIOD)[1][0].confirmed_occupancy == 3
        assert u.sportlink_bookings.refresh_state()["identity"]["shielded"] == 2
    assert sync(db, catalog, {"A": list(reversed(payloads["A"]))})[0] is None
    after = snapshot(db)
    assert after[:2] == before[:2]
    assert {k:v for k,v in after[2].items() if k != "source_revision"} == {k:v for k,v in before[2].items() if k != "source_revision"}


@pytest.mark.parametrize("name", ["Unmatched synthetic name"])
def test_indistinguishable_unlinked_duplicates_never_partially_publish(db, catalog, name):
    slot = catalog.bindings(PERIOD)[0].service
    assert sync(db, catalog, {"A": [row(slot, people()[0])]})[0] is None
    seed_work(db, slot)
    before = snapshot(db)
    value = dict(row(slot, people()[0]), naam=name)
    assert sync(db, catalog, {"A": [value, value]})[0]
    assert snapshot(db) == before
    with db.unit_of_work() as u:
        message = u.sportlink_bookings.refresh_state("attempt")["message"]
        assert name not in message


@pytest.mark.parametrize("conflict", [False, True])
def test_csv_duplicates_preserved_and_conflicting_source_values_block_only_identity(catalog, conflict):
    source = {"Rel. code": "P0", "Naam": "Synthetic 0", "Geb.dat.": "01-01-2000",
              "Lidstatus": "Definitief", "Lidsoort": "Lid", "Status lidmaatschap": "Lid",
              "Achternaam": "Example", "Voorletter(s)": "A.", "Tussenvoegsel(s)": "van", "Roepnaam": "Test0"}
    other = source | ({"Geb.dat.": "02-01-2000"} if conflict else {})
    csv = ";".join(source) + "\n" + ";".join(source.values()) + "\n" + ";".join(other.values())
    ps = SportlinkRealDataAdapter.read_volunteer_persons(csv)
    assert len(ps) == 2
    result = imported(catalog, [row(catalog.bindings(PERIOD)[0].service, ps[0])], ps)
    b, = result.bookings
    assert b.can_register_no_show == (not conflict)
    assert "VOLUNTEER_PERSON_DUPLICATE" in b.identity_issues
    assert ("VOLUNTEER_PERSON_CONFLICT" in b.identity_issues) == conflict
    assert all(s.severity == "WARNING" for s in result.signals)


def test_warning_counts_deduplicate_names_but_not_bookings(db, catalog, capsys):
    slot = catalog.bindings(PERIOD)[0].service
    value = dict(row(slot, people()[0]), naam="Missing synthetic volunteer")
    second = dict(value, datumvanaf=(slot.starts_at + timedelta(minutes=5)).isoformat())
    shielded = dict(value, naam="Afgeschermd")
    assert sync(db, catalog, {"A": [value, second, shielded]})[0] is None
    with db.unit_of_work() as u:
        state = u.sportlink_bookings.refresh_state()
        report = state["identity"]
        assert state["status"] == "Geslaagd, met aandachtspunten"
        assert (report["total"], report["shielded"], report["unlinked"], report["problem_names"]) == (3, 1, 3, 1)
        assert len(report["details"]) == 1 and report["details"][0]["bookings"] == 2
        assert report["categories"][0]["names"] == 1
        attempt = u.sportlink_bookings.refresh_state("attempt")
        assert attempt["status"] == "Geslaagd, met aandachtspunten"
        assert "Missing synthetic volunteer" not in json.dumps(attempt)
    assert capsys.readouterr() == ("", "")


def test_durable_facts_survive_warning_success_and_real_failure(db, catalog):
    slot = catalog.bindings(PERIOD)[0].service
    assert sync(db, catalog, {"A": [row(slot, people()[0])]})[0] is None
    with db.unit_of_work() as u:
        b, = u.sportlink_bookings.all()
        app = NoShowApplicationService(u, IDENTITY)
        app.register(NoShowEvent("N", b.assignment_id, b.person_id, b.starts_at, NOW,
                                 IDENTITY.subject_id, season_id(b.starts_at.date())), source_revision=source_revision(u))
        app.revoke("N", reason="Synthetic correction", revoked_at=NOW)
        fact, revocation = u.no_shows.get("N"), u.no_show_revocations.for_no_show("N")
    assert sync(db, catalog, {"A": [dict(row(slot, people()[0]), naam="Afgeschermd")]})[0] is None
    before = snapshot(db)
    assert sync(db, catalog, {"A": [row(slot, people()[0])], "B": TimeoutError("synthetic-secret")})[0]
    assert snapshot(db) == before
    with db.unit_of_work() as u:
        assert u.no_shows.get("N") == fact
        assert u.no_show_revocations.for_no_show("N") == revocation


def test_unlinked_overlap_on_combined_bar_slots(db):
    from dvk.shift_catalog import load_shift_catalog
    catalog = load_shift_catalog()
    slot = next(b.service for b in catalog.bindings(PERIOD)
                if b.task_code == "701" and b.service.starts_at.weekday() == 2 and b.service.starts_at.hour == 19)
    value = dict(naam="Afgeschermd", datumvanaf=slot.starts_at.isoformat(),
                 datumtot=(slot.starts_at + timedelta(hours=3, minutes=30)).isoformat())
    assert sync(db, catalog, {"741": [value]})[0] is None
    with db.unit_of_work() as u:
        services, needs, _, _ = VolunteerPlanningApplicationService(u, IDENTITY, catalog).planning_data(PERIOD)
        occupied = [(s, n) for s, n in zip(services, needs) if n.confirmed_occupancy]
        assert len(occupied) == 3  # BL-14: two catalog slots plus the actual long source interval.
        assert all(n.confirmed_occupancy == 1 for _, n in occupied)
        assert len(u.sportlink_bookings.all()) == 1


@pytest.mark.parametrize("shielded_count", [1, 2, 3])
def test_local_ui_shows_names_counts_and_excludes_unlinked_no_show_options(tmp_path, monkeypatch, shielded_count):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    from dvk.persistence import SQLiteDatabase
    from dvk.shift_catalog import load_shift_catalog

    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1] / "streamlit_app.py").read_text().replace(
        "value=date.today()", "value=date(2026, 10, 19)"))
    database = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    database.initialize()
    c = load_shift_catalog()
    slot = c.bindings(PERIOD)[0].service
    known = row(slot, people()[0])
    unknown = dict(known, naam="Unmatched synthetic volunteer")
    shielded = dict(known, naam="Afgeschermd")
    assert sync(database, c, {c.bindings(PERIOD)[0].task_code: [known, unknown] + [shielded] * shielded_count})[0] is None
    app = AppTest.from_file(str(script)).run()
    app.button(key="nav-planning").click().run()
    app.button(key="resume-planning").click().run()
    assert not app.exception
    text = "\n".join(item.value for item in app.get("markdown"))
    assert f"Opgehaalde Sportlink-inroosteringen: {2 + shielded_count}" in text
    assert f"Afgeschermd: {shielded_count}" in text
    assert f"Zonder betrouwbare unieke persoonskoppeling: {1 + shielded_count}" in text
    assert any("Geslaagd, met aandachtspunten" in item.value for item in app.markdown)
    tables = [t.value.to_string() for t in app.table]
    assert any("Unmatched synthetic volunteer" in t and "Geen overeenkomstig lid" in t for t in tables)
    assert any("Afgeschermd" in t and "Nee" in t for t in tables)
    source_table = next(t.value for t in app.table if "No-showregistratie mogelijk" in t.value.columns)
    assert source_table.to_string(index=False).count("Afgeschermd") == shielded_count
    from ui_table_events import table
    service_table = table(app, "services_editor-").value
    assert service_table.loc[service_table["Sportlink"].str.contains("Afgeschermd"), "Sportlink"].iloc[0].count("Afgeschermd") == shielded_count
    assert "source_occurrence" not in text + "\n".join(tables) + service_table.to_string()
    from sportlink_fixtures import open_no_show_ui
    open_no_show_ui(app, database, monkeypatch)
    no_show = next(w for w in app.selectbox if w.label == "Inroostering")
    assert len(no_show.options) == 1
    assert people()[0].sportlink_name in no_show.options[0]
    assert "Afgeschermd" not in no_show.options[0]


def test_old_booking_json_keeps_key_and_snapshot_without_migration(db, catalog):
    from dataclasses import asdict
    from dvk.persistence.sportlink_bookings import booking_from_dict

    b, = imported(catalog, [row(catalog.bindings(PERIOD)[0].service, people()[0])], people()).bookings
    old = asdict(b)
    old.pop("identity_issues")
    old.pop("source_occurrence")
    restored = booking_from_dict(json.loads(json.dumps(old, default=str)))
    assert restored.assignment_id == b.assignment_id
    assert restored.can_register_no_show
    assert restored == b


def test_unlinked_bookings_do_not_hide_eligible_no_show_with_recent_limit(db, catalog):
    slot = catalog.bindings(PERIOD)[0].service
    linked, = imported(catalog, [row(slot, people()[0])], people()).bookings
    unlinked = tuple(replace(linked, person_id=None, person_name=None, volunteer_name=f"Synthetic unknown {i}")
                     for i in range(55))
    with db.unit_of_work() as u:
        seed_bookings(u, (linked, *unlinked))
        u.commit()
        assert NoShowApplicationService(u, IDENTITY).available_assignments(limit=1) == (linked,)


def test_source_name_presentation_is_preserved_without_changing_exact_matching(catalog):
    p = people()[0]
    value = dict(row(catalog.bindings(PERIOD)[0].service, p), naam=f"  {p.sportlink_name}  ")
    b, = imported(catalog, [value], (p,)).bookings
    assert b.volunteer_name == value["naam"]
    assert b.person_id == p.person_id
    assert b.can_register_no_show


@pytest.mark.parametrize("count", [1, 2, 3])
def test_identical_shielded_rows_remain_separate_after_reopen_and_refresh(db, catalog, count):
    from dvk.persistence import SQLiteDatabase

    slot = catalog.bindings(PERIOD)[0].service
    value = dict(row(slot, people()[0]), naam="Afgeschermd")
    single, = imported(catalog, [value], people()).bookings
    # Explicit pre-correction key contract, independent of the new occurrence field.
    import hashlib
    from datetime import timezone
    legacy_key = ("Afgeschermd", "A", slot.starts_at.astimezone(timezone.utc).isoformat(),
                  slot.ends_at.astimezone(timezone.utc).isoformat(), value["lokatie"])
    assert single.assignment_id == "SLU-" + hashlib.sha256(json.dumps(legacy_key, ensure_ascii=False).encode()).hexdigest()
    assert sync(db, catalog, {"A": [value] * count})[0] is None
    before = snapshot(db)[0]
    assert len(before) == len({b.assignment_id for b in before}) == count
    assert single.assignment_id in {b.assignment_id for b in before}
    assert {b.source_occurrence for b in before} == set(range(1, count + 1))
    assert len({b.provenance.source_record_key for b in before}) == count
    for b in before:
        assert b.person_id is None and b.person_name is None
        assert b.volunteer_name == "Afgeschermd" and not b.can_register_no_show
        assert b.provenance.source_value == str(value)
        assert b.provenance.kind == "SOURCE_FACT"
    reopened = SQLiteDatabase(db.path)
    with reopened.unit_of_work() as u:
        assert u.sportlink_bookings.all() == before
        app = VolunteerPlanningApplicationService(u, IDENTITY, catalog)
        assert app.planning_data(PERIOD)[1][0].confirmed_occupancy == count
        assert app.service_names(PERIOD)[slot.service_id] == ", ".join(["Afgeschermd"] * count)
        report = u.sportlink_bookings.refresh_state()["identity"]
        assert (report["total"], report["shielded"], report["unlinked"]) == (count, count, count)
        no_show = NoShowApplicationService(u, IDENTITY)
        assert no_show.registration_choices(before) == ()
        assert no_show.available_assignments() == ()
        for b in before:
            event = NoShowEvent("N", b.assignment_id, "invented", b.starts_at, NOW,
                                IDENTITY.subject_id, season_id(b.starts_at.date()))
            with pytest.raises(ValueError, match="betrouwbare"):
                no_show.register(event, source_revision=source_revision(u))
        assert not u.no_shows.all()
        assert u._connection.execute('SELECT count(*) FROM sportlink_sanction_assessments').fetchone()[0] == 0
    assert sync(reopened, catalog, {"A": [value] * count})[0] is None
    assert snapshot(reopened)[0] == before


def test_shielded_counts_replace_instead_of_accumulating(db, catalog):
    slot = catalog.bindings(PERIOD)[0].service
    value = dict(row(slot, people()[0]), naam="Afgeschermd")
    for count in (1, 3, 2, 0):
        assert sync(db, catalog, {"A": [value] * count})[0] is None
        with db.unit_of_work() as u:
            assert len(u.sportlink_bookings.all()) == count
            assert VolunteerPlanningApplicationService(u, IDENTITY, catalog).planning_data(PERIOD)[1][0].confirmed_occupancy == count


def test_shielded_group_numbering_and_mixed_occupancy_are_order_independent(db, catalog):
    from itertools import permutations

    slot = catalog.bindings(PERIOD)[0].service
    known = row(slot, people()[0])
    shielded = dict(known, naam="Afgeschermd")
    other_group = dict(shielded, lokatie="Other synthetic location")
    values = [shielded, other_group, known, shielded]
    expected_keys = None
    for order in permutations(values):
        assert sync(db, catalog, {"A": order})[0] is None
        with db.unit_of_work() as u:
            bookings = u.sportlink_bookings.all()
            keys = {b.assignment_id for b in bookings}
            if expected_keys is None:
                expected_keys = keys
            assert keys == expected_keys and len(keys) == 4
            assert [b.source_occurrence for b in bookings if b.location == "Other synthetic location"] == [1]
            assert VolunteerPlanningApplicationService(u, IDENTITY, catalog).planning_data(PERIOD)[1][0].confirmed_occupancy == 4
    assert sync(db, catalog, {"A": [shielded, shielded, known]})[0] is None
    with db.unit_of_work() as u:
        assert VolunteerPlanningApplicationService(u, IDENTITY, catalog).planning_data(PERIOD)[1][0].confirmed_occupancy == 3
        assert len(NoShowApplicationService(u, IDENTITY).available_assignments()) == 1


@pytest.mark.parametrize("linked", [False, True])
def test_other_duplicates_still_block_with_identical_shielded_rows(db, catalog, linked):
    slot = catalog.bindings(PERIOD)[0].service
    known = row(slot, people()[0])
    shielded = dict(known, naam="Afgeschermd")
    assert sync(db, catalog, {"A": [shielded, shielded, known]})[0] is None
    seed_work(db, slot)
    before = snapshot(db)
    duplicate = known if linked else dict(known, naam="Unmatched synthetic volunteer")
    assert sync(db, catalog, {"A": [shielded, shielded, duplicate, duplicate]})[0]
    assert snapshot(db) == before


@pytest.mark.parametrize("failure", ["fetch", "invalid", "rollback"])
def test_identical_shielded_refresh_preserves_state_on_failure(db, catalog, monkeypatch, failure):
    from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository

    slot = catalog.bindings(PERIOD)[0].service
    value = dict(row(slot, people()[0]), naam="Afgeschermd")
    assert sync(db, catalog, {"A": [value, value]})[0] is None
    seed_work(db, slot)
    before = snapshot(db)
    payload = {"A": [value] * 3}
    if failure == "fetch":
        payload["B"] = TimeoutError("synthetic failure")
    elif failure == "invalid":
        payload["A"].append(dict(value, datumtot=slot.starts_at.isoformat()))
    else:
        def fail(self, identifier):
            raise RuntimeError("synthetic delete failure")
        monkeypatch.setattr(SQLiteTemporaryPlanningRepository, "remove", fail)
    if failure == "rollback":
        with pytest.raises(RuntimeError, match="synthetic delete failure"):
            sync(db, catalog, payload)
    else:
        assert sync(db, catalog, payload)[0]
    assert snapshot(db) == before


@pytest.mark.parametrize("shielded", [False, True])
def test_pre_occurrence_payloads_keep_existing_keys(catalog, shielded):
    from dataclasses import asdict
    from dvk.persistence.sportlink_bookings import booking_from_dict

    value = row(catalog.bindings(PERIOD)[0].service, people()[0])
    if shielded:
        value["naam"] = "Afgeschermd"
    b, = imported(catalog, [value], people()).bookings
    old = asdict(b)
    old.pop("source_occurrence")
    restored = booking_from_dict(json.loads(json.dumps(old, default=str)))
    assert restored == b and restored.assignment_id == b.assignment_id
    # Occurrence must never alter keys for any other kind of booking.
    if not shielded:
        assert replace(b, source_occurrence=3).assignment_id == b.assignment_id
        unlinked = replace(b, person_id=None, person_name=None)
        assert replace(unlinked, source_occurrence=3).assignment_id == unlinked.assignment_id


# Preserve historical BL-11 dates with an explicit test clock.
pytestmark = pytest.mark.usefixtures("historical_registration_context")
