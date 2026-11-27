"""Actual Streamlit candidate order, selected explanations and approval/undo."""
from dataclasses import replace
from datetime import timedelta

import pytest

from dvk.candidate_context import CandidateContextApplicationService
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_ui_v05 import candidate_buttons, candidate_checks, operational_page, refresh_candidate_sources
from test_candidate_context_v05 import context, exports
from test_candidate_person_issues_v05 import rows, write_rows
from test_programma_team_linking_v05 import row
from test_volunteer_planning_integration_v05 import PERIOD, snapshot


@pytest.mark.parametrize('afternoon', [False,True])
def test_real_group_order_ranks_home_facts_and_planning_roundtrip(operational_page, monkeypatch, afternoon):
    app, db, _ = operational_page
    s = next(b.service for b in load_shift_catalog().bindings(PERIOD)
             if b.service.starts_at.weekday()==5
             and (b.service.starts_at.hour>=13 if afternoon else b.service.starts_at.hour<12))
    teams = ['O17-1','Senioren','Away','None','OtherDay','MO15']
    if not afternoon:
        teams.append('O18-1')
    members = [dict(pid=f'M{i}',born='01-01-2012' if i in (1,6,7) else '01-01-1990',team=team,number=str(i))
               for i,team in enumerate(teams,1)]
    data = exports(members=members,hours=[(f'M{i}',10 if i>2 else i,0,0,0,10 if i>2 else i) for i in range(1,len(teams)+1)])
    team_rows = rows(data,'teams')
    team_rows[4]['Speeldag'] = 'Algemeen/Zondag'
    # A second registration must not create a second candidate for M6.
    team_rows.append(dict(team_rows[5],Team='Extra'))
    write_rows(data,'teams',team_rows)
    matches = []
    fixtures = [('O17-1','home',s.starts_at),
                            ('Senioren','home',s.ends_at),
                            ('Away','away',s.ends_at),
                            ('MO15','home',s.starts_at-timedelta(hours=2))]
    if not afternoon:
        fixtures.append(('O18-1', 'home', s.starts_at - timedelta(minutes=30)))
    for name,side,start in fixtures:
        values = dict(thuisteam='CKC '+name,wedstrijddatum=start.isoformat(),wedstrijdcode=name)
        if side=='away':
            values.update(thuisteam='Other',uitteam='CKC '+name,
                          thuisteamclubrelatiecode='OTHER',uitteamclubrelatiecode='BBDZ08H')
        matches.append(row(**values))
    ctx = replace(context(data,matches),period=PERIOD)
    monkeypatch.setattr(CandidateContextApplicationService,'load',lambda *a,**k: ctx)
    refresh_candidate_sources(app)
    app.session_state['selected_service_id'] = s.service_id
    app.run()
    assert not app.exception
    # M5 is BL-20 and must not be offered while enough regular candidates exist.
    expected = ['M2','M4','M6','M3'] if afternoon else ['M1','M7','M2','M4','M6','M3']
    names = ['Synthetisch lid ' + pid for pid in expected]
    assert [button.label for button in candidate_buttons(app)] == names
    before = snapshot(db)
    for index, pid in enumerate(expected):
        candidate_buttons(app)[index].click().run()
        assert any(f'Rang {index + 1}' in item.value for item in app.caption)
        if pid == 'M1':
            assert any('Aftrap tijdens de dienst geeft voorrang' in item.value for item in app.markdown)
        if pid == 'M7':
            assert any('Aftrap vóór de dienst geeft lagere prioriteit' in item.value for item in app.markdown)
        if pid in {'M1', 'M7', 'M6'}:
            assert any('Wedstrijd van kandidaat' in item.value for item in app.info)
        if pid == 'M6':
            assert any('Jeugdteam met een niet-overlappende thuiswedstrijd' in item.value for item in app.markdown)
    assert snapshot(db) == before
    candidate_checks(app)[expected.index('M6')].check().run()
    app.button(key='planner-assign').click().run()
    assert not app.exception and snapshot(db) != before
    assert 'Synthetisch lid M6' not in [button.label for button in candidate_buttons(app)]
    next(button for button in app.button if (button.key or '').startswith('planner-undo-duty-')).click().run()
    assert not app.exception
    assert [button.label for button in candidate_buttons(app)] == names
