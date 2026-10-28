"""Confirmed Iteration 1 contract; exclusively synthetic source data."""
from dataclasses import replace
from datetime import timedelta

import pytest

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.persistence import SQLiteDatabase
from dvk.planning_session import PlanningSessionApplicationService
from dvk.team_matchday import EMERGENCY_MATCHDAY_REASON
from test_candidate_context_v05 import IDENTITY, PERIOD, context, exports, need, propose, service
from test_candidate_person_issues_v05 import data_with_two, rows, write_rows, ids
from test_programma_team_linking_v05 import row


def team_data(days, *, players=None, names=None):
    data = exports(members=[dict(pid=f'M{i}', born='01-01-1990', team='O17-1', number=str(i))
                            for i in range(1, len(days) + 1)])
    teams = rows(data, 'teams')
    for i, (team, day) in enumerate(zip(teams, days)):
        team['Speeldag'] = day
        team['Team'] = names[i] if names else f'Team {i}'
        if players and not players[i]:
            team.update({'Teamrol': 'Trainer', 'Spelend lid': 'Nee'})
    write_rows(data, 'teams', teams)
    return data


def slot(weekday):
    s = service()
    offset = (weekday - s.starts_at.weekday()) % 7
    return replace(s, starts_at=s.starts_at + timedelta(days=offset), ends_at=s.ends_at + timedelta(days=offset))


def plan(data, weekday=5, minimum=1, occupancy=0, maximum=4, planning_app=None):
    s = slot(weekday)
    n = replace(need(s), minimum_staff=minimum, maximum_staff=maximum,
                confirmed_occupancy=occupancy, open_need=max(0, minimum-occupancy),
                remaining_capacity=max(0, maximum-occupancy))
    s = replace(s, required_staff=minimum)
    return CandidateContextApplicationService(IDENTITY).propose(
        context(data), service=s, need=n, planning_app=planning_app or PlanningApplicationService(IDENTITY),
        proposal_run_id='synthetic'), s, n


@pytest.mark.parametrize('weekday,day', [(5,'Algemeen/Zaterdag'),(6,'Algemeen/Zondag')])
def test_own_matchday_regular(weekday, day):
    result, _, _ = plan(team_data([day]), weekday)
    assert result.planned[0].staffing_purpose == 'minimum_coverage'
    assert EMERGENCY_MATCHDAY_REASON not in result.planned[0].proposal.uncertainties


@pytest.mark.parametrize('weekday,other,own', [(5,'Algemeen/Zondag','Algemeen/Zaterdag'),
                                            (6,'Algemeen/Zaterdag','Algemeen/Zondag')])
def test_other_day_only_if_other_suitable_candidates_insufficient(weekday, other, own):
    data = team_data([other, own])
    result, _, _ = plan(data, weekday)
    assert ids(result) == ['M2']
    result, _, _ = plan(data, weekday, minimum=2)
    assert ids(result) == ['M2','M1']
    emergency = result.planned[1]
    assert emergency.staffing_purpose == 'emergency_minimum_coverage'
    assert EMERGENCY_MATCHDAY_REASON in emergency.proposal.uncertainties
    assert not plan(data, weekday, occupancy=1)[0].planned[1:]
    assert ids(plan(team_data([other]), weekday, occupancy=1)[0]) == []


@pytest.mark.parametrize('weekday', [5,6])
@pytest.mark.parametrize('reverse', [False,True])
def test_all_player_memberships_allow_both_days_independent_of_order(weekday, reverse):
    data = team_data(['Algemeen/Zaterdag'])
    teams = rows(data,'teams')
    teams.append(dict(teams[0], Team='Other', Speeldag='Algemeen/Zondag'))
    write_rows(data,'teams',teams[::-1] if reverse else teams)
    assert plan(data,weekday)[0].planned[0].staffing_purpose == 'minimum_coverage'


def test_same_day_multiple_teams_and_nonplaying_roles_and_weekdays():
    data = team_data(['Algemeen/Zaterdag'])
    teams = rows(data,'teams')
    teams.append(dict(teams[0], Team='Other'))
    write_rows(data,'teams',teams)
    assert plan(data,5)[0].planned[0].staffing_purpose == 'minimum_coverage'
    for day in range(5):
        assert plan(data,day)[0].planned[0].staffing_purpose == 'minimum_coverage'
    # A trainer's team does not establish player matchday restriction.
    assert plan(team_data(['Algemeen/Zondag'], players=[False]),5)[0].planned[0].staffing_purpose == 'minimum_coverage'
    data['teams'] = data['teams'].splitlines(keepends=True)[0]
    assert plan(data,6)[0].planned[0].staffing_purpose == 'minimum_coverage'


@pytest.mark.parametrize('day', ['', 'Onbekend', 'Zondag'])
def test_missing_unknown_and_unproven_spelling_block_context(day):
    with pytest.raises(CandidateSourceError, match='Speeldag'):
        context(team_data([day]))


def test_conflicting_team_matchdays_block_but_two_team2_identities_survive():
    data = team_data(['Algemeen/Zaterdag','Algemeen/Zondag'],names=['Same','Same'])
    with pytest.raises(CandidateSourceError,match='tegenstrijdige'):
        context(data)
    data = team_data(['Algemeen/Zaterdag','Algemeen/Zondag'],names=['2','2'])
    ctx = context(data)
    assert {t.team_id for t in ctx.program.team_memberships} == {'2 / Algemeen/Zaterdag','2 / Algemeen/Zondag'}
    # Also validate on propose, so an altered context cannot skip the boundary.
    broken = replace(ctx.source.team_memberships[0],matchday='')
    with pytest.raises(CandidateSourceError,match='Speeldag'):
        propose(replace(ctx, source=replace(ctx.source,team_memberships=(broken,))))


@pytest.mark.parametrize('invalid', ['zero','negative','missing','duplicate','invalid','membership','birth'])
def test_unusable_regular_candidate_does_not_hide_emergency_need(invalid):
    data = team_data(['Algemeen/Zondag','Algemeen/Zaterdag'])
    if invalid in {'membership','birth'}:
        members = rows(data,'leden')
        members[1]['Lidstatus' if invalid=='membership' else 'Geb.dat.'] = 'onbekend'
        write_rows(data,'leden',members)
    else:
        hours = rows(data,'vrijwilligers_periode')
        if invalid == 'missing': hours = hours[:1]
        elif invalid == 'duplicate': hours.append(dict(hours[1]))
        elif invalid == 'invalid': hours[1]['Voldaan'] = 'ongeldig'
        else:
            hours[1].update({'Voldaan': '10' if invalid=='zero' else '12',
                             'Niet ingedeeld': '0' if invalid=='zero' else '-2'})
        write_rows(data,'vrijwilligers_periode',hours)
    result, _, _ = plan(data)
    assert ids(result) == ['M1']
    assert result.planned[0].staffing_purpose == 'emergency_minimum_coverage'


def test_emergency_still_respects_match_conflict_and_maximum_capacity():
    data = team_data(['Algemeen/Zondag'],names=['O17-1'])
    assert not propose(context(data,[row(wedstrijddatum='2026-10-24T11:00:00+0200')])).planned
    assert not plan(data,occupancy=4)[0].planned


def test_policy_uncertainty_and_no_sportlink_duty_remain_separate():
    result = propose(context(exports(functions=[{'Rel. code':'M1','Functie':'Onbekend synthetisch'}])))
    assert ids(result) == ['M1']
    assert result.controls[0].status == 'niet betrouwbaar beoordeelbaar'
    result = propose(context(exports(hours=[('M1',0,0,0,0,0)])))
    assert not result.planned and result.controls[0].expectation.status == 'taakplichtig'


def test_temporary_occupancy_emergency_guard_approval_undo_and_history(tmp_path):
    db = SQLiteDatabase(tmp_path/'synthetic.sqlite')
    data = team_data(['Algemeen/Zondag','Algemeen/Zondag'])
    with db.unit_of_work() as uow:
        PlanningSessionApplicationService(uow,IDENTITY).start(PERIOD)
        result,s,n = plan(data,planning_app=PlanningApplicationService(IDENTITY,uow=uow))
        decisions = ProposalDecisionApplicationService(IDENTITY,uow=uow)
        cases = {c.person.person_id:c for c in result.cases}
        selections = tuple((p.proposal,cases[p.proposal.person_id],f'A{i}') for i,p in enumerate(result.planned))
        assert len(selections)==2 and not uow.temporary_planning.all()
        with pytest.raises(ValueError,match='minimumbezetting'):
            decisions.approve_many(selections,s,n)
        decisions.reject(selections[1][0],selections[1][1],reason_category='other',reason='Synthetic historical decision')
        assert len(plan(data,planning_app=PlanningApplicationService(IDENTITY,uow=uow))[0].planned)==2
        decisions.approve_many(selections[:1],s,n)
    with db.unit_of_work() as uow:
        result,_,_ = plan(data,planning_app=PlanningApplicationService(IDENTITY,uow=uow))
        assert not result.planned  # Temporary occupancy now meets minimum.
        with pytest.raises(ValueError,match='minimumbezetting'):
            ProposalDecisionApplicationService(IDENTITY,uow=uow).approve_many(selections[1:],s,n)
        ProposalDecisionApplicationService(IDENTITY,uow=uow).undo('A0')
        assert len(plan(data,planning_app=PlanningApplicationService(IDENTITY,uow=uow))[0].planned)==2
        assert uow.decisions.get(selections[1][0].proposal_id).decision == 'rejected'  # Historical decisions survive undo.


def test_orphan_team_row_cannot_hide_invalid_or_conflicting_matchday():
    for day in ['', 'Algemeen/Zondag']:
        data = team_data(['Algemeen/Zaterdag'],names=['Same'])
        teams = rows(data,'teams')
        teams.append(dict(teams[0], **{'Rel. code':'ORPHAN','Speeldag':day}))
        write_rows(data,'teams',teams)
        with pytest.raises(CandidateSourceError,match='Speeldag'):
            context(data)


@pytest.mark.parametrize('field,value', [('Teamsoort',''),('Teamsoort','Onbekend'),('Spelend lid','Onbekend')])
def test_ambiguous_player_source_does_not_bypass_filter(field,value):
    data = team_data(['Algemeen/Zondag'])
    teams = rows(data,'teams')
    teams[0][field] = value
    write_rows(data,'teams',teams)
    assert not plan(data)[0].planned


def test_positive_open_hours_without_registered_duty_do_not_create_planning_duty():
    # Negative correction can yield E>0 even when A=0; DVK does not invent duty.
    result = propose(context(exports(hours=[('M1',0,-5,0,0,5)])))
    assert result.controls[0].expectation.status == 'taakplichtig'
    assert not result.planned


def test_temporarily_unavailable_regular_person_does_not_mask_minimum_shortage(tmp_path):
    from dvk.planning_workqueue import TemporaryPlanning
    from dvk.workstream_model import DutyAssignment
    db = SQLiteDatabase(tmp_path/'synthetic.sqlite')
    data = team_data(['Algemeen/Zondag','Algemeen/Zaterdag'])
    with db.unit_of_work() as uow:
        s = slot(5)
        other = replace(s,service_id='OTHER')
        uow.temporary_planning.add(TemporaryPlanning(
            DutyAssignment('A','P','OTHER','M2','member',3,'synthetic'),other))
        uow.commit()
        result,_,_ = plan(data,planning_app=PlanningApplicationService(IDENTITY,uow=uow))
        assert ids(result)==['M1']
        assert result.planned[0].staffing_purpose=='emergency_minimum_coverage'


@pytest.mark.parametrize('dataset,field,code,label', [
    ('functies', 'Begindatum', 'INVALID_FUNCTION_DATE', 'Ongeldige geldigheidsdatum van een functie'),
    ('functies', 'Einddatum', 'INVALID_FUNCTION_DATE', 'Ongeldige geldigheidsdatum van een functie'),
    ('commissies', 'Begindatum', 'INVALID_COMMITTEE_START_DATE', 'Ongeldige begindatum van een commissie'),
    ('commissies', 'Einddatum', 'INVALID_COMMITTEE_END_DATE', 'Ongeldige einddatum van een commissie'),
])
def test_policy_date_error_preserves_candidate_and_duty_control(dataset, field, code, label):
    from dvk.duty_control_presenter import load_duty_dashboard
    data = exports()
    write_rows(data, dataset, [{'Rel. code': 'M1', 'Functie': 'Trainer Senioren',
                               'Commissie': 'Synthetische commissie', field: 'ongeldige datum'}])
    ctx = context(data)
    result = propose(ctx)
    assert ids(result) == ['M1']
    assert any(s.code == code and s.severity == 'ERROR' for s in ctx.source.signals)
    assert any(s.code == code for s in result.controls[0].signals)
    assert result.controls[0].status == 'niet betrouwbaar beoordeelbaar'
    dashboard = load_duty_dashboard(data, as_of=service().starts_at.date(),
                                    source_period=ctx.source_period, isolate_person_errors=True)
    control = next(r for r in dashboard.rows if r.person_id == 'M1')
    assert control.status == 'niet betrouwbaar beoordeelbaar'
    assert label in control.why
