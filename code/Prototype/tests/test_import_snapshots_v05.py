from datetime import datetime, timezone

import pytest

from dvk.import_management import ImportBatch, ImportStatus, SnapshotRecord
from dvk.import_workflow import confirm_import, mark_validated, preview_differences
from dvk.persistence import SQLiteDatabase

NOW = datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc)


def batch(batch_id="B1", status=ImportStatus.RECEIVED):
    return ImportBatch(batch_id, "Sportlink", "leden", "2026-2027", NOW, "tester", status)


def record(key, source, canonical, provenance="prov"):
    return SnapshotRecord("PREVIEW", key, source, canonical, provenance)


def test_v01_confirmed_import_creates_snapshot_and_keeps_provenance(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    validated = mark_validated(batch(), validation_summary="ok", has_blocking_signals=False)
    with db.unit_of_work() as uow:
        uow.import_batches.add(validated); uow.commit()
    with db.unit_of_work() as uow:
        snapshot = confirm_import(uow, validated, (record("P1", "raw-name", "canonical-name", "source->canonical"),),
                                  snapshot_id="S1", confirmed_at=NOW, confirmed_by="planner")
    with db.unit_of_work() as uow:
        assert uow.import_batches.get("B1").status is ImportStatus.CONFIRMED
        assert uow.snapshots.get("S1") == snapshot
        assert uow.snapshots.records("S1")[0].provenance_payload == "source->canonical"


def test_v02_invalid_import_cannot_replace_valid_snapshot(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    valid = mark_validated(batch("B1"), validation_summary="ok", has_blocking_signals=False)
    with db.unit_of_work() as uow:
        uow.import_batches.add(valid); uow.commit()
    with db.unit_of_work() as uow:
        confirm_import(uow, valid, (record("P1", "old", "old"),), snapshot_id="S1", confirmed_at=NOW, confirmed_by="planner")
    invalid = mark_validated(batch("B2"), validation_summary="blocking DQ", has_blocking_signals=True)
    with db.unit_of_work() as uow:
        uow.import_batches.add(invalid); uow.commit()
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError):
            confirm_import(uow, invalid, (record("P1", "bad", "bad"),), snapshot_id="S2", confirmed_at=NOW, confirmed_by="planner")
    with db.unit_of_work() as uow:
        assert uow.snapshots.latest("Sportlink", "leden", "2026-2027").snapshot_id == "S1"
        assert uow.import_batches.get("B2").status is ImportStatus.INVALID


def test_v03_preview_shows_add_remove_and_change_before_confirmation(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    first = mark_validated(batch("B1"), validation_summary="ok", has_blocking_signals=False)
    with db.unit_of_work() as uow:
        uow.import_batches.add(first); uow.commit()
    with db.unit_of_work() as uow:
        confirm_import(uow, first, (record("A", "raw-a", "one"), record("B", "raw-b", "two")),
                       snapshot_id="S1", confirmed_at=NOW, confirmed_by="planner")
    second = mark_validated(batch("B2"), validation_summary="ok", has_blocking_signals=False)
    with db.unit_of_work() as uow:
        uow.import_batches.add(second); uow.commit()
    proposed = (record("A", "raw-a2", "changed"), record("C", "raw-c", "three"))
    with db.unit_of_work() as uow:
        diffs = preview_differences(uow, second, proposed)
        assert [(d.record_key, d.change_type) for d in diffs] == [
            ("A", "RECORD_CHANGED"), ("B", "RECORD_REMOVED"), ("C", "RECORD_ADDED")]
        assert uow.snapshots.latest("Sportlink", "leden", "2026-2027").snapshot_id == "S1"


def test_second_confirmed_snapshot_supersedes_but_does_not_delete_first(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    for bid, sid, value in (("B1", "S1", "one"), ("B2", "S2", "two")):
        current = mark_validated(batch(bid), validation_summary="ok", has_blocking_signals=False)
        with db.unit_of_work() as uow:
            uow.import_batches.add(current); uow.commit()
        with db.unit_of_work() as uow:
            snapshot = confirm_import(uow, current, (record("A", value, value),), snapshot_id=sid,
                                      confirmed_at=NOW, confirmed_by="planner")
    with db.unit_of_work() as uow:
        assert uow.snapshots.get("S1") is not None
        assert uow.snapshots.get("S2").supersedes_snapshot_id == "S1"
