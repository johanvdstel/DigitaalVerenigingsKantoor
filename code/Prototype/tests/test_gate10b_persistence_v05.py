from datetime import datetime

import pytest

from dvk.no_show import NoShowEvent
from dvk.persistence import SQLiteDatabase
from dvk.replacement_duty import ReplacementDuty, active_sanction_state
from dvk.workstream_model import AssignmentProposal, DutyAssignment


def _proposal(identifier, service, person="P1"):
    return AssignmentProposal(identifier, service, person, "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ())


def _seed(uow):
    uow.proposals.add(_proposal("P-ORIG", "S-ORIG"))
    uow.assignments.add(DutyAssignment("A-ORIG", "P-ORIG", "S-ORIG", "P1", "member", 4, "planner"))
    uow.proposals.add(_proposal("P-REPL", "S-REPL"))
    uow.assignments.add(DutyAssignment("A-REPL", "P-REPL", "S-REPL", "P1", "member", 4, "planner"))
    when = datetime(2026, 9, 18, 10)
    uow.no_shows.add(NoShowEvent("N1", "A-ORIG", "P1", when, when, "planner", "2026/2027"))
    uow.commit()


def _replacement(completed=True):
    return ReplacementDuty(
        "R1", "N1", "A-REPL", "P1", "2026/2027",
        datetime(2026, 9, 20, 9), "planner",
        datetime(2026, 9, 21, 12) if completed else None,
        "planner" if completed else None,
    )


def test_replacement_survives_database_reopen_and_reconstructs_active_state(tmp_path):
    db = SQLiteDatabase(tmp_path / "replacement.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow:
        uow.replacements.add(_replacement())
        uow.commit()
    with db.unit_of_work() as uow:
        stored = uow.replacements.get("R1")
        assert stored == _replacement()
        state = active_sanction_state(
            "P1", "2026/2027",
            uow.no_shows.for_person_season("P1", "2026/2027"),
            uow.replacements.for_person_season("P1", "2026/2027"),
        )
        assert state.counter == 0
        assert state.repaired_no_show_ids == ("N1",)


def test_replacement_requires_existing_no_show_and_assignment(tmp_path):
    db = SQLiteDatabase(tmp_path / "fk.sqlite"); db.initialize()
    with db.unit_of_work() as uow:
        with pytest.raises(Exception):
            uow.replacements.add(_replacement())


def test_only_one_replacement_path_per_no_show_and_assignment(tmp_path):
    db = SQLiteDatabase(tmp_path / "unique.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow:
        uow.replacements.add(_replacement())
        uow.commit()
    duplicate = ReplacementDuty(
        "R2", "N1", "A-REPL", "P1", "2026/2027",
        datetime(2026, 9, 22, 9), "planner",
    )
    with db.unit_of_work() as uow:
        with pytest.raises(Exception):
            uow.replacements.add(duplicate)


def test_planned_replacement_persists_without_resetting_counter(tmp_path):
    db = SQLiteDatabase(tmp_path / "planned.sqlite"); db.initialize()
    with db.unit_of_work() as uow: _seed(uow)
    with db.unit_of_work() as uow:
        uow.replacements.add(_replacement(completed=False)); uow.commit()
    with db.unit_of_work() as uow:
        state = active_sanction_state(
            "P1", "2026/2027",
            uow.no_shows.for_person_season("P1", "2026/2027"),
            uow.replacements.for_person_season("P1", "2026/2027"),
        )
        assert state.counter == 1
