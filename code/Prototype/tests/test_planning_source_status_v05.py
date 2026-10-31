"""BL-24 source evidence and synthetic UI regression."""
from dataclasses import replace
from datetime import datetime

from dvk.candidate_context import CandidateContextApplicationService
from dvk.historical_backlog import HISTORICAL_FILENAME, unavailable_history
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.planning_source_presenter import planning_source_rows
from dvk.sportlink_exports import EXPORT_FILENAMES, default_export_directory
from test_candidate_context_v05 import context, exports, IDENTITY, PERIOD, factory
from test_candidate_context_ui_v05 import operational_page

MOMENT = datetime.fromisoformat('2026-10-20T12:34:00+02:00')
TIME = 'Laatst ingelezen / opgehaald'


def indexed(**kwargs):
    return {r['Databron']: r for r in planning_source_rows(**kwargs)}


def test_eight_sources_even_before_loading_and_no_invented_time():
    rows = indexed()
    assert list(rows) == [*EXPORT_FILENAMES.values(), HISTORICAL_FILENAME,
                          'Sportlink Vrijwilligers', 'Sportlink Programma']
    assert all(r[TIME] == 'onbekend' for r in rows.values())
    assert all(r['Status'] in {'Niet geladen', 'Niet opgehaald'} for r in rows.values())


def test_known_csv_time_and_optional_history_are_independent():
    ctx = context()
    history = replace(unavailable_history('Historische bron ontbreekt.'), loaded_at=None)
    rows = indexed(context=replace(ctx, csv_loaded_at=MOMENT, historical_backlog=history))
    for filename in EXPORT_FILENAMES.values():
        assert rows[filename][TIME] == '20-10-2026 12:34'
        assert rows[filename]['Status'] == 'Ingelezen'
    assert rows[HISTORICAL_FILENAME][TIME] == 'onbekend'
    assert 'planning blijft bruikbaar' in rows[HISTORICAL_FILENAME]['Bruikbaarheid']
    assert rows['Sportlink Programma']['Status'] == 'Technisch geslaagd'
    assert 'geen operationele wedstrijden' in rows['Sportlink Programma']['Toelichting']


def test_provided_exports_have_unknown_import_time_and_no_age_warning():
    rows = indexed(context=context())
    assert rows['Leden.csv'][TIME] == 'onbekend'
    old = replace(context(), csv_loaded_at=datetime.fromisoformat('2000-01-01T12:00:00+01:00'))
    for name in ('Functies.csv', 'Commissies.csv'):
        row = indexed(context=old)[name]
        assert row[TIME] == '01-01-2000 12:00'
        assert row['Bruikbaarheid'] == 'Beschikbaar'
        assert row['Toelichting'] == ''


def test_missing_regular_source_never_claims_other_files_available():
    (default_export_directory() / 'Teams.csv').unlink()
    from dvk.candidate_context import CandidateSourceError
    import pytest
    with pytest.raises(CandidateSourceError) as error:
        CandidateContextApplicationService(IDENTITY).load(
            period=PERIOD, source_period='2026-2027', client_id='synthetic', client_factory=factory(b'[]'))
    rows = indexed(load_error=str(error.value))
    assert rows['Teams.csv']['Status'] == 'Niet geladen'
    assert "'Teams.csv' ontbreekt" in rows['Teams.csv']['Toelichting']
    assert all(rows[n]['Bruikbaarheid'] == 'Onbekend' for n in EXPORT_FILENAMES.values())


def test_local_load_metadata_preserved(monkeypatch):
    from dvk.local_csv_sources import LoadedLocalExports
    monkeypatch.setattr(LocalCsvSourceApplicationService, 'load',
                        lambda self: LoadedLocalExports(exports(), MOMENT, tuple(EXPORT_FILENAMES.values())))
    ctx = CandidateContextApplicationService(IDENTITY).load(
        period=PERIOD, source_period='2026-2027', client_id='synthetic', client_factory=factory(b'[]'))
    assert ctx.csv_loaded_at == MOMENT


def test_history_read_time_known_even_if_structure_invalid(monkeypatch):
    monkeypatch.setattr('dvk.local_csv_sources.read_export_text', lambda *a: 'invalid\n')
    history = LocalCsvSourceApplicationService().historical_backlog(person_ids=())
    assert not history.available
    assert history.loaded_at is not None
    rows = indexed(context=replace(context(), historical_backlog=history))
    assert rows[HISTORICAL_FILENAME][TIME] != 'onbekend'
    assert rows[HISTORICAL_FILENAME]['Status'] == 'Niet beschikbaar / onbruikbaar'


def test_program_transport_failure_and_semantic_failure_are_distinct():
    ctx = context()
    failed = indexed(context=replace(ctx, program=None, error='Programma API niet beschikbaar'))['Sportlink Programma']
    assert failed['Status'] == 'Aanvraag mislukt'
    assert failed[TIME] == 'onbekend'
    invalid = indexed(context=replace(ctx, error='Teamkoppeling onbekend'))['Sportlink Programma']
    assert invalid['Status'] == 'Technisch geslaagd'
    assert invalid['Bruikbaarheid'].startswith('Niet bruikbaar')
    assert 'Teamkoppeling onbekend' in invalid['Toelichting']


def test_volunteer_failure_preserves_last_success_time_and_usability():
    success = dict(start='2026-10-19', end='2026-10-25', fetched_at=MOMENT.isoformat(), identity={'total': 0})
    row = indexed(volunteer_success=success, volunteer_matching=True)['Sportlink Vrijwilligers']
    assert row['Status'] == 'Technisch geslaagd'
    assert 'inroosteringen: 0' in row['Toelichting']
    row = indexed(volunteer_success=success, volunteer_matching=True,
                  volunteer_attempt={'status': 'Mislukt', 'message': 'Synthetische netwerkfout'})['Sportlink Vrijwilligers']
    assert row['Status'] == 'Laatste verversing mislukt'
    assert row[TIME] == '20-10-2026 12:34'
    assert row['Bruikbaarheid'] == 'Gevalideerd voor gekozen periode'
    assert 'Vorige bron behouden' in row['Toelichting']


def test_ui_shows_complete_table_and_refresh_preserves_planning(operational_page):
    app, _, observed = operational_page
    detail = next(e for e in app.expander if e.label == 'Bronstatus en actualiteit')
    assert len(detail.dataframe[0].value) == 8
    assert detail.dataframe[0].value.Databron.tolist() == list(indexed())
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert len(observed) == 2
    assert 'selected_service_id' in app.session_state


def test_demo_never_presents_synthetic_metadata_as_live():
    assert all(r['Status'] == 'Demonstratie' and r[TIME] == 'onbekend'
               for r in planning_source_rows(context=context(), demo=True))


def test_available_history_time_and_partial_warnings_are_preserved():
    from dvk.historical_backlog import HistoricalBacklogSource
    from dvk.real_data_import import DataQualitySignal
    signal = DataQualitySignal('SYNTHETIC', 'WARNING', 'historical_duty', 'M1', 'Synthetische bronafwijking')
    history = HistoricalBacklogSource(True, signals=(signal,), message='Planner borgt vorig seizoen.', loaded_at=MOMENT)
    row = indexed(context=replace(context(), historical_backlog=history))[HISTORICAL_FILENAME]
    assert row[TIME] == '20-10-2026 12:34'
    assert row['Status'] == 'Ingelezen'
    assert row['Bruikbaarheid'] == 'Deels bruikbaar; zie bronmeldingen'
    assert row['Toelichting'] == history.message


def test_regular_source_warnings_do_not_claim_whole_source_unusable():
    from dvk.real_data_import import DataQualitySignal
    ctx = context()
    signal = DataQualitySignal('SYNTHETIC', 'WARNING', 'functies', 'M1', 'Synthetische functie onbekend')
    ctx = replace(ctx, source=replace(ctx.source, signals=(signal,)))
    row = indexed(context=ctx)['Functies.csv']
    assert row['Status'] == 'Ingelezen'
    assert row['Bruikbaarheid'] == 'Bronmeldingen; zie datakwaliteit'
    assert row['Toelichting'] == signal.message
