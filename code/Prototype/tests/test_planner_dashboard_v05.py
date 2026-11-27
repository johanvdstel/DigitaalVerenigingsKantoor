from types import SimpleNamespace

from dvk.planner_presenter import period_capacity
from dvk.planning_session import PlanningSessionApplicationService
from test_new_planning_9a2 import open_page, sources
from test_volunteer_planning_integration_v05 import IDENTITY


def capacity_row(maximum, sportlink, temporary=0):
    return SimpleNamespace(maximum_staff=maximum, source_occupancy=sportlink,
                           temporary_occupancy=temporary, remaining_capacity=max(0, maximum - sportlink - temporary))


def test_maximum_capacity_rounding_and_unknown_values():
    known = period_capacity((capacity_row(8, 4, 1),), True)
    assert (known.maximum, known.sportlink, known.temporary, known.free) == (8, 4, 1, 3)
    assert known.percentages == (50, 13, 37)
    unknown = period_capacity((capacity_row(8, 0, 1),), False)
    assert (unknown.maximum, unknown.sportlink, unknown.temporary, unknown.free) == (8, None, 1, None)
    assert unknown.percentages is None
    assert period_capacity((), True).percentages is None
    assert period_capacity((capacity_row(0, 0),), True).percentages is None


def test_overbooking_does_not_hide_free_capacity_elsewhere():
    totals = period_capacity((capacity_row(2, 3), capacity_row(4, 0, 1)), True)
    assert (totals.maximum, totals.sportlink, totals.temporary, totals.free) == (6, 3, 1, 3)
    assert totals.overbooked and totals.percentages is None


def test_confirmed_period_change_loads_once_and_cancel_loads_nothing(tmp_path, sources):
    _, calls = sources
    app, database = open_page(tmp_path)
    app.button(key="nav-planning").click().run()
    app.button(key="activate-planning").click().run()
    first_calls = list(calls)
    assert first_calls and not app.exception
    with database.unit_of_work() as uow:
        initial = PlanningSessionApplicationService(uow, IDENTITY).current()
    app.button(key="start-new-planning").click().run()
    app.radio(key="planning-mode").set_value("Dag").run()
    app.date_input(key="planning-from").set_value(initial.period.start).run()
    app.button(key="activate-planning").click().run()
    app.button(key="cancel-close-planning").click().run()
    assert calls == first_calls
    with database.unit_of_work() as uow:
        assert PlanningSessionApplicationService(uow, IDENTITY).current() == initial
    app.button(key="activate-planning").click().run()
    app.button(key="confirm-close-planning").click().run()
    assert not app.exception and calls == first_calls * 2
    with database.unit_of_work() as uow:
        current = PlanningSessionApplicationService(uow, IDENTITY).current()
        assert current.session_id != initial.session_id
        assert current.period.start == current.period.end == initial.period.start
    app.button(key="planner-review").click().run()
    app.button(key="close-planning-review").click().run()
    assert not app.exception and calls == first_calls * 2


def test_fallback_action_bar_without_native_bottom(tmp_path, monkeypatch, sources):
    import streamlit as st

    monkeypatch.delattr(st, "bottom", raising=False)
    app, _ = open_page(tmp_path)
    app.button(key="nav-planning").click().run()
    app.button(key="activate-planning").click().run()
    assert not app.exception and app.button(key="planner-assign").disabled
    app.button(key="planner-review").click().run()
    assert not app.exception and app.button(key="close-planning-review")
