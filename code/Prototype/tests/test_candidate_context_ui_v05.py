"""Synthetic Streamlit integration; no local CSVs, HTTP or CKC database."""
from synthetic_demo_screen import use_synthetic_demo
from ui_table_events import table as ui_table
from dataclasses import replace
from ui_table_events import table, pick

import pytest
from streamlit.testing.v1 import AppTest

from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.programma_client import ProgrammaFetchStats
from dvk.application_services import PlanningApplicationService
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_v05 import IDENTITY, exports, factory
from test_planning_ui_names_v05 import page
from test_volunteer_planning_integration_v05 import PERIOD, seed_work, snapshot, sync


def refresh_candidate_sources(app):
    app.button(key="nav-sources").click().run()
    app.button(key="load-candidate-sources").click().run()
    app.button(key="nav-planning").click().run()


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
    assert observed == []
    refresh_candidate_sources(app)
    assert observed == [PERIOD]
    assert sync(db, load_shift_catalog(), {})[0] is None
    app.run()
    app.session_state['selected_service_id'] = ui_table(app, "services_editor-").value.iloc[0].service_id
    app.run()
    return app, db, observed


def test_operational_candidates_have_names_hours_and_human_approval(operational_page):
    app, db, observed = operational_page
    refresh_candidate_sources(app)
    assert not app.exception
    assert observed == [PERIOD, PERIOD]
    assert 'Synthetisch lid M1' in table(app).value.Kandidaat.tolist()
    assert not any('BL-03' in t.value for t in app.caption)
    assert not any('DVK-beleidscontrole taakplicht:' in t.value for t in app.caption)
    pick(app)
    assert any(t.value == '#### Synthetisch lid M1' for t in app.markdown)
    assert any('DVK-beleidscontrole taakplicht: Geen vrijstellingsgrond gevonden' in t.value for t in app.caption)
    assert any('Openstaande uren: 10.' in t.value for t in app.caption)
    assert any('technisch geslaagd' in t.value for t in app.caption)
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
    refresh_candidate_sources(app)
    assert any(t.key and t.key.startswith('candidate-table-') for t in app.dataframe)
    ctx = app.session_state['candidate-context']
    def failure(*a, **k):
        return replace(ctx, program=None, stats=ProgrammaFetchStats(1, 3, 1),
                       error='Programma API niet beschikbaar: synthetische technische fout')
    monkeypatch.setattr(CandidateContextApplicationService, 'load', failure)
    refresh_candidate_sources(app)
    assert not app.exception
    assert any('Programma API niet beschikbaar' in e.value for e in app.error)
    assert not any(t.key and t.key.startswith('candidate-table-') for t in app.dataframe)
    assert not any('Geen wedstrijd' == t.value for t in app.markdown)
    assert any('Wedstrijdcontext onbekend' in t.value for t in app.info)
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_failed_csv_refresh_cannot_retain_previous_proposals(operational_page, monkeypatch):
    app, _, _ = operational_page
    refresh_candidate_sources(app)
    assert any(t.key and t.key.startswith('candidate-table-') for t in app.dataframe)
    def failure(*a, **k):
        raise CandidateSourceError('Synthetische onleesbare CSV')
    monkeypatch.setattr(CandidateContextApplicationService, 'load', failure)
    refresh_candidate_sources(app)
    assert not app.exception
    assert any('onleesbare CSV' in e.value for e in app.error)
    assert not any(t.key and t.key.startswith('candidate-table-') for t in app.dataframe)
    assert 'candidate-context' not in app.session_state


def test_failed_candidate_refresh_reaches_other_browser_on_rerun(operational_page, monkeypatch):
    first, db, observed = operational_page
    assert table(first).value.Kandidaat.tolist()
    seed_work(db, load_shift_catalog().bindings(PERIOD)[0].service)
    before = snapshot(db)
    proposal_run_key = f"proposal-run-{first.session_state['selected_service_id']}"
    assert proposal_run_key in first.session_state

    second = AppTest.from_file(str(db.path.with_name("streamlit_app.py")), default_timeout=20).run()
    second.button(key="nav-planning").click().run()
    second.button(key="resume-planning").click().run()
    assert not second.exception
    calls = []

    def failure(*args, **kwargs):
        calls.append(kwargs["period"])
        raise CandidateSourceError("Synthetische onleesbare CSV")

    monkeypatch.setattr(CandidateContextApplicationService, "load", failure)
    refresh_candidate_sources(second)
    assert not second.exception and calls == [PERIOD]
    assert any("onleesbare CSV" in item.value for item in second.error)

    def unexpected_source_call(*args, **kwargs):
        pytest.fail("Een rerun mag geen nieuwe CSV- of API-bron ophalen.")

    monkeypatch.setattr("dvk.local_csv_sources.read_export_text", unexpected_source_call)
    monkeypatch.setattr("dvk.programma_client.SportlinkProgrammaClient.fetch_rows", unexpected_source_call)
    monkeypatch.setattr("dvk.vrijwilligers_client.SportlinkVrijwilligersClient.fetch_rows", unexpected_source_call)
    first.run()
    assert not first.exception and calls == [PERIOD] and observed == [PERIOD]
    assert first.session_state["selected_service_id"]
    assert any("onleesbare CSV" in item.value for item in first.error)
    assert not any(node.key and node.key.startswith("candidate-table-") for node in first.dataframe)
    assert proposal_run_key not in first.session_state
    assert snapshot(db) == before


def test_period_change_and_demo_switch_do_not_reuse_operational_context(operational_page):
    from datetime import timedelta
    app, _, _ = operational_page
    refresh_candidate_sources(app)
    app.date_input[0].set_value(PERIOD.start + timedelta(days=7)).run()
    app.button(key='confirm-period-change').click().run()
    assert not app.exception
    assert 'candidate-context' not in app.session_state
    use_synthetic_demo(app)
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
    refresh_candidate_sources(app)
    assert not app.exception
    assert 'Synthetisch lid M1' in table(app).value.Kandidaat.tolist()
    assert not 'Synthetisch lid M2' in table(app).value.Kandidaat.tolist()
    assert any('de overige kandidaten worden normaal beoordeeld' in t.value for t in app.info)
    assert any('UNKNOWN_MEMBERSHIP_STATUS: 1' in t.value for t in app.caption)
    assert not any('vernieuw de exports' in t.value for t in app.error)


@pytest.mark.parametrize('other_matchday,temporary_same_day', [(True, False), (False, True), (True, True)])
def test_no_exception_input_and_emergency_visible_with_explicit_approval(
        operational_page, monkeypatch, other_matchday, temporary_same_day):
    from test_iteration1_candidates_v05 import team_data
    from test_candidate_context_v05 import context
    from test_volunteer_planning_integration_v05 import snapshot
    app, db, _ = operational_page
    ctx = replace(context(team_data(['Algemeen/Zondag' if other_matchday else 'Algemeen/Zaterdag'])),period=PERIOD)
    if temporary_same_day:
        # Exercise presentation of the stored same-day reason, alone and combined
        # with the teamspeeldag emergency produced by the domain service.
        original_propose = CandidateContextApplicationService.propose
        def propose_with_temporary_reason(self, *args, **kwargs):
            result = original_propose(self, *args, **kwargs)
            return replace(result, planned=tuple(replace(item, proposal=replace(
                item.proposal, suitability='emergency',
                uncertainties=item.proposal.uncertainties + ('temporary_planning_same_day_emergency',)))
                for item in result.planned))
        monkeypatch.setattr(CandidateContextApplicationService, 'propose', propose_with_temporary_reason)
    monkeypatch.setattr(CandidateContextApplicationService,'load',lambda *a, **k: ctx)
    refresh_candidate_sources(app)
    # Select Saturday, while the only player has Sunday as team matchday.
    saturday = next(b.service for b in load_shift_catalog().bindings(PERIOD)
                    if b.service.starts_at.weekday()==5)
    app.session_state['selected_service_id'] = saturday.service_id
    app.run()
    assert not app.exception
    if other_matchday:
        assert 'Noodkandidaat' in table(app).value.iloc[0]['Doel']
    remarks = table(app).value.iloc[0]['Opmerkingen']
    assert ('andere teamspeeldag' in remarks) == other_matchday
    assert ('al tijdelijk ingepland op dezelfde dag' in remarks) == temporary_same_day
    captions = ' '.join(c.value for c in app.caption)
    assert 'secundaire actie' not in captions
    assert 'uitzonderingen worden alleen expliciet vastgelegd' not in captions
    assert 'Niet selecteren is geen afwijzing' in captions
    assert not any('Uitzondering' in b.label for b in app.button)
    assert not any(w.label in {'Reden','Toelichting'} for w in app.text_input)
    before = snapshot(db)
    pick(app)
    assert snapshot(db)==before
    captions = ' '.join(c.value for c in app.caption)
    assert ('andere teamspeeldag' in captions) == other_matchday
    assert ('al tijdelijk ingepland op dezelfde dag' in captions) == temporary_same_day
    next(b for b in app.button if b.label=='Selectie bevestigen').click().run()
    assert not app.exception
    assert len(snapshot(db)[1])==1
    # A failed Teams refresh hides the earlier proposal but preserves planning.
    before = snapshot(db)
    def broken(*a,**k):
        raise CandidateSourceError('Teams-bronfout: Speeldag ontbreekt of is onbekend.')
    monkeypatch.setattr(CandidateContextApplicationService,'load',broken)
    refresh_candidate_sources(app)
    assert any('Speeldag' in e.value for e in app.error)
    assert not any(t.key and t.key.startswith('candidate-table-') for t in app.dataframe)
    assert snapshot(db)==before
