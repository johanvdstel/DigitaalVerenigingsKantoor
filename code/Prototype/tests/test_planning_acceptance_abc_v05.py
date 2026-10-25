"""A/B/C synthetic acceptance; D/E intentionally make no product changes."""
from dataclasses import replace
from datetime import date

import pytest

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_context import CandidateContextApplicationService
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.planning_session import PlanningSessionApplicationService
from dvk.sportlink_exports import EXPORT_FILENAMES, export_path
from test_candidate_context_v05 import exports, context, propose, service, need, IDENTITY, PERIOD
from test_candidate_person_issues_v05 import rows, write_rows, data_with_two
from test_candidate_context_ui_v05 import operational_page


def save(data):
    for dataset, value in data.items():
        export_path(dataset).write_bytes(value)


def test_a_rejected_duplicate_rows_keep_names_status_values_and_separate_source_rows():
    data = data_with_two()
    members = rows(data, 'leden')
    members[1].update({'Lidstatus': 'Oud bondslid', 'Afmelddatum': '01-01-2015', 'Email': 'must-not-be-kept@example.invalid'})
    duplicate = dict(members[1], **{'Lidstatus': 'Oud relatie', 'Afmelddatum': '01-01-2023'})
    write_rows(data, 'leden', members + [duplicate])
    ctx = context(data)
    details = [d for d in ctx.diagnostic_details if d.code == 'CONFLICTING_DUPLICATE_MEMBERSHIP']
    assert len(details) == 2
    assert [d.row_number for d in details] == [2, 3]
    assert all(d.person_id == 'M2' and d.name == 'Synthetisch lid M2' and d.filename == 'Leden.csv' for d in details)
    assert [dict(d.values)['Afmelddatum'] for d in details] == ['01-01-2015', '01-01-2023']
    assert all('Email' not in dict(d.values) and 'Geb.dat.' not in dict(d.values) for d in details)
    assert [p.proposal.person_id for p in propose(ctx).planned] == ['M1']


def test_a_unknown_status_is_human_readable_and_identified():
    data = data_with_two(); members = rows(data, 'leden')
    members[1]['Lidstatus'] = 'Overschrijving spelactiviteit'; write_rows(data, 'leden', members)
    detail, = [d for d in context(data).diagnostic_details if d.code == 'UNKNOWN_MEMBERSHIP_STATUS']
    assert detail.person_id == 'M2' and detail.name and 'Lidstatus' in detail.description
    assert dict(detail.values)['Lidstatus'] == 'Overschrijving spelactiviteit'


def many():
    members = [dict(pid=f'M{i}', born='01-01-1990', team='O17-1', number=str(i)) for i in range(6)]
    return context(exports(members=members, hours=[(m['pid'], 10, 0, i, 0, 10-i) for i,m in enumerate(members)]))


@pytest.mark.parametrize('capacity', [1, 3])
def test_b_all_candidates_are_ranked_even_beyond_capacity(capacity):
    ctx = many(); slot = service(); staffing = replace(need(slot), maximum_staff=capacity, remaining_capacity=capacity)
    result = CandidateContextApplicationService(IDENTITY).propose(
        ctx, service=slot, need=staffing, planning_app=PlanningApplicationService(IDENTITY), proposal_run_id='test')
    assert [p.proposal.person_id for p in result.planned] == [f'M{i}' for i in range(6)]
    assert [p.proposal.priority_rank for p in result.planned] == list(range(1,7))


@pytest.mark.parametrize('selected,capacity,valid', [(1,3,True), (3,3,True), (4,3,False)])
def test_b_batch_approval_keeps_capacity_and_atomic_guards(tmp_path, selected, capacity, valid):
    ctx = many(); result = propose(ctx); slot = service()
    staffing = replace(need(slot), maximum_staff=capacity, remaining_capacity=capacity)
    db = SQLiteDatabase(tmp_path/'synthetic.sqlite')
    with db.unit_of_work() as uow:
        PlanningSessionApplicationService(uow, IDENTITY).start(PERIOD)
        app = PlanningApplicationService(IDENTITY, uow=uow)
        ids = tuple(p.proposal.person_id for p in result.planned[:selected])
        assert bool(app.selection_problem(person_ids=ids, service=slot, staffing_need=staffing)) is not valid
        cases = {c.person.person_id:c for c in result.cases}
        choices = tuple((p.proposal,cases[p.proposal.person_id],f'A{i}') for i,p in enumerate(result.planned[:selected]))
        if valid:
            assert len(ProposalDecisionApplicationService(IDENTITY,uow=uow).approve_many(choices,slot,staffing)) == selected
        else:
            with pytest.raises(ValueError, match='capacity'):
                ProposalDecisionApplicationService(IDENTITY,uow=uow).approve_many(choices,slot,staffing)
    with db.unit_of_work() as uow:
        assert len(PlanningApplicationService(IDENTITY,uow=uow).active_planning()) == (selected if valid else 0)


def test_c_shared_input_is_read_only_and_explicit_reload_reads_new_bytes():
    data = exports(); save(data)
    app = LocalCsvSourceApplicationService()
    first = app.load()
    expected = {k:v.decode("utf-8-sig").replace("\r\n", "\n").encode() for k,v in data.items()}
    assert first.exports == expected
    assert set(first.filenames) == set(EXPORT_FILENAMES.values())
    changed = dict(data); changed['functies'] += b'M1;Trainer Senioren\r\n'; save(changed)
    second = app.load()
    assert second.loaded_at >= first.loaded_at and second.exports != first.exports
    assert first.exports == expected  # The already loaded snapshot is never silently changed.
    assert all(export_path(k).read_bytes() == v for k,v in changed.items())


@pytest.mark.parametrize('fault', ['missing', 'unreadable', 'structure'])
def test_c_local_errors_are_not_published_as_current(fault, monkeypatch):
    save(exports())
    if fault == 'missing':
        export_path('leden').unlink()
    elif fault == 'unreadable':
        export_path('leden').write_bytes(b'\xff')
    else:
        export_path('leden').write_bytes(b'Wrong header\nvalue\n')
    with pytest.raises(ValueError):
        LocalCsvSourceApplicationService().duty_control(as_of=date(2026,10,24), source_period='2026-2027')


def test_c_ui_failed_duty_refresh_removes_previous_dashboard(tmp_path):
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    save(exports())
    script=tmp_path/'streamlit_app.py'; script.write_text((Path(__file__).parents[1]/'streamlit_app.py').read_text())
    app=AppTest.from_file(str(script),default_timeout=20)
    app.session_state['dvk-screen']='control';app.session_state['duty-control-date']=date(2026,10,24)
    app.run(); assert not app.exception and app.dataframe
    export_path('leden').unlink()
    app.button(key='refresh-duty-sources').click().run()
    assert app.error and not app.dataframe and 'local-duty-control' not in app.session_state
    assert not app.get('file_uploader')


def test_b_ui_rejects_excess_selection_without_writes(operational_page, monkeypatch):
    from dvk.candidate_context import CandidateContextApplicationService
    app,db,_=operational_page
    ctx=replace(many(),period=app.session_state['candidate-context'].period)
    monkeypatch.setattr(CandidateContextApplicationService,'load',lambda *a,**k:ctx)
    app.button(key='load-candidate-sources').click().run()
    choices=[c.key for c in app.checkbox if c.key.startswith('pick-')]
    assert len(choices)==6
    for key in choices:
        app.checkbox(key=key).check().run()
    confirm=next(b for b in app.button if b.label=='Selectie bevestigen')
    assert confirm.disabled
    assert any('meer kandidaten geselecteerd' in w.value for w in app.warning)
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY,uow=uow).active_planning()
