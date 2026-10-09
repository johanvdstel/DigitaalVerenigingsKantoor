from datetime import datetime

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.security import AuthorizationError, Identity, Permission
from dvk.workstream_model import AssignmentProposal, DutyAssignment
from sportlink_fixtures import booking, seed_bookings


def identity(*permissions):
    return Identity("planner", "Planner", frozenset(permissions))


def seed(uow):
    seed_bookings(uow, [booking()])


def event(assignment=None, person="MEM1"):
    source = booking()
    when = source.starts_at
    return NoShowEvent("N1", assignment or source.assignment_id, person, when, when, "planner", "2026/2027", source)


def test_register_requires_existing_assignment_and_persists_assessment(tmp_path):
    db = SQLiteDatabase(tmp_path / "app.sqlite"); db.initialize()
    with db.unit_of_work() as uow: seed(uow)
    with db.unit_of_work() as uow:
        result = NoShowApplicationService(uow, identity(Permission.MANAGE_NO_SHOWS)).register(event())
        assert result.counter == 1
        assert result.replacement_service_required is True
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") is not None
        assert uow.sanctions.get("N1").counter == 1


def test_register_rejects_unknown_assignment(tmp_path):
    db = SQLiteDatabase(tmp_path / "unknown.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        service = NoShowApplicationService(uow, identity(Permission.MANAGE_NO_SHOWS))
        with pytest.raises(ValueError, match="existing inroostering"):
            service.register(event(assignment="missing"))


def test_register_rejects_person_mismatch(tmp_path):
    db = SQLiteDatabase(tmp_path / "mismatch.sqlite"); db.initialize()
    with db.unit_of_work() as uow: seed(uow)
    with db.unit_of_work() as uow:
        service = NoShowApplicationService(uow, identity(Permission.MANAGE_NO_SHOWS))
        with pytest.raises(ValueError, match="match inroostering"):
            service.register(event(person="OTHER"))


def test_unauthorized_no_show_action_has_no_partial_write(tmp_path):
    db = SQLiteDatabase(tmp_path / "unauthorized.sqlite"); db.initialize()
    with db.unit_of_work() as uow: seed(uow)
    with db.unit_of_work() as uow:
        with pytest.raises(AuthorizationError):
            NoShowApplicationService(uow, identity()).register(event())
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") is None


def test_revoke_is_authorized_auditable_correction(tmp_path):
    db = SQLiteDatabase(tmp_path / "revoke.sqlite"); db.initialize()
    allowed = identity(Permission.MANAGE_NO_SHOWS)
    with db.unit_of_work() as uow: seed(uow)
    with db.unit_of_work() as uow: NoShowApplicationService(uow, allowed).register(event())
    with db.unit_of_work() as uow:
        corrected = NoShowApplicationService(uow, allowed).revoke("N1", reason="ten onrechte geregistreerd", revoked_at=datetime(2026, 9, 18, 12))
        assert corrected.no_show_id == "N1"
        assert corrected.revoked_by == "planner"
        assert uow.no_shows.get("N1") == event()
        assert uow.no_show_revocations.for_no_show("N1") == corrected
