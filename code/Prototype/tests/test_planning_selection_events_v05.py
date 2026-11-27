"""Drive the real dashboard's native selection widgets with synthetic data."""
from dataclasses import replace

from dvk.application_services import PlanningApplicationService
from dvk.candidate_context import CandidateContextApplicationService
from test_candidate_context_ui_v05 import (
    candidate_buttons, candidate_checks, duty_buttons, operational_page, refresh_candidate_sources,
)
from test_candidate_context_v05 import IDENTITY
from test_planning_acceptance_abc_v05 import many


def active(database):
    with database.unit_of_work() as uow:
        return PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_repeated_choices_keep_widget_and_do_not_revert(operational_page):
    app, database, calls = operational_page
    original = [button.key for button in duty_buttons(app)]
    for index in (1, 2, 0, 2, 1, 0):
        duty_buttons(app)[index].click().run()
        assert not app.exception
        assert app.session_state['selected_service_id'] == original[index].removeprefix('planner-duty-')
        assert [button.key for button in duty_buttons(app)] == original
        candidate_buttons(app)[0].click().run()
        assert not any(check.value for check in candidate_checks(app))
        assert app.session_state['selected_service_id'] == original[index].removeprefix('planner-duty-')
    assert not active(database) and len(calls) == 1


def test_choice_survives_confirmation_and_planning_wide_undo(operational_page):
    app, database, calls = operational_page
    duty_buttons(app)[1].click().run()
    source = app.session_state['selected_service_id']
    candidate_checks(app)[0].check().run()
    app.button(key='planner-assign').click().run()
    assert not app.exception and len(active(database)) == 1
    assert app.session_state['selected_service_id'] == source
    duty_buttons(app)[2].click().run()
    other = app.session_state['selected_service_id']
    app.button(key='planner-review').click().run()
    undo = next(button for button in app.button if (button.key or '').startswith('planner-undo-review-'))
    undo.click().run()
    assert not app.exception and not active(database)
    app.button(key='close-planning-review').click().run()
    assert app.session_state['selected_service_id'] == other and len(calls) == 1


def test_multiple_candidates_within_capacity_confirm_and_undo(operational_page, monkeypatch):
    app, database, _ = operational_page
    context = replace(many(), period=app.session_state['candidate-context'].period)
    monkeypatch.setattr(CandidateContextApplicationService, 'load', lambda *args, **kwargs: context)
    refresh_candidate_sources(app)
    duty_buttons(app)[1].click().run()
    selected = app.session_state['selected_service_id']
    app.checkbox(key='planner-free-only').check().run()
    candidate_checks(app)[0].check().run()
    candidate_buttons(app)[1].click().run()
    assert [checkbox.value for checkbox in candidate_checks(app)][:2] == [True, False]
    candidate_checks(app)[1].check().run()
    assert not active(database)
    app.button(key='planner-assign').click().run()
    assert not app.exception
    assert {entry.assignment.person_id for entry in active(database)} == {'M0', 'M1'}
    assert app.session_state['selected_service_id'] == selected
    assert all(button.key != f'planner-duty-{selected}' for button in duty_buttons(app))
    next(button for button in app.button if (button.key or '').startswith('planner-undo-duty-')).click().run()
    assert not app.exception and len(active(database)) == 1
    assert any(button.key == f'planner-duty-{selected}' for button in duty_buttons(app))
