"""BL-16 application boundaries and publication failures, synthetic data only."""
from dataclasses import replace
from datetime import timedelta
import sqlite3

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent, season_id
from dvk.planning import PlanningPeriod
from dvk.planning_session import PlanningSessionApplicationService
from dvk.security import Identity
from dvk.volunteer_planning import VolunteerPlanningApplicationService
from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository
from dvk.persistence.planning_session import SQLitePlanningSessionRepository
from dvk.persistence.sportlink_bookings import SQLiteSportlinkBookingRepository
from test_volunteer_planning_integration_v05 import (
    db, catalog, IDENTITY, PERIOD, NOW, people, row, client, sync, seed_work, snapshot,
)


def session(db):
    with db.unit_of_work() as u:
        return u.planning_sessions.get()


def publish(db, catalog):
    service = catalog.bindings(PERIOD)[0].service
    assert sync(db, catalog, {'A': [row(service, people()[0])]})[0] is None
    return service


def event(booking, identifier='N'):
    return NoShowEvent(identifier, booking.assignment_id, booking.person_id or 'invented',
                       booking.starts_at, NOW, IDENTITY.subject_id, season_id(booking.starts_at.date()))


def selected(db):
    with db.unit_of_work() as u:
        return NoShowApplicationService(u, IDENTITY).assignment_contexts(period=PERIOD)[0]


@pytest.mark.parametrize('mode', ['none', 'pending', 'missing_metadata', 'wrong_period', 'wrong_session', 'wrong_revision', 'failed_status'])
def test_no_validated_active_source_rejects_selection_and_registration(db, catalog, mode):
    publish(db, catalog)
    choice = selected(db)
    with db.unit_of_work() as u:
        active = u.planning_sessions.get()
        if mode == 'none': u.planning_sessions.remove()
        elif mode == 'pending': u.planning_sessions.save(replace(active, source_revision=None))
        else:
            state = u.sportlink_bookings.refresh_state()
            if mode == 'missing_metadata': u.sportlink_bookings.clear_refresh_state()
            else:
                key, value = {'wrong_period': ('start', '2026-10-01'), 'wrong_session': ('session_id', 'other'),
                              'wrong_revision': ('source_revision', 'other'), 'failed_status': ('status', 'Mislukt')}[mode]
                u.sportlink_bookings.save_refresh_state(dict(state, **{key:value}))
        u.commit()
        app = NoShowApplicationService(u, IDENTITY)
        assert not app.available_assignments()
        assert not VolunteerPlanningApplicationService(u, IDENTITY, catalog).bookings(PERIOD)
        with pytest.raises(ValueError, match='actieve gevalideerde bron'):
            app.register(event(choice.assignment), source_revision=choice.source_revision)
        assert not u.no_shows.all()


@pytest.mark.parametrize('change', ['refresh_same_booking', 'new_period', 'close', 'new_session_same_period'])
def test_source_change_after_selection_rejected_even_when_booking_key_is_unchanged(db, catalog, change):
    service = publish(db, catalog)
    choice = selected(db)
    old = session(db)
    if change == 'refresh_same_booking':
        assert sync(db, catalog, {'A': [row(service, people()[0])]})[0] is None
        assert selected(db).assignment.assignment_id == choice.assignment.assignment_id
    else:
        with db.unit_of_work() as u:
            app = PlanningSessionApplicationService(u, IDENTITY)
            if change == 'close': app.close(confirmed=True, expected_session_id=old.session_id)
            else:
                period = PERIOD if change == 'new_session_same_period' else PlanningPeriod(PERIOD.start+timedelta(days=7), PERIOD.end+timedelta(days=7))
                app.start(period, confirmed=True, expected_session_id=old.session_id)
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        if change != 'refresh_same_booking': assert not app.available_assignments()
        with pytest.raises(ValueError, match='actieve gevalideerde bron'):
            app.register(event(choice.assignment), source_revision=choice.source_revision, period=PERIOD)
        assert not u.no_shows.all()


def test_registration_without_selection_revision_or_wrong_period_is_rejected(db, catalog):
    publish(db, catalog)
    choice = selected(db)
    wrong = PlanningPeriod(PERIOD.start, PERIOD.end+timedelta(days=7))
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        assert not app.available_assignments(period=wrong)
        for kwargs in ({}, {'source_revision': choice.source_revision, 'period': wrong}):
            with pytest.raises(ValueError): app.register(event(choice.assignment), **kwargs)
        assert not u.no_shows.all()


@pytest.mark.parametrize('change', ['close', 'new_period', 'refresh'])
def test_history_revocation_and_sanction_survive_session_boundaries(db, catalog, change):
    service = publish(db, catalog)
    choice = selected(db)
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        app.register(event(choice.assignment), source_revision=choice.source_revision)
        fact = u.no_shows.get('N')
        revocation = app.revoke('N', reason='Synthetic decision', revoked_at=NOW)
    seed_work(db, service)
    old = session(db)
    if change == 'refresh': assert sync(db, catalog, {})[0] is None
    else:
        with db.unit_of_work() as u:
            app = PlanningSessionApplicationService(u, IDENTITY)
            if change == 'close': app.close(confirmed=True, expected_session_id=old.session_id)
            else: app.start(PlanningPeriod(PERIOD.start+timedelta(days=7), PERIOD.end+timedelta(days=7)), confirmed=True, expected_session_id=old.session_id)
    with db.unit_of_work() as u:
        assert u.no_shows.get('N') == fact
        assert u.no_show_revocations.for_no_show('N') == revocation
        assert NoShowApplicationService(u, IDENTITY).current_state(fact.person_id, fact.season).counter == 0
        assert not u.temporary_planning.all()


@pytest.mark.parametrize('fault', ['first_transport', 'later_transport', 'later_invalid', 'identity_warning'])
def test_replacement_failure_preserves_session_work_success_and_booking_snapshot(db, catalog, fault):
    service = publish(db, catalog); seed_work(db, service)
    before, old = snapshot(db), session(db)
    payloads = {'A': [row(service, people()[0])]}
    if fault == 'first_transport': payloads['A'] = TimeoutError('synthetic')
    elif fault == 'later_transport': payloads['B'] = TimeoutError('synthetic')
    elif fault == 'later_invalid': payloads['B'] = b'{"error":"synthetic"}'
    else: payloads['A'][0]['naam'] = 'Unlinked synthetic person'
    error, _ = sync(db, catalog, payloads)
    if fault == 'identity_warning':
        assert error is None and session(db).source_revision != old.source_revision
        assert not snapshot(db)[1]
    else:
        assert error and snapshot(db) == before and session(db) == old


@pytest.mark.parametrize('fault', ['bookings', 'temporary', 'success_metadata', 'session_revision'])
def test_publication_write_failure_rolls_back_even_when_caller_catches_and_commits(db, catalog, monkeypatch, fault):
    service = publish(db, catalog); seed_work(db, service)
    before, old = snapshot(db), session(db)
    def fail(*a, **k): raise sqlite3.OperationalError('synthetic publication failure')
    cls, method = {'bookings': (SQLiteSportlinkBookingRepository, 'replace_all'),
                   'temporary': (SQLiteTemporaryPlanningRepository, 'remove'),
                   'success_metadata': (SQLiteSportlinkBookingRepository, 'save_refresh_state'),
                   'session_revision': (SQLitePlanningSessionRepository, 'save')}[fault]
    with db.unit_of_work() as u:
        with monkeypatch.context() as patch:
            patch.setattr(cls, method, fail)
            with pytest.raises(sqlite3.OperationalError):
                VolunteerPlanningApplicationService(u, IDENTITY, catalog).synchronize(period=PERIOD,
                    client=client({}, []), client_id='synthetic', persons=people(), imported_at=NOW,
                    confirmed=True, source_revision=old.source_revision)
        u.commit()  # Must not publish a partial DELETE/INSERT from the failed call.
    assert snapshot(db) == before and session(db) == old


def test_replacement_requires_confirmation_before_any_network_access(db, catalog):
    publish(db, catalog)
    seen = []
    before, old = snapshot(db), session(db)
    with db.unit_of_work() as u:
        with pytest.raises(ValueError, match='Bevestig'):
            VolunteerPlanningApplicationService(u, IDENTITY, catalog).synchronize(period=PERIOD,
                client=client({}, seen), client_id='synthetic', persons=people(), imported_at=NOW)
    assert not seen and snapshot(db) == before and session(db) == old


def test_source_change_during_fetch_cannot_overwrite_new_session(db, catalog):
    publish(db, catalog)
    old = session(db)
    delegate = client({}, [])
    class ChangingClient:
        changed = False
        def fetch_rows(self, **kwargs):
            if not self.changed:
                self.changed = True
                with db.unit_of_work() as other:
                    PlanningSessionApplicationService(other, IDENTITY).start(PERIOD,
                        confirmed=True, expected_session_id=old.session_id)
            return delegate.fetch_rows(**kwargs)
    with db.unit_of_work() as u:
        with pytest.raises(ValueError, match='gewijzigd'):
            VolunteerPlanningApplicationService(u, IDENTITY, catalog).synchronize(period=PERIOD,
                client=ChangingClient(), client_id='synthetic', persons=people(), imported_at=NOW,
                confirmed=True, source_revision=old.source_revision)
    assert session(db).session_id != old.session_id and session(db).source_revision is None
    assert snapshot(db) == ((), (), None)


@pytest.mark.parametrize('operation', ['current', 'start', 'close'])
def test_session_services_enforce_existing_permissions(db, operation):
    with db.unit_of_work() as u:
        app = PlanningSessionApplicationService(u, Identity('none','None',frozenset()))
        with pytest.raises(PermissionError):
            if operation == 'current': app.current()
            elif operation == 'start': app.start(PERIOD)
            else: app.close(confirmed=True)


def test_booking_outside_active_period_is_not_selectable_or_registerable(db, catalog):
    publish(db, catalog)
    choice = selected(db)
    outside = replace(choice.assignment, starts_at=choice.assignment.starts_at-timedelta(days=7),
                      ends_at=choice.assignment.ends_at-timedelta(days=7))
    with db.unit_of_work() as u:
        u.sportlink_bookings.replace_all((outside,)); u.commit()
        app = NoShowApplicationService(u, IDENTITY)
        assert not app.available_assignments()
        with pytest.raises(ValueError, match='buiten de actieve planningsperiode'):
            app.register(event(outside), source_revision=choice.source_revision)
        assert not u.no_shows.all()


def test_ui_source_replacement_between_render_and_submit_rejects_stale_selection(tmp_path):
    from test_planning_ui_names_v05 import page
    from dvk.shift_catalog import load_shift_catalog
    app, database = page(tmp_path)
    c = load_shift_catalog()
    binding = c.bindings(PERIOD)[0]
    payload = {binding.task_code:[row(binding.service, people()[0])]}
    assert sync(database, c, payload)[0] is None
    app.run()  # Render the selection using revision 1.
    assert sync(database, c, payload)[0] is None  # Same logical booking, revision 2.
    next(b for b in app.button if b.label == 'No-show bevestigen').click().run()
    assert not app.exception
    assert any('bron is gewijzigd' in e.value for e in app.error)
    with database.unit_of_work() as u: assert not u.no_shows.all()
    next(b for b in app.button if b.label == 'No-show bevestigen').click().run()
    assert not app.exception
    with database.unit_of_work() as u: assert len(u.no_shows.all()) == 1


def test_selection_cannot_label_old_bookings_with_a_new_source_revision(db, catalog, monkeypatch):
    service = publish(db, catalog)
    original = NoShowApplicationService.available_assignments
    def changed(self, *args, **kwargs):
        bookings = original(self, *args, **kwargs)
        assert sync(db, catalog, {'A':[row(service, people()[0])]})[0] is None
        return bookings
    with db.unit_of_work() as u:
        monkeypatch.setattr(NoShowApplicationService, 'available_assignments', changed)
        assert NoShowApplicationService(u, IDENTITY).assignment_contexts(period=PERIOD) == ()
