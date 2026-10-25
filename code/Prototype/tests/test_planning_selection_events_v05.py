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
