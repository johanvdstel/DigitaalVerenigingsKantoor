"""Versioned schema contracts, atomic migrations and resource ownership. Synthetic only."""
from sportlink_fixtures import source_revision
from contextlib import closing
from datetime import datetime, timezone
import sqlite3

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent, season_id
from dvk.persistence import SQLiteDatabase, migrations
from dvk.persistence import sqlite as storage
from dvk.persistence.planning_records import SQLiteTemporaryPlanningRepository
from dvk.persistence.schema_validation import SchemaValidationError, VERSION_TABLE_SQL
from dvk.planning_workqueue import TemporaryPlanning
from dvk.security import Identity, Permission
from dvk.workstream_model import DutyAssignment
from sportlink_fixtures import booking
from test_gate10b_persistence_v05 import _legacy_database, _seed


def legacy(path, version):
    with closing(sqlite3.connect(path)) as c, c:
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("BEGIN")
        c.execute(VERSION_TABLE_SQL)
        for step, migration in enumerate(migrations.MIGRATIONS[:version], 1):
            migration(c)
            c.execute("INSERT INTO schema_version VALUES (?)", (step,))


def contents(path):
    with closing(sqlite3.connect(path)) as c:
        return {name: c.execute('SELECT * FROM "' + name.replace('"', '""') + '" ORDER BY rowid').fetchall()
                for name, in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def seed_base(c):
    c.execute("INSERT INTO dvk_records VALUES ('synthetic', 'keep exact payload')")
    c.execute("INSERT INTO import_batches VALUES ('B','Sportlink','leden',NULL,'2026-10-22','synthetic','confirmed',NULL,NULL,NULL)")
    c.execute("INSERT INTO source_snapshots VALUES ('S','B','Sportlink','leden',NULL,'2026-10-22',NULL)")
    c.execute("INSERT INTO snapshot_records VALUES ('S','K','source','canonical','provenance')")


def populated(path):
    db = SQLiteDatabase(path)
    source = booking()
    identity = Identity("synthetic", "Synthetic", frozenset(Permission))
    with db.unit_of_work() as u:
        seed_base(u._connection)
        from sportlink_fixtures import seed_bookings
        seed_bookings(u, (source,))
        u.temporary_planning.add(TemporaryPlanning(
            DutyAssignment("TEMP", "P", source.service_id, "OTHER", "member", 4, "synthetic"), source.service))
        u.commit()
        app = NoShowApplicationService(u, identity)
        app.register(NoShowEvent("N", source.assignment_id, source.person_id, source.starts_at,
                                 datetime(2026, 10, 22, tzinfo=timezone.utc), identity.subject_id,
                                 season_id(source.starts_at.date())), source_revision=source_revision(u))
        app.revoke("N", reason="Synthetic revocation", revoked_at=datetime(2026, 10, 22, tzinfo=timezone.utc))
    return db


def test_new_database_has_complete_current_schema_and_immutable_guards(tmp_path):
    db = SQLiteDatabase(tmp_path / "new.sqlite")
    assert db.initialize() == 12
    with closing(sqlite3.connect(db.path)) as c:
        assert c.execute("SELECT version FROM schema_version ORDER BY version").fetchall() == [(v,) for v in range(1, 13)]
        tables = {n for n, in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"sportlink_bookings", "temporary_planning", "sportlink_no_show_events",
                "sportlink_no_show_revocations", "sportlink_sanction_assessments"} <= tables
        assert c.execute("SELECT count(*) FROM sqlite_master WHERE type='trigger'").fetchone() == (8,)
        assert c.execute("PRAGMA foreign_key_check").fetchall() == []


def test_previously_emptied_schema_is_not_silently_reinitialized(tmp_path):
    path = tmp_path / "emptied.sqlite"
    with closing(sqlite3.connect(path)) as c:
        c.execute("CREATE TABLE old_records (payload TEXT)")
        c.execute("DROP TABLE old_records")
    before = path.read_bytes()
    with pytest.raises(SchemaValidationError, match="schema_version ontbreekt"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


def test_current_reopen_preserves_every_table_and_file_bytes(tmp_path):
    db = populated(tmp_path / "current.sqlite")
    before, raw = contents(db.path), db.path.read_bytes()
    assert before["sportlink_bookings"] and before["temporary_planning"]
    assert before["sportlink_no_show_events"] and before["sportlink_no_show_revocations"]
    assert before["sportlink_sanction_assessments"] and before["snapshot_records"]
    for _ in range(2):
        assert db.initialize() == 12
        with db.unit_of_work() as u:
            assert u.no_shows.get("N") is not None
            assert u.no_show_revocations.for_no_show("N") is not None
    assert contents(db.path) == before
    assert db.path.read_bytes() == raw


@pytest.mark.parametrize("version", range(1, 12))
def test_every_valid_historical_version_migrates_without_rewriting_source_data(tmp_path, version):
    path = tmp_path / "old.sqlite"
    legacy(path, version)
    with closing(sqlite3.connect(path)) as c, c:
        c.execute("INSERT INTO dvk_records VALUES ('synthetic', 'historical payload')")
        if version >= 2:
            c.execute("INSERT INTO import_batches VALUES ('B','Sportlink','leden',NULL,'2026-10-22','synthetic','confirmed',NULL,NULL,NULL)")
    before = contents(path)
    assert SQLiteDatabase(path).initialize() == 12
    after = contents(path)
    assert after["dvk_records"] == before["dvk_records"]
    if version >= 2:
        assert after["import_batches"] == before["import_batches"]


def test_upgrade_from_11_preserves_workqueue_imports_and_all_existing_tables(tmp_path):
    path = tmp_path / "workqueue.sqlite"
    legacy(path, 11)
    source = booking()
    with closing(sqlite3.connect(path)) as c, c:
        seed_base(c)
        SQLiteTemporaryPlanningRepository(c).add(TemporaryPlanning(
            DutyAssignment("TEMP", "P", source.service_id, "OTHER", "member", 4, "synthetic"), source.service))
    before = contents(path)
    assert before["temporary_planning"] and before["snapshot_records"]
    assert SQLiteDatabase(path).initialize() == 12
    after = contents(path)
    assert all(after[name] == rows for name, rows in before.items() if name != "schema_version")


def test_historical_duplicate_no_shows_are_rejected_without_automatic_cleanup(tmp_path):
    path = tmp_path / "old-duplicates.sqlite"
    legacy(path, 7)
    with closing(sqlite3.connect(path)) as c, c:
        _seed(c)
        c.executemany("INSERT INTO no_show_events VALUES (?, 'A1', 'MEM1', '2026/2027', '2026-09-01', 'valid', '{}')",
                      [("N1",), ("N2",)])
    before = path.read_bytes()
    with pytest.raises(ValueError, match="duplicate historical records"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


@pytest.mark.parametrize("mutation,match", [
    ("DROP TABLE sportlink_bookings", "no such table: sportlink_bookings"),
    ("ALTER TABLE sportlink_bookings RENAME COLUMN payload TO other_payload", "kolom"),
    ("ALTER TABLE sportlink_bookings ADD COLUMN extra TEXT", "kolom"),
    ("DROP INDEX idx_snapshot_dataset", "index"),
    ("DROP INDEX idx_no_show_assignment; CREATE INDEX idx_no_show_assignment ON no_show_events(assignment_id)", "uniciteitsbeperking"),
    ("DROP TRIGGER sportlink_no_show_events_no_delete", "trigger"),
    ("DROP TRIGGER sportlink_no_show_events_no_delete; CREATE TRIGGER sportlink_no_show_events_no_delete BEFORE DELETE ON sportlink_no_show_events BEGIN SELECT 1; END", "trigger"),
    ("DROP TRIGGER sportlink_no_show_revocations_no_update", "trigger"),
    ("DROP TABLE sportlink_sanction_assessments; CREATE TABLE sportlink_sanction_assessments (no_show_id TEXT PRIMARY KEY, person_id TEXT NOT NULL, season TEXT NOT NULL, counter INTEGER NOT NULL, payload TEXT NOT NULL)", "foreign-key"),
    ("DROP TABLE schema_version", "schema_version ontbreekt"),
    ("DELETE FROM schema_version", "lege versieadministratie"),
    ("DELETE FROM schema_version WHERE version=6", "ontbrekende stappen"),
    ("DELETE FROM schema_version WHERE version<12", "ontbrekende stappen"),
    ("INSERT INTO schema_version VALUES (0)", "ongeldige"),
    ("INSERT INTO schema_version VALUES (-1)", "ongeldige"),
    ("INSERT INTO schema_version VALUES (13)", "toekomstige"),
    ("DROP TABLE schema_version; CREATE TABLE schema_version (version TEXT); INSERT INTO schema_version VALUES ('invalid')", "kolom"),
    ("DROP TABLE schema_version; CREATE TABLE schema_version (version INTEGER); INSERT INTO schema_version VALUES (12),(12)", "kolom"),
])
def test_inconsistent_database_is_rejected_without_any_changes(tmp_path, mutation, match):
    db = populated(tmp_path / "invalid.sqlite")
    with closing(sqlite3.connect(db.path)) as c:
        c.executescript(mutation)
    before, raw = contents(db.path), db.path.read_bytes()
    for entry in (db.initialize, db.unit_of_work().__enter__):
        with pytest.raises(SchemaValidationError, match=match):
            entry()
        assert contents(db.path) == before
        assert db.path.read_bytes() == raw
    with closing(sqlite3.connect(db.path, timeout=0)) as c:
        c.execute("BEGIN IMMEDIATE")  # Neither rejected access path retains locks.
        c.rollback()


@pytest.mark.parametrize("definition", [
    "assignment_id INTEGER PRIMARY KEY, payload TEXT NOT NULL",
    "assignment_id TEXT PRIMARY KEY, payload TEXT",
    "assignment_id TEXT PRIMARY KEY, payload TEXT NOT NULL DEFAULT '{}'",
    "assignment_id TEXT, payload TEXT NOT NULL",
])
def test_essential_column_definitions_are_checked(tmp_path, definition):
    path = tmp_path / "columns.sqlite"
    SQLiteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as c:
        c.executescript("DROP TABLE sportlink_bookings; CREATE TABLE sportlink_bookings (" + definition + ")")
    before = path.read_bytes()
    with pytest.raises(SchemaValidationError, match="kolom"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


def test_implicit_unique_constraint_is_required(tmp_path):
    path = tmp_path / "unique.sqlite"
    SQLiteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as c:
        c.executescript("""DROP TABLE sportlink_no_show_events;
            CREATE TABLE sportlink_no_show_events (no_show_id TEXT PRIMARY KEY,
            assignment_id TEXT NOT NULL, person_id TEXT NOT NULL, season TEXT NOT NULL,
            occurred_at TEXT NOT NULL, payload TEXT NOT NULL);""")
    before = path.read_bytes()
    with pytest.raises(SchemaValidationError, match="uniciteitsbeperking"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


def fail_after_last_step(c):
    migrations._SCHEMA_MIGRATIONS[11](c)
    c.execute("UPDATE dvk_records SET payload='must roll back'")
    raise RuntimeError("synthetic migration failure")


@pytest.mark.parametrize("start", [0, 9, 11])
def test_whole_upgrade_rolls_back_ddl_data_and_versions(tmp_path, monkeypatch, start):
    path = tmp_path / "failed.sqlite"
    if start == 9:
        _legacy_database(path)  # Existing authorized v10 deletions must roll back too.
    elif start:
        legacy(path, start)
    else:
        with closing(sqlite3.connect(path)):
            pass
    before, raw = contents(path), path.read_bytes()
    monkeypatch.setattr(migrations, "MIGRATIONS", migrations.MIGRATIONS[:11] + (fail_after_last_step,))
    with pytest.raises(RuntimeError, match="synthetic migration failure"):
        SQLiteDatabase(path).initialize()
    assert contents(path) == before
    if start:
        assert path.read_bytes() == raw
    monkeypatch.undo()
    assert SQLiteDatabase(path).initialize() == 12  # Retry starts from the original valid schema.


def test_result_schema_validation_also_rolls_back_version_and_partial_ddl(tmp_path, monkeypatch):
    path = tmp_path / "incomplete.sqlite"
    legacy(path, 11)
    before = path.read_bytes()
    def incomplete(c):
        c.execute("CREATE TABLE sportlink_bookings (assignment_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    monkeypatch.setattr(migrations, "MIGRATIONS", migrations.MIGRATIONS[:11] + (incomplete,))
    with pytest.raises(SchemaValidationError, match="no such table"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


def test_result_version_administration_is_checked_before_commit(tmp_path, monkeypatch):
    path = tmp_path / "version-result.sqlite"
    legacy(path, 11)
    before = path.read_bytes()
    def wrong_version(c):
        migrations._SCHEMA_MIGRATIONS[11](c)
        c.execute("DELETE FROM schema_version WHERE version=10")
    monkeypatch.setattr(migrations, "MIGRATIONS", migrations.MIGRATIONS[:11] + (wrong_version,))
    with pytest.raises(SchemaValidationError, match="versieadministratie"):
        SQLiteDatabase(path).initialize()
    assert path.read_bytes() == before


def test_healthy_current_schema_can_be_validated_on_readonly_connection(tmp_path):
    path = tmp_path / "readonly.sqlite"
    SQLiteDatabase(path).initialize()
    before = path.read_bytes()
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as c:
        assert migrations.migrate(c) == 12
    assert path.read_bytes() == before


@pytest.mark.parametrize("fail", [False, True])
def test_migrate_does_not_commit_or_discard_callers_outer_transaction(tmp_path, monkeypatch, fail):
    path = tmp_path / "outer.sqlite"
    legacy(path, 11)
    with closing(sqlite3.connect(path)) as c:
        c.execute("INSERT INTO dvk_records VALUES ('caller', 'uncommitted')")
        if fail:
            monkeypatch.setattr(migrations, "MIGRATIONS", migrations.MIGRATIONS[:11] + (fail_after_last_step,))
            with pytest.raises(RuntimeError):
                migrations.migrate(c)
        else:
            assert migrations.migrate(c) == 12
        assert c.in_transaction
        assert c.execute("SELECT payload FROM dvk_records WHERE record_id='caller'").fetchone() == ('uncommitted',)
        c.rollback()
        assert c.execute("SELECT MAX(version) FROM schema_version").fetchone() == (11,)
        assert not c.execute("SELECT * FROM dvk_records").fetchall()


@pytest.mark.parametrize("entry", ["initialize", "unit_of_work"])
@pytest.mark.parametrize("failure", ["schema", "migration", "pragma"])
def test_failed_access_closes_connections_and_releases_locks(tmp_path, monkeypatch, entry, failure):
    path = tmp_path / "closed.sqlite"
    legacy(path, 11)
    if failure == "schema":
        with closing(sqlite3.connect(path)) as c:
            c.execute("DROP TABLE dvk_records")
    if failure == "migration":
        monkeypatch.setattr(migrations, "MIGRATIONS", migrations.MIGRATIONS[:11] + (fail_after_last_step,))
    real_connect = sqlite3.connect
    opened = []
    class Tracked(sqlite3.Connection):
        closed = False
        def execute(self, sql, *args):
            if failure == "pragma" and sql == "PRAGMA foreign_keys=ON":
                raise sqlite3.OperationalError("synthetic pragma failure")
            return super().execute(sql, *args)
        def close(self):
            self.closed = True
            return super().close()
    def connect(database, *args, **kwargs):
        if str(database) == ":memory:":
            return real_connect(database, *args, **kwargs)
        result = real_connect(database, *args, factory=Tracked, **kwargs)
        opened.append(result)
        return result
    monkeypatch.setattr(sqlite3, "connect", connect)
    db = SQLiteDatabase(path)
    uow = db.unit_of_work()
    with pytest.raises((SchemaValidationError, RuntimeError, sqlite3.OperationalError)):
        db.initialize() if entry == "initialize" else uow.__enter__()
    assert opened and all(c.closed for c in opened)
    assert uow._connection is None
    with closing(real_connect(path, timeout=0)) as c:
        c.execute("BEGIN IMMEDIATE")
        c.rollback()


def test_repository_setup_failure_closes_uow_connection(tmp_path, monkeypatch):
    db = SQLiteDatabase(tmp_path / "setup.sqlite")
    db.initialize()
    def failed(*args):
        raise RuntimeError("synthetic repository setup failure")
    monkeypatch.setattr(storage, "SQLiteRecordRepository", failed)
    uow = db.unit_of_work()
    with pytest.raises(RuntimeError, match="repository setup"):
        uow.__enter__()
    assert uow._connection is None
    with closing(sqlite3.connect(db.path, timeout=0)) as c:
        c.execute("BEGIN IMMEDIATE")
        c.rollback()
