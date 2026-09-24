from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from dvk.no_show import NoShowEvent, NoShowRevocation, current_sanction_state


def ns(identifier, day):
    when = datetime(2026, 9, day, 10)
    return NoShowEvent(identifier, f"A-{identifier}", "P1", when, when, "planner", "2026/2027")


def revocation(identifier):
    return NoShowRevocation(f"R-{identifier}", identifier, "vrije toelichting", datetime(2026, 10, 1), "planner")


@pytest.mark.parametrize("number", [1, 2, 3, 4, 5])
def test_any_no_show_can_be_revoked_without_mutating_originals(number):
    events = tuple(ns(f"N{i}", i) for i in range(1, 6))
    state = current_sanction_state("P1", "2026/2027", events, (revocation(f"N{number}"),))
    assert state.counter == 4
    assert events == tuple(ns(f"N{i}", i) for i in range(1, 6))
    assert (state.assessment.card, state.assessment.fine_eur, state.assessment.suspension_matches) == ("red", 100, 3)


def test_three_no_shows_then_revoking_second_gives_two():
    events = (ns("N1", 1), ns("N2", 2), ns("N3", 3))
    before = current_sanction_state("P1", "2026/2027", events)
    assert (before.counter, before.assessment.suspension_matches) == (3, 2)
    after = current_sanction_state("P1", "2026/2027", events, (revocation("N2"),))
    assert (after.counter, after.assessment.card, after.assessment.fine_eur, after.assessment.suspension_matches) == (2, "yellow", 75, 1)


def test_all_revoked_leaves_zero_and_no_sanction():
    state = current_sanction_state("P1", "2026/2027", (ns("N1", 1),), (revocation("N1"),))
    assert state.counter == 0
    assert state.assessment is None


def test_current_state_counts_distinct_facts_even_with_equal_occurrence_times():
    state = current_sanction_state("P1", "2026/2027", (ns("N1", 1), ns("N2", 1)))
    assert state.counter == state.assessment.counter == 2


def test_other_person_and_season_do_not_count():
    assert current_sanction_state("P2", "2026/2027", (ns("N1", 1),)).counter == 0
    assert current_sanction_state("P1", "2027/2028", (ns("N1", 1),)).counter == 0


@pytest.mark.parametrize("reason", ["", " ", "\t\n", "\u2003"])
def test_whitespace_reason_is_invalid(reason):
    with pytest.raises(ValueError, match="reason"):
        NoShowRevocation("R", "N1", reason, datetime(2026, 10, 1), "planner")


def test_event_and_revocation_are_immutable():
    with pytest.raises(FrozenInstanceError):
        ns("N1", 1).recorded_by = "other"
    with pytest.raises(FrozenInstanceError):
        revocation("N1").reason = "changed"
