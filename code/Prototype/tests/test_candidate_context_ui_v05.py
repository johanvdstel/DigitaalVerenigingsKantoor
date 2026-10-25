"""Synthetic Streamlit integration; no local CSVs, HTTP or CKC database."""
from dataclasses import replace

import pytest

from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.programma_client import ProgrammaFetchStats
from dvk.application_services import PlanningApplicationService
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_v05 import IDENTITY, exports, factory
from test_planning_ui_names_v05 import page
from test_volunteer_planning_integration_v05 import sync, PERIOD


@pytest.fixture
def operational_page(tmp_path, monkeypatch):
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "synthetic")
    original = CandidateContextApplicationService.load
    observed = []
    def load(self, **kwargs):
        observed.append(kwargs['period'])
        kwargs.setdefault('exports', exports())
        kwargs.setdefault('client_factory', factory(b'[]'))
        return original(self, **kwargs)
    monkeypatch.setattr(CandidateContextApplicationService, 'load', load)
    app, db = page(tmp_path)
    assert observed == [PERIOD]  # Automatic on first operational use, not every rerun.
    assert sync(db, load_shift_catalog(), {})[0] is None
    app.run()
    app.session_state['selected_service_id'] = app.dataframe[0].value.iloc[0].service_id
    app.run()
    return app, db, observed


def test_operational_candidates_have_names_hours_and_human_approval(operational_page):
    app, db, observed = operational_page
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert observed == [PERIOD, PERIOD]
    assert any(t.value == 'Synthetisch lid M1' for t in app.markdown)
    assert any('BL-03' in t.value for t in app.caption)
    assert any('Taakplicht: Geen vrijstellingsgrond gevonden' in t.value for t in app.caption)
    assert any('Prioriteit: actuele E=10' in t.value for t in app.caption)
    assert any('technisch geslaagd' in t.value for t in app.caption)
    selection = next(c for c in app.checkbox if c.key.startswith('pick-'))
    selection.check().run()
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()
    next(b for b in app.button if b.label == 'Selectie bevestigen').click().run()
    assert not app.exception
    assert any('Synthetisch lid M1' in t.value for t in app.success)
    with db.unit_of_work() as uow:
        assert PlanningApplicationService(IDENTITY, uow=uow).active_planning()[0].assignment.person_id == 'M1'
    assert any('Synthetisch lid M1' in s for widget in app.selectbox if widget.label == 'Tijdelijke inroostering' for s in widget.options)


def test_failed_refresh_replaces_candidates_with_explicit_program_error(operational_page, monkeypatch):
    app, db, _ = operational_page
    app.button(key='load-candidate-sources').click().run()
    assert any(c.key.startswith('pick-') for c in app.checkbox)
    ctx = app.session_state['candidate-context']
    def failure(*a, **k):
        return replace(ctx, program=None, stats=ProgrammaFetchStats(1, 3, 1),
                       error='Programma API niet beschikbaar: synthetische technische fout')
    monkeypatch.setattr(CandidateContextApplicationService, 'load', failure)
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert any('Programma API niet beschikbaar' in e.value for e in app.error)
    assert not any(c.key.startswith('pick-') for c in app.checkbox)
    assert not any('Geen wedstrijd' == t.value for t in app.markdown)
    assert any('Wedstrijdcontext onbekend' in t.value for t in app.info)
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_failed_csv_refresh_cannot_retain_previous_proposals(operational_page, monkeypatch):
    app, _, _ = operational_page
    app.button(key='load-candidate-sources').click().run()
    assert any(c.key.startswith('pick-') for c in app.checkbox)
    def failure(*a, **k):
        raise CandidateSourceError('Synthetische onleesbare CSV')
    monkeypatch.setattr(CandidateContextApplicationService, 'load', failure)
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert any('onleesbare CSV' in e.value for e in app.error)
    assert not any(c.key.startswith('pick-') for c in app.checkbox)
    assert 'candidate-context' not in app.session_state


def test_period_change_and_demo_switch_do_not_reuse_operational_context(operational_page):
    from datetime import timedelta
    app, _, _ = operational_page
    app.button(key='load-candidate-sources').click().run()
    app.date_input[0].set_value(PERIOD.start + timedelta(days=7)).run()
    app.button(key='confirm-period-change').click().run()
    assert not app.exception
    assert app.session_state['candidate-context'].period != PERIOD
    app.radio(key='planning-source-mode').set_value('Demonstratie').run()
    assert not app.exception
    assert not any(b.key == 'load-candidate-sources' for b in app.button)


def test_person_warnings_do_not_show_global_csv_refresh_error(operational_page, monkeypatch):
    from test_candidate_person_issues_v05 import data_with_two, rows, write_rows
    app, _, _ = operational_page
    data = data_with_two()
    members = rows(data, 'leden')
    members[1]['Lidstatus'] = 'Overschrijving spelactiviteit'
    write_rows(data, 'leden', members)
    from test_candidate_context_v05 import context
    ctx = replace(context(data), period=PERIOD)
    monkeypatch.setattr(CandidateContextApplicationService, 'load', lambda *a, **k: ctx)
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert any(t.value == 'Synthetisch lid M1' for t in app.markdown)
    assert not any(t.value == 'Synthetisch lid M2' for t in app.markdown)
    assert any('de overige kandidaten worden normaal beoordeeld' in t.value for t in app.info)
    assert any('UNKNOWN_MEMBERSHIP_STATUS: 1' in t.value for t in app.caption)
    assert not any('vernieuw de exports' in t.value for t in app.error)
