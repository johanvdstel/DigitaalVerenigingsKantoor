"""Synthetic development regressions for population selection and bounded views."""
import ast
import csv
from datetime import date
from io import BytesIO, StringIO
from pathlib import Path
import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from dvk.duty_control_presenter import EXPORTS, load_duty_dashboard, suggested_season, validate_season
from dvk.persistence import SQLiteDatabase
from dvk.real_data_import import SportlinkRealDataAdapter
from test_duty_control_dashboard_v05 import uploads
from test_hours_control_v05 import TODAY


def member(pid='M1', status='Definitief', end='', **kwargs):
    return {'Rel. code': pid, 'Naam': 'Synthetisch lid', 'Geb.dat.': '01-01-1990',
            'Lidstatus': status, 'Lidsoort': 'Bondslid', 'Status lidmaatschap': '',
            'Afmelddatum': end, **kwargs}


def exports(tmp_path, members):
    files = uploads(tmp_path)
    stream = StringIO()
    writer = csv.DictWriter(stream, fieldnames=list(member()), delimiter=';')
    writer.writeheader()
    writer.writerows(members)
    files['leden'] = stream.getvalue().encode()
    return files


def view(tmp_path, members, as_of=TODAY):
    return load_duty_dashboard(exports(tmp_path, members), as_of=as_of, source_period='2026-2027')


@pytest.mark.parametrize('status,end,outcome', [
    ('Definitief', '', 'Meegenomen'),
    ('Definitief', '01-10-2026', 'Uitgesloten'),
    ('Afmelding in de toekomst', '01-11-2026', 'Meegenomen'),
    ('Afmelding in de toekomst', '', 'Selectieprobleem'),
    ('Oud lid', '01-10-2026', 'Uitgesloten'),
    ('Oud lid', '01-11-2026', 'Meegenomen'),
    ('Oud lid', '', 'Selectieprobleem'),
    ('Afgemeld', '01-11-2026', 'Meegenomen'),
    ('Afgemeld', '', 'Selectieprobleem'),
    ('In behandeling', '', 'Uitgesloten'),
    ('Afgewezen', '', 'Uitgesloten'),
    ('Aspirant lid', '', 'Uitgesloten'),
    ('Onbekend', '', 'Selectieprobleem'),
    ('Onbekend', '01-11-2026', 'Selectieprobleem'),
    ('Definitief', 'geen datum', 'Selectieprobleem'),
])
def test_known_statuses_and_missing_invalid_dates(tmp_path, status, end, outcome):
    dashboard = view(tmp_path, [member(status=status, end=end)])
    assert dashboard.selection[0].outcome == outcome
    assert len(dashboard.rows) == (outcome == 'Meegenomen')
    assert dashboard.selection_counts['Ingelezen unieke leden'] == 1
    assert sum(list(dashboard.selection_counts.values())[1:]) == 1


@pytest.mark.parametrize('as_of,included', [(date(2026, 9, 1), True),
                                          (date(2026, 10, 1), False),
                                          (date(2026, 10, 2), False)])
def test_historical_old_member_and_first_nonmember_day(tmp_path, as_of, included):
    dashboard = view(tmp_path, [member(status='Oud lid', end='01-10-2026')], as_of)
    assert bool(dashboard.rows) is included
    # Selected duty result is exactly the existing public comparison result.
    if included:
        assert dashboard.rows[0].expected == str(dashboard.source.compare_required_hours(as_of)[0].expected_required_hours)


@pytest.mark.parametrize('other,code', [
    (member(**{'Naam': 'Andere synthetische naam'}), 'CONFLICTING_DUPLICATE_IDENTITY'),
    (member(end='01-11-2026'), 'CONFLICTING_DUPLICATE_MEMBERSHIP')])
def test_conflicting_duplicate_is_one_selection_problem(tmp_path, other, code):
    dashboard = view(tmp_path, [member(), other])
    assert dashboard.selection_counts == {'Ingelezen unieke leden': 1, 'Meegenomen': 0,
                                         'Uitgesloten': 0, 'Selectieproblemen': 1}
    assert any(s.code == code for s in dashboard.source.signals)
    assert not dashboard.rows


def test_counts_identical_duplicates_and_preserved_diagnosis(tmp_path):
    members = [member(), member(), member('M2', 'Oud lid', '01-10-2026'),
               member('M3', 'Onbekend'), member('M4', 'Definitief', 'fout'), member('')]
    files = exports(tmp_path, members)
    dashboard = load_duty_dashboard(files, as_of=TODAY, source_period='2026-2027')
    source = SportlinkRealDataAdapter().load_exports(
        **{argument: StringIO(files[key].decode()) for key, (_, argument) in
           EXPORTS.items()},
        as_of=TODAY, source_period='2026-2027')
    assert dashboard.source.signals == source.signals
    assert dashboard.selection_counts == {'Ingelezen unieke leden': 4, 'Meegenomen': 1,
                                         'Uitgesloten': 1, 'Selectieproblemen': 2}
    assert len(dashboard.rows) == 1
    assert any(s.code == 'MISSING_PERSON_ID' for s in source.signals)


@pytest.mark.parametrize('day,season', [(date(2026, 6, 30), '2025-2026'),
                                      (date(2026, 7, 1), '2026-2027')])
def test_suggestion_uses_existing_season_boundary(day, season):
    assert suggested_season(day) == season
    assert validate_season(' ' + season + ' ') == season


@pytest.mark.parametrize('value', ['', '2026', '2026/2027', '26-27', '2026-2028', '0000-0001'])
def test_invalid_season_is_explained(value):
    with pytest.raises(ValueError, match='2026-2027'):
        validate_season(value)


def test_all_table_views_have_bounded_height():
    tree = ast.parse((Path(__file__).parents[1] / 'streamlit_app.py').read_text())
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr in {'dataframe', 'data_editor'}]
    assert len(calls) == 7
    for call in calls:
        height = next(keyword.value for keyword in call.keywords if keyword.arg == 'height')
        assert isinstance(height, ast.Constant) and 0 < height.value <= 360


def test_scroll_views_keep_all_records_and_editable_season(tmp_path, monkeypatch):
    import streamlit as st
    files = exports(tmp_path, [member(f'M{i}') for i in range(100)] +
                    [member('X', 'Afgewezen'), member('U', 'Onbekend')])
    path = tmp_path / 'streamlit_app.py'
    path.write_text((Path(__file__).parents[1] / 'streamlit_app.py').read_text())
    def unavailable(self):
        raise sqlite3.OperationalError('no such table: sportlink_bookings')
    monkeypatch.setattr(SQLiteDatabase, 'initialize', unavailable)
    monkeypatch.setattr(st, 'file_uploader', lambda label, **kwargs:
                        BytesIO(files[kwargs['key'].removeprefix('duty-control-')]))
    heights = []
    original_dataframe = st.dataframe
    def bounded_dataframe(data, **kwargs):
        heights.append(kwargs.get('height'))
        return original_dataframe(data, **kwargs)
    monkeypatch.setattr(st, 'dataframe', bounded_dataframe)
    app = AppTest.from_file(str(path))
    app.session_state['duty-control-date'] = TODAY
    app.run(timeout=20)
    assert not app.exception
    assert app.text_input(key='duty-control-period').value == '2026-2027'
    table = next(item for item in app.dataframe if 'Controlestatus' in item.value.columns)
    assert len(table.value) == 100
    assert heights == [360, 360, 360]
    selection = next(item for item in app.dataframe if 'Selectie' in item.value.columns)
    assert len(selection.value) == 2
    assert any('Onbekende Lidstatus' in str(item.value) for item in app.dataframe)
    app.radio(key='duty-control-filter').set_value('Alleen niet betrouwbaar beoordeelbaar').run()
    assert len(next(item.value for item in app.dataframe if 'Controlestatus' in item.value.columns)) == 99
    app.text_input(key='duty-control-period').set_value('2025-2026').run()
    assert app.text_input(key='duty-control-period').value == '2025-2026'
    app.date_input(key='duty-control-date').set_value(date(2026, 6, 30)).run()
    assert app.text_input(key='duty-control-period').value == '2025-2026'
    app.text_input(key='duty-control-period').set_value('verkeerd').run()
    assert any('JJJJ-JJJJ' in item.value for item in app.error)
    assert not app.dataframe


def test_season_field_validates_before_uploads_and_rejects_empty(tmp_path):
    path = tmp_path / 'streamlit_app.py'
    path.write_text((Path(__file__).parents[1] / 'streamlit_app.py').read_text())
    app = AppTest.from_file(str(path)).run(timeout=20)
    app.text_input(key='duty-control-period').set_value('').run()
    assert not app.exception
    assert any('JJJJ-JJJJ' in item.value for item in app.error)
