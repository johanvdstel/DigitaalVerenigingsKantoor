"""BL-19 contract, synthetic sources only. No operational data or network."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import date, datetime, time, timedelta, timezone
import json
from threading import Barrier

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import NoShowApplicationService
from dvk.model import Person
from dvk.no_show import MANUAL_DECLARATION, TZ, NoShowEvent, registration_period, season_id
from dvk.no_show_source import NoShowSourceApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.security import AuthorizationError, Identity, Permission
from dvk.shift_catalog import ShiftCatalog, ShiftDefinition, WeeklySlot
from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter
from dvk.vrijwilligers_client import VrijwilligersFetchError, VrijwilligersFetchResult

NOW = datetime(2026, 11, 1, 12, tzinfo=TZ)
IDENTITY = Identity('planner', 'Planner', frozenset({Permission.MANAGE_NO_SHOWS}))
PERSONS = (Person('P1', 'Alex Voorbeeld', sportlink_name='Voorbeeld, A. (Alex)'),
           Person('P2', 'Alex Voorbeeld', sportlink_name='Voorbeeld, B. (Alex)'))
CATALOG = ShiftCatalog((ShiftDefinition('741', 'Bardienst', 4, 1, 2),
                        ShiftDefinition('761', 'Andere bar', 4, 1, 2)),
                       (WeeklySlot(5, time(10), time(14), '741'), WeeklySlot(5, time(10), time(14), '761')))


class Client:
    def __init__(self, payload=None):
        self.payload = payload if payload is not None else {'741': [row()]}
        self.calls = []
        self.fail = False

    def fetch_rows(self, **kwargs):
        self.calls.append(kwargs)
        if self.fail:
            raise VrijwilligersFetchError('Sportlink Vrijwilligers connection failure')
        return VrijwilligersFetchResult(kwargs['task_code'], tuple(self.payload.get(kwargs['task_code'], ())))


def row(start=None, end=None, **changes):
    start = start or NOW - timedelta(days=1, hours=2)
    end = end or start + timedelta(hours=4)
    return dict(naam=PERSONS[0].sportlink_name, datumvanaf=start.isoformat(), datumtot=end.isoformat(), lokatie='CKC') | changes


@pytest.fixture
def db(tmp_path):
    value = SQLiteDatabase(tmp_path / 'bl19.sqlite')
    assert value.initialize() == 13
    return value


def app(uow, now=NOW, identity=IDENTITY):
    return NoShowApplicationService(uow, identity, clock=lambda: now)


def inputs(start=None, end=None, **changes):
    start = start or NOW - timedelta(days=1, hours=2)
    end = end or start + timedelta(hours=4)
    return dict(person_id='P1', persons=PERSONS, catalog=CATALOG, task_code='741', description='',
                start_day=start.date(), start_time=start.time().replace(tzinfo=None),
                end_day=end.date(), end_time=end.time().replace(tzinfo=None), confirmed=True) | changes


def source(client=None):
    return NoShowSourceApplicationService(IDENTITY, client or Client(), 'synthetic', CATALOG, PERSONS)


def test_manual_without_booking_or_session_persists_and_reopens(db):
    with db.unit_of_work() as u:
        assert app(u).register_manual(**inputs(), explanation='historische context').counter == 1
        fact, = u.no_shows.all()
        assert fact.booking is None
        assert fact.manual.declaration == MANUAL_DECLARATION
        assert fact.manual.declaration_confirmed and fact.manual.task_identity_verified
        assert fact.recorded_at == NOW and fact.recorded_by == 'planner'
        assert u.planning_sessions.get() is None
        assert not u.sportlink_bookings.all() and not u.temporary_planning.all()
    with SQLiteDatabase(db.path).unit_of_work() as u:
        assert u.no_shows.all() == (fact,)
        assert app(u).current_state('P1', fact.season).counter == 1


def test_regular_consult_and_confirmation_do_not_publish_planning(db):
    client = Client(); service = source(client)
    consulted = service.consult(NOW)
    assert len(client.calls) == 2
    with db.unit_of_work() as u:
        assert app(u).register_booking(consulted.bookings[0], source=service).counter == 1
        fact, = u.no_shows.all()
        assert fact.booking.provenance.source_system == 'Sportlink'
        assert fact.registration_mode == 'Sportlink'
        assert not u.sportlink_bookings.all() and u.planning_sessions.get() is None
    assert len(client.calls) == 3 and client.calls[-1]['task_code'] == '741'
    assert client.calls[0]['weekoffset'] <= -3


@pytest.mark.parametrize('change', ['gone', 'location', 'person', 'interval', 'failure'])
def test_confirmation_rechecks_source_and_rejects_changed_booking(db, change):
    client = Client(); service = source(client); selected, = service.consult(NOW).bookings
    if change == 'gone': client.payload = {}
    elif change == 'location': client.payload['741'][0]['lokatie'] = 'Andere locatie'
    elif change == 'person': client.payload['741'][0]['naam'] = PERSONS[1].sportlink_name
    elif change == 'interval': client.payload['741'][0]['datumtot'] = (selected.ends_at+timedelta(minutes=1)).isoformat()
    else: client.fail = True
    with db.unit_of_work() as u:
        with pytest.raises((ValueError, VrijwilligersFetchError)):
            app(u).register_booking(selected, source=service)
        assert not u.no_shows.all()
        assert app(u).register_manual(**inputs()).counter == 1


@pytest.mark.parametrize('days,allowed', [(14, True), (0, True), (15, False), (-1, False)])
@pytest.mark.parametrize('mode', ['manual', 'sportlink'])
def test_registration_date_bounds_are_inclusive_and_shared(db, days, allowed, mode):
    start = NOW.replace(hour=10) - timedelta(days=days)
    with db.unit_of_work() as u:
        def register():
            if mode == 'manual': return app(u).register_manual(**inputs(start))
            service = source(Client({'741': [row(start)]}))
            # Passing a previously selected booking still rechecks the current window.
            selected = SportlinkVrijwilligersAdapter().import_rows(task_code='741', rows=[row(start)],
                services=(), imported_at=NOW, persons=PERSONS, planning_definitions=CATALOG.definitions).bookings[0]
            return app(u).register_booking(selected, source=service)
        if allowed: assert register().counter == 1
        else:
            with pytest.raises(ValueError): register()
            assert not u.no_shows.all()


@pytest.mark.parametrize('seconds,allowed', [(-1, False), (0, True), (1, True)])
def test_before_and_at_service_start(db, seconds, allowed):
    start = NOW
    with db.unit_of_work() as u:
        operation = lambda: app(u, start+timedelta(seconds=seconds)).register_manual(**inputs(start))
        if allowed: assert operation().counter == 1
        else:
            with pytest.raises(ValueError, match='dienstaanvang'): operation()


def test_confirmation_clock_after_midnight_rechecks_lower_bound(db):
    selected_at = NOW.replace(hour=23, minute=59)
    start = selected_at.replace(hour=10) - timedelta(days=14)
    with db.unit_of_work() as u:
        assert app(u, selected_at).manual_context(**inputs(start))
        with pytest.raises(ValueError, match='14 kalenderdagen'):
            app(u, selected_at+timedelta(minutes=2)).register_manual(**inputs(start))


@pytest.mark.parametrize('start,end', [
    (datetime(2026, 10, 31, 23, tzinfo=TZ), datetime(2026, 11, 1, 2, tzinfo=TZ)),
    (datetime(2026, 10, 31, 8, tzinfo=TZ), datetime(2026, 10, 31, 9, tzinfo=TZ)),
])
def test_night_and_actual_non_catalog_times_remain_exact(db, start, end):
    with db.unit_of_work() as u:
        app(u).register_manual(**inputs(start, end))
        fact, = u.no_shows.all()
        assert fact.context.starts_at == start and fact.context.ends_at == end


@pytest.mark.parametrize('day', [date(2026, 3, 29), date(2026, 10, 25)])
def test_ambiguous_or_missing_dst_wall_time_rejected_for_both_sources(db, day):
    now = datetime.combine(day+timedelta(days=1), time(12), TZ)
    with db.unit_of_work() as u:
        with pytest.raises(ValueError, match='niet-eenduidige'):
            app(u, now).register_manual(**inputs(start_day=day, start_time=time(2,30), end_day=day, end_time=time(4)))
    client = Client({'741': [dict(naam=PERSONS[0].sportlink_name, datumvanaf=day.isoformat(),
                 tijdvanaf='02:30', datumtot=day.isoformat(), tijdtot='04:00')]})
    with pytest.raises(ValueError, match='bron'):
        source(client).consult(now)


@pytest.mark.parametrize('offset', ['+02:00', '+01:00'])
def test_explicit_dst_instants_are_not_guessed(db, offset):
    start = datetime.fromisoformat('2026-10-25T02:30:00'+offset)
    end = datetime.fromisoformat('2026-10-25T04:00:00+01:00')
    service = source(Client({'741': [row(start, end)]}))
    selected, = service.consult(NOW).bookings
    with db.unit_of_work() as u:
        app(u).register_booking(selected, source=service)
        fact, = u.no_shows.all()
        assert fact.context.starts_at.astimezone(timezone.utc) == start.astimezone(timezone.utc)


@pytest.mark.parametrize('end', [NOW-timedelta(days=1, hours=2), NOW-timedelta(days=2)])
def test_end_must_be_strictly_later(db, end):
    with db.unit_of_work() as u:
        with pytest.raises(ValueError, match='Eindtijd'):
            app(u).register_manual(**inputs(end=end))


@pytest.mark.parametrize('first', ['manual', 'sportlink'])
def test_exact_duplicates_across_routes_revocation_and_returning_source(db, first):
    service = source(); selected, = service.consult(NOW).bookings
    with db.unit_of_work() as u:
        a = app(u)
        if first == 'manual': a.register_manual(**inputs())
        else: a.register_booking(selected, source=service)
        original, = u.no_shows.all()
        for action in (lambda: a.register_manual(**inputs()), lambda: a.register_booking(selected, source=service)):
            with pytest.raises(ValueError, match='al een no-show'): action()
        assert a.current_state('P1', original.season).counter == 1
        a.revoke(original.no_show_id, reason='correctie', revoked_at=NOW+timedelta(days=100))
        assert a.register_booking(selected, source=service).counter == 1
        assert len(u.no_shows.all()) == 2
        assert u.no_shows.get(original.no_show_id) == original


@pytest.mark.parametrize('changes', [dict(task_code='761'), dict(start_time=time(11)),
    dict(other=True, description='Oude dienst', task_code='741'),
    dict(other=True, description='Oude dienst', task_code='')])
def test_possible_duplicates_require_acknowledging_the_actual_events(db, changes):
    with db.unit_of_work() as u:
        a = app(u); a.register_manual(**inputs())
        original, = u.no_shows.all()
        context = a.manual_context(**inputs(**changes))
        exact, possible = a.duplicate_check(context)
        assert not exact and possible == (original,)
        with pytest.raises(ValueError, match='Mogelijk duplicaat'): a.register_manual(**inputs(**changes))
        assert a.register_manual(**inputs(**changes), acknowledged_possible=(original.no_show_id,)).counter == (2 if "start_time" in changes else 1)
        if changes.get('other'):
            fact = next(e for e in u.no_shows.all() if e.no_show_id != original.no_show_id)
            assert not fact.manual.task_identity_verified and fact.booking is None


def test_other_service_requires_description_and_explicit_declaration(db):
    with db.unit_of_work() as u:
        for changes in (dict(other=True, description=''), dict(confirmed=False), dict(person_id='UNKNOWN')):
            with pytest.raises(ValueError): app(u).register_manual(**inputs(**changes))
        assert not u.no_shows.all()


def test_concurrent_manual_and_regular_registration_accepts_one_exact_active_event(db):
    barrier = Barrier(2)
    def attempt(mode):
        service = source(); selected, = service.consult(NOW).bookings
        barrier.wait(timeout=10)
        with db.unit_of_work() as u:
            try:
                if mode == 'manual': app(u).register_manual(**inputs())
                else: app(u).register_booking(selected, source=service)
                return 'registered'
            except ValueError as exc:
                assert 'al een no-show' in str(exc)
                return 'duplicate'
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(attempt, ('manual','sportlink'))) == ['duplicate','registered']
    with db.unit_of_work() as u:
        assert len(u.no_shows.all()) == 1


def test_no_new_registration_after_window_but_revocation_remains_available(db):
    with db.unit_of_work() as u:
        app(u).register_manual(**inputs())
        fact, = u.no_shows.all()
        later = app(u, NOW+timedelta(days=100))
        later.revoke(fact.no_show_id, reason='late correctie', revoked_at=NOW+timedelta(days=100))
        with pytest.raises(ValueError, match='14 kalenderdagen'): later.register_manual(**inputs())
        assert later.current_state('P1', fact.season).counter == 0


def test_history_filters_and_schema13_legacy_payload_remain_readable(db):
    service = source(); selected, = service.consult(NOW).bookings
    legacy = NoShowEvent('OLD', selected.assignment_id, selected.person_id, selected.starts_at,
                         NOW, 'historical-actor', season_id(selected.starts_at.date()), selected)
    with db.unit_of_work() as u:
        payload = asdict(legacy); payload.pop('manual')
        u._connection.execute('INSERT INTO sportlink_no_show_events VALUES (?, ?, ?, ?, ?, ?)',
            (legacy.no_show_id, legacy.assignment_id, legacy.person_id, legacy.season,
             legacy.occurred_at.isoformat(), json.dumps(payload, default=str)))
        u.commit()
        assert u.no_shows.get('OLD') == legacy
        a = app(u)
        a.revoke('OLD', reason='correctie', revoked_at=NOW)
        a.register_manual(**inputs())
        assert len(a.history()) == 2
        assert len(a.history(status='Actief')) == len(a.history(status='Ingetrokken')) == 1
        assert len(a.history(person_id='P2')) == len(a.history(season='2025/2026')) == 0


def test_all_members_including_former_members_and_namesakes_are_source_selected(db):
    from dvk.real_data_import import SportlinkRealDataAdapter
    columns = 'Rel. code;Naam;Lidstatus;Lidsoort;Status lidmaatschap;Geb.dat.;Afmelddatum'
    text = columns+'\nP1;Alex;Definitief;Bondslid;Spelend;01-01-2000;\nP2;Alex;Afgevoerd;Verenigingslid;;01-01-2000;01-09-2026'
    persons = SportlinkRealDataAdapter.read_volunteer_persons(text)
    assert len(persons) == 2
    with db.unit_of_work() as u:
        app(u).register_manual(**inputs(persons=persons, person_id='P2'))
        fact, = u.no_shows.all()
        assert fact.person_id == 'P2' and fact.manual.person_name == 'Alex'


@pytest.mark.parametrize('operation', ['manual', 'history', 'consult'])
def test_authorization_applies_outside_ui(db, operation):
    identity = Identity('other','Other',frozenset())
    with db.unit_of_work() as u:
        with pytest.raises(AuthorizationError):
            if operation == 'manual': app(u, identity=identity).register_manual(**inputs())
            elif operation == 'history': app(u, identity=identity).history()
            else: NoShowSourceApplicationService(identity, Client(), 'test', CATALOG, PERSONS).consult(NOW)


def test_standalone_ui_opens_without_starting_session(tmp_path):
    from pathlib import Path
    script = tmp_path / 'streamlit_app.py'
    script.write_text((Path(__file__).parents[1]/'streamlit_app.py').read_text())
    ui = AppTest.from_file(str(script), default_timeout=20).run()
    ui.button(key='nav-no-shows').click().run()
    assert not ui.exception
    assert any(h.value == '### No-showmanagement' for h in ui.markdown)
    assert not any(b.label in ('Planning starten', 'Planning hervatten') for b in ui.button)
    with SQLiteDatabase(tmp_path/'dvk_v05.sqlite').unit_of_work() as u:
        assert u.planning_sessions.get() is None


@pytest.mark.parametrize('failure', [False, True])
def test_independent_actions_preserve_every_planning_and_source_table(db, failure):
    from sportlink_fixtures import seed_bookings
    from dvk.planning_workqueue import TemporaryPlanning
    from dvk.workstream_model import DutyAssignment
    from test_schema_validation_v05 import contents, seed_base
    selected, = source().consult(NOW).bookings
    with db.unit_of_work() as u:
        seed_base(u._connection)
        seed_bookings(u, (selected,))
        u.temporary_planning.add(TemporaryPlanning(DutyAssignment('TEMP','P',selected.service_id,
            'P2','member',4,'planner'), selected.service))
        u.commit()
    before = contents(db.path)
    client = Client(); client.fail = failure
    if failure:
        with pytest.raises(VrijwilligersFetchError): source(client).consult(NOW)
    else:
        source(client).consult(NOW)
    with db.unit_of_work() as u:
        a = app(u); a.register_manual(**inputs())
        fact, = u.no_shows.all()
        a.revoke(fact.no_show_id, reason='synthetische correctie', revoked_at=NOW)
    after = contents(db.path)
    mutable = {'sportlink_no_show_events','sportlink_no_show_revocations','sportlink_sanction_assessments'}
    assert {k:v for k,v in before.items() if k not in mutable} == {k:v for k,v in after.items() if k not in mutable}


def test_manual_browser_route_with_api_failure_namesakes_and_other_service(tmp_path, monkeypatch):
    from pathlib import Path
    from dvk.sportlink_exports import export_path
    columns = 'Rel. code;Naam;Lidstatus;Lidsoort;Status lidmaatschap;Geb.dat.;Afmelddatum'
    export_path('leden').write_text(columns+'\nP1;Alex;Definitief;Bondslid;Spelend;01-01-2000;\nP2;Alex;Afgevoerd;Verenigingslid;;01-01-2000;01-09-2026')
    script = tmp_path / 'streamlit_app.py'
    script.write_text((Path(__file__).parents[1]/'streamlit_app.py').read_text().replace(
        'datetime.now(TZ)', 'datetime(2026, 11, 1, 12, tzinfo=TZ)'))
    original = NoShowApplicationService.__init__
    def init(self, *args, **kwargs):
        kwargs.setdefault('clock', lambda: NOW)
        original(self, *args, **kwargs)
    monkeypatch.setattr(NoShowApplicationService, '__init__', init)
    def fail(*args, **kwargs): raise VrijwilligersFetchError('Sportlink Vrijwilligers connection failure')
    monkeypatch.setattr('dvk.vrijwilligers_client.SportlinkVrijwilligersClient.fetch_rows', fail)
    ui = AppTest.from_file(str(script), default_timeout=20).run()
    ui.button(key='nav-no-shows').click().run()
    next(b for b in ui.button if b.label == 'Sportlink-diensten raadplegen').click().run()
    assert any('connection failure' in e.value for e in ui.error)
    next(r for r in ui.radio if r.label == 'Registratievorm').set_value('Handmatig').run()
    selector = next(s for s in ui.selectbox if s.label == 'Persoon')
    assert selector.options == ['Alex (relatie P1)', 'Alex (relatie P2)']
    selector.select('P2').run()
    next(s for s in ui.selectbox if s.label == 'Oorspronkelijke dienst').select('Andere dienst').run()
    next(t for t in ui.text_input if t.label == 'Dienstomschrijving (verplicht)').set_value('Historische dienst').run()
    next(t for t in ui.text_input if t.label.startswith('Oorspronkelijke taakcode')).set_value('OLD-7').run()
    next(c for c in ui.checkbox if c.label == MANUAL_DECLARATION).check().run()
    next(b for b in ui.button if b.label == 'No-show bevestigen').click().run()
    assert not ui.exception and not ui.error
    db = SQLiteDatabase(tmp_path/'dvk_v05.sqlite')
    with db.unit_of_work() as u:
        fact, = u.no_shows.all()
        assert fact.person_id == 'P2' and fact.registration_mode == 'Handmatig'
        assert fact.manual.task_code == 'OLD-7' and not fact.manual.task_identity_verified
        assert not u.sportlink_bookings.all() and u.planning_sessions.get() is None
    next(s for s in ui.selectbox if s.label == 'Status').select('Actief').run()
    next(t for t in ui.text_area if t.key == 'no-show-revocation-reason').set_value('Correctie')
    next(b for b in ui.button if b.label == 'Intrekking bevestigen').click().run()
    assert not ui.exception
    with db.unit_of_work() as u:
        assert u.no_show_revocations.for_no_show(fact.no_show_id).reason == 'Correctie'


def test_new_possible_duplicate_after_preview_requires_new_acknowledgment(db):
    with db.unit_of_work() as u:
        a = app(u); a.register_manual(**inputs())
        first, = u.no_shows.all()
        a.register_manual(**inputs(task_code='761'), acknowledged_possible=(first.no_show_id,))
        with pytest.raises(ValueError, match='Mogelijk duplicaat'):
            a.register_manual(**inputs(other=True, description='Historische taak'),
                              acknowledged_possible=(first.no_show_id,))
        assert len(u.no_shows.all()) == 2


def test_old_utc_season_payload_is_not_reinterpreted_but_new_events_use_local_season(db):
    from dvk.persistence.no_show_records import _event
    start = datetime(2026, 6, 30, 22, 30, tzinfo=timezone.utc)
    legacy = NoShowEvent('UTC-OLD','OLD','P1',start,start,'historical','2025/2026')
    payload = asdict(legacy); payload.pop('manual')
    assert _event(json.loads(json.dumps(payload, default=str))) == legacy
    now = datetime(2026, 7, 1, 2, tzinfo=TZ)
    service = source(Client({'741':[row(start, start+timedelta(hours=1))]}))
    selected, = service.consult(now).bookings
    with db.unit_of_work() as u:
        app(u, now).register_booking(selected, source=service)
        fact, = u.no_shows.all()
        assert fact.season == '2026/2027' and fact.occurred_at.date() == date(2026,7,1)


def test_regular_confirmation_uses_current_calendar_after_midnight(db):
    selected_at = NOW.replace(hour=23, minute=59)
    start = selected_at.replace(hour=10) - timedelta(days=14)
    service = source(Client({'741':[row(start)]}))
    selected, = service.consult(selected_at).bookings
    with db.unit_of_work() as u:
        with pytest.raises(ValueError):
            app(u, selected_at+timedelta(minutes=2)).register_booking(selected, source=service)
        assert not u.no_shows.all()
