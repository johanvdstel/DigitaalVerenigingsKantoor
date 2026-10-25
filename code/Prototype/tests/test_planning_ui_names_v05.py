"""UI-only PR #38: source names and relocated source controls. Synthetic data only."""
import ast
from collections import Counter
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
import json

import pytest
from streamlit.testing.v1 import AppTest

from dvk.persistence import SQLiteDatabase
from dvk.shift_catalog import load_shift_catalog
from dvk.vrijwilligers_adapter import same_task_group, overlaps_service_date
from test_volunteer_planning_integration_v05 import PERIOD, people, row, sync, seed_work, snapshot, client

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def page(tmp_path):
    script = tmp_path / "streamlit_app.py"
    script.write_text(SOURCE.read_text().replace("value=date.today()", "value=date(2026, 10, 19)"))
    app = AppTest.from_file(str(script), default_timeout=20).run()
    app.button(key="nav-planning").click().run()
    app.button(key="activate-planning").click().run()
    assert not app.exception
    return app, SQLiteDatabase(tmp_path / "dvk_v05.sqlite")


def helpers():
    tree = ast.parse(SOURCE.read_text())
    module = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef)
                             and n.name == "_sportlink_names"], type_ignores=[])
    ns = dict(same_task_group=same_task_group, overlaps_service_date=overlaps_service_date)
    exec(compile(module, str(SOURCE), "exec"), ns)
    return ns


@pytest.mark.parametrize("count", [0, 1, 2, 4])
def test_service_names_and_totals_with_existing_kies_selection(tmp_path, count):
    app, db = page(tmp_path)
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    values = [dict(row(binding.service, people()[0]), naam=chr(65 + i)) for i in range(count)]
    assert sync(db, catalog, {binding.task_code: values}, persons=())[0] is None
    seed_work(db, binding.service)
    before = snapshot(db)
    app.run()
    table = app.dataframe[0].value
    selected = table[table.service_id == binding.service.service_id].iloc[0]
    if count:
        assert Counter(selected["Sportlink"].split(", ")) == Counter(chr(65 + i) for i in range(count))
    else:
        assert selected["Sportlink"] == "geen namen"
    assert selected["Tijdelijk DVK"] == 1
    assert selected["DVK-bezetting"] == count + 1
    assert selected["Open minimum"] == max(0, binding.service.required_staff - count - 1)
    assert "Locatie" not in table.columns
    app.session_state["selected_service_id"] = binding.service.service_id
    app.run()
    assert app.dataframe[0].value.query("Kies == '☑'")["service_id"].tolist() == [binding.service.service_id]
    assert not any(t.value.startswith("Sportlink — volledige namenlijst:") for t in app.text)
    assert snapshot(db) == before


def test_shielded_and_unlinked_original_names_keep_separate_overlapping_rows(tmp_path):
    app, db = page(tmp_path)
    catalog = load_shift_catalog()
    slot = next(b.service for b in catalog.bindings(PERIOD)
                if b.task_code == "701" and b.service.starts_at.weekday() == 2 and b.service.starts_at.hour == 19)
    raw = dict(naam="Afgeschermd", datumvanaf=slot.starts_at.isoformat(),
               datumtot=(slot.starts_at + timedelta(hours=3, minutes=30)).isoformat())
    second = dict(raw, datumvanaf=(slot.starts_at + timedelta(minutes=10)).isoformat())
    unknown = dict(raw, naam="Onbekende synthetische naam")
    # 442 must not appear in the bar list, and boundary-only contact must not appear.
    assert sync(db, catalog, {"741": [raw, second, unknown]}, persons=())[0] is None
    app.session_state["selected_service_id"] = slot.service_id
    app.run()
    cells = app.dataframe[0].value
    text = cells[cells.service_id == slot.service_id].iloc[0]["Sportlink"]
    assert Counter(text.split(", ")) == Counter(["Afgeschermd", "Afgeschermd", "Onbekende synthetische naam"])
    assert cells[cells.service_id == slot.service_id].iloc[0]["DVK-bezetting"] == 3
    ns = helpers()
    source = SimpleNamespace(volunteer_name="Bronnaam", task_code="761", starts_at=slot.starts_at, ends_at=slot.ends_at)
    assert ns["_sportlink_names"](slot, catalog.bindings(PERIOD), (source,)) == "Bronnaam"
    assert ns["_sportlink_names"](slot, catalog.bindings(PERIOD), (
        SimpleNamespace(**(vars(source) | {"task_code": "442"})),
        SimpleNamespace(**(vars(source) | {"starts_at": slot.ends_at, "ends_at": slot.ends_at + timedelta(hours=1)})),
    )) == "geen namen"


def test_unknown_source_and_changed_period_never_claim_no_names(tmp_path):
    app, db = page(tmp_path)
    assert set(app.dataframe[0].value["Sportlink"]) == {"Onbekend"}
    assert sync(db, load_shift_catalog(), {})[0] is None
    app.run()
    assert set(app.dataframe[0].value["Sportlink"]) == {"geen namen"}
    app.date_input[0].set_value(PERIOD.start + timedelta(days=7)).run()
    assert not app.exception
    app.button(key="confirm-period-change").click().run()
    assert set(app.dataframe[0].value["Sportlink"]) == {"Onbekend"}


def test_long_names_remain_complete_in_readonly_cell_with_fixed_size(tmp_path):
    app, db = page(tmp_path)
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    names = ["W" * 60, "Synthetic very long volunteer name " * 4, "Afgeschermd", "Other source name"]
    assert sync(db, catalog, {binding.task_code: [dict(row(binding.service, people()[0]), naam=n) for n in names]}, persons=())[0] is None
    app.session_state["selected_service_id"] = binding.service.service_id
    app.run()
    table = app.dataframe[0]
    value = table.value[table.value.service_id == binding.service.service_id].iloc[0]["Sportlink"]
    assert table.proto.row_height == 32
    config = json.loads(table.proto.columns)
    assert config["Sportlink"]["width"] == 320
    assert config["Sportlink"]["type_config"]["type"] == "text"
    assert config["Sportlink"]["disabled"] is True
    assert "Dubbelklik" in config["Sportlink"]["help"]
    with db.unit_of_work() as u:
        full = ", ".join(b.volunteer_name for b in u.sportlink_bookings.all())
    assert value == full
    assert "…" not in value
    assert not any(t.value.startswith("Sportlink — volledige namenlijst:") for t in app.text)
    assert not any("Lange namenlijsten zijn afgekort" in c.value for c in app.caption)
    tree = ast.parse(SOURCE.read_text())
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_names_preview" for n in tree.body)


def test_source_controls_under_databronnen_and_no_show_roundtrip(tmp_path, monkeypatch):
    app, db = page(tmp_path)
    # Rendered element order must put source controls after Databronnen, not under No-shows.
    nodes = list(app.main)
    headers = {n.value: i for i, n in enumerate(nodes) if n.type == "markdown" and n.value.startswith("### ")}
    upload = next(i for i, n in enumerate(nodes) if n.type == "button" and n.label == "Sportlink-inroosteringen synchroniseren")
    assert headers["### No-shows"] < headers["### Databronnen"] < upload
    assert any("Leden.csv wordt bij synchroniseren opnieuw" in c.value for c in app.caption)
    from dvk.sportlink_exports import export_path
    export_path("leden").unlink()
    app.button[ next(i for i,b in enumerate(app.button) if b.label == "Sportlink-inroosteringen synchroniseren") ].click().run()
    assert any("Leden.csv" in e.value and "ontbreekt" in e.value for e in app.error)
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    assert sync(db, catalog, {binding.task_code: [row(binding.service, people()[0])]})[0] is None
    app.run()
    next(b for b in app.button if b.label == "No-show bevestigen").click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        fact, = u.no_shows.all()
    app.text_area(key="no-show-revocation-reason").set_value("Synthetic UI correction")
    next(b for b in app.button if b.label == "Intrekking bevestigen").click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        assert u.no_show_revocations.for_no_show(fact.no_show_id).reason == "Synthetic UI correction"


@pytest.mark.parametrize("mode", ["success", "transport", "decode"])
def test_moved_sync_uses_existing_service_with_same_arguments_and_messages(tmp_path, monkeypatch, mode):
    import streamlit as st
    import dvk.vrijwilligers_client as transport
    import dvk.real_data_import as members
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    raw = [row(binding.service, people()[0])]
    seen = []
    synthetic = client({binding.task_code: TimeoutError("synthetic-client") if mode == "transport" else raw}, seen)
    def read_local(dataset):
        if mode == "decode":
            raise ValueError("Leden.csv: synthetisch onleesbaar bestand")
        return "synthetic CSV"
    monkeypatch.setattr("dvk.local_csv_sources.read_export_text", read_local)
    monkeypatch.setattr(members.SportlinkRealDataAdapter, "read_volunteer_persons", lambda text: people())
    monkeypatch.setattr(transport, "SportlinkVrijwilligersClient", lambda *a, **k: synthetic)
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "synthetic-client")
    app, db = page(tmp_path)
    assert sync(db, catalog, {binding.task_code: raw})[0] is None
    seed_work(db, binding.service)
    before = snapshot(db)
    app.run()
    next(c for c in app.checkbox if c.key.startswith("confirm-source-")).check().run()
    next(b for b in app.button if b.label == "Sportlink-inroosteringen synchroniseren").click().run()
    assert not app.exception
    if mode != "success":
        assert app.error
        assert "synthetic-client" not in " ".join(e.value for e in app.error)
        assert snapshot(db) == before
        return
    assert any("Sportlink-inroosteringen vernieuwd" in s.value for s in app.success)
    with db.unit_of_work() as u:
        assert len(u.sportlink_bookings.all()) == 1
        assert not u.temporary_planning.all()
    assert [q["vrijwilligerstaakcode"][0] for q in seen] == list(catalog.task_codes)
