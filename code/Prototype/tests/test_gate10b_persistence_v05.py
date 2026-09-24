import json
import sqlite3
from dataclasses import asdict, replace
from datetime import datetime

import pytest

from dvk.no_show import NoShowEvent, NoShowRevocation, assess_sanction
from dvk.persistence import SQLiteDatabase
from dvk.persistence.migrations import MIGRATIONS
from dvk.persistence.planning_records import SQLiteAssignmentProposalRepository, SQLiteDutyAssignmentRepository
from dvk.workstream_model import AssignmentProposal, DutyAssignment


def _seed(connection, count=1):
    for i in range(1, count + 1):
        proposal = AssignmentProposal(f"P{i}", f"S{i}", "MEM1", "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())
        SQLiteAssignmentProposalRepository(connection).add(proposal)
        SQLiteDutyAssignmentRepository(connection).add(DutyAssignment(f"A{i}", f"P{i}", f"S{i}", "MEM1", "member", 4, "planner"))


def _event(i=1):
    when = datetime(2026, 9, i, 10)
    return NoShowEvent(f"N{i}", f"A{i}", "MEM1", when, when, "planner", "2026/2027")


def _revocation():
    return NoShowRevocation("R1", "N1", "expliciet besluit", datetime(2026, 9, 30, 12), "planner")


def test_revocation_requires_existing_fact_and_is_unique(tmp_path):
    db = SQLiteDatabase(tmp_path / "constraints.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        with pytest.raises(sqlite3.IntegrityError):
            uow.no_show_revocations.add(_revocation())
        _seed(uow._connection)
        uow.no_shows.add(_event())
        uow.no_show_revocations.add(_revocation())
        uow.commit()
    with db.unit_of_work() as uow:
        with pytest.raises(sqlite3.IntegrityError):
            uow.no_show_revocations.add(replace(_revocation(), revocation_id="R2"))
        assert uow.no_show_revocations.for_no_show("N1") == _revocation()


@pytest.mark.parametrize("table", ["no_show_events", "no_show_revocations"])
@pytest.mark.parametrize("operation", ["UPDATE", "DELETE"])
def test_database_rejects_mutation_of_both_fact_types(tmp_path, table, operation):
    db = SQLiteDatabase(tmp_path / "immutable.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        _seed(uow._connection)
        uow.no_shows.add(_event()); uow.no_show_revocations.add(_revocation()); uow.commit()
    with db.unit_of_work() as uow:
        sql = f"UPDATE {table} SET no_show_id=no_show_id" if operation == "UPDATE" else f"DELETE FROM {table}"
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            uow._connection.execute(sql)
        assert uow.no_shows.get("N1") == _event()
        assert uow.no_show_revocations.for_no_show("N1") == _revocation()


def test_uncommitted_revocation_is_rolled_back(tmp_path):
    db = SQLiteDatabase(tmp_path / "rollback.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        _seed(uow._connection); uow.no_shows.add(_event()); uow.commit()
    with db.unit_of_work() as uow:
        uow.no_show_revocations.add(_revocation())
    with db.unit_of_work() as uow:
        assert uow.no_show_revocations.for_no_show("N1") is None
        assert uow.no_shows.get("N1") == _event()


def _legacy_database(path):
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("CREATE TABLE schema_version (version INTEGER PRIMARY KEY)")
        for version, migration in enumerate(MIGRATIONS[:9], 1):
            migration(connection)
            connection.execute("INSERT INTO schema_version VALUES (?)", (version,))
        _seed(connection, 3)
        for i, status in ((1, "valid"), (2, "revoked"), (3, "valid")):
            event = _event(i)
            payload = asdict(event) | dict(status=status, correction_reason="oude correctie" if status == "revoked" else None,
                                         corrected_at="2026-09-20 10:00:00" if status == "revoked" else None,
                                         corrected_by="legacy-actor" if status == "revoked" else None)
            connection.execute("INSERT INTO no_show_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                               (event.no_show_id, event.assignment_id, event.person_id, event.season,
                                event.occurred_at.isoformat(), status, json.dumps(payload, default=str)))
            assessment = assess_sanction(event, tuple(_event(n) for n in range(1, i)))
            connection.execute("INSERT INTO sanction_assessments VALUES (?, ?, ?, ?, ?)",
                               (event.no_show_id, event.person_id, event.season, i, json.dumps(asdict(assessment))))
        # Both a valid and a legacy-revoked no-show have abandoned repair data.
        connection.execute("INSERT INTO replacement_duties VALUES ('OLD1', 'N1', 'A2', 'MEM1', '2026/2027', NULL, '{}')")
        connection.execute("INSERT INTO replacement_duties VALUES ('OLD2', 'N2', 'A3', 'MEM1', '2026/2027', '2026-09-22', '{}')")


def _unrelated_tables(connection):
    excluded = {"schema_version", "no_show_events", "sanction_assessments", "replacement_duties", "no_show_revocations"}
    return {name: connection.execute(f'SELECT * FROM "{name}"').fetchall()
            for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            if name not in excluded}


def test_migration_discards_only_authorized_legacy_data_and_never_fabricates_revocations(tmp_path):
    path = tmp_path / "legacy.sqlite"
    _legacy_database(path)
    with sqlite3.connect(path) as connection:
        before = _unrelated_tables(connection)
        facts = connection.execute("SELECT no_show_id, payload FROM no_show_events WHERE status='valid' ORDER BY no_show_id").fetchall()
        sanctions = connection.execute("SELECT * FROM sanction_assessments WHERE no_show_id IN ('N1', 'N3') ORDER BY no_show_id").fetchall()
    db = SQLiteDatabase(path)
    assert db.initialize() == 10
    assert db.initialize() == 10
    with sqlite3.connect(path) as connection:
        assert _unrelated_tables(connection) == before
        assert connection.execute("SELECT no_show_id, payload FROM no_show_events ORDER BY no_show_id").fetchall() == facts
        assert connection.execute("SELECT * FROM sanction_assessments ORDER BY no_show_id").fetchall() == sanctions
        assert connection.execute("SELECT * FROM no_show_revocations").fetchall() == []
        assert connection.execute("SELECT name FROM sqlite_master WHERE name='replacement_duties'").fetchall() == []
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") == _event(1)
        assert uow.no_shows.get("N2") is None
        assert uow.no_shows.get("N3") == _event(3)
        uow.no_show_revocations.add(_revocation()); uow.commit()
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") == _event(1)
        assert uow.no_show_revocations.for_no_show("N1") == _revocation()


def test_failed_migration_rolls_back_schema_and_legacy_deletions(tmp_path):
    path = tmp_path / "migration-failure.sqlite"
    _legacy_database(path)
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TRIGGER simulate_failure BEFORE DELETE ON no_show_events BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
    with pytest.raises(sqlite3.IntegrityError, match="simulated failure"):
        SQLiteDatabase(path).initialize()
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] == 9
        assert connection.execute("SELECT COUNT(*) FROM no_show_events").fetchone()[0] == 3
        assert connection.execute("SELECT COUNT(*) FROM sanction_assessments").fetchone()[0] == 3
        assert connection.execute("SELECT COUNT(*) FROM replacement_duties").fetchone()[0] == 2
