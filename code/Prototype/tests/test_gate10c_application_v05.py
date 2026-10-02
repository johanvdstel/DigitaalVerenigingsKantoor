from dataclasses import replace
from datetime import datetime

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.demo_data_v05 import demo_candidate_cases, demo_planning_data
from dvk.no_show import NoShowEvent, season_id
from dvk.persistence import SQLiteDatabase
from dvk.security import AuthorizationError, Identity, Permission
from dvk.workstream_model import AssignmentProposal, DutyAssignment

VC = Identity("vc1", "Vrijwilligerscommissie", frozenset({Permission.MANAGE_NO_SHOWS}))
OTHER = Identity("other", "Onbevoegd", frozenset())


def _seed(db):
    with db.unit_of_work() as uow:
        for i in range(1, 7):
            uow.proposals.add(AssignmentProposal(f"P{i}", f"S{i}", "MEM1", "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ()))
            uow.assignments.add(DutyAssignment(f"A{i}", f"P{i}", f"S{i}", "MEM1", "member", 4, "vc1"))
        uow.commit()


def _event(i, when=None):
    when = when or datetime(2026, 9, i, 10)
    return NoShowEvent(f"N{i}", f"A{i}", "MEM1", when, when, "vc1", season_id(when.date()))


@pytest.fixture
def database(tmp_path):
    db = SQLiteDatabase(tmp_path / "no-shows.sqlite")
    db.initialize()
    _seed(db)
    with db.unit_of_work() as uow:
        for i in range(1, 6):
            NoShowApplicationService(uow, VC).register(_event(i))
    return db


@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
def test_authorized_revocation_of_any_stage_is_separate_and_survives_reopen(database, number):
    with database.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        original = uow.no_shows.get(f"N{number}")
        payload_before = uow._connection.execute("SELECT payload FROM no_show_events WHERE no_show_id=?", (original.no_show_id,)).fetchone()
        revocation = app.revoke(original.no_show_id, reason="  expliciet besluit  ", revoked_at=datetime(2026, 9, 30, 12))
        assert (revocation.revoked_by, revocation.reason, revocation.revoked_at) == ("vc1", "expliciet besluit", datetime(2026, 9, 30, 12))
    with database.unit_of_work() as uow:
        assert uow.no_shows.get(original.no_show_id) == original
        assert uow._connection.execute("SELECT payload FROM no_show_events WHERE no_show_id=?", (original.no_show_id,)).fetchone() == payload_before
        assert uow.no_show_revocations.for_no_show(original.no_show_id) == revocation
        assert NoShowApplicationService(uow, VC).current_state("MEM1", "2026/2027").counter == 4
        with pytest.raises(ValueError, match="al ingetrokken"):
            NoShowApplicationService(uow, VC).revoke(original.no_show_id, reason="nogmaals", revoked_at=datetime(2026, 10, 1))
        assert len(uow.no_show_revocations.for_person_season("MEM1", "2026/2027")) == 1


@pytest.mark.parametrize("reason", ["", " ", "\t\n"])
def test_empty_reason_has_no_partial_write(database, reason):
    with database.unit_of_work() as uow:
        with pytest.raises(ValueError, match="toelichting"):
            NoShowApplicationService(uow, VC).revoke("N2", reason=reason, revoked_at=datetime(2026, 9, 30))
        assert uow.no_show_revocations.for_no_show("N2") is None
        assert uow.no_shows.get("N2") == _event(2)


def test_unauthorized_revocation_has_no_partial_write(database):
    with database.unit_of_work() as uow:
        with pytest.raises(AuthorizationError):
            NoShowApplicationService(uow, OTHER).revoke("N2", reason="besluit", revoked_at=datetime(2026, 9, 30))
        assert uow.no_show_revocations.for_no_show("N2") is None
        assert uow.no_shows.get("N2") == _event(2)


def test_unknown_no_show_is_rejected(database):
    with database.unit_of_work() as uow:
        with pytest.raises(ValueError, match="Onbekende"):
            NoShowApplicationService(uow, VC).revoke("missing", reason="besluit", revoked_at=datetime(2026, 9, 30))
        assert uow.no_show_revocations.for_person_season("MEM1", "2026/2027") == ()


def test_current_three_to_two_and_next_registration_uses_remaining_facts(tmp_path):
    db = SQLiteDatabase(tmp_path / "three.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        for i in range(1, 4):
            app.register(_event(i))
        assert app.current_state("MEM1", "2026/2027").counter == 3
        app.revoke("N2", reason="besluit", revoked_at=datetime(2026, 9, 30))
        state = app.current_state("MEM1", "2026/2027")
        assert (state.counter, state.assessment.fine_eur, state.assessment.suspension_matches) == (2, 75, 1)
        # Historical assessment is retained, current state is derived separately.
        assert uow.sanctions.get("N3").counter == 3
        assert app.register(_event(4)).counter == 3


def test_season_transition_preserves_both_facts_without_reset(tmp_path):
    db = SQLiteDatabase(tmp_path / "seasons.sqlite"); db.initialize(); _seed(db)
    old1 = _event(1, datetime(2026, 6, 29, 10))
    old2 = _event(2, datetime(2026, 6, 30, 10))
    with db.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        app.register(old1); app.register(old2)
        revoked = app.revoke("N2", reason="besluit vorig seizoen", revoked_at=datetime(2026, 7, 2))
        assert app.current_state("MEM1", "2026/2027").counter == 0
        assert app.current_state("MEM1", "2025/2026").counter == 1
        assert app.register(_event(3, datetime(2026, 7, 1, 10))).counter == 1
    with db.unit_of_work() as uow:
        assert uow.no_shows.for_person_season("MEM1", "2025/2026") == (old1, old2)
        assert uow.no_show_revocations.for_person_season("MEM1", "2025/2026") == (revoked,)
        assert uow.no_show_revocations.for_person_season("MEM1", "2026/2027") == ()
        assert NoShowApplicationService(uow, VC).current_state("MEM1", "2026/2027").counter == 1


def test_other_assignments_and_no_shows_never_infer_revocation(tmp_path):
    db = SQLiteDatabase(tmp_path / "no-inference.sqlite"); db.initialize(); _seed(db)
    with db.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        app.register(_event(1))
        assert len(app.available_assignments()) == 6
        assert app.current_state("MEM1", "2026/2027").counter == 1
        app.register(_event(2))
        app.revocable_no_shows()
        assert app.current_state("MEM1", "2026/2027").counter == 2
        assert uow.no_show_revocations.for_person_season("MEM1", "2026/2027") == ()


def test_public_queries_require_permission_before_reading():
    app = NoShowApplicationService(None, OTHER)
    for query in (app.assignment_contexts, app.revocable_no_shows, lambda: app.current_state("MEM1", "2026/2027")):
        with pytest.raises(AuthorizationError):
            query()
    with pytest.raises(AuthorizationError):
        app.revoke("N1", reason="besluit", revoked_at=datetime(2026, 9, 30))


def test_public_revocation_query_is_read_only_and_excludes_revoked(database):
    with database.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        before = uow._connection.total_changes
        assert len(app.revocable_no_shows()) == 5
        assert uow._connection.total_changes == before
        app.revoke("N2", reason="besluit", revoked_at=datetime(2026, 9, 30))
    with database.unit_of_work() as uow:
        assert [r.no_show.no_show_id for r in NoShowApplicationService(uow, VC).revocable_no_shows()] == ["N1", "N3", "N4", "N5"]


def test_assignment_context_uses_only_unique_exact_ids_and_preserves_recent_limit(database):
    services, _, _, _ = demo_planning_data(datetime(2026, 9, 14).date())
    service = replace(services[2], service_id="S1")
    person = replace(demo_candidate_cases()[2].person, person_id="MEM1")
    with database.unit_of_work() as uow:
        app = NoShowApplicationService(uow, VC)
        contexts = app.assignment_contexts(services=(service,), persons=(person,))
        context = next(c for c in contexts if c.assignment.assignment_id == "A1")
        assert context.service == service
        assert context.person_name == "Jeugdlid Thuis"
        assert [c.assignment.assignment_id for c in app.assignment_contexts(limit=1)] == ["A6"]
        for supplied_services, supplied_persons in (
            ((), ()),
            ((replace(service, service_id="OTHER"),), (replace(person, person_id="OTHER"),)),
            ((service, replace(service, location="andere locatie")), (person, replace(person, name="andere naam"))),
        ):
            missing = next(c for c in app.assignment_contexts(services=supplied_services, persons=supplied_persons) if c.assignment.assignment_id == "A1")
            assert missing.service is None
            assert missing.person_name is None
        rows = app.revocable_no_shows(services=(service,), persons=(person,))
        assert rows[0].assignment == context
