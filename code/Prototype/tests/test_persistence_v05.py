import sqlite3

import pytest

from dvk.persistence import SQLiteDatabase


def test_empty_database_is_migrated_reproducibly(tmp_path):
    path = tmp_path / "dvk.sqlite"
    database = SQLiteDatabase(path)

    latest_version = database.initialize()
    assert latest_version >= 1
    assert database.initialize() == latest_version

    with sqlite3.connect(path) as connection:
        version = connection.execute("SELECT MAX(version) FROM schema_version").fetchone()[0]
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }

    assert version == latest_version
    assert {"schema_version", "dvk_records"} <= tables


def test_committed_data_survives_new_connection(tmp_path):
    path = tmp_path / "dvk.sqlite"
    database = SQLiteDatabase(path)

    with database.unit_of_work() as uow:
        uow.records.add("record-1", "persisted")
        uow.commit()

    reopened = SQLiteDatabase(path)
    with reopened.unit_of_work() as uow:
        assert uow.records.get("record-1") == {
            "record_id": "record-1",
            "payload": "persisted",
        }


def test_uncommitted_unit_of_work_rolls_back(tmp_path):
    database = SQLiteDatabase(tmp_path / "dvk.sqlite")

    with database.unit_of_work() as uow:
        uow.records.add("record-1", "discarded")

    with database.unit_of_work() as uow:
        assert uow.records.get("record-1") is None


def test_exception_rolls_back_transaction(tmp_path):
    database = SQLiteDatabase(tmp_path / "dvk.sqlite")

    with pytest.raises(RuntimeError):
        with database.unit_of_work() as uow:
            uow.records.add("record-1", "discarded")
            raise RuntimeError("boom")

    with database.unit_of_work() as uow:
        assert uow.records.get("record-1") is None
