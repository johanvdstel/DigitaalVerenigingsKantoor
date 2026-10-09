"""Synthetic development regressions for round 4."""
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from dvk.duty_control_presenter import GROUND_TEXT, load_duty_dashboard, present_controls
from dvk.member_duty import DutyGround
from dvk.model import RoleAssignment
from test_hours_control_v05 import load, TODAY
from test_member_duty_v05 import person, source


def dashboard(tmp_path, **kwargs):
    data = load(tmp_path, **kwargs)
    return present_controls(data, data.compare_required_hours(TODAY))


@pytest.mark.parametrize("values,status", [((10,0,0,0,10), "overeenkomst"), ((0,0,0,0,0), "afwijking")])
def test_status_and_counts(tmp_path, values, status):
    view = dashboard(tmp_path, values=values)
    assert view.rows[0].status == status
    assert view.counts[status] == view.counts['totaal'] == 1
    assert view.filtered('Alle') == view.rows
    assert len(view.filtered('Alleen afwijkingen')) == (status == 'afwijking')
    assert not view.filtered('Alleen niet betrouwbaar beoordeelbaar')


def test_unknown_function_and_unknown_expectation(tmp_path):
    view = dashboard(tmp_path, unknown=True)
    assert view.rows[0].expected == '—'
    assert 'Onbekende functieclassificatie' in view.rows[0].why
    assert view.filtered('Alleen niet betrouwbaar beoordeelbaar') == view.rows
    assert view.counts['niet betrouwbaar beoordeelbaar'] == 1


def test_missing_and_ambiguous_position(tmp_path):
    data = load(tmp_path)
    for records, text in [((), 'Urenpositie ontbreekt'), (data.duty_records * 2, 'Meerdere urenposities')]:
        changed = replace(data, duty_records=records)
        row, = present_controls(changed, changed.compare_required_hours(TODAY)).rows
        assert row.status == 'niet betrouwbaar beoordeelbaar'
        assert text in row.why


@pytest.mark.parametrize('code', list(GROUND_TEXT))
def test_all_existing_grounds_are_human_readable(tmp_path, code):
    data = load(tmp_path)
    control, = data.compare_required_hours(TODAY)
    ground = DutyGround(code, 'M1')
    control = replace(control, expectation=replace(control.expectation, grounds=(ground,)))
    row, = present_controls(data, (control,)).rows
    assert code not in row.why
    assert row.why and 'nadere beoordeling' not in row.why


def test_actual_household_and_personal_explanation():
    data = source(person('A'), person('B'), roles=(RoleAssignment('A', 'Assistenttrainer'),))
    rows = present_controls(data, data.compare_required_hours(TODAY)).rows
    assert 'Persoonlijke vrijstelling' in rows[0].why
    assert 'Huishoudvrijstelling' in rows[1].why and 'Lid A' in rows[1].why


def test_family_explanations():
    data = source(person('A', date(2010,1,1)), person('B', date(2012,1,1)))
    rows = present_controls(data, data.compare_required_hours(TODAY)).rows
    assert 'oudste kwalificerende minderjarige' in rows[0].why
    assert 'jonger kind' in rows[1].why and 'Lid A' in rows[1].why


def uploads(tmp_path):
    load(tmp_path, extra=True)
    return {key: (tmp_path / filename).read_bytes() for key, filename in
            [('leden','members.csv'), ('functies','functions.csv'), ('commissies','committees.csv'),
             ('teams','teams.csv'), ('vrijwilligers_periode','hours.csv')]}


def test_memory_end_to_end_identity_period_and_date(tmp_path):
    files = uploads(tmp_path)
    view = load_duty_dashboard(files, as_of=TODAY, source_period='Expliciete periode')
    assert view.rows[0].member == 'Synthetisch lid'  # hours export has another name
    assert view.rows[0].person_id == 'M1'
    assert view.rows[0].status == 'overeenkomst'
    assert all(p.source_period == 'Expliciete periode' for p in view.source.provenance)
    assert b'Functie' not in files['teams']
    assert view.source.derive_member_duties(TODAY)[0].as_of == TODAY


def test_b02_same_row_through_dashboard(tmp_path):
    files = uploads(tmp_path)
    files['teams'] = b'Rel. code;Team;Teamsoort;Teamrol;Spelend lid\nM1;A;Bond;Trainer;Ja\nM1;B;Vereniging;Teamspeler;Ja\n'
    view = load_duty_dashboard(files, as_of=TODAY, source_period='2026')
    assert view.rows[0].expected == '0'
    assert 'Geen relevante voetbaldeelname' in view.rows[0].why


@pytest.mark.parametrize('kind', ['missing', 'column', 'encoding', 'date', 'period'])
def test_input_errors_are_presentable(tmp_path, kind):
    files = uploads(tmp_path)
    period = '2026'
    if kind == 'missing': files.pop('teams')
    if kind == 'column': files['teams'] = b'Naam\nTest\n'
    if kind == 'encoding': files['leden'] = b'\xff'
    if kind == 'date': files['leden'] = files['leden'].replace(b'01-01-1990', b'not-a-date')
    if kind == 'period': period = ''
    with pytest.raises(ValueError):
        load_duty_dashboard(files, as_of=TODAY, source_period=period)


def test_read_only_ui_boundary():
    text = (Path(__file__).parents[1] / 'streamlit_app.py').read_text().split('### Taakplichtcontrole')[1]
    assert 'st.dataframe' in text and 'st.file_uploader' in text
    assert 'database' not in text and 'st.button' not in text and 'st.data_editor' not in text


def test_streamlit_initial_render(tmp_path):
    from streamlit.testing.v1 import AppTest
    app_file = Path(__file__).parents[1] / 'streamlit_app.py'
    local_app = tmp_path / 'streamlit_app.py'
    local_app.write_text(app_file.read_text())
    app = AppTest.from_file(str(local_app)).run(timeout=20)
    assert not app.exception
    assert any('Taakplichtcontrole' in item.value for item in app.markdown)
    assert any(item.label == 'Peildatum taakplichtcontrole' for item in app.date_input)
    radio = next(item for item in app.radio if item.label == 'Toon taakplichtcontrole')
    assert radio.options == ['Alle', 'Alleen afwijkingen', 'Alleen niet betrouwbaar beoordeelbaar']


@pytest.mark.parametrize('body', [b'M1;"unfinished', b'M1;A;Bond;Teamspeler;Ja;extra'])
def test_malformed_csv_is_not_silently_repaired(tmp_path, body):
    files = uploads(tmp_path)
    files['teams'] = b'Rel. code;Team;Teamsoort;Teamrol;Spelend lid\n' + body
    with pytest.raises(ValueError, match='Teams'):
        load_duty_dashboard(files, as_of=TODAY, source_period='2026')


def test_mixed_population_counts_and_filters(tmp_path):
    data = load(tmp_path)
    control, = data.compare_required_hours(TODAY)
    controls = (control, replace(control, status='afwijking'),
                replace(control, status='niet betrouwbaar beoordeelbaar'))
    view = present_controls(data, controls)
    assert view.counts == {'totaal': 3, 'overeenkomst': 1, 'afwijking': 1,
                           'niet betrouwbaar beoordeelbaar': 1}
    assert len(view.filtered('Alle')) == 3
    assert len(view.filtered('Alleen afwijkingen')) == 1
    assert len(view.filtered('Alleen niet betrouwbaar beoordeelbaar')) == 1


@pytest.mark.parametrize('values,status', [((10,0,0,0,10), 'overeenkomst'),
                                           ((0,0,0,0,0), 'afwijking')])
def test_contact_value_preserves_imported_control_status(tmp_path, values, status):
    data = load(tmp_path, values=values)
    rows = []
    for contact in (True, False, None):
        changed = replace(data, persons=(replace(data.persons[0], contact_via_parent=contact),))
        row, = present_controls(changed, changed.compare_required_hours(TODAY)).rows
        assert row.status == status
        rows.append(row)
    assert rows[0] == rows[1] == rows[2]
