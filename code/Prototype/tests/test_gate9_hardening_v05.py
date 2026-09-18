from datetime import datetime

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.security import Identity, Permission
from dvk.workstream_model import AssignmentProposal, DutyAssignment


IDENTITY = Identity("planner", "Planner", frozenset({Permission.MANAGE_NO_SHOWS}))


def _seed(uow):
    proposal = AssignmentProposal("P-H", "S1", "MEM1", "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())
    uow.proposals.add(proposal)
    uow.assignments.add(DutyAssignment("A-H", "P-H", "S1", "MEM1", "member", 4, "planner"))
    uow.commit()


def _event(no_show_id="N-H"):
    when = datetime(2026, 9, 18, 10)
    return NoShowEvent(no_show_id, "A-H", "MEM1", when, when, "planner", "2026/2027")


def test_same_assignment_cannot_receive_second_no_show(tmp_path):
    db = SQLiteDatabase(tmp_path / "duplicate.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow: NoShowApplicationService(uow, IDENTITY).register(_event())
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="al een no-show"):
            NoShowApplicationService(uow, IDENTITY).register(_event("N-H-2"))


def test_revoked_no_show_has_no_effective_sanction(tmp_path):
    db = SQLiteDatabase(tmp_path / "revoke-sanction.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow: NoShowApplicationService(uow, IDENTITY).register(_event())
    with db.unit_of_work() as uow:
        NoShowApplicationService(uow, IDENTITY).revoke("N-H", reason="fout geregistreerd", corrected_at=datetime(2026, 9, 18, 12))
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N-H").status == "revoked"
        assert uow.sanctions.get("N-H") is None


def test_no_show_application_service_exposes_assignments_without_ui_sql(tmp_path):
    db = SQLiteDatabase(tmp_path / "read.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow:
        rows = NoShowApplicationService(uow, IDENTITY).available_assignments()
        assert [row.assignment_id for row in rows] == ["A-H"]
