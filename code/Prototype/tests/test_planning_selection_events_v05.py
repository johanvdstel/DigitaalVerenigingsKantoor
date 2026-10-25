"""Stable row actions keep service selection and widget identity consistent."""
from test_candidate_context_ui_v05 import operational_page
from test_candidate_context_v05 import IDENTITY
from dvk.application_services import PlanningApplicationService
from ui_table_events import table, choose_service, pick


def test_repeated_choices_keep_widget_and_do_not_revert(operational_page):
    app, db, _ = operational_page
    original = table(app, "services_editor-")
    ids = original.value.service_id.tolist()
    for index in (1, 2, 0, 2, 1, 0):
        choose_service(app, index)
        assert not app.exception
        assert app.session_state["selected_service_id"] == ids[index]
        assert table(app, "services_editor-").value.query("Kies == '☑'").service_id.tolist() == [ids[index]]
        assert table(app, "services_editor-").proto.id == original.proto.id
        pick(app)
        app.run()
        assert app.session_state["selected_service_id"] == ids[index]
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_choice_survives_confirmation_and_undo(operational_page):
    app, _, _ = operational_page
    ids = table(app, "services_editor-").value.service_id.tolist()
    original_id = table(app, "services_editor-").proto.id
    choose_service(app, 1); pick(app)
    next(b for b in app.button if b.label == "Selectie bevestigen").click().run()
    assert not app.exception
    assert table(app, "services_editor-").proto.id == original_id
    choose_service(app, 2)
    assert app.session_state["selected_service_id"] == ids[2]
    next(b for b in app.button if b.label == "Tijdelijke inroostering ongedaan maken").click().run()
    choose_service(app, 0)
    assert app.session_state["selected_service_id"] == ids[0]
    assert not app.exception


def test_multiple_candidates_within_capacity_confirm_and_undo(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_planning_acceptance_abc_v05 import many
    app, db, _ = operational_page
    ctx=replace(many(),period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService,"load",lambda *a,**k:ctx)
    app.button(key="load-candidate-sources").click().run()
    choose_service(app,1)
    pick(app,0); pick(app,1)
    confirm=next(b for b in app.button if b.label=="Selectie bevestigen")
    assert not confirm.disabled
    with db.unit_of_work() as uow:
        assert not PlanningApplicationService(IDENTITY,uow=uow).active_planning()
    confirm.click().run()
    assert not app.exception
    with db.unit_of_work() as uow:
        active=PlanningApplicationService(IDENTITY,uow=uow).active_planning()
        assert {entry.assignment.person_id for entry in active} == {"M0","M1"}
    assert table(app,"services_editor-").value.iloc[1]["Vrije capaciteit"] == 0
    next(b for b in app.button if b.label=="Tijdelijke inroostering ongedaan maken").click().run()
    assert not app.exception
    with db.unit_of_work() as uow:
        assert len(PlanningApplicationService(IDENTITY,uow=uow).active_planning()) == 1
    assert table(app,"services_editor-").value.iloc[1]["Vrije capaciteit"] == 1
