from datetime import date,datetime,timedelta,time
from dvk.candidate_selection import assess_candidate
from dvk.demo_data_v05 import demo_candidate_cases,demo_previous_season_backlog,demo_team_memberships,demo_planning_data
from dvk.prioritization import prioritize_candidates
from dvk.workstream_cases import TODAY
from dvk.workstream_model import DutyService,Match

def _context():
    m=date(2026,9,14)
    services=(DutyService("BAR-WO-1","Bardienst",datetime.combine(m+timedelta(days=2),time(19)),datetime.combine(m+timedelta(days=2),time(22)),"Clubhuis",2),DutyService("BAR-ZA-1","Bardienst",datetime.combine(m+timedelta(days=5),time(9)),datetime.combine(m+timedelta(days=5),time(13)),"Clubhuis",3),DutyService("CK-ZA-1","Gastvrouw/heer",datetime.combine(m+timedelta(days=5),time(12,30)),datetime.combine(m+timedelta(days=5),time(17)),"Commissiekamer",1))
    matches=(Match("W-001","Senioren 1",datetime.combine(m+timedelta(days=5),time(14,30)),"home"),Match("W-002","SEN-8",datetime.combine(m+timedelta(days=5),time(12,15)),"away"),Match("W-003","JO17-1",datetime.combine(m+timedelta(days=6),time(10,30)),"away"))
    return services,matches,demo_candidate_cases()

def test_demo_population_complete_three_teams():
    services,_,cases=_context(); memberships=demo_team_memberships(services[0],cases)
    assert {x.team_id for x in memberships}=={"Senioren 1","SEN-8","JO17-1"}
    assert all(c.sportlink_duty and c.sportlink_duty.required_hours is not None for c in cases)

def test_weekday_all_three_eligible_before_capacity_cut():
    services,matches,cases=_context(); s=services[0]; memberships=demo_team_memberships(s,cases)
    aa=tuple(assess_candidate(c,s,memberships,matches,TODAY) for c in cases)
    assert {x.person_id for x in aa if x.eligible}=={"W08P","W07P","W04P"}
    pp=prioritize_candidates(tuple(x for x in aa if x.eligible),cases,s.starts_at.date(),demo_previous_season_backlog())
    assert {x.person_id for x in pp}=={"W08P","W07P","W04P"}

def test_saturday_team_context():
    services,matches,cases=_context(); memberships=demo_team_memberships(services[1],cases)
    bar={x.person_id:x for x in (assess_candidate(c,services[1],memberships,matches,TODAY) for c in cases)}
    ck={x.person_id:x for x in (assess_candidate(c,services[2],memberships,matches,TODAY) for c in cases)}
    assert bar["W08P"].eligible and bar["W08P"].match_relation=="home_match_same_day"
    assert not bar["W07P"].eligible and bar["W07P"].match_relation=="away_match_overlaps_service"
    assert bar["W04P"].eligible
    assert not ck["W08P"].eligible and ck["W08P"].match_relation=="home_match_overlaps_service"
    assert not ck["W07P"].eligible and ck["W07P"].match_relation=="away_match_overlaps_service"
    assert ck["W04P"].eligible


def test_central_demo_dataset_contains_all_planning_inputs():
    services, needs, matches, statuses = demo_planning_data(date(2026,9,14))
    assert {s.service_id for s in services} == {"BAR-WO-1","BAR-ZA-1","CK-ZA-1"}
    assert {n.service_id for n in needs} == {"BAR-WO-1","BAR-ZA-1","CK-ZA-1"}
    assert {m.team_id for m in matches} == {"Senioren 1","SEN-8","JO17-1"}
    assert len(statuses) == 3
