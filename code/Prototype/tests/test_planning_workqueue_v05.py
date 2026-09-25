"""Issue #12: FR-02–05; temporary planning never fabricates Sportlink facts."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Barrier

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import PlanningApplicationService, ProposalDecisionApplicationService
from dvk.candidate_selection import select_candidates
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod
from dvk.prioritization import prioritize_candidates
from dvk.proposals import create_assignment_proposal
from dvk.security import Identity, Permission
from dvk.staffing import StaffingNeed
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import DutyService

IDENTITY = Identity("planner", "Planner", frozenset({Permission.VIEW_PLANNING, Permission.DECIDE_PROPOSAL}))
JAN = replace(W_CASE_BY_ID["W08"], person=replace(W_CASE_BY_ID["W08"].person, name="Jan"))
OTHER = W_CASE_BY_ID["W07"]
A = DutyService("A", "Bardienst", datetime(2026, 9, 19, 9), datetime(2026, 9, 19, 13), "Clubhuis", 2)
SOURCE = StaffingNeed("A", 2, 3, 1, 1, 2)


def proposal(db, service=A, case=JAN, pid="P"):
    with db.unit_of_work() as uow:
        assessment = PlanningApplicationService(IDENTITY, uow=uow).assess_candidates(
            cases=(case,), service=service, team_memberships=(), matches=(), today=TODAY,
        )[0]
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    return create_assignment_proposal(pid, service, case, assessment, priority)


def approve(db, service=A, case=JAN, pid="P", aid="LOCAL", need=SOURCE):
    p = proposal(db, service, case, pid)
    with db.unit_of_work() as uow:
        return ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(
            p, service, case, assignment_id=aid, staffing_need=need,
        )


def state(db, service=A, need=SOURCE, case=JAN):
    with db.unit_of_work() as uow:
        app = PlanningApplicationService(IDENTITY, uow=uow)
        staffing = app.staffing_needs(services=(service,), source_needs=(need,))[0]
        assessment = app.assess_candidates(cases=(case,), service=service, team_memberships=(), matches=(), today=TODAY)[0]
        return staffing, assessment, app.active_planning()


def test_fr02_fr03_reload_staffing_minimum_then_maximum_and_source_separation(tmp_path):
    path = tmp_path / "planning.sqlite"
    db = SQLiteDatabase(path)
    before = state(db)[0]
    result = approve(db)
    # A completely new database/service instance is also the reload boundary.
    db = SQLiteDatabase(path)
    after, candidate, active = state(db)
    assert (before.open_need, after.open_need) == (1, 0)
    assert (before.remaining_capacity, after.remaining_capacity) == (2, 1)
    assert after.confirmed_occupancy == 1
    assert after.temporary_occupancy == 1
    assert after.planning_occupancy == 2
    assert result.updated_case is JAN
    assert result.updated_case.sportlink_duty is JAN.sportlink_duty
    assert active[0].assignment == result.assignment
    assert result.assignment.status == "temporary"
    assert active[0].service == A
    assert not candidate.eligible
    with db.unit_of_work() as uow:
        assert uow.assignments.get("LOCAL") is None  # no legacy no-show source
        assert uow.decisions.get("P").decided_by == "planner"
        overview = PlanningApplicationService(IDENTITY, uow=uow).build_overview(
            period=PlanningPeriod(date(2026, 9, 19), date(2026, 9, 19)),
            services=(A,), staffing_needs=(after,),
        )
        assert overview.services[0].confirmed_occupancy == 2  # no double count
        assert overview.services[0].source_occupancy == 1
    approve(db, case=OTHER, pid="P2", aid="LOCAL2", need=after)
    final = state(db)[0]
    assert (final.open_need, final.remaining_capacity, final.planning_occupancy) == (0, 0, 3)


def test_fr04_duplicate_hidden_and_refused_with_fresh_proposal_id(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    stale = proposal(db, pid="SECOND")
    approve(db)
    with db.unit_of_work() as uow:
        active = PlanningApplicationService(IDENTITY, uow=uow).active_planning()
        assert select_candidates((JAN,), A, (), (), TODAY, active_planning=active) == ()
        with pytest.raises(ValueError, match="same_service"):
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(
                stale, A, JAN, assignment_id="SECOND", staffing_need=SOURCE,
            )
        assert uow.proposals.get("SECOND") is None
    assert len(state(db)[2]) == 1


@pytest.mark.parametrize("start,end,eligible,preference", [
    (datetime(2026, 9, 19, 12, 30), datetime(2026, 9, 19, 17), False, "none"),
    (datetime(2026, 9, 19, 13), datetime(2026, 9, 19, 17), True, "avoid"),
    (datetime(2026, 9, 19, 13, 30), datetime(2026, 9, 19, 17), True, "avoid"),
    (datetime(2026, 9, 23, 19), datetime(2026, 9, 23, 22), True, "neutral"),
])
def test_fr04_interval_boundaries_and_other_day(tmp_path, start, end, eligible, preference):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    service = replace(A, service_id="B", starts_at=start, ends_at=end)
    need = replace(SOURCE, service_id="B")
    stale = proposal(db, service=service, pid="STALE")
    approve(db)
    _, assessment, active = state(db, service, need)
    assert (assessment.eligible, assessment.preference) == (eligible, preference)
    candidates = select_candidates((JAN,), service, (), (), TODAY, active_planning=active)
    assert bool(candidates) == eligible
    with db.unit_of_work() as uow:
        app = ProposalDecisionApplicationService(IDENTITY, uow=uow)
        if not eligible:
            with pytest.raises(ValueError, match="overlap"):
                app.approve(stale, service, JAN, assignment_id="BAD", staffing_need=need)
        elif preference == "avoid":
            with pytest.raises(ValueError, match="nood-/uitwijkkandidaat"):
                app.approve(stale, service, JAN, assignment_id="STALE", staffing_need=need)
    if eligible:
        fresh = proposal(db, service=service, pid="FRESH")
        assert fresh.suitability == ("emergency" if preference == "avoid" else "suitable")
        with db.unit_of_work() as uow:
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(fresh, service, JAN, assignment_id="B", staffing_need=need)
        assert len(state(db)[2]) == 2


def test_fr04_exact_requested_nonoverlap_example_and_undo_reassesses(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    morning = replace(A, ends_at=datetime(2026, 9, 19, 12))
    afternoon = replace(A, service_id="B", starts_at=datetime(2026, 9, 19, 12, 30), ends_at=datetime(2026, 9, 19, 17))
    need = replace(SOURCE, service_id="B")
    approve(db, service=morning)
    assert state(db, afternoon, need)[1].preference == "avoid"
    with db.unit_of_work() as uow:
        ProposalDecisionApplicationService(IDENTITY, uow=uow).undo("LOCAL")
    assert state(db, afternoon, need)[1].preference == "neutral"


def test_fr03_central_maximum_ignores_stale_ui_capacity(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    third = replace(JAN, person=replace(JAN.person, person_id="THIRD"), sportlink_duty=replace(JAN.sportlink_duty, person_id="THIRD"))
    stale = proposal(db, case=third, pid="THIRD")
    approve(db)
    approve(db, case=OTHER, pid="P2", aid="LOCAL2")
    with db.unit_of_work() as uow:
        with pytest.raises(ValueError, match="remaining service capacity"):
            ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(stale, A, third, assignment_id="THIRD", staffing_need=SOURCE)
        assert uow.proposals.get("THIRD") is None
    assert len(state(db)[2]) == 2


def test_fr05_undo_only_selected_planning_restores_capacity_and_candidates(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    approve(db)
    approve(db, case=OTHER, pid="P2", aid="LOCAL2")
    with db.unit_of_work() as uow:
        ProposalDecisionApplicationService(IDENTITY, uow=uow).undo("LOCAL")
    staffing, candidate, active = state(db)
    assert (staffing.open_need, staffing.remaining_capacity) == (0, 1)
    assert candidate.eligible and candidate.preference == "neutral"
    assert [entry.assignment.assignment_id for entry in active] == ["LOCAL2"]
    with db.unit_of_work() as uow:
        app = ProposalDecisionApplicationService(IDENTITY, uow=uow)
        with pytest.raises(ValueError, match="niet meer actief"):
            app.undo("LOCAL")
        app.undo("LOCAL2")
        assert not uow.no_shows.all()
    assert state(db)[0] == SOURCE
    approve(db, pid="AGAIN", aid="AGAIN")


def test_batch_duplicate_person_and_partial_failure_leave_no_active_planning(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    p1, p2 = proposal(db), proposal(db, pid="P2")
    with db.unit_of_work() as uow:
        app = ProposalDecisionApplicationService(IDENTITY, uow=uow)
        with pytest.raises(ValueError, match="person can only be selected once"):
            app.approve_many(((p1, JAN, "1"), (p2, JAN, "2")), A, SOURCE)
        assert not uow.temporary_planning.all()
    p2 = proposal(db, case=OTHER, pid="OTHER")
    with db.unit_of_work() as uow:
        app = ProposalDecisionApplicationService(IDENTITY, uow=uow)
        with pytest.raises(Exception):
            app.approve_many(((p1, JAN, "SAME"), (p2, OTHER, "SAME")), A, SOURCE)
        # Even catching the exception inside the UoW cannot commit a partial batch.
        uow.commit()
    assert state(db)[2] == ()
    with db.unit_of_work() as uow:
        assert uow.proposals.get("P") is None
        assert uow.decisions.get("P") is None


def test_parallel_confirmations_cannot_overfill_last_place(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    db.initialize()
    p1, p2 = proposal(db), proposal(db, case=OTHER, pid="P2")
    barrier = Barrier(2)
    need = replace(SOURCE, confirmed_occupancy=2, open_need=0, remaining_capacity=1)

    def confirm(p, case, aid):
        with db.unit_of_work() as uow:
            barrier.wait(timeout=5)
            try:
                ProposalDecisionApplicationService(IDENTITY, uow=uow).approve(p, A, case, assignment_id=aid, staffing_need=need)
                return "ok"
            except ValueError as exc:
                assert "remaining service capacity" in str(exc)
                return "full"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [pool.submit(confirm, p1, JAN, "1"), pool.submit(confirm, p2, OTHER, "2")]
        assert sorted(f.result() for f in results) == ["full", "ok"]
    assert len(state(db)[2]) == 1


def test_same_demo_id_in_another_week_is_a_different_occurrence(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    approve(db)
    next_week = replace(A, starts_at=A.starts_at + timedelta(days=7), ends_at=A.ends_at + timedelta(days=7))
    staffing, candidate, _ = state(db, next_week)
    assert staffing == SOURCE
    assert candidate.eligible and candidate.preference == "neutral"


def test_undo_and_read_require_authorization(tmp_path):
    db = SQLiteDatabase(tmp_path / "planning.sqlite")
    approve(db)
    with db.unit_of_work() as uow:
        unauthorized = Identity("visitor", "Visitor", frozenset())
        with pytest.raises(PermissionError):
            ProposalDecisionApplicationService(unauthorized, uow=uow).undo("LOCAL")
        with pytest.raises(PermissionError):
            PlanningApplicationService(unauthorized, uow=uow).active_planning()
    assert len(state(db)[2]) == 1


def test_streamlit_reload_and_undo_use_persisted_workqueue(tmp_path):
    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1] / "streamlit_app.py").read_text())
    from dvk.demo_data_v05 import demo_planning_data
    services, needs, _, _ = demo_planning_data(date(2026, 9, 14))
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    approve(db, service=services[0], need=needs[0])
    for _ in range(2):
        # New session, empty session_state; only SQLite preserves the position.
        app = AppTest.from_file(str(script), default_timeout=15).run()
        app.date_input[0].set_value(date(2026, 9, 14)).run()
        assert not app.exception
        selector = next(w for w in app.selectbox if w.label == "Tijdelijke inroostering")
        assert "wo 16-09 19:00–22:00" in selector.options[0]
        assert "LOCAL" not in selector.options[0]
        table = app.dataframe[0].value
        assert table.iloc[0]["Open minimum"] == 0
        assert table.iloc[0]["Vrije capaciteit"] == 1
        assert table.iloc[0]["Sportlink"] == 1
        assert table.iloc[0]["Tijdelijk DVK"] == 1
    next(w for w in app.button if w.label == "Tijdelijke inroostering ongedaan maken").click().run()
    assert not app.exception
    assert app.dataframe[0].value.iloc[0]["Open minimum"] == 1
    assert app.dataframe[0].value.iloc[0]["Vrije capaciteit"] == 2
    assert state(db)[2] == ()


def test_streamlit_confirmation_refreshes_staffing_and_candidate_list(tmp_path):
    script = tmp_path / "streamlit_app.py"
    script.write_text((Path(__file__).parents[1] / "streamlit_app.py").read_text())
    app = AppTest.from_file(str(script), default_timeout=15).run()
    app.date_input[0].set_value(date(2026, 9, 14))
    app.session_state["selected_service_id"] = "BAR-WO-1"
    app.run()
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    app.checkbox[0].check().run()
    assert state(db)[2] == ()  # Selecting alone is not human confirmation.
    next(w for w in app.button if w.label == "Selectie bevestigen").click().run()
    assert not app.exception
    assert app.dataframe[0].value.iloc[0]["Open minimum"] == 0
    assert app.dataframe[0].value.iloc[0]["Vrije capaciteit"] == 1
    assert len(state(db)[2]) == 1
    assert not any("W08P" in w.key for w in app.checkbox)
    # Minimum reached: a second explicit confirmation can still fill maximum.
    app.checkbox[0].check().run()
    next(w for w in app.button if w.label == "Selectie bevestigen").click().run()
    assert not app.exception
    assert app.dataframe[0].value.iloc[0]["Vrije capaciteit"] == 0
    assert len(state(db)[2]) == 2
    assert not app.checkbox
    next(w for w in app.button if w.label == "Tijdelijke inroostering ongedaan maken").click().run()
    assert not app.exception
    assert len(state(db)[2]) == 1
    assert any("W08P" in w.key for w in app.checkbox)
    app.checkbox[0].check().run()
    next(w for w in app.button if w.label == "Selectie bevestigen").click().run()
    assert not app.exception
    assert len(state(db)[2]) == 2
