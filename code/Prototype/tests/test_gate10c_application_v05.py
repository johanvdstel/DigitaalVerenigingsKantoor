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


def test_public_overview_preserves_link_choices_pending_and_completed_flow(tmp_path):
    db = SQLiteDatabase(tmp_path / "overview.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow:
        app = ReplacementDutyApplicationService(uow, VC)
        before = uow._connection.total_changes
        overview = app.overview()
        assert uow._connection.total_changes == before
        assert [o.no_show.no_show_id for o in overview.link_options] == ["N1"]
        option = overview.link_options[0]
        assert option.original_assignment.assignment.assignment_id == "A0"
        assert [c.assignment.assignment_id for c in option.available_assignments] == ["A2", "AR"]
        assert not overview.pending and not overview.with_no_show
        app.register_replacement(_replacement())
        linked = app.overview()
        assert not linked.link_options
        assert [r.replacement.replacement_id for r in linked.pending] == ["R1"]
        assert linked.pending[0].assignment.assignment.assignment_id == "AR"
        assert not linked.with_no_show
        state = app.complete_replacement("R1", completed_at=datetime(2026, 9, 25, 22))
        assert state.counter == 0
        completed = app.overview()
        assert not completed.link_options and not completed.pending and not completed.with_no_show


def test_valid_replacement_no_show_is_separate_and_revocation_restores_pending(tmp_path):
    db = SQLiteDatabase(tmp_path / "overview-no-show.sqlite"); db.initialize(); _seed(db)
    when = datetime(2026, 9, 25, 20)
    with db.unit_of_work() as uow:
        app = ReplacementDutyApplicationService(uow, VC)
        app.register_replacement(_replacement())
        NoShowApplicationService(uow, VC).register(NoShowEvent("N2", "AR", "P1", when, when, "vc1", "2026/2027"))
    # Query after reopen: status comes from persisted facts, not UI session state.
    with db.unit_of_work() as uow:
        app = ReplacementDutyApplicationService(uow, VC)
        overview = app.overview()
        assert not overview.pending
        assert [r.replacement.replacement_id for r in overview.with_no_show] == ["R1"]
        assert overview.with_no_show[0].assignment.assignment.assignment_id == "AR"
        assert uow.replacements.get("R1").completed is False
        NoShowApplicationService(uow, VC).revoke("N2", reason="registratiefout", corrected_at=datetime(2026, 9, 26))
        corrected = app.overview()
        assert not corrected.with_no_show
        assert [r.replacement.replacement_id for r in corrected.pending] == ["R1"]


def test_overview_does_not_hide_no_show_when_completion_is_already_stored(tmp_path):
    db = SQLiteDatabase(tmp_path / "completed-no-show.sqlite"); db.initialize(); _seed(db)
    when = datetime(2026, 9, 25, 20)
    with db.unit_of_work() as uow:
        app = ReplacementDutyApplicationService(uow, VC)
        app.register_replacement(_replacement())
        app.complete_replacement("R1", completed_at=datetime(2026, 9, 25, 22))
        NoShowApplicationService(uow, VC).register(NoShowEvent("N2", "AR", "P1", when, when, "vc1", "2026/2027"))
        overview = app.overview()
        assert not overview.pending
        assert [r.replacement.replacement_id for r in overview.with_no_show] == ["R1"]
        assert uow.replacements.get("R1").completed is True


def test_public_queries_require_existing_no_show_permission_before_reading():
    # None as UoW proves authorization fails before repository access.
    with pytest.raises(AuthorizationError):
        ReplacementDutyApplicationService(None, OTHER).overview()
    with pytest.raises(AuthorizationError):
        NoShowApplicationService(None, OTHER).assignment_contexts()


def test_revoked_original_no_show_is_not_offered_for_linking(tmp_path):
    db = SQLiteDatabase(tmp_path / "revoked-original.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow:
        NoShowApplicationService(uow, VC).revoke("N1", reason="registratiefout", corrected_at=datetime(2026, 9, 19))
        assert not ReplacementDutyApplicationService(uow, VC).overview().link_options


def test_assignment_context_uses_only_unique_exact_ids_and_preserves_recent_limit(tmp_path):
    from dataclasses import replace
    from dvk.demo_data_v05 import demo_candidate_cases, demo_planning_data
    db = SQLiteDatabase(tmp_path / "human-context.sqlite"); db.initialize(); _seed(db)
    services, _, _, _ = demo_planning_data(datetime(2026, 9, 14).date())
    service = replace(services[2], service_id="SR")
    person = replace(demo_candidate_cases()[2].person, person_id="P1")
    with db.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        contexts = app.assignment_contexts(services=(service,), persons=(person,))
        replacement_context = next(c for c in contexts if c.assignment.assignment_id == "AR")
        assert replacement_context.service == service
        assert replacement_context.person_name == "Jeugdlid Thuis"
        assert [c.assignment.assignment_id for c in app.assignment_contexts(limit=1)] == ["A2"]
        for supplied_services, supplied_persons in (
            ((), ()),
            ((replace(service, service_id="OTHER"),), (replace(person, person_id="OTHER"),)),
            ((service, replace(service, location="andere locatie")), (person, replace(person, name="andere naam"))),
        ):
            missing = next(c for c in app.assignment_contexts(services=supplied_services, persons=supplied_persons) if c.assignment.assignment_id == "AR")
            assert missing.service is None
            assert missing.person_name is None
        replacement_app = ReplacementDutyApplicationService(uow, VC)
        replacement_app.register_replacement(_replacement())
        overview = replacement_app.overview(services=(service,), persons=(person,))
        assert overview.pending[0].assignment == replacement_context
