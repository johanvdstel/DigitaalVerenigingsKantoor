"""Export settings and source navigation with synthetic files and SQLite only."""
from datetime import date
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

import pytest

from dvk.candidate_context import CandidateContextApplicationService
from dvk.historical_backlog import HISTORICAL_FILENAME
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.real_data_import import SportlinkRealDataAdapter
from dvk.shift_catalog import load_shift_catalog
from dvk.sportlink_exports import (
    EXPORT_FILENAMES, ExportFileError, default_export_directory, save_export_directory,
)
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
from test_candidate_context_v05 import exports
from test_navigation_v05 import app_at
from test_planning_ui_names_v05 import page
from test_volunteer_planning_integration_v05 import PERIOD, seed_work, snapshot, sync
from ui_table_events import table


def test_configured_path_survives_process_restart_and_is_shared():
    previous = default_export_directory()
    folder = Path.home() / "synthetische exports"
    shutil.copytree(previous, folder)
    for dataset, contents in exports().items():
        (folder / EXPORT_FILENAMES[dataset]).write_bytes(contents)

    assert save_export_directory("~/synthetische exports") == folder.resolve()
    new_process = subprocess.check_output([
        sys.executable, "-c",
        "from dvk.sportlink_exports import default_export_directory; print(default_export_directory())",
    ], text=True)
    assert Path(new_process.strip()) == folder.resolve()

    sources = LocalCsvSourceApplicationService()
    assert sources.load().directory == folder.resolve()
    assert sources.volunteer_persons() == SportlinkRealDataAdapter.read_volunteer_persons(
        (folder / "Leden.csv").read_text(encoding="utf-8-sig"))
    result = sources.duty_control(as_of=date(2026, 10, 24), source_period="2026-2027")
    assert result.sources.directory == folder.resolve()
    assert result.dashboard.source.persons[0].person_id == "M1"
    assert load_shift_catalog() == load_shift_catalog(folder)
    assert not sources.historical_backlog(person_ids=("M1",)).available
    explicit = previous / "Leden.csv"
    assert SportlinkRealDataAdapter.read_rows(explicit, "leden") == []
    assert SportlinkRealDataAdapter.read_rows(None, "leden")


def test_invalid_or_inaccessible_map_does_not_replace_saved_setting(monkeypatch):
    selected = save_export_directory(str(default_export_directory()))
    original = os.scandir

    def scandir(path):
        if Path(path) == selected.parent:
            raise PermissionError("synthetic denial")
        return original(path)

    monkeypatch.setattr(os, "scandir", scandir)
    for value in ("", "relatief", str(selected / "Leden.csv"), str(selected / "onbekend"), str(selected.parent)):
        with pytest.raises(ExportFileError, match="bestaande, toegankelijke exportmap"):
            save_export_directory(value)
        assert default_export_directory() == selected


def test_open_sources_reports_files_independently_and_does_not_create_database(tmp_path):
    folder = default_export_directory()
    (folder / "Teams.csv").unlink()
    (folder / "Commissies.csv").unlink()
    (folder / "Commissies.csv").mkdir()
    app = app_at(tmp_path)
    app.button(key="nav-sources").click().run()
    assert not app.exception
    csv_rows, api_rows = (data.value.set_index("Databron") for data in app.dataframe)
    assert csv_rows.loc["Teams.csv", "Beschikbaarheid"] == "Ontbreekt"
    assert csv_rows.loc["Teams.csv", "Verplicht"] == "Ja"
    assert csv_rows.loc["Commissies.csv", "Beschikbaarheid"] == "Niet leesbaar"
    assert csv_rows.loc["Leden.csv", "Beschikbaarheid"] == "Aanwezig en toegankelijk"
    assert csv_rows.loc["Leden.csv", "Status"] == "Niet geladen"
    assert csv_rows.loc[HISTORICAL_FILENAME, "Verplicht"] == "Nee"
    assert csv_rows.loc[HISTORICAL_FILENAME, "Beschikbaarheid"] == "Ontbreekt"
    assert set(api_rows.Status) == {"Niet opgehaald"}
    assert not (tmp_path / "dvk_v05.sqlite").exists()


def test_open_sources_does_not_migrate_old_database(tmp_path):
    path = tmp_path / "dvk_v05.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE synthetic_marker (value TEXT)")
        connection.execute("INSERT INTO synthetic_marker VALUES ('bewaren')")
    before = path.read_bytes()
    app = app_at(tmp_path)
    app.button(key="nav-sources").click().run()
    assert not app.exception
    assert any("afwijkend databaseschema" in warning.value for warning in app.warning)
    assert path.read_bytes() == before


def test_save_and_navigation_keep_validated_source_and_temporary_work(tmp_path, monkeypatch):
    calls = []

    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError("Opening and saving may not load sources")

    monkeypatch.setattr(CandidateContextApplicationService, "load", forbidden)
    app, db = page(tmp_path)
    catalog = load_shift_catalog()
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db, catalog, {})[0] is None
    monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows", forbidden)
    seed_work(db, service)
    before = snapshot(db)

    app.button(key="nav-sources").click().run()
    assert next(b for b in app.button if b.label == "Sportlink-inroosteringen synchroniseren").disabled
    new_folder = tmp_path / "andere exports"
    new_folder.mkdir()
    field = next(w for w in app.text_input if w.label == "Sportlink-exportmap")
    submit = next(b for b in app.button if b.label == "Exportmap opslaan")
    field.set_value(str(new_folder / "ontbreekt"))
    submit.click().run()
    assert any("bestaande, toegankelijke exportmap" in error.value for error in app.error)
    field = next(w for w in app.text_input if w.label == "Sportlink-exportmap")
    submit = next(b for b in app.button if b.label == "Exportmap opslaan")
    field.set_value(str(new_folder))
    submit.click().run()
    assert any("Exportmap opgeslagen" in success.value for success in app.success)
    assert default_export_directory() == new_folder.resolve()
    assert snapshot(db) == before and not calls

    restarted = app_at(tmp_path)
    restarted.button(key="nav-sources").click().run()
    assert any(str(new_folder) in caption.value for caption in restarted.caption)
    api = restarted.dataframe[1].value.set_index("Databron")
    assert api.loc["Sportlink Vrijwilligers", "Bruikbaarheid"] == "Gevalideerd voor gekozen periode"
    restarted.button(key="nav-planning").click().run()
    restarted.button(key="resume-planning").click().run()
    assert not restarted.exception and not calls
    assert table(restarted, "services_editor-").value["Tijdelijk DVK"].sum() == 1
    assert snapshot(db) == before
