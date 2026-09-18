from datetime import datetime
import pytest
from dvk.application_services import NoShowApplicationService, ReplacementDutyApplicationService
from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.replacement_duty import ReplacementDuty
from dvk.security import AuthorizationError, Identity, Permission
from dvk.workstream_model import AssignmentProposal, DutyAssignment

VC = Identity("vc1", "Vrijwilligerscommissie", frozenset({Permission.MANAGE_NO_SHOWS}))
OTHER = Identity("other", "Onbevoegd", frozenset())

def _proposal(pid, sid):
    return AssignmentProposal(pid, sid, "P1", "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())

def _seed(db):
    with db.unit_of_work() as uow:
        for pid, aid, sid in (("P0", "A0", "S0"), ("P1R", "AR", "SR"), ("P2", "A2", "S2")):
            uow.proposals.add(_proposal(pid, sid))
            uow.assignments.add(DutyAssignment(aid, pid, sid, "P1", "member", 4, "vc1"))
        uow.commit()
    when = datetime(2026, 9, 18, 10)
    with db.unit_of_work() as uow:
        NoShowApplicationService(uow, VC).register(NoShowEvent("N1", "A0", "P1", when, when, "vc1", "2026/2027"))

def _replacement():
    return ReplacementDuty("R1", "N1", "AR", "P1", "2026/2027", datetime(2026, 9, 19, 9), "vc1")

def test_linking_replacement_keeps_counter_at_one(tmp_path):
    db = SQLiteDatabase(tmp_path / "link.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow:
        state = ReplacementDutyApplicationService(uow, VC).register_replacement(_replacement())
        assert state.counter == 1

def test_authorized_completion_resets_active_counter_to_zero(tmp_path):
    db = SQLiteDatabase(tmp_path / "complete.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow: ReplacementDutyApplicationService(uow, VC).register_replacement(_replacement())
    with db.unit_of_work() as uow:
        state = ReplacementDutyApplicationService(uow, VC).complete_replacement("R1", completed_at=datetime(2026, 9, 25, 22))
        assert state.counter == 0
        assert state.repaired_no_show_ids == ("N1",)
        assert uow.replacements.get("R1").completed_by == "vc1"

def test_unauthorized_member_cannot_confirm_replacement(tmp_path):
    db = SQLiteDatabase(tmp_path / "auth.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow: ReplacementDutyApplicationService(uow, VC).register_replacement(_replacement())
    with db.unit_of_work() as uow:
        with pytest.raises(AuthorizationError):
            ReplacementDutyApplicationService(uow, OTHER).complete_replacement("R1", completed_at=datetime(2026, 9, 25, 22))

def test_no_show_on_replacement_assignment_does_not_reset_and_becomes_stage_two(tmp_path):
    db = SQLiteDatabase(tmp_path / "replacement-no-show.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow: ReplacementDutyApplicationService(uow, VC).register_replacement(_replacement())
    when = datetime(2026, 9, 25, 20)
    with db.unit_of_work() as uow:
        assessment = NoShowApplicationService(uow, VC).register(NoShowEvent("N2", "AR", "P1", when, when, "vc1", "2026/2027"))
        assert assessment.counter == 2
    with db.unit_of_work() as uow:
        assert uow.replacements.get("R1").completed is False
