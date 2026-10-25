"""Operational source connection; every person and HTTP response is synthetic."""
import csv
import io
import json
import ssl
from dataclasses import replace
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from zoneinfo import ZoneInfo

import pytest

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.planning import PlanningPeriod
from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.programma_client import ProgrammaFetchError, SportlinkProgrammaClient
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_model import DutyService
from test_programma_client_v04 import FakeResponse
from test_programma_team_linking_v05 import row

DAY = date(2026, 10, 24)
PERIOD = PlanningPeriod(DAY, DAY + timedelta(days=6))
IDENTITY = Identity('synthetic-planner', 'Planner', frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL}))
TZ = ZoneInfo('Europe/Amsterdam')


def csv_bytes(fields, rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fields, delimiter=';')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue().encode('utf-8-sig')


def exports(*, members=None, functions=(), hours=None):
    members = members or [dict(pid='M1', born='01-01-1990', team='O17-1', number='17')]
    member_rows = [{'Rel. code': m['pid'], 'Naam': 'Synthetisch lid ' + m['pid'], 'Geb.dat.': m['born'],
                    'Lidstatus': 'Definitief', 'Lidsoort': 'Bondslid', 'Status lidmaatschap': '',
                    'Postcode': '8000AA', 'Huisnummer': m.get('number', '17'), 'Toevoeging': ''} for m in members]
    team_rows = [{'Rel. code': m['pid'], 'Team': m['team'], 'Teamsoort': 'Bond',
                  'Teamrol': 'Teamspeler', 'Spelend lid': 'Ja', 'Speeldag': 'Zaterdag'} for m in members]
    hours = hours if hours is not None else [(m['pid'], 10, 0, 0, 0, 10) for m in members]
    hour_fields = ['Relatiecode', 'Verplichte punten', 'Gecorrigeerde punten', 'Voldaan', 'Nog ingedeeld', 'Niet ingedeeld']
    return {'leden': csv_bytes(list(member_rows[0]), member_rows),
            'teams': csv_bytes(list(team_rows[0]), team_rows),
            'functies': csv_bytes(['Rel. code', 'Functie'], functions),
            'commissies': csv_bytes(['Rel. code', 'Commissie', 'Functie'], []),
            'vrijwilligers_periode': csv_bytes(hour_fields, [dict(zip(hour_fields, values)) for values in hours])}


def service(hour=11):
    start = datetime(2026, 10, 24, hour, tzinfo=TZ)
    return DutyService('S-SYNTHETIC', 'Bardienst', start, start + timedelta(hours=3), 'Kantine', 1)


def need(s):
    return StaffingNeed(s.service_id, 1, 4, 0, 1, 4)


def factory(payload, sleeps=None):
    def make(adapter):
        return SportlinkProgrammaClient(adapter, opener=lambda *a, **k: FakeResponse(payload),
                                        sleeper=(sleeps.append if sleeps is not None else lambda _: None))
    return make


def context(data=None, rows=None, *, client_factory=None):
    return CandidateContextApplicationService(IDENTITY).load(
        period=PERIOD, source_period='2026-2027', client_id='synthetic',
        exports=exports() if data is None else data,
        client_factory=client_factory or factory(json.dumps(rows or []).encode()))


def propose(ctx, slot=None):
    slot = slot or service()
    return CandidateContextApplicationService(IDENTITY).propose(
        ctx, service=slot, need=need(slot), planning_app=PlanningApplicationService(IDENTITY),
        proposal_run_id='synthetic-run')


@pytest.mark.parametrize('payload', [b'[]', b'{"items":[]}', b'[{"wedstrijdcode":"synthetic"}]'])
def test_valid_list_and_empty_list_are_success_without_retries(payload):
    waits = []
    client = factory(payload, waits)(SportlinkProgrammaAdapter(club_relation_code='BBDZ08H'))
    result = client.fetch_rows(client_id='synthetic')
    assert isinstance(result.rows, tuple)
    assert (client.stats.calls, client.stats.retries, client.stats.failures) == (1, 0, 0)
    assert not waits


@pytest.mark.parametrize('payload', [b'', b'{}', b'{"error":"synthetic"}', b'{"error":"synthetic","items":[]}',
                                     b'{"items":null}', b'null', b'not-json', b'[null]', b'["text"]'])
def test_invalid_response_is_explicit_and_not_an_empty_match_list(payload):
    client = factory(payload)(SportlinkProgrammaAdapter(club_relation_code='BBDZ08H'))
    with pytest.raises(ProgrammaFetchError):
        client.fetch_rows(client_id='synthetic')
    assert client.stats.failures == 1
    assert client.stats.retries == 0  # Rooster2 also does not retry invalid JSON.


@pytest.mark.parametrize('failure', [TimeoutError(), URLError('synthetic'),
                                     HTTPError('https://synthetic.invalid/?secret=private', 503, '', {}, None)])
def test_transport_failure_is_retried_and_success_is_normal_context(failure):
    waits, calls = [], []
    def make(adapter):
        def opener(*a, **k):
            calls.append(1)
            if len(calls) < 3:
                raise failure
            return FakeResponse(b'[]')
        return SportlinkProgrammaClient(adapter, opener=opener, sleeper=waits.append)
    ctx = context(client_factory=make)
    assert ctx.error is None and ctx.program.matches == ()
    assert waits == [1.5, 1.5]
    assert (ctx.stats.calls, ctx.stats.retries, ctx.stats.failures) == (1, 2, 0)
    assert propose(ctx).planned


def test_definitive_failure_is_visible_and_proposals_are_blocked_without_request_details():
    waits = []
    def make(adapter):
        def opener(*a, **k):
            raise URLError('synthetic private URL and response')
        return SportlinkProgrammaClient(adapter, opener=opener, sleeper=waits.append)
    ctx = context(client_factory=make)
    assert 'Programma API niet beschikbaar' in ctx.error
    assert 'private' not in ctx.error
    assert (ctx.stats.calls, ctx.stats.retries, ctx.stats.failures) == (1, 3, 1)
    assert waits == [1.5] * 3
    with pytest.raises(CandidateSourceError):
        propose(ctx)


def test_ssl_failure_is_not_retried_like_rooster2():
    waits = []
    def opener(*a, **k):
        raise URLError(ssl.SSLError('synthetic certificate'))
    client = SportlinkProgrammaClient(SportlinkProgrammaAdapter(club_relation_code='BBDZ08H'),
                                     opener=opener, sleeper=waits.append)
    with pytest.raises(ProgrammaFetchError, match='SSL'):
        client.fetch_rows(client_id='synthetic')
    assert not waits and client.stats.failures == 1


@pytest.mark.parametrize('born,side,kickoff,eligible,preference,category', [
    ('01-01-1990', 'HOME', 11, False, 'none', 'member'),
    ('01-01-2012', 'HOME', 11, True, 'preferred', 'parent_guardian'),
    ('01-01-1990', 'HOME', 15, True, 'preferred', 'member'),
    ('01-01-1990', 'AWAY', 11, False, 'none', 'member'),
    ('01-01-2012', 'AWAY', 11, False, 'none', 'parent_guardian'),
    ('01-01-1990', 'AWAY', 15, True, 'avoid', 'member'),
])
def test_existing_senior_youth_and_parent_match_rules(born, side, kickoff, eligible, preference, category):
    data = exports(members=[dict(pid='M1', born=born, team='O17-1')])
    match = row(wedstrijddatum=f'2026-10-24T{kickoff:02}:00:00+0200')
    if side == 'AWAY':
        match.update(thuisteamclubrelatiecode='OTHER', uitteamclubrelatiecode='BBDZ08H', uitteam='CKC O17-1')
    result = propose(context(data, [match]))
    assessment, = result.assessments
    assert assessment.eligible is eligible
    assert assessment.preference == preference
    assert assessment.executor_category == category
    assert assessment.team_id == 'O17-1'
    assert bool(result.planned) is eligible


def test_source_v05_qualification_is_used_without_rewriting_raw_membership(monkeypatch):
    def legacy_must_not_run(*a, **k):
        raise AssertionError('legacy task duty was called')
    monkeypatch.setattr('dvk.candidate_selection.derive_duty_qualification', legacy_must_not_run)
    ctx = context()
    result = propose(ctx)
    assert result.cases[0].membership.status == 'Definitief'
    expectation = result.controls[0].expectation
    assert expectation.policy_version == 'ckc-v05-round2'
    assert result.cases[0].context['duty_expectation'] == expectation
    assert result.planned[0].proposal.E == 10


def test_source_family_rule_selects_oldest_minor_without_parent_relationship_guess():
    members = [dict(pid='OLD', born='01-01-2010', team='O17-1'),
               dict(pid='YOUNG', born='01-01-2013', team='O17-1')]
    result = propose(context(exports(members=members)))
    assert [item.proposal.person_id for item in result.planned] == ['OLD']
    assert not result.cases[0].relationships
    assert next(c for c in result.controls if c.person_id == 'YOUNG').expectation.status == 'vrijgesteld'


def test_youth_weekend_after_1230_is_still_excluded():
    result = propose(context(exports(members=[dict(pid='M1', born='01-01-2012', team='O17-1')])), service(13))
    assert not result.planned
    assert result.assessments[0].match_relation == 'youth_weekend_after_1230'


def test_real_abcd_positions_and_existing_priority_without_fictitious_backlog():
    members = [dict(pid='LOW', born='01-01-1990', team='O17-1', number='1'),
               dict(pid='HIGH', born='01-01-1990', team='O17-1', number='2')]
    data = exports(members=members, hours=[('LOW', 10, 1, 2, 3, 4), ('HIGH', 10, 0, 0, 0, 10)])
    result = propose(context(data))
    assert [(p.person_id, p.remaining_hours) for p in result.priorities] == [('HIGH', 10), ('LOW', 4)]
    assert all(p.previous_season_backlog == 0 and not p.previous_season_considered for p in result.priorities)
    assert all('BL-03' in ' '.join(p.explanation) for p in result.priorities)
    low = next(p.proposal for p in result.planned if p.proposal.person_id == 'LOW')
    assert (low.A, low.B, low.C, low.D, low.E) == (10, 1, 2, 3, 4)


@pytest.mark.parametrize('data', [exports(functions=[{'Rel. code': 'M1', 'Functie': 'Onbekend synthetisch'}]),
                                 exports(members=[dict(pid='M1', born='', team='O17-1')])])
def test_uncertain_source_duty_does_not_create_a_proposal(data):
    result = propose(context(data))
    assert not result.planned
    assert result.controls[0].status == 'niet betrouwbaar beoordeelbaar'


def test_duplicate_hours_do_not_choose_a_record():
    result = propose(context(exports(hours=[('M1', 10, 0, 0, 0, 10)] * 2)))
    assert not result.planned
    assert any(s.code == 'AMBIGUOUS_DUTY_POSITION' for s in result.controls[0].signals)


@pytest.mark.parametrize('bad_row', [row(thuisteam='CKC Onbekend'), row(wedstrijddatum='invalid')])
def test_unresolved_team_or_datetime_blocks_partial_program_context(bad_row):
    ctx = context(rows=[row(wedstrijddatum='2026-10-24T16:00:00+0200'), bad_row])
    assert ctx.error
    with pytest.raises(CandidateSourceError):
        propose(ctx)


def test_incomplete_csv_import_does_not_produce_a_context():
    data = exports()
    del data['teams']
    with pytest.raises(CandidateSourceError):
        context(data)
    data = exports()
    data['leden'] += b'extra;broken;row\n'
    with pytest.raises(CandidateSourceError):
        context(data)


def test_invalid_csv_hours_exclude_the_person_and_keep_diagnostics():
    # PR #44 follow-up: person issues no longer block the entire source.
    ctx = context(exports(hours=[('M1', 10, 0, 0, 0, 999)]))
    assert ctx.error is None and ctx.signal_counts['DUTY_REMAINING_MISMATCH'] == 1
    result = propose(ctx)
    assert not result.planned
    assert result.controls[0].status == 'niet betrouwbaar beoordeelbaar'


def test_different_period_or_hours_season_cannot_reuse_a_candidate_context():
    ctx = context()
    with pytest.raises(CandidateSourceError):
        propose(replace(ctx, period=PlanningPeriod(date(2026, 11, 1), date(2026, 11, 2))))
    with pytest.raises(CandidateSourceError):
        propose(replace(ctx, source_period='2025-2026'))


def test_default_paths_use_existing_import_boundary_without_real_files(monkeypatch):
    observed = []
    data = exports()
    def read(dataset):
        observed.append(dataset)
        return data[dataset].decode('utf-8-sig')
    monkeypatch.setattr('dvk.candidate_context.read_export_text', read)
    ctx = CandidateContextApplicationService(IDENTITY).load(
        period=PERIOD, source_period='2026-2027', client_id='synthetic', client_factory=factory(b'[]'))
    assert set(observed) == set(data)
    assert propose(ctx).planned


def test_actual_proposal_can_be_human_approved_and_undone_without_changing_source(tmp_path):
    from dvk.persistence import SQLiteDatabase
    from dvk.planning_session import PlanningSessionApplicationService
    db = SQLiteDatabase(tmp_path / 'synthetic.sqlite')
    ctx = context()
    slot = service()
    with db.unit_of_work() as uow:
        PlanningSessionApplicationService(uow, IDENTITY).start(PERIOD)
        result = CandidateContextApplicationService(IDENTITY).propose(
            ctx, service=slot, need=need(slot), planning_app=PlanningApplicationService(IDENTITY, uow=uow),
            proposal_run_id='test')
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()
        chosen = result.planned[0].proposal
        approved, = ProposalDecisionApplicationService(IDENTITY, uow=uow).approve_many(
            ((chosen, result.cases[0], 'synthetic-assignment'),), slot, need(slot))
        assert approved.assignment.person_id == 'M1'
    with db.unit_of_work() as uow:
        assert len(PlanningApplicationService(IDENTITY, uow=uow).active_planning()) == 1
        ProposalDecisionApplicationService(IDENTITY, uow=uow).undo('synthetic-assignment')
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()
    assert ctx.source.duty_records[0].position.D == 0


def test_v05_function_and_household_exemption_are_preserved():
    data = exports(members=[dict(pid='M1', born='01-01-1990', team='O17-1'),
                            dict(pid='M2', born='01-01-1991', team='O17-1')],
                   functions=[{'Rel. code': 'M2', 'Functie': 'Trainer Senioren'}])
    result = propose(context(data))
    assert not result.planned
    assert all(c.expectation.status == 'vrijgesteld' for c in result.controls)
    assert any(g.code == 'household_function' for g in result.controls[0].expectation.grounds)


def test_first_match_behavior_is_preserved_without_reordering():
    conflict = row(wedstrijddatum='2026-10-24T11:00:00+0200', wedstrijdcode='first')
    later = row(wedstrijddatum='2026-10-24T18:00:00+0200', wedstrijdcode='second')
    assert not propose(context(rows=[conflict, later])).planned
    assert propose(context(rows=[later, conflict])).planned


def test_first_team_membership_behavior_is_preserved():
    data = exports()
    fields = ['Rel. code', 'Team', 'Teamsoort', 'Teamrol', 'Spelend lid', 'Speeldag']
    rows = [{'Rel. code': 'M1', 'Team': name, 'Teamsoort': 'Bond', 'Teamrol': 'Teamspeler',
             'Spelend lid': 'Ja', 'Speeldag': 'Zaterdag'} for name in ('Senioren', 'O17-1')]
    data['teams'] = csv_bytes(fields, rows)
    match = row(wedstrijddatum='2026-10-24T11:00:00+0200')
    result = propose(context(data, [match]))
    assert result.assessments[0].team_id == 'Senioren'
    assert result.planned
    data['teams'] = csv_bytes(fields, rows[::-1])
    assert not propose(context(data, [match])).planned


def test_no_extra_program_count_or_period_completeness_gate():
    # The accepted trust decision: only technically received facts are used.
    ctx = context(rows=[row(wedstrijddatum='2026-12-24T18:00:00+0100')])
    assert ctx.error is None
    assert propose(ctx).planned
    # A complete-looking row count is not a DVK completeness requirement either.
    ctx = context(rows=[row(wedstrijdcode=str(i), wedstrijddatum='2026-12-24T18:00:00+0100') for i in range(500)])
    assert ctx.error is None and propose(ctx).planned


def test_invalid_season_is_an_explicit_source_error():
    with pytest.raises(CandidateSourceError, match='seizoen'):
        CandidateContextApplicationService(IDENTITY).load(
            period=PERIOD, source_period='', client_id='synthetic', exports=exports())


def test_source_context_requires_view_planning_permission():
    from dvk.security import AuthorizationError
    app = CandidateContextApplicationService(Identity('unprivileged', 'Geen toegang', frozenset()))
    with pytest.raises(AuthorizationError):
        app.load(period=PERIOD, source_period='2026-2027', client_id='synthetic', exports=exports())


def test_explicit_qualification_remains_person_bound_and_false_excludes():
    from dvk.candidate_selection import assess_candidate
    from dvk.model import DutyQualification
    result = propose(context())
    case = result.cases[0]
    no = DutyQualification('M1', False, 'synthetic-exemption', 'M1')
    assessment = assess_candidate(case, service(), (), (), DAY, qualification=no)
    assert not assessment.eligible and assessment.exclusion_reason == 'synthetic-exemption'
    with pytest.raises(ValueError, match='different person'):
        assess_candidate(case, service(), (), (), DAY, qualification=replace(no, person_id='OTHER'))
