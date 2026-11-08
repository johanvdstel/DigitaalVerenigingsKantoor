from datetime import date, datetime, timezone

from dvk.application_services import EngineRunApplicationService, ImportApplicationService
from dvk.import_management import ImportBatch, ImportStatus, SnapshotRecord
from dvk.persistence import SQLiteDatabase
from dvk.run_context import EngineRun, EngineRunStatus
from dvk.security import Identity, Permission
from dvk.versioning import ConfigVersion, PolicyVersion, SoftwareVersion

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc)
START = date(2026, 9, 14)
END = date(2026, 9, 20)
COMMIT = "dbf34d01f0e407578549562c94bfcd56e2cc98c1"
PLANNER = Identity("planner", "Planner", frozenset({
    Permission.PREVIEW_IMPORT, Permission.CONFIRM_IMPORT, Permission.RECORD_ENGINE_RUN
}))


def test_import_application_service_previews_then_confirms_atomically(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    batch = ImportBatch("B1", "Sportlink", "leden", "2026-2027", NOW, "tester",
                        ImportStatus.AWAITING_CONFIRMATION, "ok")
    records = (SnapshotRecord("PREVIEW", "P1", "raw", "canonical", "prov"),)
    with db.unit_of_work() as uow:
        uow.import_batches.add(batch)
        uow.commit()
    with db.unit_of_work() as uow:
        app = ImportApplicationService(uow, PLANNER)
        preview = app.preview(batch, records)
        assert [(d.record_key, d.change_type) for d in preview.differences] == [("P1", "RECORD_ADDED")]
        assert uow.snapshots.latest("Sportlink", "leden", "2026-2027") is None
        snapshot = app.confirm(batch, records, snapshot_id="S1", confirmed_at=NOW)
        assert snapshot.snapshot_id == "S1"
    with db.unit_of_work() as uow:
        assert uow.snapshots.get("S1") is not None
        confirmed = uow.import_batches.get("B1")
        assert confirmed.status is ImportStatus.CONFIRMED
        assert confirmed.confirmed_by == "planner"


def test_engine_run_application_service_records_versioned_run(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    run = EngineRun("R1", NOW, "planner", START, END, EngineRunStatus.COMPLETED,
                    (), (), "policy-v0.5", "shift-catalog-v1", "dvk-0.5", NOW)
    with db.unit_of_work() as uow:
        uow.policy_versions.add(PolicyVersion.create("policy-v0.5", {"required_hours": 10}, created_at=NOW, created_by="tester", effective_from=START))
        uow.config_versions.add(ConfigVersion.create("shift-catalog-v1", {"BAR": {"minimum": 2, "maximum": 4}}, created_at=NOW, created_by="tester", effective_from=START))
        uow.software_versions.add(SoftwareVersion("dvk-0.5", "dvk-0.5", COMMIT, NOW))
        app = EngineRunApplicationService(uow, PLANNER)
        assert app.record(run) == run
    with db.unit_of_work() as uow:
        assert uow.engine_runs.get("R1") == run
