"""BL-16 replaces PR #35's process-start deletion rule. Synthetic SQLite only."""
from ui_table_events import table as ui_table
from datetime import date
from pathlib import Path
import json
import sqlite3
import subprocess
import sys

import pytest
from streamlit.testing.v1 import AppTest

from dvk.persistence import SQLiteDatabase
from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository
from dvk.planning import PlanningPeriod
from dvk.planning_runtime import prepare_planning, choose_period
from dvk.planning_session import PlanningSessionApplicationService
from test_planning_workqueue_v05 import approve, OTHER
from test_no_show_sportlink_v05 import SOURCE, event
from sportlink_fixtures import seed_bookings, source_revision
from dvk.application_services import NoShowApplicationService
from dvk.security import Identity, Permission

P1 = PlanningPeriod(date(2026, 9, 14), date(2026, 9, 20))
P2 = PlanningPeriod(date(2026, 9, 21), date(2026, 9, 27))
ROOT = Path(__file__).parents[1]
IDENTITY = Identity('planner', 'Planner', frozenset(Permission))


def seed_work(db):
    approve(db)
    approve(db, case=OTHER, pid='P2', aid='LOCAL2')


def work(db):
    with db.unit_of_work() as uow:
        return uow.temporary_planning.all()


def rows(db):
    with sqlite3.connect(db.path) as connection:
        names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        return {name: connection.execute(f'SELECT * FROM "{name}" ORDER BY rowid').fetchall() for name in names}


def current(db):
    with db.unit_of_work() as uow:
        return PlanningSessionApplicationService(uow, IDENTITY).current()


def test_empty_start_and_every_connection_is_readonly(tmp_path):
    db = SQLiteDatabase(tmp_path / 'session.sqlite'); db.initialize()
    before = rows(db)
    assert prepare_planning(db) is None
    assert rows(db) == before
    assert choose_period(db, P1)
    seed_work(db)
    before = rows(db)
    for _ in range(3):
        assert prepare_planning(SQLiteDatabase(db.path)) == P1
        assert rows(db) == before


@pytest.mark.parametrize('with_work', [False, True])
def test_period_change_always_requires_confirmation_and_cancel_retains_all(tmp_path, with_work):
    db = SQLiteDatabase(tmp_path / 'period.sqlite')
    assert choose_period(db, P1)
    if with_work: seed_work(db)
    before = rows(db)
    assert not choose_period(db, P2)
    assert rows(db) == before and prepare_planning(db) == P1
    assert choose_period(db, P1)
    assert rows(db) == before
    assert choose_period(db, P2, discard=True)
    assert prepare_planning(db) == P2 and not work(db)


def test_failed_close_rolls_back_and_retry_keeps_period_until_commit(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / 'failure.sqlite'); choose_period(db, P1); seed_work(db)
    before = rows(db)
    original = SQLiteTemporaryPlanningRepository.remove
    calls = []
    def fail_second(self, identifier):
        calls.append(identifier)
        if len(calls) == 2: raise sqlite3.OperationalError('synthetic delete failure')
        return original(self, identifier)
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail_second)
        with pytest.raises(sqlite3.OperationalError): choose_period(db, P2, discard=True)
    assert rows(db) == before
    assert choose_period(db, P2, discard=True)
    assert prepare_planning(db) == P2 and not work(db)


def test_real_process_restart_restores_entire_session_work_source_and_history(tmp_path):
    db = SQLiteDatabase(tmp_path / 'restart.sqlite')
    with db.unit_of_work() as uow:
        seed_bookings(uow, [SOURCE])
        app = NoShowApplicationService(uow, IDENTITY)
        app.register(event(), source_revision=source_revision(uow))
        app.revoke('N1', reason='Synthetic historical reason', revoked_at=SOURCE.ends_at)
    seed_work(db)
    before = rows(db)
    script = '''
import json, sys
from dvk.persistence import SQLiteDatabase
from dvk.planning_runtime import prepare_planning
db = SQLiteDatabase(sys.argv[1]); period = prepare_planning(db)
with db.unit_of_work() as uow:
    print(json.dumps([period.start.isoformat(), len(uow.temporary_planning.all()),
        len(uow.sportlink_bookings.all()), uow.no_shows.get('N1').booking.person_name,
        uow.no_show_revocations.for_no_show('N1').reason]))
'''
    for _ in range(2):
        result = subprocess.run([sys.executable, '-c', script, str(db.path)], cwd=ROOT,
                                capture_output=True, text=True, check=True, timeout=30)
        assert json.loads(result.stdout) == [SOURCE.starts_at.date().isoformat(), 2, 1, SOURCE.person_name, 'Synthetic historical reason']
        assert rows(db) == before


def ui(tmp_path):
    path = tmp_path / 'streamlit_app.py'
    path.write_text((ROOT / 'streamlit_app.py').read_text().replace('value=date.today()', 'value=date(2026, 9, 14)'))
    app = AppTest.from_file(str(path), default_timeout=20).run()
    app.button(key='nav-planning').click().run()
    assert prepare_planning(SQLiteDatabase(tmp_path / 'dvk_v05.sqlite')) is None
    app.button(key='activate-planning').click().run()
    app.radio(key='planning-source-mode').set_value('Demonstratie').run()
    assert not app.exception
    return app, SQLiteDatabase(tmp_path / 'dvk_v05.sqlite'), path


def seed_ui(db):
    from dvk.demo_data_v05 import demo_planning_data
    services, needs, _, _ = demo_planning_data(P1.start)
    approve(db, service=services[0], need=needs[0])


def test_reruns_navigation_refresh_and_new_browser_resume_preserve_entire_work(tmp_path):
    app, db, path = ui(tmp_path); seed_ui(db)
    before = rows(db)
    app.run()
    for nav in ('nav-home', 'nav-control', 'nav-planning'):
        app.button(key=nav).click().run()
        assert not app.exception and rows(db) == before
    assert not any(b.key == 'resume-planning' for b in app.button)
    for _ in range(2):  # A fresh websocket/browser session, including browser-refresh.
        fresh = AppTest.from_file(str(path), default_timeout=20).run()
        fresh.button(key='nav-planning').click().run()
        assert not fresh.exception and not fresh.metric
        assert rows(db) == before
        fresh.button(key='resume-planning').click().run()
        assert not fresh.exception and fresh.metric
        assert rows(db) == before


def test_ui_new_planning_cancel_and_confirm(tmp_path):
    app, db, _ = ui(tmp_path); seed_ui(db)
    before = rows(db)
    app.button(key='start-new-planning').click().run()
    assert 'niet langer nodig' in app.warning[0].value
    assert 'Sportlink' in app.warning[0].value
    app.button(key='cancel-close-planning').click().run()
    assert rows(db) == before
    app.button(key='start-new-planning').click().run()
    app.button(key='confirm-close-planning').click().run()
    assert not app.exception and current(db) is None and not work(db)
    assert app.button(key='activate-planning')


def test_ui_period_cancel_confirm_and_no_work_confirmation(tmp_path):
    app, db, _ = ui(tmp_path)
    before = rows(db)
    app.date_input(key='planning-from').set_value(P2.start).run()
    assert app.warning and prepare_planning(db) == P1
    app.button(key='cancel-period-change').click().run()
    assert not app.exception and rows(db) == before
    seed_ui(db)
    before = rows(db)
    app.date_input(key='planning-from').set_value(P2.start).run()
    assert rows(db) == before
    app.button(key='confirm-period-change').click().run()
    assert not app.exception and prepare_planning(db) == P2 and not work(db)
    assert set(ui_table(app, "services_editor-").value['Sportlink']) == {'Onbekend'}


def test_stale_close_confirmation_cannot_close_another_session(tmp_path):
    db = SQLiteDatabase(tmp_path / 'stale.sqlite'); choose_period(db, P1)
    old = current(db)
    choose_period(db, P2, discard=True)
    before = rows(db)
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError):
            PlanningSessionApplicationService(uow, IDENTITY).close(confirmed=True, expected_session_id=old.session_id)
    assert rows(db) == before


def test_new_browser_can_cancel_new_planning_and_still_resume(tmp_path):
    _, db, path = ui(tmp_path); seed_ui(db)
    before = rows(db)
    fresh = AppTest.from_file(str(path), default_timeout=20).run()
    fresh.button(key='nav-planning').click().run()
    fresh.button(key='start-new-planning').click().run()
    assert rows(db) == before
    fresh.button(key='cancel-close-planning').click().run()
    assert rows(db) == before
    fresh.button(key='resume-planning').click().run()
    assert not fresh.exception and rows(db) == before


def test_failed_ui_period_delete_retains_old_session_and_navigation(tmp_path, monkeypatch):
    app, db, _ = ui(tmp_path); seed_ui(db)
    before = rows(db)
    app.date_input(key='planning-from').set_value(P2.start).run()
    def fail(*a): raise sqlite3.OperationalError('no such table: synthetic_delete_failure')
    with monkeypatch.context() as patch:
        patch.setattr(SQLiteTemporaryPlanningRepository, 'remove', fail)
        app.button(key='confirm-period-change').click().run()
    assert not app.exception and app.error
    assert rows(db) == before
    app.button(key='nav-control').click().run()
    assert not app.exception and not app.get('file_uploader')
    assert app.button(key='refresh-duty-sources')


# Preserve historical BL-11 dates with an explicit test clock.
pytestmark = pytest.mark.usefixtures("historical_registration_context")
