from datetime import datetime

import pytest

from dvk.no_show import NoShowEvent, NoShowRevocation, assess_sanction, season_id


def event(identifier, when, *, person="P1"):
    return NoShowEvent(identifier, f"A-{identifier}", person, when, when, "planner", season_id(when.date()))


def test_season_runs_from_july_through_june():
    assert season_id(datetime(2026, 7, 1).date()) == "2026/2027"
    assert season_id(datetime(2027, 6, 30).date()) == "2026/2027"
    assert season_id(datetime(2027, 7, 1).date()) == "2027/2028"


def test_first_no_show_warns_and_requires_self_arranged_replacement():
    current = event("N1", datetime(2026, 9, 1, 10))
    result = assess_sanction(current, ())
    assert (result.counter, result.card, result.fine_eur, result.suspension_matches) == (1, None, 0, 0)
    assert result.replacement_service_required is True
    assert result.board_follow_up is False


@pytest.mark.parametrize(
    "number,card,fine,suspension,board",
    [(2, "yellow", 75, 1, False), (3, "yellow", 75, 2, False), (4, "red", 100, 3, True), (5, "red", 100, 3, True)],
)
def test_sanction_ladder(number, card, fine, suspension, board):
    events = tuple(event(f"N{i}", datetime(2026, 9, i, 10)) for i in range(1, number + 1))
    result = assess_sanction(events[-1], events[:-1])
    assert (result.counter, result.card, result.fine_eur, result.suspension_matches, result.board_follow_up) == (number, card, fine, suspension, board)
    assert result.replacement_service_required is False


def test_previous_season_no_show_does_not_count():
    old = event("OLD", datetime(2026, 6, 30, 10))
    current = event("NEW", datetime(2026, 7, 1, 10))
    assert assess_sanction(current, (old,)).counter == 1


def test_revoked_no_show_does_not_count():
    original = event("N1", datetime(2026, 9, 1, 10))
    revoked = NoShowRevocation("R1", "N1", "registratiefout", datetime(2026, 9, 3), "planner")
    current = event("N2", datetime(2026, 9, 2, 10))
    assert assess_sanction(current, (original,), (revoked,)).counter == 1


def test_revoked_current_event_cannot_create_sanction():
    with pytest.raises(ValueError):
        assess_sanction(event("N1", datetime(2026, 9, 1, 10)), (),
                        (NoShowRevocation("R1", "N1", "registratiefout", datetime(2026, 9, 3), "planner"),))
