from datetime import datetime

from dvk.no_show import NoShowEvent, NoShowRevocation, assess_sanction, season_id
from dvk.persistence import SQLiteDatabase
from dvk.workstream_model import AssignmentProposal, DutyAssignment


def _seed_assignment(uow, person="P1"):
    proposal = AssignmentProposal("P-NO", "S1", person, "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())
    assignment = DutyAssignment("A-NO", proposal.proposal_id, "S1", person, "member", 4, "planner")
    uow.proposals.add(proposal)
    uow.assignments.add(assignment)


def test_no_show_and_sanction_survive_database_reopen(tmp_path):
    db = SQLiteDatabase(tmp_path / "gate9.sqlite")
    db.initialize()
    when = datetime(2026, 9, 18, 10)
    event = NoShowEvent("N1", "A-NO", "P1", when, when, "planner", season_id(when.date()))
    sanction = assess_sanction(event, ())
    with db.unit_of_work() as uow:
        _seed_assignment(uow)
        uow.no_shows.add(event)
        uow.sanctions.add(sanction)
        uow.commit()
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("N1") == event
        assert uow.sanctions.get("N1") == sanction
        assert uow.no_shows.for_person_season("P1", "2026/2027") == (event,)


def test_revocation_is_separate_fact_without_changing_history(tmp_path):
    db = SQLiteDatabase(tmp_path / "gate9-revoke.sqlite")
    db.initialize()
    when = datetime(2026, 9, 18, 10)
    event = NoShowEvent("N1", "A-NO", "P1", when, when, "planner", "2026/2027")
    revoked = NoShowRevocation("R1", "N1", "incorrect registered", datetime(2026, 9, 18, 11), "planner")
    with db.unit_of_work() as uow:
        _seed_assignment(uow)
        uow.no_shows.add(event)
        uow.commit()
    with db.unit_of_work() as uow:
        uow.no_show_revocations.add(revoked)
        uow.commit()
    with db.unit_of_work() as uow:
        stored = uow.no_shows.get("N1")
        assert stored == event
        assert uow.no_show_revocations.for_no_show("N1") == revoked
