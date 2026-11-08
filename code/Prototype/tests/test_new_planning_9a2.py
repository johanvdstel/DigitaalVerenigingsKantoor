"""Automatic start and durable resume with synthetic Sportlink inputs only."""
from datetime import datetime, timedelta
from pathlib import Path
import os
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

from dvk import local_csv_sources
from dvk.historical_backlog import HISTORICAL_FILENAME
from dvk.new_planning import NewPlanningApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod
from dvk.planning_session import PlanningSessionApplicationService, TZ
from dvk.programma_client import ProgrammaFetchError, ProgrammaFetchResult, SportlinkProgrammaClient
from dvk.shift_catalog import load_shift_catalog
from dvk.sportlink_exports import EXPORT_FILENAMES, default_export_directory
from dvk.vrijwilligers_client import (
    SportlinkVrijwilligersClient, VrijwilligersFetchError, VrijwilligersFetchResult,
)
from test_candidate_context_v05 import exports
from test_historical_backlog_v05 import history_row, history_text
from test_planning_ui_names_v05 import SOURCE
from test_programma_team_linking_v05 import row as program_row
from test_volunteer_planning_integration_v05 import IDENTITY, PERIOD, people, row, seed_work, snapshot
from ui_table_events import table


def open_page(tmp_path):
    script = tmp_path / "streamlit_app.py"
    script.write_text(SOURCE.read_text())
    app = AppTest.from_file(str(script), default_timeout=20).run()
    return app, SQLiteDatabase(tmp_path / "dvk_v05.sqlite")


def statuses(app):
    return next(node.value.set_index("Databron") for node in app.dataframe
                if "Databron" in node.value and len(node.value) == 8)


@pytest.fixture
def sources(monkeypatch):
    folder = default_export_directory()
    for dataset, data in exports(functions=({"Rel. code": "M1", "Functie": "Trainer Senioren"},)).items():
        (folder / EXPORT_FILENAMES[dataset]).write_bytes(data)
    (folder / HISTORICAL_FILENAME).write_text(history_text([history_row("M1", value=4)]))
    calls = []
    read = local_csv_sources.read_export_text

    def record_csv(dataset, explicit_path=None):
        calls.append(("csv", Path(explicit_path).name))
        return read(dataset, explicit_path)

    def fetch_programma(self, **kwargs):
        calls.append(("program", None))
        return ProgrammaFetchResult(())

    def fetch_volunteers(self, *, task_code, **kwargs):
        calls.append(("volunteers", task_code))
        return VrijwilligersFetchResult(task_code, ())

    monkeypatch.setattr(local_csv_sources, "read_export_text", record_csv)
    monkeypatch.setattr(SportlinkProgrammaClient, "fetch_rows", fetch_programma)
    monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows", fetch_volunteers)
    return folder, calls


def test_current_week_and_one_ordered_load_cycle(sources, tmp_path):
    _, calls = sources
    app, database = open_page(tmp_path)
    app.button(key="nav-sources").click().run()
    app.button(key="nav-planning").click().run()
    assert not calls
    assert not any(b.label == "Sportlink-inroosteringen synchroniseren" for b in app.button)
    today = datetime.now(TZ).date()
    monday = today - timedelta(days=today.weekday())
    expected = PlanningPeriod(monday, monday + timedelta(days=6))
    assert app.radio(key="planning-mode").value == "Week"
    assert app.date_input(key="planning-from").value == today
    assert any(f"{expected.start:%d-%m-%Y} t/m {expected.end:%d-%m-%Y}" in item.value for item in app.markdown)
    app.button(key="activate-planning").click().run()
    assert not app.exception
    with database.unit_of_work() as uow:
        assert PlanningSessionApplicationService(uow, IDENTITY).current().period == expected
    ordered = [("csv", name) for name in (*EXPORT_FILENAMES.values(), HISTORICAL_FILENAME)]
    ordered += [("program", None)] + [("volunteers", code) for code in load_shift_catalog().task_codes]
    assert calls == ordered
    for _ in range(2):
        app.run()
        app.button(key="nav-sources").click().run()
        app.button(key="nav-planning").click().run()
    assert calls == ordered
    source_rows = statuses(app)
    for name in EXPORT_FILENAMES.values():
        expected_status = "Ingelezen, geen regels" if name == "Commissies.csv" else "Ingelezen"
        assert source_rows.loc[name, "Status"] == expected_status
    assert source_rows.loc["Sportlink Programma", "Status"] == "Geslaagd, geen operationele wedstrijden"
    assert source_rows.loc["Sportlink Vrijwilligers", "Status"] == "Geslaagd, geen inroosteringen"
    assert set(table(app, "services_editor-").value["Sportlink"]) == {"geen namen"}


def test_custom_period_and_durable_resume_with_two_shielded_bookings(sources, tmp_path, monkeypatch):
    folder, calls = sources
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    app, database = open_page(tmp_path)

    def program(self, **kwargs):
        calls.append(("program", None))
        return ProgrammaFetchResult((program_row(thuisteam="CKC O17-1", wedstrijdcode="SYNTH",
                                                  wedstrijddatum=binding.service.starts_at.isoformat()),))

    def volunteers(self, *, task_code, **kwargs):
        calls.append(("volunteers", task_code))
        shielded = dict(row(binding.service, people()[0]), naam="Afgeschermd")
        return VrijwilligersFetchResult(task_code, (shielded, shielded) if task_code == binding.task_code else ())

    monkeypatch.setattr(SportlinkProgrammaClient, "fetch_rows", program)
    monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows", volunteers)
    app.button(key="nav-planning").click().run()
    app.radio(key="planning-mode").set_value("Aangepast").run()
    app.date_input(key="planning-from").set_value(PERIOD.start).run()
    app.date_input(key="planning-until").set_value(PERIOD.end).run()
    assert not calls
    app.button(key="activate-planning").click().run()
    assert not app.exception
    context = app.session_state["candidate-context"]
    assert context.period == PERIOD and context.program.matches[0].match_id == "SYNTH"
    assert context.historical_backlog.values == {"M1": 4}
    assert len(context.source.roles) == 1
    bookings = snapshot(database)[0]
    assert len(bookings) == 2 and len({booking.assignment_id for booking in bookings}) == 2
    assert all(booking.volunteer_name == "Afgeschermd" and booking.person_id is None for booking in bookings)
    seed_work(database, binding.service)
    before = snapshot(database)
    before_calls = list(calls)
    # Remove the source exports to prove the reopened app uses the stored context.
    for filename in (*EXPORT_FILENAMES.values(), HISTORICAL_FILENAME):
        (folder / filename).unlink()
    fresh = AppTest.from_file(str(tmp_path / "streamlit_app.py"), default_timeout=20).run()
    fresh.button(key="nav-planning").click().run()
    assert not fresh.metric
    fresh.button(key="resume-planning").click().run()
    assert not fresh.exception and fresh.session_state["candidate-context"] == context
    assert set(statuses(fresh).loc[["Sportlink Programma", "Sportlink Vrijwilligers"], "Status"]) == {
        "Technisch geslaagd",
    }
    assert table(fresh, "services_editor-").value["Tijdelijk DVK"].sum() == 1
    assert snapshot(database) == before and calls == before_calls
    child = subprocess.check_output([
        sys.executable, "-c", """
import sys
from dvk.persistence import SQLiteDatabase
with SQLiteDatabase(sys.argv[1]).unit_of_work(migrate_schema=False) as uow:
    session = uow.planning_sessions.get()
    context = uow.planning_sessions.candidate_sources(session.session_id).context
    print(context.program.matches[0].match_id, context.historical_backlog.values["M1"])
""", str(database.path),
    ], text=True)
    assert child.strip() == "SYNTH 4"


@pytest.mark.parametrize("fault", [
    "missing-csv", "missing-members", "invalid-csv", "programma", "invalid-programma", "vrijwilligers",
])
def test_partial_sources_stay_explicit_and_only_safe_results_are_used(sources, tmp_path, monkeypatch, fault):
    folder, calls = sources
    if fault == "missing-csv":
        (folder / "Functies.csv").unlink()
    elif fault == "missing-members":
        (folder / "Leden.csv").unlink()
    elif fault == "invalid-csv":
        (folder / "Functies.csv").write_text("Verkeerde kolom\nsynthese\n")
    elif fault in {"programma", "invalid-programma"}:
        def fail_program(self, **kwargs):
            calls.append(("program", None))
            cause = "invalid_response" if fault == "invalid-programma" else "transport"
            raise ProgrammaFetchError("synthetic-private", cause=cause)
        monkeypatch.setattr(SportlinkProgrammaClient, "fetch_rows", fail_program)
    else:
        def fail_volunteers(self, *, task_code, **kwargs):
            calls.append(("volunteers", task_code))
            raise VrijwilligersFetchError("connection failure")
        monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows", fail_volunteers)

    app, database = open_page(tmp_path)
    app.button(key="nav-planning").click().run()
    app.button(key="activate-planning").click().run()
    assert not app.exception
    rows = statuses(app)
    program = rows.loc["Sportlink Programma", "Status"]
    volunteers = rows.loc["Sportlink Vrijwilligers", "Status"]
    if fault.startswith("missing"):
        assert program == "Niet opgehaald"
        missing = "Functies.csv" if fault == "missing-csv" else "Leden.csv"
        assert rows.loc[missing, "Status"] == "Niet beschikbaar"
        assert "ontbreekt" in rows.loc[missing, "Toelichting"]
    if fault == "missing-members":
        assert volunteers == "Niet opgehaald"
        assert "Leden.csv" in rows.loc["Sportlink Vrijwilligers", "Toelichting"]
        assert calls == [("csv", "Leden.csv")]
    if fault == "invalid-csv":
        assert program == "Niet opgehaald"
        assert rows.loc["Functies.csv", "Status"] == "Niet beschikbaar"
        assert "ontbrekende verplichte kolommen" in rows.loc["Functies.csv", "Toelichting"]
    if fault in {"programma", "invalid-programma"}:
        assert program == "Aanvraag mislukt"
        assert rows.loc["Leden.csv", "Status"] == "Ingelezen"
        diagnosis = "ongeldige respons" if fault == "invalid-programma" else "verbinding of gegevensoverdracht"
        assert diagnosis in rows.loc["Sportlink Programma", "Toelichting"]
        assert "synthetic-private" not in rows.loc["Sportlink Programma", "Toelichting"]
    if fault not in {"missing-members", "vrijwilligers"}:
        assert volunteers == "Geslaagd, geen inroosteringen"
    if fault == "vrijwilligers":
        assert volunteers == "Laatste verversing mislukt"
        assert program == "Geslaagd, geen operationele wedstrijden"
        assert "Geen gevalideerde bron gepubliceerd" in rows.loc["Sportlink Vrijwilligers", "Toelichting"]
    has_valid_occupancy = fault not in {"missing-members", "vrijwilligers"}
    service_rows = table(app, "services_editor-").value
    assert set(service_rows["Sportlink"]) == ({"geen namen"} if has_valid_occupancy else {"Onbekend"})
    app.session_state["selected_service_id"] = service_rows.iloc[0].service_id
    app.run()
    assert not app.exception
    assert any("Kandidaten zijn beschikbaar na een geslaagde bronimport" in item.value for item in app.info)
    assert not any(frame.key and frame.key.startswith("candidate-table-") for frame in app.dataframe)
    assert not any("eerste automatische bronlading" in item.value for item in app.warning)
    with database.unit_of_work() as uow:
        sessions = PlanningSessionApplicationService(uow, IDENTITY)
        current = sessions.current()
        assert not current.initial_load_pending and sessions.candidate_sources(current.session_id) is not None
    assert bool(snapshot(database)[2]) == has_valid_occupancy


@pytest.mark.parametrize("stop_at", ["before-volunteers", "before-context-commit"])
def test_interrupted_initial_load_is_visible_after_process_restart(sources, tmp_path, stop_at):
    _, calls = sources
    db_path = tmp_path / "dvk_v05.sqlite"
    child = subprocess.run([sys.executable, "-c", """
import os
import sys
from unittest.mock import patch

from dvk.new_planning import NewPlanningApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.persistence.planning_session import SQLitePlanningSessionRepository
from dvk.programma_client import SportlinkProgrammaClient, ProgrammaFetchResult
from dvk.shift_catalog import load_shift_catalog
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient, VrijwilligersFetchResult
from test_volunteer_planning_integration_v05 import IDENTITY, PERIOD, people, row

database = SQLiteDatabase(sys.argv[1])
stop_at = sys.argv[2]
catalog = load_shift_catalog()
binding = catalog.bindings(PERIOD)[0]

def volunteers(self, *, task_code, **kwargs):
    booking = dict(row(binding.service, people()[0]), naam="Afgeschermd")
    return VrijwilligersFetchResult(task_code, (booking,) if task_code == binding.task_code else ())

def progress(message):
    if stop_at == "before-volunteers" and message.startswith("Feitelijke"):
        os._exit(42)

save = SQLitePlanningSessionRepository.save_candidate_sources
def save_and_exit(self, *args):
    save(self, *args)
    os._exit(43)

if stop_at == "before-context-commit":
    SQLitePlanningSessionRepository.save_candidate_sources = save_and_exit

with (
    patch.object(SportlinkProgrammaClient, "fetch_rows", return_value=ProgrammaFetchResult(())),
    patch.object(SportlinkVrijwilligersClient, "fetch_rows", volunteers),
):
    NewPlanningApplicationService(database, IDENTITY).start(
        period=PERIOD, catalog=catalog, source_period="2026-2027", client_id="synthetic", progress=progress,
    )
""", str(db_path), stop_at], env={**os.environ, "PYTHONPATH": os.pathsep.join(sys.path)})
    assert child.returncode == (42 if stop_at == "before-volunteers" else 43)

    app, database = open_page(tmp_path)
    before = snapshot(database)
    has_valid_occupancy = stop_at == "before-context-commit"
    assert bool(before[2]) == has_valid_occupancy
    assert len(before[0]) == int(has_valid_occupancy)
    if has_valid_occupancy:
        assert before[0][0].volunteer_name == "Afgeschermd"
    with database.unit_of_work() as uow:
        sessions = PlanningSessionApplicationService(uow, IDENTITY)
        current = sessions.current()
        assert current.initial_load_pending
        assert sessions.candidate_sources(current.session_id) is None

    app.button(key="nav-planning").click().run()
    app.button(key="resume-planning").click().run()
    assert not app.exception and not calls
    assert any("niet volledig afgerond" in item.value and "Databronnen" in item.value for item in app.warning)
    assert any("Wedstrijdcontext onbekend" in item.value for item in app.info)
    status = statuses(app).loc["Sportlink Vrijwilligers", "Status"]
    assert status == ("Technisch geslaagd" if has_valid_occupancy else "Niet opgehaald")
    assert snapshot(database) == before


def test_start_refuses_existing_work_before_reading_sources(sources, tmp_path):
    _, calls = sources
    catalog = load_shift_catalog()
    database = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    progress = []
    service = NewPlanningApplicationService(database, IDENTITY)
    args = dict(period=PERIOD, catalog=catalog, source_period="2026-2027",
                client_id="synthetic", progress=progress.append)
    session = service.start(**args)
    assert [line.split()[0] for line in progress] == ["Lokale", "Wedstrijdprogramma", "Feitelijke"]
    seed_work(database, catalog.bindings(PERIOD)[0].service)
    before = snapshot(database)
    before_calls = list(calls)
    with pytest.raises(ValueError, match="Bevestig"):
        service.start(**args)
    assert calls == before_calls and snapshot(database) == before
    with database.unit_of_work() as uow:
        sessions = PlanningSessionApplicationService(uow, IDENTITY)
        assert sessions.current().session_id == session.session_id
        assert sessions.candidate_sources(session.session_id).context is not None
        sessions.close(confirmed=True, expected_session_id=session.session_id)
    with database.unit_of_work() as uow:
        assert PlanningSessionApplicationService(uow, IDENTITY).candidate_sources(session.session_id) is None
