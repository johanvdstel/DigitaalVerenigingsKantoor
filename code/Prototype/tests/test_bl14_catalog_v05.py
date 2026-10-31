"""BL-14 contract: synthetic local CSV, actual source intervals and session reload."""
from dataclasses import replace
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest
from streamlit.testing.v1 import AppTest

from dvk.shift_catalog import (load_shift_catalog, CatalogFileError, ShiftCatalog,
    ShiftDefinition, WeeklySlot, local_moment)
from dvk.planning import PlanningPeriod
from dvk.planning_session import PlanningSessionApplicationService
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from dvk.application_services import NoShowApplicationService, PlanningApplicationService, ProposalDecisionApplicationService
from dvk.no_show import NoShowEvent
from dvk.security import Identity
from dvk.sportlink_exports import default_export_directory
from test_volunteer_planning_integration_v05 import (db, catalog, PERIOD, NOW, IDENTITY, people, row,
    client, sync, snapshot, seed_work)

TZ = ZoneInfo('Europe/Amsterdam')


def test_local_csv_and_no_packaged_fallback():
    folder = default_export_directory()
    assert len(load_shift_catalog().bindings(PERIOD)) == 29
    (folder / 'shift_definitions.csv').unlink()
    with pytest.raises(CatalogFileError, match='shift_definitions.csv'):
        load_shift_catalog()


@pytest.mark.parametrize('change', ['columns', 'duplicate', 'code', 'friday', 'nan'])
def test_invalid_definition_is_explicit(change):
    path = default_export_directory() / 'shift_definitions.csv'
    text = path.read_text()
    if change == 'columns': text = text.replace('task_code,', 'wrong,', 1)
    if change == 'duplicate': text += text.splitlines()[1] + '\n'
    if change == 'code': text = text.replace('741,', 'bad code,')
    if change == 'friday': text = text.replace('2,4,1,2', '2,4,,2')
    if change == 'nan': text = text.replace('2.5', 'nan')
    path.write_text(text)
    with pytest.raises(CatalogFileError): load_shift_catalog()


@pytest.mark.parametrize('fields', [
    '4,23:00,02:00,741,2026-10-23,',
    '4,23:00,02:00,741,2026-10-24,2026-10-23',
    '4,23:00,23:00,741,,',
    '5,23:00,02:00,741,2026-10-23,2026-10-23',
    '4,23:00,02:00,unknown,,',
    '4,23:00,02:00,741,20261023,20261023',
    '9,23:00,02:00,741,,',
])
def test_invalid_slot_is_explicit(fields):
    path = default_export_directory() / 'shift_week_pattern.csv'
    path.write_text(path.read_text() + fields + '\n')
    with pytest.raises(CatalogFileError): load_shift_catalog()


def test_dated_night_added_inclusive_and_uses_actual_duration():
    path = default_export_directory() / 'shift_week_pattern.csv'
    path.write_text(path.read_text() + '4,23:00,02:00,741,2026-10-23,2026-10-23\n')
    catalog = load_shift_catalog()
    bindings = catalog.bindings(PERIOD)
    assert len(bindings) == 30
    service = next(b.service for b in bindings if b.service.starts_at.hour == 23)
    assert service.starts_at.date() == date(2026,10,23)
    assert service.ends_at.date() == date(2026,10,24)
    assert (service.duration_hours, service.required_staff) == (3,1)
    assert service == next(b.service for b in catalog.bindings(PlanningPeriod(date(2026,10,23),date(2026,10,23))) if b.service.starts_at.hour == 23)
    assert len(catalog.bindings(PlanningPeriod(date(2026,10,26), date(2026,11,1)))) == 29


@pytest.mark.parametrize('dated', [False, True])
def test_duplicate_concrete_slot_rejected(dated):
    path = default_export_directory() / 'shift_week_pattern.csv'
    path.write_text(path.read_text() + ('4,18:00,20:30,741,2026-10-23,2026-10-23\n' if dated else '4,18:00,20:30,741,,\n'))
    with pytest.raises(CatalogFileError, match='Dubbel'): load_shift_catalog()


@pytest.mark.parametrize('day', [date(2026,3,29),date(2026,10,25)])
def test_dst_ambiguous_or_missing_clock_rejected(day):
    with pytest.raises(ValueError, match='niet-eenduidige'): local_moment(day,time(2,30))


def test_dst_crossing_has_elapsed_duration():
    definition = ShiftDefinition('A','Synthetic',1,1,2)
    cat = ShiftCatalog((definition,), (WeeklySlot(5,time(23),time(4),'A'),))
    service = cat.bindings(PlanningPeriod(date(2026,10,24),date(2026,10,24)))[0].service
    assert service.duration_hours == 6


def test_used_codes_include_incidental_outside_period(db, catalog):
    cat = ShiftCatalog(catalog.definitions + (ShiftDefinition('C','Unused',1,1,2),
        ShiftDefinition('D','Dated',1,1,2)), catalog.slots + (
        WeeklySlot(4,time(12),time(13),'D',date(2027,1,1),date(2027,1,1)),))
    error, seen = sync(db,cat,{})
    assert error is None
    assert [q['vrijwilligerstaakcode'][0] for q in seen] == ['A','B','D']


@pytest.mark.parametrize('mode', ['outside','partial','long','exact'])
def test_actual_services_visible_unique_and_count_people_once(db,catalog,mode):
    original = catalog.bindings(PERIOD)[0].service
    actual = original
    if mode == 'outside': actual = replace(original, starts_at=original.starts_at+timedelta(hours=3),ends_at=original.ends_at+timedelta(hours=3))
    if mode == 'partial': actual = replace(original,starts_at=original.starts_at+timedelta(minutes=30))
    if mode == 'long': actual = replace(original,ends_at=original.ends_at+timedelta(hours=2))
    ps = people(2)
    assert sync(db,catalog,{'A':[row(actual,p) for p in ps]},ps)[0] is None
    with db.unit_of_work() as u:
        app = VolunteerPlanningApplicationService(u,IDENTITY,catalog)
        services,needs,_,_ = app.planning_data(PERIOD)
        assert len(services) == (2 if mode == 'exact' else 3)
        concrete = next(s for s in services if (s.starts_at,s.ends_at)==(actual.starts_at,actual.ends_at))
        need = next(n for n in needs if n.service_id==concrete.service_id)
        assert need.confirmed_occupancy == 2
        assert concrete.duration_hours == actual.duration_hours
        assert len(app.service_names(PERIOD)) == len(services)
        assert len(NoShowApplicationService(u,IDENTITY).assignment_contexts(period=PERIOD)) == 2


def test_equal_intervals_different_codes_stay_separate(db):
    cat = ShiftCatalog((ShiftDefinition('701','First',1,1,2),ShiftDefinition('741','Second',1,1,3)),
        (WeeklySlot(0,time(18),time(19),'701'),WeeklySlot(1,time(18),time(19),'741')))
    service = cat.bindings(PERIOD)[0].service
    assert sync(db,cat,{'701':[row(service,people()[0])],'741':[row(service,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        services,needs,_,_ = VolunteerPlanningApplicationService(u,IDENTITY,cat).planning_data(PERIOD)
        assert len(services)==3
        assert [n.confirmed_occupancy for n in needs]==[1,0,1]


def test_reload_is_explicit_preserves_durable_history_and_pins_configuration(db,catalog):
    original = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{'A':[row(original,people()[0])]})[0] is None
    seed_work(db,original)
    with db.unit_of_work() as u:
        old = u.planning_sessions.get()
        booking = u.sportlink_bookings.all()[0]
        no_show = NoShowApplicationService(u,IDENTITY)
        no_show.register(NoShowEvent('N',booking.assignment_id,booking.person_id,booking.starts_at,NOW,IDENTITY.subject_id,'2026/2027'),source_revision=old.source_revision)
        no_show.revoke('N',reason='Synthetic',revoked_at=NOW)
    before = snapshot(db)
    with db.unit_of_work() as u:
        app = PlanningSessionApplicationService(u,IDENTITY)
        assert app.catalog() == catalog
        with pytest.raises(ValueError,match='Bevestig'): app.reload_catalog(PERIOD,catalog=catalog)
    assert snapshot(db)==before
    with db.unit_of_work() as u:
        app = PlanningSessionApplicationService(u,IDENTITY)
        new = app.reload_catalog(PERIOD,confirmed=True,expected_session_id=old.session_id,catalog=catalog)
        assert new.session_id != old.session_id and new.source_revision is None
    assert snapshot(db)==((),(),None)
    with db.unit_of_work() as u:
        assert PlanningSessionApplicationService(u,IDENTITY).catalog() == catalog
        assert u.no_shows.get('N').booking.assignment_id == booking.assignment_id
        assert u.no_show_revocations.for_no_show('N') is not None
        assert not NoShowApplicationService(u,IDENTITY).available_assignments()
    # Repeating an unchanged reload must still create another session.
    with db.unit_of_work() as u:
        newer = PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id=new.session_id,catalog=catalog)
        assert newer.session_id != new.session_id


def test_invalid_reload_preserves_session_and_work(db,catalog):
    original = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{})[0] is None
    seed_work(db,original)
    before = snapshot(db)
    (default_export_directory()/'shift_week_pattern.csv').unlink()
    with db.unit_of_work() as u:
        current = u.planning_sessions.get()
        with pytest.raises(CatalogFileError):
            PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id=current.session_id)
        assert PlanningSessionApplicationService(u,IDENTITY).catalog() == catalog
        assert u.planning_sessions.get() == current
    assert snapshot(db)==before


def test_incidental_unoccupied_and_additional_source_support_proposal_confirm_undo(db,catalog):
    from test_planning_workqueue_v05 import JAN, proposal
    dated = WeeklySlot(0,time(21),time(23),'A',PERIOD.start,PERIOD.start)
    cat = ShiftCatalog(catalog.definitions,catalog.slots+(dated,))
    assert sync(db,cat,{})[0] is None
    with db.unit_of_work() as u:
        services,needs,_,_ = VolunteerPlanningApplicationService(u,IDENTITY,cat).planning_data(PERIOD)
        unoccupied = next(s for s in services if s.starts_at.hour==21)
        unoccupied_need = next(n for n in needs if n.service_id==unoccupied.service_id)
        assert (unoccupied_need.confirmed_occupancy,unoccupied_need.open_need)==(0,1)
    p = proposal(db,unoccupied,JAN,'INCIDENTAL')
    with db.unit_of_work() as u:
        result = ProposalDecisionApplicationService(IDENTITY,uow=u).approve(p,unoccupied,JAN,assignment_id='INCIDENTAL',staffing_need=unoccupied_need)
        assert result.assignment.scheduled_hours==2
        ProposalDecisionApplicationService(IDENTITY,uow=u).undo('INCIDENTAL')
    actual = replace(unoccupied,starts_at=unoccupied.starts_at+timedelta(minutes=15))
    assert sync(db,cat,{'A':[row(actual,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        services,needs,_,_ = VolunteerPlanningApplicationService(u,IDENTITY,cat).planning_data(PERIOD)
        extra = next(s for s in services if s.starts_at==actual.starts_at)
        need = next(n for n in needs if n.service_id==extra.service_id)
    p = proposal(db,extra,JAN,'EXTRA')
    with db.unit_of_work() as u:
        result = ProposalDecisionApplicationService(IDENTITY,uow=u).approve(p,extra,JAN,assignment_id='EXTRA',staffing_need=need)
        assert result.assignment.scheduled_hours==1.75
        after = PlanningApplicationService(IDENTITY,uow=u).staffing_needs(services=(extra,),source_needs=(need,))[0]
        assert (after.confirmed_occupancy,after.temporary_occupancy)==(1,1)
        ProposalDecisionApplicationService(IDENTITY,uow=u).undo('EXTRA')
        assert not u.temporary_planning.all()


def test_no_show_booking_key_unchanged_on_new_context(db,catalog):
    from dvk.vrijwilligers_adapter import SportlinkVrijwilligersAdapter, ServiceBinding
    original = catalog.bindings(PERIOD)[0].service
    source = row(original,people()[0])
    legacy = SportlinkVrijwilligersAdapter().import_rows(task_code='A',rows=[source],
        services=[ServiceBinding('A',original)],persons=people(),imported_at=NOW).bookings[0]
    assert sync(db,catalog,{'A':[source]})[0] is None
    with db.unit_of_work() as u:
        assert u.sportlink_bookings.all()[0].assignment_id==legacy.assignment_id


def test_reload_write_failure_and_stale_session_do_not_clear_work(db,catalog,monkeypatch):
    from dvk.persistence.planning_session import SQLitePlanningSessionRepository
    original = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{})[0] is None
    seed_work(db,original)
    before = snapshot(db)
    with db.unit_of_work() as u:
        old = u.planning_sessions.get()
        with pytest.raises(ValueError):
            PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id='stale',catalog=catalog)
    assert snapshot(db)==before
    def fail(*args): raise RuntimeError('Synthetic write failure')
    monkeypatch.setattr(SQLitePlanningSessionRepository,'save',fail)
    with db.unit_of_work() as u:
        with pytest.raises(RuntimeError):
            PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id=old.session_id,catalog=catalog)
        u.commit()  # Even a caller that catches the error cannot partially publish.
    assert snapshot(db)==before


def test_session_catalog_stays_loaded_across_restart_and_file_change(db,catalog):
    assert sync(db,catalog,{})[0] is None
    path = default_export_directory()/'shift_definitions.csv'
    path.write_text('invalid')
    from dvk.persistence import SQLiteDatabase
    restarted = SQLiteDatabase(db.path)
    with restarted.unit_of_work() as u:
        assert PlanningSessionApplicationService(u,IDENTITY).catalog()==catalog
        assert VolunteerPlanningApplicationService(u,IDENTITY,load_shift_catalog(Path(__file__).parents[1]/'dvk'/'configuration')).catalog==catalog


def test_reload_requires_authorization(db,catalog):
    with db.unit_of_work() as u:
        app = PlanningSessionApplicationService(u,Identity('none','None',frozenset()))
        with pytest.raises(PermissionError): app.reload_catalog(PERIOD,confirmed=True,catalog=catalog)


from test_candidate_context_ui_v05 import operational_page


def test_reload_ui_cancel_confirm_invalid_and_unknown_source(operational_page):
    app,db,_ = operational_page
    with db.unit_of_work() as u:
        old = u.planning_sessions.get()
    app.button(key='reload-catalog').click().run()
    assert any('beëindigt' in w.value for w in app.warning)
    app.button(key='cancel-reload-catalog').click().run()
    with db.unit_of_work() as u: assert u.planning_sessions.get()==old
    app.button(key='reload-catalog').click().run()
    app.button(key='confirm-reload-catalog').click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        new = u.planning_sessions.get()
        assert new.session_id != old.session_id
        assert new.source_revision is None
    assert any('Geen gevalideerde' in w.value for w in app.warning)
    (default_export_directory()/'shift_definitions.csv').unlink()
    app.button(key='reload-catalog').click().run()
    assert app.error and not app.exception
    with db.unit_of_work() as u: assert u.planning_sessions.get()==new


def test_old_application_instance_cannot_publish_after_reload(db,catalog):
    assert sync(db,catalog,{})[0] is None
    with db.unit_of_work() as u:
        old = VolunteerPlanningApplicationService(u,IDENTITY,catalog)
        current = u.planning_sessions.get()
        PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id=current.session_id,catalog=catalog)
        seen=[]
        with pytest.raises(ValueError,match='gewijzigd'):
            old.synchronize(period=PERIOD,client=client({},seen),client_id='synthetic',persons=people(),imported_at=NOW)
        assert not seen


def test_reload_then_refresh_and_failed_refresh_keep_correct_session(db,catalog):
    from urllib.error import URLError
    original = catalog.bindings(PERIOD)[0].service
    assert sync(db,catalog,{'A':[row(original,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        current=u.planning_sessions.get()
        new=PlanningSessionApplicationService(u,IDENTITY).reload_catalog(PERIOD,confirmed=True,expected_session_id=current.session_id,catalog=catalog)
    assert sync(db,catalog,{'A':URLError('synthetic')})[0]
    with db.unit_of_work() as u:
        assert u.planning_sessions.get()==new
        assert not VolunteerPlanningApplicationService(u,IDENTITY,catalog).source(PERIOD)[2]
    assert sync(db,catalog,{'A':[row(original,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        assert u.planning_sessions.get().session_id==new.session_id
        assert VolunteerPlanningApplicationService(u,IDENTITY,catalog).source(PERIOD)[2]


def test_additional_service_operational_ui_candidates_confirmation_and_undo(operational_page):
    from ui_table_events import table, pick
    app,db,_ = operational_page
    catalog=load_shift_catalog()
    original=catalog.bindings(PERIOD)[0].service
    actual=replace(original,starts_at=original.starts_at+timedelta(minutes=15))
    assert sync(db,catalog,{'701':[row(actual,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        services,_,_,_=VolunteerPlanningApplicationService(u,IDENTITY,catalog).planning_data(PERIOD)
        extra=next(s for s in services if s.starts_at==actual.starts_at)
    app.session_state['selected_service_id']=extra.service_id
    app.run()
    assert not app.exception
    assert 'Synthetisch lid M1' in table(app).value.Kandidaat.tolist()
    pick(app)
    next(b for b in app.button if b.label=='Selectie bevestigen').click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        entry=u.temporary_planning.all()[0]
        assert entry.service.service_id==extra.service_id
        assert entry.assignment.scheduled_hours==0.75
    next(b for b in app.button if b.label=='Tijdelijke inroostering ongedaan maken').click().run()
    assert not app.exception
    with db.unit_of_work() as u: assert not u.temporary_planning.all()


def test_legacy_session_requires_reload_without_deleting_work(operational_page):
    app,db,_=operational_page
    with db.unit_of_work() as u:
        current=u.planning_sessions.get()
        u.planning_sessions.save(replace(current,catalog=None))
        u.commit()
    app.run()
    assert not app.exception
    assert any('nog geen ingelezen lokale catalogus' in w.value for w in app.warning)
    with db.unit_of_work() as u: assert u.planning_sessions.get().session_id==current.session_id
    app.button(key='reload-catalog').click().run()
    app.button(key='confirm-reload-catalog').click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        assert u.planning_sessions.get().catalog is not None
        assert u.planning_sessions.get().session_id != current.session_id


@pytest.mark.parametrize('day',[PERIOD.start,PERIOD.end])
def test_source_night_at_period_boundary_belongs_to_start_date(db,catalog,day):
    original=catalog.bindings(PERIOD)[0].service
    actual=replace(original,starts_at=datetime.combine(day,time(23),TZ),
                   ends_at=datetime.combine(day+timedelta(days=1),time(2),TZ))
    outside=replace(actual,starts_at=actual.starts_at-timedelta(days=8),ends_at=actual.ends_at-timedelta(days=8))
    assert sync(db,catalog,{'A':[row(actual,people()[0]),row(outside,people()[0])]})[0] is None
    with db.unit_of_work() as u:
        bookings=u.sportlink_bookings.all()
        assert len(bookings)==1
        assert bookings[0].starts_at.date()==day
        services,needs,_,_=VolunteerPlanningApplicationService(u,IDENTITY,catalog).planning_data(PERIOD)
        night=next(s for s in services if s.starts_at==actual.starts_at)
        assert night.duration_hours==3
        assert next(n for n in needs if n.service_id==night.service_id).confirmed_occupancy==1


def test_source_separate_utc_date_time_uses_local_day_and_norm(db):
    catalog=load_shift_catalog()
    period=PlanningPeriod(date(2026,10,24),date(2026,10,24))
    value=dict(naam=people()[0].sportlink_name,datumvanaf='2026-10-23T00:00:00Z',
        tijdvanaf='23:30',datumtot='2026-10-24T00:00:00Z',tijdtot='00:30',lokatie='Synthetic')
    assert sync(db,catalog,{'741':[value]},period=period)[0] is None
    with db.unit_of_work() as u:
        services,needs,_,_=VolunteerPlanningApplicationService(u,IDENTITY,catalog).planning_data(period)
        extra=next(s for s in services if s.starts_at.hour==1)
        assert extra.starts_at.date()==period.start
        assert (extra.starts_at.minute,extra.ends_at.hour,extra.ends_at.minute)==(30,2,30)
        assert extra.required_staff==2  # Saturday, not the Friday UTC calendar date.
        assert extra.duration_hours==1
        overview=PlanningApplicationService(IDENTITY,uow=u).build_overview(period=period,services=services,staffing_needs=needs)
        assert extra.service_id in {s.service_id for s in overview.services}


def test_source_explicit_instants_during_clock_change_are_not_guessed_or_reversed(db):
    catalog=load_shift_catalog()
    value=dict(naam=people()[0].sportlink_name,datumvanaf='2026-10-25T00:30:00Z',
        datumtot='2026-10-25T01:15:00Z',lokatie='Synthetic')
    assert sync(db,catalog,{'761':[value]})[0] is None
    with db.unit_of_work() as u:
        services,_,_,_=VolunteerPlanningApplicationService(u,IDENTITY,catalog).planning_data(PERIOD)
        extra=next(s for s in services if s.starts_at.hour==2)
        assert extra.starts_at.fold==0 and extra.ends_at.fold==1
        assert extra.duration_hours==0.75
