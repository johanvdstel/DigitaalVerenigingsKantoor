"""Synthetic regressions: explain existing grounds without changing decisions."""
from dataclasses import replace
from datetime import date
from io import BytesIO
from pathlib import Path
import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from dvk.duty_control_presenter import present_controls, load_duty_dashboard
from dvk.model import RoleAssignment
from dvk.persistence import SQLiteDatabase
from test_member_duty_v05 import person, source, TODAY
from test_duty_population_dashboard_v05 import exports, member


def younger(**kwargs):
    return person('Y', date(2012, 1, 1), **kwargs)


def older(**kwargs):
    return person('O', date(2010, 1, 1), **kwargs)


def diagnosed(data):
    before = data.compare_required_hours(TODAY)
    dashboard = present_controls(data, before)
    assert data.compare_required_hours(TODAY) == before
    assert tuple((r.person_id, r.status, r.expected) for r in dashboard.rows) == tuple(
        (c.person_id, c.status, '—' if c.expected_required_hours is None else str(c.expected_required_hours)) for c in before)
    assert dashboard.source.signals == data.signals
    return next(r for r in dashboard.rows if r.person_id == 'Y')


@pytest.mark.parametrize('field,label', [('postal_code', 'Postcode'), ('house_number', 'Huisnummer')])
def test_missing_address_field_is_specific(field, label):
    p = replace(younger(), **{field: None})
    row = diagnosed(source(p))
    assert any(label in d.issue and d.subject == 'Beoordeeld lid' for d in row.family_diagnostics)
    assert not any(d.criterion == 'Ouders' for d in row.family_diagnostics)
    assert row.expected == '—'


def test_blank_addition_is_not_missing_information():
    row = diagnosed(source(younger(house_number_addition=''), older(house_number_addition=None)))
    assert row.expected == '0'
    assert not row.family_diagnostics


@pytest.mark.parametrize('whose', ['assessed', 'other'])
def test_missing_parents_identifies_which_member(whose):
    a = younger(parent_names=('Synthetische ouder Y', None))
    b = replace(older(parent_names=('Synthetische ouder O', None)), house_number='18')
    if whose == 'assessed': a = replace(a, parent_names=(None, None))
    else: b = replace(b, parent_names=(None, None))
    row = diagnosed(source(a,b))
    assert row.expected == '10'
    assert row.family_diagnostics == ()


def test_multiple_members_and_causes_stay_separate():
    a = younger(parent_names=('Ouder Y', None))
    b = replace(older(), house_number='18')
    c = replace(older(), person_id='C', name='Ander synthetisch lid', postal_code=None,
                house_number=None, address_conflicting=True, parent_data_conflicting=True)
    row = diagnosed(source(a,b,c))
    assert {d.compared_person_id for d in row.family_diagnostics} == {'C'}
    c_details = [d for d in row.family_diagnostics if d.compared_person_id == 'C']
    assert len(c_details) == 3
    assert any('Postcode' in d.issue for d in c_details)
    assert any('Huisnummer' in d.issue for d in c_details)
    assert any(d.criterion == 'Adres' and 'conflicteren' in d.issue for d in c_details)
    assert not any(d.criterion == 'Ouders' for d in c_details)


@pytest.mark.parametrize('whose', ['assessed', 'other'])
def test_conflicts_are_explained_without_guessed_conflicting_fields(whose):
    a = younger(address_conflicting=whose == 'assessed', parent_data_conflicting=whose == 'assessed')
    b = replace(older(address_conflicting=whose == 'other', parent_data_conflicting=whose == 'other'), house_number='18')
    row = diagnosed(source(a,b))
    conflicts = [d for d in row.family_diagnostics if 'conflicteren' in d.issue]
    assert len(conflicts) == (2 if whose == 'assessed' else 1)
    assert {d.involved_member for d in conflicts} == {a.name if whose == 'assessed' else b.name}
    assert not any('Postcode' in d.issue or 'Huisnummer' in d.issue for d in conflicts)


def test_proven_exemption_keeps_additional_diagnosis():
    data = source(replace(younger(), postal_code=None), roles=(RoleAssignment('Y','Assistenttrainer'),))
    expectation, = data.derive_member_duties(TODAY)
    assert expectation.status == 'vrijgesteld' and expectation.expected_required_hours == 0
    row = diagnosed(data)
    assert row.expected == '0' and row.family_diagnostics


def test_valid_single_parent_is_not_called_incomplete():
    a = younger(parent_names=('Geregistreerde ouder', None))
    b = older(parent_names=('Geregistreerde ouder', None))
    row = diagnosed(source(a,b))
    assert row.expected == '0' and not row.family_diagnostics


def test_ui_details_are_read_only_and_follow_filter(tmp_path, monkeypatch):
    import streamlit as st
    from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
    members = [member('M1', **{'Geb.dat.':'01-01-2012', 'Postcode':''}),
               member('M2', **{'Geb.dat.':'01-01-2010'})]
    files = exports(tmp_path, members)
    files['teams'] = files['teams'] + b'M2;Senioren;Bond;Teamspeler;Ja\r\n'
    view = load_duty_dashboard(files, as_of=TODAY, source_period='2026-2027')
    path = tmp_path / 'streamlit_app.py'
    path.write_text((Path(__file__).parents[1] / 'streamlit_app.py').read_text())
    def unavailable(self):
        raise sqlite3.OperationalError('no such table: sportlink_bookings')
    def forbidden(*args, **kwargs):
        pytest.fail('No database/Sportlink access allowed for details')
    monkeypatch.setattr(SQLiteDatabase,'initialize',unavailable)
    monkeypatch.setattr(sqlite3,'connect',forbidden)
    monkeypatch.setattr(SportlinkVrijwilligersClient,'fetch_rows',forbidden)
    monkeypatch.setattr(st,'file_uploader',lambda label, **kwargs: BytesIO(files[kwargs['key'].removeprefix('duty-control-')]))
    app = AppTest.from_file(str(path))
    app.session_state['duty-control-date'] = TODAY
    app.session_state['duty-control-period'] = '2026-2027'
    app.run(timeout=20)
    assert not app.exception
    details = next(item.value for item in app.dataframe if 'Oorzaak' in item.value.columns)
    assert len(details) == sum(len(r.family_diagnostics) for r in view.rows)
    assert 'Relatiecode' not in details.columns
    assert any('Postcode' in value for value in details['Oorzaak'])
    app.radio(key='duty-control-filter').set_value('Alleen afwijkingen').run()
    assert not app.exception
    assert not any('Oorzaak' in item.value.columns for item in app.dataframe)


@pytest.mark.parametrize('same_address', [False, True])
def test_birth_diagnosis_requires_same_registered_address(same_address):
    b = replace(older(), birth_date=None, house_number='17' if same_address else '18')
    row = diagnosed(source(younger(), b))
    assert bool(row.family_diagnostics) is same_address
    if same_address:
        d, = row.family_diagnostics
        assert d.criterion == 'Geboortedatum'
        assert d.subject == 'Ander vergeleken lid'
        assert d.involved_member == 'Lid O'
