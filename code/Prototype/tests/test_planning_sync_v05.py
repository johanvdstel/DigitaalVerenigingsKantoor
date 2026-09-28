"""FR-06–08: only a fresh API fetch plus explicitly offered CSV closes planning."""
from dataclasses import asdict, replace
import json
from datetime import date, datetime
from unittest.mock import Mock

import pytest

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.import_management import ImportBatch, ImportStatus, SnapshotRecord
from dvk.import_workflow import confirm_import
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod
from dvk.planning_sync import PlanningSyncApplicationService
from dvk.security import Identity, Permission
from dvk.vrijwilligers_adapter import ServiceBinding, TZ
from dvk.vrijwilligers_client import VrijwilligersFetchResult
from test_planning_workqueue_v05 import A, SOURCE, JAN, OTHER, proposal

IDENTITY = Identity("planner", "Planner", frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL, Permission.CONFIRM_IMPORT}))
PERIOD = PlanningPeriod(date(2026, 9, 14), date(2026, 9, 20))
CSV = ("Relatiecode;Verplichte punten;Gecorrigeerde punten;Voldaan;Nog ingedeeld;Niet ingedeeld\n"
       f"{JAN.person.person_id};10;0;2;4;4\n{OTHER.person.person_id};10;0;1;2;7\n").encode()


@pytest.fixture
def db(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    with db.unit_of_work() as uow:
        PlanningSyncApplicationService(uow, IDENTITY).select_period(PERIOD)
    for i, case in enumerate((JAN, OTHER)):
        p = proposal(db, case=case, pid=f"P{i}")
        with db.unit_of_work() as uow:
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(p, A, case, assignment_id=f"A{i}", staffing_need=SOURCE)
    return db


def arguments(name="Afgeschermd"):
    client = Mock()
    client.fetch_rows.return_value = VrijwilligersFetchResult("741", ({
        "naam": name, "datumvanaf": "2026-09-19", "datumtot": "2026-09-19",
        "tijdvanaf": "09:00", "tijdtot": "13:00", "lokatie": "Clubhuis",
    },))
    return dict(csv_content=CSV, current_export_confirmed=True, client=client, client_id="runtime-only",
                bindings=(ServiceBinding("741", replace(A, starts_at=A.starts_at.replace(tzinfo=TZ), ends_at=A.ends_at.replace(tzinfo=TZ))),),
                persons=(JAN.person, OTHER.person))


def state(db):
    with db.unit_of_work() as uow:
        return uow.planning_state.get(), uow.temporary_planning.all()


@pytest.mark.parametrize("dataset", ["vrijwilligers_rooster", "vrijwilligers_periode"])
def test_individual_source_confirmation_never_clears(db, dataset):
    before = state(db)
    with db.unit_of_work() as uow:
        now = datetime.now(TZ)
        batch = ImportBatch("separate", "Sportlink", dataset, None, now, "planner", ImportStatus.AWAITING_CONFIRMATION)
        records = ()
        if dataset == "vrijwilligers_periode":
            from dvk.real_data_import import SportlinkRealDataAdapter
            adapter = SportlinkRealDataAdapter()
            rows = adapter.parse_csv(CSV.decode(), dataset)
            duties, provenance, signals = adapter.import_duty_rows(
                rows, person_ids={JAN.person.person_id, OTHER.person.person_id}, imported_at=now)
            assert not signals
            records = tuple(SnapshotRecord("", duty.registration.person_id, json.dumps(row),
                json.dumps(asdict(duty.registration)), json.dumps(asdict(prov), default=str))
                for row, duty, prov in zip(rows, duties, provenance))
        uow.import_batches.add(batch)
        confirm_import(uow, batch, records, snapshot_id="separate", confirmed_at=now, confirmed_by="planner")
    assert state(db) == before


def test_double_sync_clears_every_person_without_reconciliation_and_counts_privacy(db):
    with db.unit_of_work() as uow:
        app = PlanningSyncApplicationService(uow, IDENTITY)
        completed = app.synchronize(**arguments())
        assert completed.sync_id is not None
        assert uow.temporary_planning.all() == ()
        assert app.bookings()[0].volunteer_name == "Afgeschermd"
        roster = uow.snapshots.get(completed.roster_snapshot_id)
        duty = uow.snapshots.get(completed.duty_snapshot_id)
        assert roster.source_period == "2026-09-14/2026-09-20"
        assert duty.source_period is None
        assert roster.import_batch_id != duty.import_batch_id
        assert uow.snapshots.records(duty.snapshot_id)[0].provenance_payload
        planning = PlanningApplicationService(IDENTITY, uow=uow)
        need = planning.staffing_needs(services=(A,), source_needs=(SOURCE,))[0]
        assert (need.confirmed_occupancy, need.temporary_occupancy, need.open_need) == (1, 0, 1)
        cases = planning.current_cases((JAN, OTHER))
        assert cases[0].sportlink_duty.scheduled_hours == 4
        assert planning.assess_candidates(cases=cases, service=A, team_memberships=(), matches=(), today=date(2026, 9, 19))[0].eligible
    assert state(db)[0] == completed


@pytest.mark.parametrize("failure", ["api", "roster_validation", "csv_columns", "csv_value", "missing_member", "no_confirmation"])
def test_failures_preserve_entire_queue(db, failure):
    before = state(db)
    args = arguments()
    if failure == "api": args["client"].fetch_rows.side_effect = RuntimeError("unavailable")
    elif failure == "roster_validation": args["client"].fetch_rows.return_value = VrijwilligersFetchResult("741", ({"naam": "Afgeschermd"},))
    elif failure == "csv_columns": args["csv_content"] = b"wrong;columns\n"
    elif failure == "csv_value": args["csv_content"] = CSV.replace(b";10;", b";invalid;")
    elif failure == "missing_member": args["csv_content"] = CSV.splitlines(keepends=True)[0] + CSV.splitlines(keepends=True)[1]
    elif failure == "no_confirmation": args["current_export_confirmed"] = False
    with db.unit_of_work() as uow:
        with pytest.raises((ValueError, RuntimeError)):
            PlanningSyncApplicationService(uow, IDENTITY).synchronize(**args)
        uow.commit()
        if failure.startswith("csv_") or failure == "missing_member":
            assert uow.snapshots.latest("Sportlink", "vrijwilligers_rooster", "2026-09-14/2026-09-20") is not None
    assert state(db) == before


def test_final_commit_failure_rolls_back_success_and_clear(db, monkeypatch):
    before = state(db)
    with db.unit_of_work() as uow:
        original = uow.commit
        calls = 0
        def fail_final():
            nonlocal calls
            calls += 1
            if calls == 3: raise RuntimeError("commit failed")
            original()
        monkeypatch.setattr(uow, "commit", fail_final)
        with pytest.raises(RuntimeError, match="commit failed"):
            PlanningSyncApplicationService(uow, IDENTITY).synchronize(**arguments())
        original()  # caught errors cannot accidentally commit a partial completion
        assert uow.snapshots.latest("Sportlink", "vrijwilligers_periode", None) is not None
    assert state(db) == before


def test_discard_allows_new_period_and_has_no_revocation_history(db):
    with db.unit_of_work() as uow:
        app = PlanningSyncApplicationService(uow, IDENTITY)
        new = PlanningPeriod(date(2026, 10, 5), date(2026, 10, 31))
        with pytest.raises(ValueError, match="periode"):
            app.select_period(new)
        app.discard()
        assert uow.temporary_planning.all() == ()
        assert not uow.no_shows.all()
        assert app.select_period(new).period == new


def test_outside_period_is_refused_by_application(db):
    outside = replace(A, starts_at=datetime(2026, 10, 1, 9), ends_at=datetime(2026, 10, 1, 13))
    p = proposal(db, service=outside, pid="outside")
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="buiten"):
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(p, outside, JAN, assignment_id="outside", staffing_need=SOURCE)


def test_old_confirmed_csv_cannot_close_new_attempt(db):
    with db.unit_of_work() as uow:
        app = PlanningSyncApplicationService(uow, IDENTITY)
        old_state = app.synchronize(**arguments())
        old_roster = uow.snapshots.get(old_state.roster_snapshot_id)
        old_duty = uow.snapshots.get(old_state.duty_snapshot_id)
        with pytest.raises(ValueError, match="verse bronnen"):
            app._complete("different-attempt", old_state, old_roster, old_duty)
        assert app.state() == old_state
        args = arguments()
        args["csv_content"] = b""
        with pytest.raises(ValueError, match="actuele Sportlink CSV"):
            app.synchronize(**args)
        args["client"].fetch_rows.assert_not_called()


def test_concurrent_planning_change_prevents_clear(db):
    before = state(db)
    args = arguments()
    fetched = args["client"].fetch_rows.return_value
    def concurrent(**kwargs):
        with db.unit_of_work() as other:
            ProposalDecisionApplicationService(IDENTITY, uow=other).undo("A0")
        return fetched
    args["client"].fetch_rows.side_effect = concurrent
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="tijdens synchronisatie gewijzigd"):
            PlanningSyncApplicationService(uow, IDENTITY).synchronize(**args)
    after = state(db)
    assert after[0].sync_id == before[0].sync_id
    assert [entry.assignment.assignment_id for entry in after[1]] == ["A1"]


def test_discard_failure_rolls_back_everything(db, monkeypatch):
    before = state(db)
    with db.unit_of_work() as uow:
        def fail(): raise RuntimeError("discard commit failed")
        monkeypatch.setattr(uow, "commit", fail)
        with pytest.raises(RuntimeError):
            PlanningSyncApplicationService(uow, IDENTITY).discard()
    assert state(db) == before


def test_migration_preserves_unscoped_work_and_requires_explicit_period(tmp_path):
    import sqlite3
    from dvk.persistence.migrations import MIGRATIONS
    path = tmp_path / "old.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
        for version, migrate in enumerate(MIGRATIONS[:11], 1):
            migrate(connection)
            connection.execute("INSERT INTO schema_version VALUES (?)", (version,))
    db = SQLiteDatabase(path)
    with db.unit_of_work() as uow:
        assert uow.planning_state.get().period is None
        p = proposal(db, pid="old")
        from dvk.dashboard_actions import approve_from_dashboard
        from dvk.planning_workqueue import TemporaryPlanning
        result = approve_from_dashboard(p, A, JAN, "planner", "old")
        uow.temporary_planning.add(TemporaryPlanning(result.assignment, A))
        uow.planning_state.discard()  # emulate pre-period workqueue
        uow.commit()
    with db.unit_of_work() as uow:
        app = PlanningSyncApplicationService(uow, IDENTITY)
        assert len(uow.temporary_planning.all()) == 1
        with pytest.raises(ValueError, match="volledige bestaande"):
            app.select_period(PlanningPeriod(date(2026, 10, 5), date(2026, 10, 31)))
        app.select_period(PERIOD)
        assert len(uow.temporary_planning.all()) == 1


def test_visible_source_booking_controls_availability_and_hours(db):
    with db.unit_of_work() as uow:
        PlanningSyncApplicationService(uow, IDENTITY).synchronize(**arguments(name=JAN.person.name))
        planning = PlanningApplicationService(IDENTITY, uow=uow)
        assessment = planning.assess_candidates(cases=(JAN, OTHER), service=A,
            team_memberships=(), matches=(), today=date(2026, 9, 19))[0]
        assert not assessment.eligible
        assert "Sportlink" in assessment.exclusion_reason
        assert planning.current_cases((JAN,))[0].sportlink_duty.completed_hours == 2


def test_explicit_new_identical_export_is_allowed_but_api_is_always_fetched(db):
    args = arguments()
    with db.unit_of_work() as uow:
        app = PlanningSyncApplicationService(uow, IDENTITY)
        first = app.synchronize(**args)
        second = app.synchronize(**args)
        assert first.sync_id != second.sync_id
        assert first.duty_snapshot_id != second.duty_snapshot_id
        assert args["client"].fetch_rows.call_count == 2


@pytest.mark.parametrize("offset,days,start,end", [
    (-1, 7, date(2026, 9, 21), date(2026, 9, 27)),
    (0, 7, date(2026, 9, 28), date(2026, 10, 4)),
    (0, 1, date(2026, 9, 28), date(2026, 9, 28)),
    (0, 10, date(2026, 9, 28), date(2026, 10, 7)),
])
def test_ckc_verified_sunday_calendar_semantics(offset, days, start, end):
    from dvk.planning_sync import sportlink_period, sportlink_parameters
    today = date(2026, 9, 27)
    period = sportlink_period(today=today, weekoffset=offset, days=days)
    assert period == PlanningPeriod(start, end)
    assert sportlink_parameters(period, today=today) == {"weekoffset": offset, "days": days}


def test_stored_period_remains_identical_across_week_rollover():
    from dvk.planning_sync import sportlink_period, sportlink_parameters
    period = PlanningPeriod(date(2026, 9, 28), date(2026, 10, 4))
    for today, expected in ((date(2026, 9, 27), 0), (date(2026, 9, 28), -1)):
        params = sportlink_parameters(period, today=today)
        assert params["weekoffset"] == expected
        assert sportlink_period(today=today, **params) == period


def test_non_monday_period_cannot_be_selected(db):
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="maandag"):
            PlanningSyncApplicationService(uow, IDENTITY).select_period(
                PlanningPeriod(date(2026, 9, 29), date(2026, 10, 4)))


def test_exact_active_period_is_sent_to_real_client_url(db):
    import json
    from urllib.parse import parse_qs, urlparse
    from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
    from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter
    from test_vrijwilligers_client_v04 import Response
    args = arguments()
    seen = []
    rows = args["client"].fetch_rows.return_value.rows
    def opener(request, timeout):
        seen.append(parse_qs(urlparse(request.full_url).query))
        assert request.get_method() == "GET"
        return Response(json.dumps(rows).encode())
    args["client"] = SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter(), opener=opener)
    with db.unit_of_work() as uow:
        PlanningSyncApplicationService(uow, IDENTITY, clock=lambda: datetime(2026, 9, 27, 12, tzinfo=TZ)).synchronize(**args)
    assert seen[0]["weekoffset"] == ["-2"]
    assert seen[0]["aantaldagen"] == ["7"]


def test_week_rollover_during_fetch_keeps_queue(db):
    before = state(db)
    moment = [datetime(2026, 9, 27, 23, 59, tzinfo=TZ)]
    args = arguments()
    fetched = args["client"].fetch_rows.return_value
    def fetch(**kwargs):
        moment[0] = datetime(2026, 9, 28, 0, 0, tzinfo=TZ)
        return fetched
    args["client"].fetch_rows.side_effect = fetch
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="kalenderweek"):
            PlanningSyncApplicationService(uow, IDENTITY, clock=lambda: moment[0]).synchronize(**args)
    assert state(db) == before


def test_stale_proposal_cannot_override_new_sportlink_hours(db):
    stale = proposal(db, service=replace(A, starts_at=datetime(2026, 9, 20, 9), ends_at=datetime(2026, 9, 20, 13)), pid="stale")
    with db.unit_of_work() as uow:
        PlanningSyncApplicationService(uow, IDENTITY).synchronize(**arguments())
        with pytest.raises(ValueError, match="urenpositie is gewijzigd"):
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(
                stale, replace(A, starts_at=datetime(2026, 9, 20, 9), ends_at=datetime(2026, 9, 20, 13)),
                JAN, assignment_id="stale", staffing_need=SOURCE)
        assert uow.temporary_planning.all() == ()


def test_streamlit_csv_action_closes_queue_and_requires_new_offer(tmp_path, monkeypatch):
    from io import BytesIO
    from pathlib import Path
    import streamlit as st
    from streamlit.testing.v1 import AppTest
    from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
    csv = ("Relatiecode;Verplichte punten;Gecorrigeerde punten;Voldaan;Nog ingedeeld;Niet ingedeeld\n"
           "W08P;10;0;0;1;9\nW07P;10;0;0;2;8\nW04P;10;0;0;3;7\n").encode()
    offered = []
    def upload(*args, key, **kwargs):
        if not offered: offered.append(key)
        return BytesIO(csv) if key == offered[0] else None
    monkeypatch.setattr(st, "file_uploader", upload)
    calls = []
    def fetch(self, **kwargs):
        calls.append(kwargs)
        return VrijwilligersFetchResult(kwargs["task_code"], ())
    monkeypatch.setattr(SportlinkVrijwilligersClient, "fetch_rows", fetch)
    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1] / "streamlit_app.py").read_text())
    app = AppTest.from_file(str(script), default_timeout=15).run()
    app.date_input[0].set_value(date(2026, 9, 14))
    app.session_state["selected_service_id"] = "BAR-WO-1"
    app.run()
    next(w for w in app.checkbox if w.key.startswith("pick-")).check().run()
    next(w for w in app.button if w.label == "Selectie bevestigen").click().run()
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    assert len(state(db)[1]) == 1
    for widget in app.text_input:
        if widget.label == "Sportlink client-id": widget.set_value("test-runtime")
        elif widget.label.startswith("Sportlink-taakcode"): widget.set_value("741")
    next(w for w in app.checkbox if w.key.startswith("sync-current-")).check()
    old_attempt = app.session_state["sync-upload-attempt"]
    next(w for w in app.button if w.label.startswith("Sportlink synchroniseren")).click().run()
    assert not app.exception
    assert state(db)[1] == ()
    assert state(db)[0].sync_id is not None
    assert app.session_state["sync-upload-attempt"] != old_attempt
    assert app.dataframe[0].value.iloc[0]["Sportlink"] == 0
    assert app.dataframe[0].value.iloc[0]["Tijdelijk DVK"] == 0
    assert len(calls) == 1
    next(w for w in app.button if w.label.startswith("Sportlink synchroniseren")).click().run()
    assert len(calls) == 1  # No silent reuse of the old offer.
    assert any("actuele Sportlink CSV" in error.value for error in app.error)


def test_streamlit_discard_requires_explicit_confirmation(tmp_path):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1] / "streamlit_app.py").read_text())
    app = AppTest.from_file(str(script), default_timeout=15).run()
    app.date_input[0].set_value(date(2026, 9, 14))
    app.session_state["selected_service_id"] = "BAR-WO-1"
    app.run()
    next(w for w in app.checkbox if w.key.startswith("pick-")).check().run()
    next(w for w in app.button if w.label == "Selectie bevestigen").click().run()
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    next(w for w in app.button if w.label == "Volledige tijdelijke planning weggooien").click().run()
    assert state(db)[1]
    next(w for w in app.button if w.label == "Ja, volledige planning weggooien").click().run()
    assert not app.exception
    assert not state(db)[1]
    assert not app.date_input[0].disabled
