from datetime import date, datetime, timezone

import pytest

from dvk.import_management import ImportBatch, ImportStatus, SnapshotRecord
from dvk.import_workflow import confirm_import
from dvk.persistence import SQLiteDatabase
from dvk.run_context import EngineRun, EngineRunStatus, SourceFetch, SourceFetchStatus
from dvk.versioning import ConfigVersion, PolicyVersion, SoftwareVersion

NOW = datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc)
START = date(2026, 9, 14)
END = date(2026, 9, 20)
COMMIT = "fabbb5f439148e89d1f431f0e0c452b87b6fcc84"


def run(run_id="R1", status=EngineRunStatus.COMPLETED, fetches=(), snapshots=()):
    return EngineRun(run_id, NOW, "planner", START, END, status, snapshots, fetches, "policy-v0.5", "shift-catalog-v1", "dvk-0.5", NOW)


def add_versions(uow):
    uow.policy_versions.add(PolicyVersion.create("policy-v0.5", {"required_hours": 10}, created_at=NOW, created_by="tester", effective_from=START))
    uow.config_versions.add(ConfigVersion.create("shift-catalog-v1", {"BAR": {"minimum": 2, "maximum": 4}}, created_at=NOW, created_by="tester", effective_from=START))
    uow.software_versions.add(SoftwareVersion("dvk-0.5", "dvk-0.5", COMMIT, NOW))


def test_successful_empty_fetch_is_distinct_from_failed_fetch():
    empty = SourceFetch("F1", "Sportlink", "Programma", NOW, NOW, START, END, SourceFetchStatus.SUCCEEDED, 0)
    failed = SourceFetch("F2", "Sportlink", "Programma", NOW, NOW, START, END, SourceFetchStatus.FAILED, None, "CONNECTION_FAILURE")
    assert empty.record_count == 0 and empty.error_category is None
    assert failed.record_count is None and failed.error_category == "CONNECTION_FAILURE"


def test_engine_run_requires_explicit_config_version():
    with pytest.raises(ValueError, match="config_version"):
        EngineRun("R1", NOW, "planner", START, END, EngineRunStatus.COMPLETED, (), (), "policy-v0.5", " ", "dvk-0.5", NOW)


def test_engine_run_rejects_unknown_version_reference(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="unknown version"):
            uow.engine_runs.add(run())


def test_engine_run_persists_snapshot_live_fetch_policy_config_and_engine_context(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    batch = ImportBatch("B1", "Sportlink", "leden", "2026-2027", NOW, "tester", ImportStatus.AWAITING_CONFIRMATION, "ok")
    with db.unit_of_work() as uow: uow.import_batches.add(batch); uow.commit()
    with db.unit_of_work() as uow: confirm_import(uow, batch, (SnapshotRecord("PREVIEW", "P1", "raw", "canonical", "prov"),), snapshot_id="S1", confirmed_at=NOW, confirmed_by="planner")
    fetch = SourceFetch("F1", "Sportlink", "Programma", NOW, NOW, START, END, SourceFetchStatus.SUCCEEDED, 12)
    engine_run = run(fetches=("F1",), snapshots=("S1",))
    with db.unit_of_work() as uow: add_versions(uow); uow.source_fetches.add(fetch); uow.engine_runs.add(engine_run); uow.commit()
    with db.unit_of_work() as uow:
        assert uow.source_fetches.get("F1") == fetch
        restored = uow.engine_runs.get("R1")
        assert restored == engine_run
        assert uow.policy_versions.get(restored.policy_version).content_hash
        assert uow.config_versions.get(restored.config_version).content_hash
        assert uow.software_versions.get(restored.engine_version).git_commit_sha == COMMIT


def test_engine_run_can_reference_multiple_read_only_live_sources(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    programma = SourceFetch("FP", "Sportlink", "Programma", NOW, NOW, START, END, SourceFetchStatus.SUCCEEDED, 8)
    vrijwilligers = SourceFetch("FV", "Sportlink", "Vrijwilligers", NOW, NOW, START, END, SourceFetchStatus.SUCCEEDED, 3)
    engine_run = run(fetches=("FP", "FV"))
    with db.unit_of_work() as uow: add_versions(uow); uow.source_fetches.add(programma); uow.source_fetches.add(vrijwilligers); uow.engine_runs.add(engine_run); uow.commit()
    with db.unit_of_work() as uow:
        restored = uow.engine_runs.get("R1")
        assert set(restored.source_fetch_ids) == {"FP", "FV"}
        assert uow.source_fetches.get("FP").dataset_type == "Programma"
        assert uow.source_fetches.get("FV").dataset_type == "Vrijwilligers"


def test_failed_live_fetch_remains_historical_context_not_empty_data(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    failed = SourceFetch("F1", "Sportlink", "Vrijwilligers", NOW, NOW, START, END, SourceFetchStatus.FAILED, None, "HTTP_503")
    engine_run = run(status=EngineRunStatus.FAILED, fetches=("F1",))
    with db.unit_of_work() as uow: add_versions(uow); uow.source_fetches.add(failed); uow.engine_runs.add(engine_run); uow.commit()
    with db.unit_of_work() as uow:
        restored = uow.source_fetches.get("F1")
        assert restored.status is SourceFetchStatus.FAILED
        assert restored.record_count is None
        assert restored.error_category == "HTTP_503"
        assert uow.engine_runs.get("R1").status is EngineRunStatus.FAILED
