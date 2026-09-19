from dataclasses import replace
from datetime import timedelta
from .model import SportlinkDutyRegistration
from .workstream_cases import W_CASE_BY_ID
from .workstream_model import TeamMembership

DEMO_TEAM_BY_PERSON={"W08P":"Senioren 1","W07P":"SEN-8","W04P":"JO17-1"}
DEMO_PREVIOUS_SEASON_BACKLOG={"W08P":4,"W07P":2,"W04P":6}

def demo_candidate_cases():
    return (
        replace(W_CASE_BY_ID["W08"], title="Senioren 1 — thuiswedstrijd"),
        replace(W_CASE_BY_ID["W07"], title="SEN-8 — uitwedstrijd"),
        replace(W_CASE_BY_ID["W04"], title="JO17-1 — jeugdlid/oudersituatie", sportlink_duty=SportlinkDutyRegistration("W04P",10,0,3,1)),
    )

def demo_team_memberships(service, cases=None):
    cases=cases or demo_candidate_cases()
    return tuple(TeamMembership(c.person.person_id,DEMO_TEAM_BY_PERSON[c.person.person_id],service.starts_at.date()-timedelta(days=60),service.starts_at.date()+timedelta(days=300)) for c in cases)

def demo_previous_season_backlog():
    return dict(DEMO_PREVIOUS_SEASON_BACKLOG)
