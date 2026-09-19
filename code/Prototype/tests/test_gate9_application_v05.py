from datetime import datetime

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.security import AuthorizationError, Identity, Permission
from dvk.workstream_model import AssignmentProposal, DutyAssignment


def identity(*permissions):
    return Identity("planner", "Planner", frozenset(permissions))


def seed(uow):
    proposal = AssignmentProposal("P1", "S1", "MEM1", "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())
    uow.proposals.add(proposal)
    uow.assignments.add(DutyAssignment("A1", "P1", "S1", "MEM1", "member", 4, "planner"))
    uow.commit()


def event(assignment="A1", person="MEM1"):
    when = datetime(2026, 9, 18, 10)
    return NoShowEvent("N1", assignment, person, when, when, "planner", "2026/2027")


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
        corrected = NoShowApplicationService(uow, allowed).revoke("N1", reason="ten onrechte geregistreerd", corrected_at=datetime(2026, 9, 18, 12))
        assert corrected.status == "revoked"
        assert corrected.corrected_by == "planner"
