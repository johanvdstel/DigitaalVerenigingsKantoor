"""Iteration 9 decisions, including the explicit youth-home fallback addition.

Synthetic members only. Existing duty/executor derivation and source facts stay
separate from the new team-based selection categories.
"""
from dataclasses import replace
from datetime import date, datetime, timedelta
from itertools import permutations

import pytest

from dvk.candidate_selection import assess_candidate, is_youth_team
from dvk.candidate_presenter import priority_explanation
from dvk.prioritization import prioritize_candidates
from dvk.proposals import create_assignment_proposal
from dvk.recommendation_planner import plan_recommendations
from dvk.workstream_cases import W_CASE_BY_ID
from dvk.workstream_model import DutyService, Match, TeamMembership


def slot(hour=11, minute=0):
    start = datetime(2026, 10, 24, hour, minute)
    return DutyService('I9', 'bardienst', start, start + timedelta(hours=3), 'Kantine', 1)


def member(pid='I9', born=date(2012, 1, 1), hours=10):
    template = W_CASE_BY_ID['W08']
    return replace(template, person=replace(template.person, person_id=pid, birth_date=born),
                   membership=replace(template.membership, person_id=pid),
                   sportlink_duty=replace(template.sportlink_duty, person_id=pid,
                                         required_hours=hours, completed_hours=0, scheduled_hours=0))


def assess(team='O17-1', *, service=None, kickoff=10, side='home', born=date(2012, 1, 1)):
    s = service or slot()
    case = member(born=born)
    match = Match('MATCH-I9', team, s.starts_at.replace(hour=kickoff, minute=0), side)
    a = assess_candidate(case, s, (TeamMembership('I9', team),), (match,), s.starts_at.date())
    return case, s, match, a


@pytest.mark.parametrize('team', ['JO7', 'O9-1', 'JO19-2', 'MO15', 'MO17-2', 'O20', 'JO20-1', 'MO20'])
def test_youth_team_names(team):
    assert is_youth_team(team)


@pytest.mark.parametrize('team', ['O21', 'JO21-1', 'O23', 'MO23', 'CKC 1', 'VR1', 'Zon2', 'JO', 'O200', 'Senioren'])
def test_senior_team_names(team):
    assert not is_youth_team(team)


@pytest.mark.parametrize('born', [date(2012,1,1), date(2008,1,1), date(2006,1,1), date(1990,1,1)])
@pytest.mark.parametrize('team,eligible,group', [('O20',True,'youth_home'), ('O21',False,'none'), ('CKC 1',False,'none')])
def test_group_uses_team_and_never_individual_age(born, team, eligible, group):
    _, _, _, a = assess(team, born=born)
    assert (a.eligible,a.preference) == (eligible,group)


@pytest.mark.parametrize('minute,eligible,group', [(29,True,'youth_home'), (30,False,'none'), (31,False,'none')])
def test_start_boundary_and_service_crossing_1230(minute, eligible, group):
    _, s, _, a = assess(service=slot(12,minute),kickoff=12)
    assert s.ends_at.hour > 12
    assert (a.eligible,a.preference) == (eligible,group)


@pytest.mark.parametrize('hour,minute', [(12,29), (12,30), (12,31)])
def test_senior_home_nonoverlap_primary_on_either_side_of_boundary(hour,minute):
    _, _, _, a = assess('O23', service=slot(hour,minute),kickoff=9)
    assert a.eligible and a.preference == 'preferred'


@pytest.mark.parametrize('hour,minute,kickoff', [(9,0,12), (12,29,9), (12,30,9), (12,31,9), (14,0,12)])
def test_youth_home_nonoverlap_is_neutral_but_retains_actual_match(hour,minute,kickoff):
    case, s, match, a = assess(service=slot(hour,minute),kickoff=kickoff)
    assert a.eligible and a.preference == 'neutral'
    assert a.home_away == 'home' and a.match_relation == 'home_match_same_day'
    ranked, = prioritize_candidates((a,),(case,),s.starts_at.date())
    proposal = create_assignment_proposal('I9-P',s,case,a,ranked,(match,))
    assert proposal.match_starts_at == match.starts_at
    assert proposal.team_id == 'O17-1' and proposal.home_away == 'home'
    explanation = priority_explanation(proposal)
    assert 'Jeugdteam met een niet-overlappende thuiswedstrijd' in explanation
    assert 'het team speelt wel thuis' in explanation


@pytest.mark.parametrize('hour,kickoff', [(9,12), (14,12)])
@pytest.mark.parametrize('team', ['O17-1','O23'])
@pytest.mark.parametrize('side', ['home','away'])
def test_exact_touching_boundaries_do_not_conflict(hour,kickoff,team,side):
    _, _, _, a = assess(team,service=slot(hour),kickoff=kickoff,side=side)
    assert a.eligible


@pytest.mark.parametrize('team', ['O17-1','O23'])
@pytest.mark.parametrize('side', ['home','away'])
def test_afternoon_overlap_excludes_all_teams(team,side):
    _, _, _, a = assess(team,service=slot(13),kickoff=12,side=side)
    assert not a.eligible


@pytest.mark.parametrize('group', ['youth_home', 'preferred', 'neutral'])
def test_group_dominates_hours(group):
    s = slot()
    cases = (member('A',hours=1),member('B',hours=100))
    base = assess_candidate(cases[0],s,(),(),s.starts_at.date())
    groups = ['youth_home','preferred','neutral','avoid']
    assessments = (replace(base,person_id='A',preference=group),
                   replace(base,person_id='B',preference=groups[groups.index(group)+1]))
    assert [p.person_id for p in prioritize_candidates(assessments,cases,s.starts_at.date(),{'B':999})] == ['A','B']


@pytest.mark.parametrize('month',range(1,13))
def test_full_season_order_hours_then_positive_history_then_person_key(month):
    s = slot()
    cases = (member('HIGH',hours=11),member('HISTORY'),member('A'),member('B'),member('NEG'),member('UNKNOWN'))
    base = assess_candidate(cases[0],s,(),(),s.starts_at.date())
    assessments = tuple(replace(base,person_id=c.person.person_id) for c in cases)
    original = tuple(c.sportlink_duty for c in cases)
    ranked = prioritize_candidates(assessments[::-1],cases,date(2027,month,1),{'HIGH':0,'HISTORY':8,'A':0,'B':0,'NEG':-4})
    assert [p.person_id for p in ranked] == ['HIGH','HISTORY','A','B','NEG','UNKNOWN']
    assert ranked[1].previous_season_backlog == 8
    assert tuple(c.sportlink_duty for c in cases) == original
    assert 'geen positieve historische achterstand' in ranked[-2].explanation
    assert 'historische achterstand onbekend' in ranked[-1].explanation


def test_other_weekend_is_last_group_even_with_more_hours_and_better_match_group():
    s = slot()
    cases = (member('REG',hours=1),member('OTHER',hours=100))
    base = assess_candidate(cases[0],s,(),(),s.starts_at.date())
    ranked = prioritize_candidates((replace(base,person_id='OTHER',preference='youth_home'),
                                    replace(base,person_id='REG',preference='avoid')),
                                   cases,s.starts_at.date(),other_weekend_person_ids=frozenset({'OTHER'}))
    assert [(p.person_id,p.rank) for p in ranked] == [('REG',1),('OTHER',2)]


@pytest.mark.parametrize('conflict', [False,True])
def test_all_team_memberships_and_matches_independent_of_source_order(conflict):
    case, s, match, _ = assess('O23',kickoff=16)
    teams = (TeamMembership('I9','O23'),TeamMembership('I9','O17-1'),TeamMembership('I9','Other'))
    matches = (match,Match('Y','O17-1',s.starts_at,'home'),
               Match('SECOND','O23',s.starts_at if conflict else s.starts_at.replace(hour=20),'away'))
    for team_order in permutations(teams):
        for match_order in permutations(matches):
            a = assess_candidate(case,s,team_order,match_order,s.starts_at.date())
            assert a.eligible is not conflict
            if not conflict:
                assert a.team_id == 'O17-1' and a.preference == 'youth_home'
            else:
                assert a.match_relation == 'away_match_overlaps_service'


def test_inactive_team_registration_cannot_cause_conflict():
    case, s, match, _ = assess('O23',kickoff=11)
    memberships = (TeamMembership('I9','O23',end_date=s.starts_at.date()-timedelta(days=1)),)
    assert assess_candidate(case,s,memberships,(match,),s.starts_at.date()).eligible


def test_recommendation_equality_keeps_different_groups_separate():
    s = slot()
    cases = (member('A'),member('B'))
    base = assess_candidate(cases[0],s,(),(),s.starts_at.date())
    ranked = prioritize_candidates((replace(base,person_id='B',preference='preferred'),
                                    replace(base,person_id='A',preference='youth_home')),cases,s.starts_at.date())
    assert [p.person_id for p in plan_recommendations(ranked,(s,)).recommended] == ['A']


def test_recommendation_does_not_treat_bl20_as_equal_to_regular_group():
    s = slot()
    cases = (member('A'),member('B'))
    base = assess_candidate(cases[0],s,(),(),s.starts_at.date())
    ranked = prioritize_candidates((replace(base,person_id='A'),replace(base,person_id='B')),
                                   cases,s.starts_at.date(),other_weekend_person_ids=frozenset({'B'}))
    assert [p.person_id for p in plan_recommendations(ranked,(s,)).recommended] == ['A']


def test_proposal_match_time_follows_selected_match_not_source_order():
    case, s, overlap, _ = assess(kickoff=11)
    later = replace(overlap,match_id='LATER',starts_at=s.ends_at)
    for matches in ((overlap,later),(later,overlap)):
        a = assess_candidate(case,s,(TeamMembership('I9','O17-1'),),matches,s.starts_at.date())
        priority, = prioritize_candidates((a,),(case,),s.starts_at.date())
        proposal = create_assignment_proposal('I9-P',s,case,a,priority,matches)
        assert proposal.match_starts_at == overlap.starts_at
        assert proposal.match_relation == 'home_match_overlaps_service'


def test_bl20_ranks_offer_only_shortage_and_keep_regular_away_ahead():
    from dvk.candidate_context import CandidateContextApplicationService
    from dvk.application_services import PlanningApplicationService
    from dvk.team_matchday import EMERGENCY_MATCHDAY_REASON
    from test_candidate_context_v05 import IDENTITY, context, need, service
    from test_iteration1_candidates_v05 import team_data
    from test_candidate_person_issues_v05 import rows, write_rows
    from test_programma_team_linking_v05 import row
    data = team_data(['Algemeen/Zondag','Algemeen/Zaterdag'],names=['OtherDay','Senioren'])
    hours = rows(data,'vrijwilligers_periode')
    hours[1].update({'Voldaan':'9','Niet ingedeeld':'1'})
    write_rows(data,'vrijwilligers_periode',hours)
    match = row(thuisteam='Other',uitteam='CKC Senioren',
                thuisteamclubrelatiecode='OTHER',uitteamclubrelatiecode='BBDZ08H',
                wedstrijddatum='2026-10-24T18:00:00+0200')
    ctx = context(data,[match])
    for minimum,expected in ((1,['M2']),(2,['M2','M1'])):
        s = replace(service(),required_staff=minimum)
        n = replace(need(s),minimum_staff=minimum,open_need=minimum)
        result = CandidateContextApplicationService(IDENTITY).propose(
            ctx,service=s,need=n,planning_app=PlanningApplicationService(IDENTITY),proposal_run_id='I9')
        assert [p.proposal.person_id for p in result.planned] == expected
        assert [p.proposal.priority_rank for p in result.planned] == list(range(1,len(expected)+1))
        if minimum==2:
            assert EMERGENCY_MATCHDAY_REASON in result.planned[-1].proposal.uncertainties
