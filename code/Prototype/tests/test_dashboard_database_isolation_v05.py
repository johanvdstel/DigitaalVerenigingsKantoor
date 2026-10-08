"""Synthetic development tests for the planning/dashboard failure boundary."""
from io import BytesIO
from pathlib import Path
import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import PlanningApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.persistence import migrations
from test_duty_control_dashboard_v05 import uploads
from test_hours_control_v05 import TODAY


APP = Path(__file__).parents[1] / 'streamlit_app.py'


def local_app(tmp_path):
    path = tmp_path / 'streamlit_app.py'
    path.write_text(APP.read_text())
    return path


def control_visible(app):
    assert not app.exception
    assert any('Taakplichtcontrole — read-only' in item.value for item in app.markdown)
    assert app.radio(key='duty-control-filter').options == [
        'Alle', 'Alleen afwijkingen', 'Alleen niet betrouwbaar beoordeelbaar']
    assert len([item for item in app.get('file_uploader')
                if item.key and item.key.startswith('duty-control-')]) == 5


@pytest.mark.parametrize('schema', ['missing_table', 'earlier_version_12'])
def test_version_12_inconsistency_does_not_block_or_repair(tmp_path, monkeypatch, schema):
    path = local_app(tmp_path)
    db_path = tmp_path / 'dvk_v05.sqlite'
    if schema == 'missing_table':
        SQLiteDatabase(db_path).initialize()
        with sqlite3.connect(db_path) as connection:
            connection.execute('DROP TABLE sportlink_bookings')
    else:
        # Reproduce the older version-number contract with synthetic data only.
        with monkeypatch.context() as patch:
            patch.setattr(migrations, 'MIGRATIONS', migrations.MIGRATIONS[:11])
            SQLiteDatabase(db_path).initialize()
        with sqlite3.connect(db_path) as connection:
            connection.execute('CREATE TABLE planning_state (singleton INTEGER PRIMARY KEY)')
            connection.execute('INSERT INTO schema_version VALUES (12)')
    before = db_path.read_bytes()
    app = AppTest.from_file(str(path)).run(timeout=20)
    control_visible(app)
    assert len(app.error) == 1
    assert 'databaseprobleem' in app.error[0].value
    assert 'sportlink_bookings' not in app.error[0].value
    assert db_path.read_bytes() == before
    with sqlite3.connect(db_path) as connection:
        assert connection.execute('SELECT MAX(version) FROM schema_version').fetchone() == (12,)
        assert not connection.execute("SELECT 1 FROM sqlite_master WHERE name='sportlink_bookings'").fetchone()


def test_valid_database_preserves_planning_and_no_show_screen(tmp_path):
    path = local_app(tmp_path)
    db_path = tmp_path / 'dvk_v05.sqlite'
    assert SQLiteDatabase(db_path).initialize() == 12
    before = db_path.read_bytes()
    app = AppTest.from_file(str(path)).run(timeout=20)
    control_visible(app)
    assert not app.error
    assert any(item.label == 'Diensten' for item in app.metric)
    assert any(item.value == '### No-shows' for item in app.markdown)
    assert db_path.read_bytes() == before


def test_five_uploads_render_without_sqlite_or_sportlink_access(tmp_path, monkeypatch):
    import streamlit as st
    from dvk.vrijwilligers_client import SportlinkVrijwilligersClient

    files = uploads(tmp_path)
    path = local_app(tmp_path)

    def unavailable(self):
        raise sqlite3.OperationalError('no such table: sportlink_bookings')

    def forbidden(*args, **kwargs):
        pytest.fail('Task control must not access SQLite or Sportlink')

    monkeypatch.setattr(SQLiteDatabase, 'initialize', unavailable)
    monkeypatch.setattr(sqlite3, 'connect', forbidden)
    monkeypatch.setattr(SportlinkVrijwilligersClient, 'fetch_rows', forbidden)
    monkeypatch.setattr(st, 'file_uploader', lambda label, **kwargs:
                        BytesIO(files[kwargs['key'].removeprefix('duty-control-')]))
    app = AppTest.from_file(str(path))
    app.session_state['duty-control-period'] = 'Synthetisch seizoen'
    app.session_state['duty-control-date'] = TODAY
    app.run(timeout=20)
    assert not app.exception
    assert len(app.error) == 1
    assert any(item.label == 'Totaal' and item.value == '1' for item in app.metric)
    assert app.dataframe[0].value.iloc[0]['Lid'] == 'Synthetisch lid'
    assert not (tmp_path / 'dvk_v05.sqlite').exists()


@pytest.mark.parametrize('failure', [RuntimeError('synthetic programming error'),
                                     sqlite3.OperationalError('near SELECT: syntax error')])
def test_programming_errors_are_not_hidden(tmp_path, monkeypatch, failure):
    def broken(*args, **kwargs):
        raise failure
    monkeypatch.setattr(PlanningApplicationService, 'build_overview', broken)
    app = AppTest.from_file(str(local_app(tmp_path))).run(timeout=20)
    assert len(app.exception) == 1
    assert str(failure) in app.exception[0].message
    assert not app.error


def test_later_no_show_database_failure_does_not_block_dashboard(tmp_path, monkeypatch):
    from dvk.application_services import NoShowApplicationService

    def unavailable(*args, **kwargs):
        raise sqlite3.OperationalError('no such table: sportlink_no_show_revocations')

    monkeypatch.setattr(NoShowApplicationService, 'revocable_no_shows', unavailable)
    app = AppTest.from_file(str(local_app(tmp_path))).run(timeout=20)
    control_visible(app)
    assert len(app.error) == 1
    assert any(item.value == '### No-shows' for item in app.markdown)


def test_database_open_failure_does_not_block_dashboard(tmp_path, monkeypatch):
    def unavailable(self):
        failure = sqlite3.OperationalError('unable to open database file')
        failure.sqlite_errorcode = sqlite3.SQLITE_CANTOPEN
        raise failure

    monkeypatch.setattr(SQLiteDatabase, 'initialize', unavailable)
    app = AppTest.from_file(str(local_app(tmp_path))).run(timeout=20)
    control_visible(app)
    assert len(app.error) == 1
