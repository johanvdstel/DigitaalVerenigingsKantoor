"""Synthetic lifecycle regression: process start is not a rerun or connection."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path
import json
import sqlite3
import subprocess
import sys
from threading import Barrier

import pytest
from streamlit.testing.v1 import AppTest

from dvk.persistence import SQLiteDatabase
from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository
from dvk.persistence.sqlite import SQLiteUnitOfWork
from dvk.planning import PlanningPeriod
from dvk.planning_runtime import prepare_planning, choose_period
from test_planning_workqueue_v05 import approve, OTHER
from test_no_show_sportlink_v05 import SOURCE, IDENTITY, event
from sportlink_fixtures import seed_bookings
from dvk.application_services import NoShowApplicationService

P1 = PlanningPeriod(date(2026, 9, 14), date(2026, 9, 20))
P2 = PlanningPeriod(date(2026, 9, 21), date(2026, 9, 27))
ROOT = Path(__file__).parents[1]


def seed_work(db):
    approve(db)
    approve(db, case=OTHER, pid="P2", aid="LOCAL2")


def work(db):
    with db.unit_of_work() as uow:
        return uow.temporary_planning.all()


def durable_rows(db):
    with sqlite3.connect(db.path) as connection:
        names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {name: connection.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall()
                for name in names if name != 'temporary_planning'}


def test_startup_clears_only_work_and_repeated_connections_keep_new_work(tmp_path):
    db = SQLiteDatabase(tmp_path / 'lifecycle.sqlite')
    seed_work(db)
    with db.unit_of_work() as uow:
        seed_bookings(uow, [SOURCE])
        service = NoShowApplicationService(uow, IDENTITY)
        service.register(event())
        service.revoke('N1', reason='Synthetic decision', revoked_at=SOURCE.ends_at)
    before = durable_rows(db)
    assert prepare_planning(db) is None
    assert work(db) == ()
    assert durable_rows(db) == before
    approve(db, pid='NEW', aid='NEW')
    current = work(db)
    for _ in range(3):
        assert prepare_planning(SQLiteDatabase(db.path)) is None
        assert work(db) == current


def test_failed_startup_rolls_back_and_retries(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / 'failure.sqlite')
    seed_work(db)
    before = work(db)
    original = SQLiteTemporaryPlanningRepository.remove
    calls = []
    def fail_second(self, identifier):
        calls.append(identifier)
        if len(calls) == 2:
            raise sqlite3.OperationalError('synthetic delete failure')
        return original(self, identifier)
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail_second)
        with pytest.raises(sqlite3.OperationalError):
            prepare_planning(db)
    assert work(db) == before
    assert prepare_planning(db) is None
    assert work(db) == ()


def test_concurrent_first_access_initializes_exactly_once(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / 'concurrent.sqlite')
    seed_work(db)
    barrier = Barrier(6)
    commits = []
    original = SQLiteUnitOfWork.commit
    def commit(self):
        commits.append(True)
        original(self)
    monkeypatch.setattr(SQLiteUnitOfWork, 'commit', commit)
    def first_access(_):
        barrier.wait(timeout=10)
        return prepare_planning(SQLiteDatabase(db.path))
    with ThreadPoolExecutor(max_workers=6) as pool:
        assert list(pool.map(first_access, range(6))) == [None] * 6
    assert commits == [True]
    assert work(db) == ()


def test_period_change_requires_confirmation_and_commits_atomically(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / 'period.sqlite')
    assert choose_period(db, P1)
    assert choose_period(db, P2)  # No work: no confirmation.
    assert choose_period(db, P1)
    seed_work(db)
    before, durable = work(db), durable_rows(db)
    assert not choose_period(db, P2)
    assert prepare_planning(db) == P1 and work(db) == before
    assert choose_period(db, P1)  # Cancellation keeps the original period.
    original = SQLiteTemporaryPlanningRepository.remove
    calls = []
    def fail_second(self, identifier):
        calls.append(identifier)
        if len(calls) == 2:
            raise sqlite3.OperationalError('synthetic delete failure')
        return original(self, identifier)
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail_second)
        with pytest.raises(sqlite3.OperationalError):
            choose_period(db, P2, discard=True)
    assert prepare_planning(db) == P1 and work(db) == before
    assert durable_rows(db) == durable
    assert choose_period(db, P2, discard=True)
    assert prepare_planning(db) == P2 and work(db) == ()
    assert durable_rows(db) == durable


def test_real_process_restart_clears_work_and_keeps_durable_no_show_context(tmp_path):
    db = SQLiteDatabase(tmp_path / 'restart.sqlite')
    seed_work(db)
    with db.unit_of_work() as uow:
        seed_bookings(uow, [SOURCE])
        app = NoShowApplicationService(uow, IDENTITY)
        app.register(event())
        app.revoke('N1', reason='Synthetic historical reason', revoked_at=SOURCE.ends_at)
    before = durable_rows(db)
    script = '''
import json, sys
from datetime import datetime
from dvk.persistence import SQLiteDatabase
from dvk.planning_runtime import prepare_planning
from dvk.planning_workqueue import TemporaryPlanning
from dvk.workstream_model import DutyAssignment, DutyService

db = SQLiteDatabase(sys.argv[1])
prepare_planning(db)
with db.unit_of_work() as uow:
    count = len(uow.temporary_planning.all())
    service = DutyService('S', 'Synthetic duty', datetime(2026,9,19,9), datetime(2026,9,19,13), 'Synthetic', 1)
    assignment = DutyAssignment('CHILD', 'P', 'S', 'PERSON', 'member', 4, 'planner')
    uow.temporary_planning.add(TemporaryPlanning(assignment, service))
    uow.commit()
prepare_planning(SQLiteDatabase(sys.argv[1]))
with db.unit_of_work() as uow:
    print(json.dumps([count, len(uow.temporary_planning.all()), uow.no_shows.get('N1').booking.person_name,
                      uow.no_show_revocations.for_no_show('N1').reason]))
'''
    for _ in range(2):
        result = subprocess.run([sys.executable, '-c', script, str(db.path)], cwd=ROOT,
                                capture_output=True, text=True, check=True, timeout=60)
        assert json.loads(result.stdout) == [0, 1, SOURCE.person_name, 'Synthetic historical reason']
        assert durable_rows(db) == before


def ui(tmp_path):
    path = tmp_path / 'streamlit_app.py'
    path.write_text((ROOT / 'streamlit_app.py').read_text().replace(
        'value=date.today()', 'value=date(2026, 9, 14)'))
    app = AppTest.from_file(str(path), default_timeout=20).run()
    app.button(key='nav-planning').click().run()
    assert not app.exception
    return app, SQLiteDatabase(tmp_path / 'dvk_v05.sqlite'), path


def seed_ui(db):
    from dvk.demo_data_v05 import demo_planning_data
    services, needs, _, _ = demo_planning_data(P1.start)
    approve(db, service=services[0], need=needs[0])


def test_reruns_navigation_and_new_browser_session_keep_work(tmp_path):
    app, db, path = ui(tmp_path)
    seed_ui(db)
    before = work(db)
    app.run()
    assert work(db) == before
    next(x for x in app.number_input if x.label == 'Aantal dagen voor Sportlink-uitvraag').set_value(7).run()
    app.radio(key='planning-mode').set_value('Aangepast').run()
    assert work(db) == before  # Same actual period, different selector mode.
    for nav in ('nav-home', 'nav-control', 'nav-planning'):
        app.button(key=nav).click().run()
        assert not app.exception and work(db) == before
    # A fresh AppTest models a fresh browser session, not a new process.
    refreshed = AppTest.from_file(str(path), default_timeout=20).run()
    refreshed.button(key='nav-planning').click().run()
    assert not refreshed.exception
    assert work(db) == before and prepare_planning(db) == P1
    assert any(x.label == 'DVK-planningsbezetting' for x in refreshed.metric)


def test_ui_period_cancel_confirm_and_empty_change(tmp_path):
    app, db, _ = ui(tmp_path)
    app.date_input(key='planning-from').set_value(P2.start).run()
    assert not app.warning and prepare_planning(db) == P2
    app.date_input(key='planning-from').set_value(P1.start).run()
    seed_ui(db)
    before = work(db)
    app.date_input(key='planning-from').set_value(P2.start).run()
    assert 'alle tijdelijke indelingen verwijderd' in app.warning[0].value
    assert prepare_planning(db) == P1 and work(db) == before
    app.button(key='cancel-period-change').click().run()
    assert not app.exception and not app.warning
    assert app.date_input(key='planning-from').value == P1.start
    assert work(db) == before
    app.date_input(key='planning-from').set_value(P2.start).run()
    app.button(key='confirm-period-change').click().run()
    assert not app.exception
    assert prepare_planning(db) == P2 and work(db) == ()
    assert any(x.label == 'Diensten' for x in app.metric)


def test_ui_failed_delete_keeps_old_period_and_control_reachable(tmp_path, monkeypatch):
    app, db, _ = ui(tmp_path)
    seed_ui(db)
    before = work(db)
    app.date_input(key='planning-from').set_value(P2.start).run()
    def fail(self, identifier):
        raise sqlite3.OperationalError('no such table: synthetic_delete_failure')
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail)
        app.button(key='confirm-period-change').click().run()
    assert not app.exception and app.error
    assert prepare_planning(db) == P1 and work(db) == before
    app.button(key='nav-control').click().run()
    assert not app.exception and len(app.get('file_uploader')) == 5


def test_failed_first_ui_access_does_not_display_old_work_and_can_retry(tmp_path, monkeypatch):
    path = tmp_path / 'streamlit_app.py'
    path.write_text((ROOT / 'streamlit_app.py').read_text())
    db = SQLiteDatabase(tmp_path / 'dvk_v05.sqlite')
    seed_work(db)
    before = work(db)
    app = AppTest.from_file(str(path), default_timeout=20).run()
    def fail(self, identifier):
        raise sqlite3.OperationalError('no such table: synthetic_delete_failure')
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail)
        app.button(key='nav-planning').click().run()
    assert not app.exception and app.error
    assert not app.metric and not app.selectbox
    assert work(db) == before
    app.button(key='nav-control').click().run()
    assert not app.exception and len(app.get('file_uploader')) == 5
    app.button(key='nav-planning').click().run()
    assert not app.exception and work(db) == ()
