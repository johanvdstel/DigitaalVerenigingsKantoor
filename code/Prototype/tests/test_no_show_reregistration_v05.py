"""Re-register only after revocation; all data is synthetic and local to tmp_path."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from datetime import timedelta
import sqlite3
from threading import Barrier

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.persistence import SQLiteDatabase, migrations
from dvk.persistence.schema_validation import SchemaValidationError
from sportlink_fixtures import booking, seed_bookings, source_revision
from test_no_show_sportlink_v05 import IDENTITY, SOURCE, event
from test_schema_validation_v05 import contents


def db_with_source(tmp_path):
    db = SQLiteDatabase(tmp_path / 'reregister.sqlite')
    with db.unit_of_work() as u:
        seed_bookings(u, (SOURCE,))
    return db


def register(db, identifier):
    with db.unit_of_work() as u:
        return NoShowApplicationService(u, IDENTITY).register(event(identifier=identifier), source_revision=source_revision(u))


@pytest.mark.parametrize('cycles', [1, 3, 6])
def test_repeated_register_revoke_and_reregister_preserves_history_and_correct_counters(tmp_path, cycles):
    db = db_with_source(tmp_path)
    facts, revocations = [], []
    for i in range(cycles):
        assert register(db, f'N{i}').counter == 1
        with db.unit_of_work() as u:
            app = NoShowApplicationService(u, IDENTITY)
            stored = u.no_shows.get(f'N{i}')
            facts.append(stored)
            assert app.current_state(SOURCE.person_id, '2026/2027').counter == 1
            assert tuple(c.no_show for c in app.revocable_no_shows()) == (stored,)
            with pytest.raises(ValueError, match='al een no-show'):
                app.register(event(identifier=f'DUP{i}'), source_revision=source_revision(u))
            assert not u.no_shows.get(f'DUP{i}')
            revocations.append(app.revoke(f'N{i}', reason=f'Synthetic correction {i}', revoked_at=SOURCE.ends_at+timedelta(minutes=i)))
            assert app.current_state(SOURCE.person_id, '2026/2027').counter == 0
            assert not app.revocable_no_shows()
        assert SQLiteDatabase(db.path).initialize() == 13
        with db.unit_of_work() as u:
            assert u.no_shows.history_for_assignment(SOURCE.assignment_id) == tuple(facts)
            for fact, revocation in zip(facts, revocations):
                assert u.no_shows.get(fact.no_show_id) == fact
                assert u.no_show_revocations.for_no_show(fact.no_show_id) == revocation
            assert u._connection.execute('SELECT count(*) FROM sportlink_sanction_assessments').fetchone()[0] == i+1
    assert register(db, 'FINAL').counter == 1
    with db.unit_of_work() as u:
        assert len(u.no_shows.history_for_assignment(SOURCE.assignment_id)) == cycles+1
        assert NoShowApplicationService(u, IDENTITY).current_state(SOURCE.person_id, '2026/2027').counter == 1
        with pytest.raises(ValueError, match='al een no-show'):
            NoShowApplicationService(u, IDENTITY).register(event(identifier='FINAL-DUP'), source_revision=source_revision(u))


def test_other_active_earlier_no_show_still_counts_after_reregistration(tmp_path):
    db = db_with_source(tmp_path)
    other = booking(SOURCE.person_id, when=SOURCE.starts_at-timedelta(days=1))
    with db.unit_of_work() as u:
        seed_bookings(u, (other, SOURCE))
        app = NoShowApplicationService(u, IDENTITY)
        app.register(event(other, 'EARLIER'), source_revision=source_revision(u))
    assert register(db, 'ORIGINAL').counter == 2
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        app.revoke('ORIGINAL', reason='Synthetic correction', revoked_at=SOURCE.ends_at)
        assert app.current_state(SOURCE.person_id, '2026/2027').counter == 1
    assessment = register(db, 'REPEAT')
    assert (assessment.counter, assessment.card, assessment.fine_eur) == (2, 'yellow', 75)
    with db.unit_of_work() as u:
        assert NoShowApplicationService(u, IDENTITY).current_state(SOURCE.person_id, '2026/2027').counter == 2


def test_concurrent_reregistration_accepts_only_one_active_fact(tmp_path):
    db = db_with_source(tmp_path); register(db, 'ORIGINAL')
    with db.unit_of_work() as u:
        NoShowApplicationService(u, IDENTITY).revoke('ORIGINAL', reason='Synthetic correction', revoked_at=SOURCE.ends_at)
    barrier = Barrier(2)
    def attempt(identifier):
        barrier.wait(timeout=10)
        try: return register(db, identifier).counter
        except ValueError as exc:
            assert 'al een no-show' in str(exc)
            return 'duplicate'
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(attempt, ('A', 'B')), key=str) == [1, 'duplicate']
    with db.unit_of_work() as u:
        assert len(u.no_shows.history_for_assignment(SOURCE.assignment_id)) == 2
        assert NoShowApplicationService(u, IDENTITY).current_state(SOURCE.person_id, '2026/2027').counter == 1


def version12_with_history(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / 'version12.sqlite')
    with monkeypatch.context() as patch:
        patch.setattr(migrations, 'MIGRATIONS', migrations.MIGRATIONS[:12])
        with db.unit_of_work() as u:
            other = booking('TEST002', when=SOURCE.starts_at+timedelta(days=1))
            seed_bookings(u, (SOURCE, other))
            app = NoShowApplicationService(u, IDENTITY)
            app.register(event(other, 'OTHER-ACTIVE'), source_revision=source_revision(u))
            app.register(event(identifier='OLD'), source_revision=source_revision(u))
            app.revoke('OLD', reason='Synthetic historical correction', revoked_at=SOURCE.ends_at)
    return db


def test_upgrade_from_12_preserves_all_rows_fks_triggers_and_allows_reregistration(tmp_path, monkeypatch):
    db = version12_with_history(tmp_path, monkeypatch)
    before = contents(db.path)
    assert db.initialize() == 13
    after = contents(db.path)
    assert all(after[name] == rows for name, rows in before.items() if name != 'schema_version')
    assert after['schema_version'] == before['schema_version']+[(13,)]
    with closing(sqlite3.connect(db.path)) as c:
        c.execute('PRAGMA foreign_keys=ON')
        assert c.execute('PRAGMA foreign_key_check').fetchall() == []
        assert c.execute('PRAGMA integrity_check').fetchone() == ('ok',)
        assert not c.execute("SELECT name FROM sqlite_temp_master").fetchall()
        for table in ('sportlink_no_show_events', 'sportlink_no_show_revocations'):
            for operation in ('UPDATE', 'DELETE'):
                statement = f'DELETE FROM {table}' if operation=='DELETE' else f'UPDATE {table} SET payload=payload' if table.endswith('events') else f'UPDATE {table} SET reason=reason'
                with pytest.raises(sqlite3.IntegrityError, match='immutable'): c.execute(statement)
                c.rollback()
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO sportlink_no_show_revocations VALUES ('BAD', 'MISSING', 'synthetic', '2026-10-23', 'planner')")
    assert register(db, 'NEW').counter == 1
    with db.unit_of_work() as u:
        assert u.no_shows.get('OLD') and u.no_show_revocations.for_no_show('OLD')
        assert len(u.no_shows.history_for_assignment(SOURCE.assignment_id)) == 2


@pytest.mark.parametrize('fault', ['after_migration', 'missing_index', 'during_copy'])
def test_failed_version13_upgrade_rolls_back_entire_schema_and_history(tmp_path, monkeypatch, fault):
    db = version12_with_history(tmp_path, monkeypatch)
    before, raw = contents(db.path), db.path.read_bytes()
    original = migrations.MIGRATIONS[12]
    def failing(c):
        if fault == 'during_copy':
            class FailingCopy:
                def execute(self, sql, *args):
                    if sql.startswith('INSERT INTO main."sportlink_no_show_revocations"'):
                        raise sqlite3.OperationalError('synthetic copy failure')
                    return c.execute(sql, *args)
            original(FailingCopy())
        else:
            original(c)
            if fault == 'after_migration': raise sqlite3.OperationalError('synthetic final failure')
            c.execute('DROP INDEX idx_sportlink_no_show_assignment')
    with monkeypatch.context() as patch:
        patch.setattr(migrations, 'MIGRATIONS', migrations.MIGRATIONS[:12]+(failing,))
        with pytest.raises((sqlite3.OperationalError, SchemaValidationError)):
            db.initialize()
    assert contents(db.path) == before and db.path.read_bytes() == raw
    assert db.initialize() == 13
    assert register(db, 'AFTER-RETRY').counter == 1


def test_ui_register_revoke_and_reregister_same_booking_keeps_history(tmp_path, monkeypatch):
    from test_planning_ui_names_v05 import page
    from test_volunteer_planning_integration_v05 import PERIOD, people, row, sync
    from dvk.shift_catalog import load_shift_catalog
    app, db = page(tmp_path)
    catalog = load_shift_catalog()
    binding = catalog.bindings(PERIOD)[0]
    assert sync(db, catalog, {binding.task_code:[row(binding.service, people()[0])]})[0] is None
    from sportlink_fixtures import open_no_show_ui
    open_no_show_ui(app, db, monkeypatch)
    next(b for b in app.button if b.label == 'No-show bevestigen').click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        original, = u.no_shows.all()
    app.text_area(key='no-show-revocation-reason').set_value('Synthetic UI correction')
    next(b for b in app.button if b.label == 'Intrekking bevestigen').click().run()
    assert not app.exception
    next(b for b in app.button if b.label == 'No-show bevestigen').click().run()
    assert not app.exception and not app.error
    assert any(w.value.startswith('Eerste no-show:') for w in app.warning)
    with db.unit_of_work() as u:
        assert u.no_shows.get(original.no_show_id) == original
        assert u.no_show_revocations.for_no_show(original.no_show_id).reason == 'Synthetic UI correction'
        assert len(u.no_shows.history_for_assignment(original.assignment_id)) == 2
        assert NoShowApplicationService(u, IDENTITY).current_state(original.person_id, original.season).counter == 1


# Preserve historical BL-11 dates with an explicit test clock.
pytestmark = pytest.mark.usefixtures("historical_registration_context")
