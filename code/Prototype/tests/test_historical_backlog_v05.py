"""BL-03 contract: only synthetic CSVs, supplied in memory or synthetic HOME."""
from dataclasses import replace
from datetime import date, timedelta

import pytest

from dvk.candidate_context import CandidateContextApplicationService
from dvk.application_services import PlanningApplicationService
from dvk.candidate_presenter import priority_explanation
from dvk.historical_backlog import HISTORICAL_FILENAME, import_historical_backlog
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.planning import PlanningPeriod
from dvk.prioritization import prioritize_candidates
from dvk.sportlink_exports import default_export_directory
from test_candidate_context_v05 import (IDENTITY, context, csv_bytes, exports, need,
                                        propose, service)
from test_candidate_person_issues_v05 import data_with_two, ids

FIELDS = ['Relatiecode', 'Verplichte punten', 'Gecorrigeerde punten', 'Voldaan',
          'Nog ingedeeld', 'Niet ingedeeld', 'Volledige naam', 'Regeling', 'Toegewezen taak']


def history_row(pid='M1', value=6):
    return dict(zip(FIELDS, [pid, 10, 0, 10-value, 0, value, 'Onjuiste synthetische naam', '', '']))


def history_text(rows):
    return csv_bytes(FIELDS, rows).decode('utf-8-sig')


def history(rows, people=('M1', 'M2')):
    return import_historical_backlog(history_text(rows), people)


@pytest.mark.parametrize('value', [7, 0, -3])
def test_source_values_preserved_and_names_not_used(value):
    result = history([history_row(value=value)])
    assert result.available and result.values == {'M1': value}
    assert result.records[0].source_remaining_hours == value
    assert not result.signals


@pytest.mark.parametrize('error,code', [
    ('duplicate', 'HISTORICAL_DUPLICATE_PERSON'),
    ('invalid', 'HISTORICAL_INVALID_HOURS'),
    ('mismatch', 'HISTORICAL_FORMULA_MISMATCH'),
    ('unknown_person', 'HISTORICAL_UNMATCHED_PERSON'),
    ('empty_person', 'HISTORICAL_UNMATCHED_PERSON'),
])
def test_bad_relation_not_used_without_hiding_other_rows(error, code):
    row = history_row()
    rows = [row, history_row('M2', 4)]
    if error == 'duplicate':
        rows.append(dict(row))
    elif error == 'invalid':
        row['Niet ingedeeld'] = 'geen getal'
    elif error == 'mismatch':
        row['Niet ingedeeld'] = '9'
    else:
        row['Relatiecode'] = 'ORPHAN' if error == 'unknown_person' else ''
    result = history(rows)
    assert result.available and result.values == {'M2': 4}
    assert any(s.code == code for s in result.signals)
    if error == 'mismatch':
        assert result.records[0].source_remaining_hours == 9
        assert result.records[0].position.E == 6


@pytest.mark.parametrize('value', ['', 'NaN', 'Infinity', '1.5', 'tekst'])
def test_existing_whole_number_validation_reused(value):
    row = history_row()
    row['Niet ingedeeld'] = value
    assert not history([row]).values


@pytest.mark.parametrize('text', ['Relatiecode;Niet ingedeeld\nM1;4',
    history_text([history_row()]) + 'extra;broken;row\n',
    ';'.join(FIELDS) + '\n"M1;10;0;4;0;6;broken'])
def test_structure_error_is_nonfatal_unavailable_source(text):
    result = import_historical_backlog(text, ['M1'])
    assert not result.available and not result.values
    assert 'planning blijft bruikbaar' in result.message


@pytest.mark.parametrize('mode', ['missing', 'invalid_utf8', 'directory'])
def test_optional_local_file_does_not_become_mandatory(mode):
    path = default_export_directory() / HISTORICAL_FILENAME
    if mode == 'invalid_utf8':
        path.write_bytes(b'\xff')
    elif mode == 'directory':
        path.mkdir()
    result = LocalCsvSourceApplicationService().historical_backlog(person_ids=['M1'])
    assert not result.available and 'niet meegewogen' in result.message
    # Current functions must not read the historical path at all.
    loaded = LocalCsvSourceApplicationService().load()
    assert len(loaded.exports) == 5 and HISTORICAL_FILENAME not in loaded.filenames


def test_local_loading_in_operational_context_and_refresh():
    path = default_export_directory() / HISTORICAL_FILENAME
    path.write_text(history_text([history_row(value=-3)]), encoding='utf-8-sig')
    ctx = context()
    assert ctx.historical_backlog.values == {'M1': -3}
    assert propose(ctx).planned
    path.write_text(history_text([history_row(value=8)]))
    assert context().historical_backlog.values == {'M1': 8}


@pytest.mark.parametrize('year', [2026, 2027])
@pytest.mark.parametrize('month,day,consider', [(6,30,False),(7,1,True),(11,30,True),
                                               (12,1,True),(12,31,True),(1,1,False)])
def test_all_boundaries_use_service_date_and_repeat_annually(year,month,day,consider):
    ctx = replace(context(), historical_backlog=history([history_row()]))
    s = service()
    start = s.starts_at.replace(year=year,month=month,day=day)
    s = replace(s, starts_at=start, ends_at=start+timedelta(hours=3))
    begin = year if month >= 7 else year-1
    ctx = replace(ctx,period=PlanningPeriod(start.date(),start.date()),source_period=f'{begin}-{begin+1}')
    result = CandidateContextApplicationService(IDENTITY).propose(
        ctx,service=s,need=need(s),planning_app=PlanningApplicationService(IDENTITY),
        proposal_run_id='synthetic-boundary')
    assert result.priorities[0].previous_season_considered is consider
    assert result.priorities[0].previous_season_backlog == (6 if consider else 0)


def test_priority_order_current_then_history_then_match_and_stable_id():
    result = propose(context(data_with_two()))
    assessments = tuple(replace(a,preference='preferred' if a.person_id=='M1' else 'neutral')
                        for a in result.assessments)
    ranked = prioritize_candidates(assessments,result.cases,date(2026,12,31),{'M1':0,'M2':9})
    assert [p.person_id for p in ranked] == ['M2','M1']
    ranked = prioritize_candidates(assessments,result.cases,date(2027,1,1),{'M1':0,'M2':9})
    assert [p.person_id for p in ranked] == ['M1','M2']
    cases = tuple(replace(c,sportlink_duty=replace(c.sportlink_duty,completed_hours=1))
                  if c.person.person_id=='M2' else c for c in result.cases)
    assert prioritize_candidates(assessments,cases,date(2026,12,31),{'M2':99})[0].person_id=='M1'
    equal = tuple(replace(a,preference='neutral') for a in assessments)
    for values in ({'M1':-5,'M2':0}, {'M2':0}, {'M1':0,'M2':0}):
        assert [p.person_id for p in prioritize_candidates(equal[::-1],result.cases,date(2026,10,1),values)]==['M1','M2']


@pytest.mark.parametrize('state', ['positive','zero','negative','unknown','unavailable','outside'])
def test_explanation_distinguishes_all_states_without_changing_current_hours(state):
    ctx = context(data_with_two())
    source = history([history_row(value={'positive':6,'negative':-3}.get(state,0))])
    if state=='unknown':
        source = history([])
    ctx = replace(ctx,historical_backlog=source if state!='unavailable' else None)
    result = propose(ctx)
    p = next(i.proposal for i in result.planned if i.proposal.person_id=='M1')
    if state=='outside':
        priorities = prioritize_candidates(result.assessments,result.cases,date(2027,1,1),source.values)
        priority = next(x for x in priorities if x.person_id=='M1')
        p=replace(p,applied_priority_rules=priority.explanation,previous_season_backlog=priority.previous_season_backlog)
    explanation=priority_explanation(p)
    expected={'positive':'vorig seizoen: 6','zero':'0 uur','negative':'geen krediet',
              'unknown':'geen vastgestelde nulachterstand','unavailable':'niet beschikbaar',
              'outside':'uitsluitend van juli tot en met december'}[state]
    assert expected in explanation
    assert (p.A,p.B,p.C,p.D,p.E)==(10,0,0,0,10)
    assert len(result.planned)==2
    assert 'BL-03' not in explanation and '-3' not in explanation


def test_duty_control_does_not_access_historical_source(monkeypatch):
    from dvk.local_csv_sources import LoadedLocalExports
    from datetime import datetime
    data = exports()
    monkeypatch.setattr(LocalCsvSourceApplicationService, 'load',
                        lambda self: LoadedLocalExports(data, datetime.now(), tuple(data)))
    def forbidden(*args, **kwargs):
        raise AssertionError('Duty control must never load historical hours')
    monkeypatch.setattr(LocalCsvSourceApplicationService, 'historical_backlog', forbidden)
    result = LocalCsvSourceApplicationService().duty_control(as_of=date(2026,10,24),source_period='2026-2027')
    assert result.dashboard.rows[0].registered == '10'


def test_omitted_mapping_is_not_presented_as_proven_zero():
    result = propose(context())
    ranked = prioritize_candidates(result.assessments, result.cases, date(2026,10,24))
    assert ranked[0].previous_season_backlog == 0  # Neutral ranking only.
    assert not ranked[0].previous_season_considered
    assert 'historische achterstand onbekend' in ranked[0].explanation
