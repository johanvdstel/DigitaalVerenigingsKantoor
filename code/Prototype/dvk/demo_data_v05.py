"""DVK v0.5 integrale demo/testdataset.

Menselijk leesbare verwachting
------------------------------
Kandidaten
* W08P / Senior Grote E / Senioren 1: actuele openstaande uren 7; vorig seizoen 4.
* W07P / Senior Urenpositie / SEN-8: actuele openstaande uren 3; vorig seizoen 2.
* W04P / Jeugdlid Thuis / JO17-1: demo-uren A=10 B=0 C=3 D=1, dus 6 open; vorig seizoen 6.
  De aanvullende urenpositie bestaat alleen in deze integrale v0.5 dataset; W04 zelf blijft ongewijzigd.

Wedstrijden in de gekozen week
* Senioren 1: zaterdag 14:30 thuis.
* SEN-8: zaterdag 12:15 uit.
* JO17-1: zondag 10:30 uit.

Diensten
* Woensdag bar 19:00-22:00, min 2/max 3, 1 bevestigd.
* Zaterdag bar 09:00-13:00, min 3/max 5, 3 bevestigd.
* Zaterdag commissiekamer 12:30-17:00, min 1/max 2, 0 bevestigd.

Verwachte selectiecontext
* Woensdag: alle drie zijn vóór capaciteitsafkapping geschikt; er is geen wedstrijd die dag.
* Zaterdag bar: Senioren 1 is geschikt (thuiswedstrijd pas 14:30); SEN-8 niet
  (uitwedstrijd overlapt); JO17-1 is geschikt (wedstrijd zondag).
* Zaterdag commissiekamer: Senioren 1 niet (thuiswedstrijd overlapt); SEN-8 niet
  (uitwedstrijd overlapt); JO17-1 is geschikt (wedstrijd zondag).

Dit bestand is de gezaghebbende integrale demo-fixture voor de v0.5 UI en end-to-end tests.
De afzonderlijke historische regressiecases (C-, W-, I-, R-, V-cases) blijven daarnaast
hun eigen geaccepteerde bronnen houden en worden vóór v0.6 geconsolideerd in één
regressiecatalogus.
"""
from dataclasses import replace
from datetime import date, datetime, time, timedelta

from .model import SportlinkDutyRegistration
from .planning import PlanningSourceStatus
from .staffing import StaffingNeed
from .workstream_cases import W_CASE_BY_ID
from .workstream_model import DutyService, Match, TeamMembership

DEMO_TEAM_BY_PERSON={"W08P":"Senioren 1","W07P":"SEN-8","W04P":"JO17-1"}
DEMO_PREVIOUS_SEASON_BACKLOG={"W08P":4,"W07P":2,"W04P":6}

def demo_candidate_cases():
    return (
        replace(W_CASE_BY_ID["W08"], description="Senioren 1 — thuiswedstrijd"),
        replace(W_CASE_BY_ID["W07"], description="SEN-8 — uitwedstrijd"),
        replace(W_CASE_BY_ID["W04"], description="JO17-1 — jeugdlid/oudersituatie", sportlink_duty=SportlinkDutyRegistration("W04P",10,0,3,1)),
    )

def demo_team_memberships(service, cases=None):
    cases=cases or demo_candidate_cases()
    return tuple(TeamMembership(c.person.person_id,DEMO_TEAM_BY_PERSON[c.person.person_id],service.starts_at.date()-timedelta(days=60),service.starts_at.date()+timedelta(days=300)) for c in cases)

def demo_previous_season_backlog():
    return dict(DEMO_PREVIOUS_SEASON_BACKLOG)

def demo_planning_data(start: date):
    monday=start-timedelta(days=start.weekday())
    services=(
        DutyService("BAR-WO-1","Bardienst",datetime.combine(monday+timedelta(days=2),time(19)),datetime.combine(monday+timedelta(days=2),time(22)),"Clubhuis",2),
        DutyService("BAR-ZA-1","Bardienst",datetime.combine(monday+timedelta(days=5),time(9)),datetime.combine(monday+timedelta(days=5),time(13)),"Clubhuis",3),
        DutyService("CK-ZA-1","Gastvrouw/heer",datetime.combine(monday+timedelta(days=5),time(12,30)),datetime.combine(monday+timedelta(days=5),time(17)),"Commissiekamer",1),
    )
    needs=(StaffingNeed("BAR-WO-1",2,3,1,1,2),StaffingNeed("BAR-ZA-1",3,5,3,0,2),StaffingNeed("CK-ZA-1",1,2,0,1,2))
    matches=(
        Match("W-001","Senioren 1",datetime.combine(monday+timedelta(days=5),time(14,30)),"home"),
        Match("W-002","SEN-8",datetime.combine(monday+timedelta(days=5),time(12,15)),"away"),
        Match("W-003","JO17-1",datetime.combine(monday+timedelta(days=6),time(10,30)),"away"),
    )
    statuses=(PlanningSourceStatus("Sportlink Wedstrijden",datetime.now()-timedelta(minutes=18),"actueel"),PlanningSourceStatus("Sportlink Diensten",datetime.now()-timedelta(minutes=12),"actueel"),PlanningSourceStatus("Leden- en vrijwilligersgegevens",datetime.now()-timedelta(days=1),"bevestigd"))
    return services,needs,matches,statuses
