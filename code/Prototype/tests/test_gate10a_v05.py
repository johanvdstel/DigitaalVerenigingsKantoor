from datetime import datetime

from dvk.no_show import NoShowEvent
from dvk.replacement_duty import ReplacementDuty, active_sanction_state


def ns(identifier, day):
    when = datetime(2026, 9, day, 10)
    return NoShowEvent(identifier, f"A-{identifier}", "P1", when, when, "planner", "2026/2027")


def replacement(no_show_id, *, completed=True):
    return ReplacementDuty(
        f"R-{no_show_id}", no_show_id, f"AR-{no_show_id}", "P1", "2026/2027",
        datetime(2026, 9, 20, 9), "planner",
        datetime(2026, 9, 21, 12) if completed else None,
        "planner" if completed else None,
    )


def test_first_no_show_without_completed_replacement_stays_at_one():
    state = active_sanction_state("P1", "2026/2027", (ns("N1", 18),), ())
    assert state.counter == 1
    assert state.assessment.replacement_service_required is True


def test_scheduled_but_not_completed_replacement_does_not_reset_counter():
    state = active_sanction_state("P1", "2026/2027", (ns("N1", 18),), (replacement("N1", completed=False),))
    assert state.counter == 1


def test_completed_replacement_resets_first_no_show_to_zero_but_preserves_history_reference():
    state = active_sanction_state("P1", "2026/2027", (ns("N1", 18),), (replacement("N1"),))
    assert state.counter == 0
    assert state.assessment is None
    assert state.repaired_no_show_ids == ("N1",)


def test_next_no_show_after_successful_repair_is_first_stage_again():
    state = active_sanction_state(
        "P1", "2026/2027", (ns("N1", 18), ns("N2", 25)), (replacement("N1"),)
    )
    assert state.counter == 1
    assert state.assessment.no_show_id == "N2"
    assert state.assessment.replacement_service_required is True


def test_unrepaired_first_no_show_makes_next_no_show_stage_two():
    state = active_sanction_state("P1", "2026/2027", (ns("N1", 18), ns("N2", 25)), ())
    assert state.counter == 2
    assert state.assessment.card == "yellow"
    assert state.assessment.fine_eur == 75
    assert state.assessment.suspension_matches == 1


def test_completed_replacement_cannot_repair_stage_two():
    # N1 is not repaired before N2 occurs, so N2 is stage 2. A replacement
    # linked to N2 must not reset that later-stage sanction.
    state = active_sanction_state(
        "P1", "2026/2027", (ns("N1", 18), ns("N2", 25)), (replacement("N2"),)
    )
    assert state.counter == 2
    assert state.repaired_no_show_ids == ()
