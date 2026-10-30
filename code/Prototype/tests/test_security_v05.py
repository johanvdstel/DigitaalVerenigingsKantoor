from datetime import datetime, timezone

import pytest

from dvk.application_services import ImportApplicationService
from dvk.import_management import ImportBatch, ImportStatus, SnapshotRecord
from dvk.persistence import SQLiteDatabase
from dvk.security import AuthorizationError, Authorizer, Identity, Permission

NOW = datetime(2026, 9, 17, 10, 0, tzinfo=timezone.utc)


def identity(subject: str, *permissions: Permission) -> Identity:
    return Identity(subject, subject.title(), frozenset(permissions))


def test_authorizer_uses_explicit_permissions_not_role_names():
    authorizer = Authorizer()
    user = identity("vrijwilligerscommissie", Permission.VIEW_PLANNING)
    authorizer.require(user, Permission.VIEW_PLANNING)
    with pytest.raises(AuthorizationError):
        authorizer.require(user, Permission.CONFIRM_IMPORT)


def test_unauthorized_import_confirmation_has_no_partial_changes(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    batch = ImportBatch("B1", "Sportlink", "leden", "2026-2027", NOW, "uploader",
                        ImportStatus.AWAITING_CONFIRMATION, "ok")
    records = (SnapshotRecord("PREVIEW", "P1", "raw", "canonical", "prov"),)
    with db.unit_of_work() as uow:
        uow.import_batches.add(batch)
        uow.commit()
    with db.unit_of_work() as uow:
        app = ImportApplicationService(uow, identity("viewer", Permission.PREVIEW_IMPORT))
        assert len(app.preview(batch, records).differences) == 1
        with pytest.raises(AuthorizationError):
            app.confirm(batch, records, snapshot_id="S1", confirmed_at=NOW)
        assert uow.snapshots.get("S1") is None
        assert uow.import_batches.get("B1").status is ImportStatus.AWAITING_CONFIRMATION
    with db.unit_of_work() as uow:
        assert uow.snapshots.get("S1") is None
        assert uow.import_batches.get("B1").status is ImportStatus.AWAITING_CONFIRMATION


def test_authenticated_identity_is_recorded_as_confirmer(tmp_path):
    db = SQLiteDatabase(tmp_path / "dvk.sqlite")
    batch = ImportBatch("B1", "Sportlink", "leden", "2026-2027", NOW, "uploader",
                        ImportStatus.AWAITING_CONFIRMATION, "ok")
    records = (SnapshotRecord("PREVIEW", "P1", "raw", "canonical", "prov"),)
    with db.unit_of_work() as uow:
        uow.import_batches.add(batch)
        uow.commit()
    with db.unit_of_work() as uow:
        app = ImportApplicationService(uow, identity("importbeheerder", Permission.CONFIRM_IMPORT))
        app.confirm(batch, records, snapshot_id="S1", confirmed_at=NOW)
    with db.unit_of_work() as uow:
        assert uow.import_batches.get("B1").confirmed_by == "importbeheerder"
