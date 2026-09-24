import ast
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from dvk.application_services import AssignmentContext
from dvk.demo_data_v05 import demo_candidate_cases, demo_planning_data
from dvk.no_show import NoShowEvent
from dvk.application_services import NoShowApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.security import Identity, Permission
from dvk.workstream_model import AssignmentProposal

import pytest
from streamlit.testing.v1 import AppTest
from dvk.workstream_model import DutyAssignment


SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def _presentation_namespace():
    """Execute the pure formatting helpers without starting the Streamlit app."""
    tree = ast.parse(SOURCE.read_text())
    selected = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in {"_datum_met_dag", "_assignment_label"}
    ) or (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DAGEN" for t in node.targets)
    )]
    namespace = {"datetime": datetime}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


def _context():
    services, _, _, _ = demo_planning_data(datetime(2026, 9, 14).date())
    person = demo_candidate_cases()[2].person
    assignment = DutyAssignment("UI-technical-assignment", "proposal", services[2].service_id, person.person_id, "parent_guardian", 4.5, "vc1")
    return AssignmentContext(assignment, services[2], person.name)


def test_shared_assignment_label_shows_actual_human_context_without_internal_ids():
    context = _context()
    label = _presentation_namespace()["_assignment_label"](context)
    assert label == "za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis"
    assert context.assignment.assignment_id == "UI-technical-assignment"
    assert context.assignment.assignment_id not in label
    assert context.assignment.service_id not in label
    assert context.assignment.person_id not in label


def test_missing_context_is_explicit_without_guessing_name_service_or_date():
    context = _context()
    label = _presentation_namespace()["_assignment_label"]
    assert label(AssignmentContext(context.assignment, None, None)) == "Datum/tijd en dienst onbekend — Persoon onbekend"
    assert label(AssignmentContext(context.assignment, None, context.person_name)) == "Datum/tijd en dienst onbekend — Jeugdlid Thuis"
    assert label(AssignmentContext(context.assignment, context.service, None)).endswith(" — Persoon onbekend")


def test_streamlit_uses_public_services_instead_of_repositories_or_private_state():
    tree = ast.parse(SOURCE.read_text())
    attributes = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute)]
    assert not any(isinstance(node.value, ast.Name) and node.value.id == "uow" for node in attributes)
    assert not any(node.attr.startswith("_") for node in attributes)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert any(node.func.attr == "revocable_no_shows" for node in calls)
    assert any(node.func.attr == "assignment_contexts" for node in calls)


@pytest.fixture
def rendered_app(tmp_path):
    # Run the real app against a disposable SQLite database, never the local demo.
    script = tmp_path / "streamlit_app.py"
    script.write_text(SOURCE.read_text())
    db = SQLiteDatabase(tmp_path / "dvk_v05.sqlite")
    db.initialize()
    context = _context()
    with db.unit_of_work() as uow:
        for i in range(1, 3):
            aid, pid = f"technical-assignment-{i}", f"technical-proposal-{i}"
            uow.proposals.add(AssignmentProposal(pid, context.service.service_id, context.assignment.person_id, "member", 10, 0, 0, 0, 10, 0, False, None, None, None, "no_match_context", "normal", 1, ()))
            uow.assignments.add(replace(context.assignment, assignment_id=aid, proposal_id=pid))
        uow.commit()
        for i in range(1, 3):
            when = context.service.starts_at
            NoShowApplicationService(uow, Identity("vc1", "VC", frozenset({Permission.MANAGE_NO_SHOWS}))).register(
                NoShowEvent(f"technical-no-show-{i}", f"technical-assignment-{i}", context.assignment.person_id, when, when, "vc1", "2026/2027"))
    app = AppTest.from_file(str(script), default_timeout=15).run()
    app.date_input[0].set_value(datetime(2026, 9, 14).date()).run()
    assert not app.exception
    return app, db


def _revocation_selector(app):
    return next(widget for widget in app.selectbox if widget.label == "No-show intrekken")


def _confirm(app):
    return next(widget for widget in app.button if widget.label == "Intrekking bevestigen")


def test_revocation_ui_uses_human_labels_and_distinct_internal_keys(rendered_app):
    app, db = rendered_app
    selector = _revocation_selector(app)
    assert selector.options == ["za 19-09 12:30–17:00 — Gastvrouw/heer — Jeugdlid Thuis"] * 2
    assert selector.value == "technical-no-show-1"
    selector.select("technical-no-show-2").run()
    assert _revocation_selector(app).value == "technical-no-show-2"
    assert app.text_area[0].label == "Toelichting voor intrekking (verplicht)"
    with db.unit_of_work() as uow:
        assert uow.no_show_revocations.for_no_show("technical-no-show-2") is None


def test_revocation_ui_requires_explicit_confirmation_and_shows_current_season_counter(rendered_app):
    app, db = rendered_app
    _revocation_selector(app).select("technical-no-show-2")
    app.text_area[0].set_value("Uitdrukkelijk besluit").run()
    with db.unit_of_work() as uow:
        original = uow.no_shows.get("technical-no-show-2")
        assert uow.no_show_revocations.for_no_show("technical-no-show-2") is None
    _confirm(app).click().run()
    assert not app.exception
    assert any(message.value == "No-show ingetrokken. Actuele no-showteller voor Jeugdlid Thuis in seizoen 2026/2027: 1." for message in app.success)
    assert app.text_area[0].value == ""
    assert len(_revocation_selector(app).options) == 1
    with db.unit_of_work() as uow:
        assert uow.no_shows.get("technical-no-show-2") == original
        revocation = uow.no_show_revocations.for_no_show("technical-no-show-2")
        assert revocation.reason == "Uitdrukkelijk besluit"
        assert revocation.revoked_by == "demo-planner"
        assert revocation.revoked_at is not None
    # Selection options and all visible feedback contain no internal identifiers.
    texts = [widget.label for widget in app.selectbox] + [text for widget in app.selectbox for text in widget.options]
    texts += [message.value for kind in (app.error, app.success, app.info, app.warning, app.markdown) for message in kind]
    assert not any("technical-" in text for text in texts)


def test_revocation_ui_reports_service_validation_without_partial_write(rendered_app):
    app, db = rendered_app
    app.text_area[0].set_value("   ")
    _confirm(app).click().run()
    assert not app.exception
    assert any("toelichting" in message.value for message in app.error)
    assert app.text_area[0].value == "   "
    with db.unit_of_work() as uow:
        assert uow.no_show_revocations.for_no_show("technical-no-show-1") is None


def test_streamlit_source_compiles_without_importing_or_starting_app():
    compile(SOURCE.read_text(), str(SOURCE), "exec")


def test_duplicate_no_show_registration_shows_message_without_second_event(rendered_app):
    app, db = rendered_app
    context = _context()
    assignment_id = "technical-assignment-registration"
    with db.unit_of_work() as uow:
        services, _, _, _ = demo_planning_data(datetime(2026, 9, 14).date())
        uow.assignments.add(replace(context.assignment, assignment_id=assignment_id, proposal_id="technical-proposal-1", service_id=services[0].service_id))
        uow.commit()
    app.run()
    next(widget for widget in app.selectbox if widget.label == "Inroostering").select(assignment_id)
    next(widget for widget in app.button if widget.label == "No-show bevestigen").click().run()
    assert not app.exception
    assert not app.error
    with db.unit_of_work() as uow:
        original = uow.no_shows.for_assignment(assignment_id)
        assert original is not None
        before = uow.no_shows.all()
    next(widget for widget in app.button if widget.label == "No-show bevestigen").click().run()
    assert not app.exception
    assert any("voor deze inroostering is al een no-show geregistreerd" in message.value for message in app.error)
    with db.unit_of_work() as uow:
        assert uow.no_shows.all() == before
        assert uow.no_shows.for_assignment(assignment_id) == original
        assert sum(event.assignment_id == assignment_id for event in uow.no_shows.all()) == 1


def test_successful_revocation_does_not_reuse_reason_for_next_no_show(rendered_app):
    app, db = rendered_app
    app.text_area[0].set_value("Toelichting voor de eerste intrekking")
    _confirm(app).click().run()
    assert not app.exception
    assert app.text_area[0].value == ""
    remaining_id = _revocation_selector(app).value
    app.run()
    assert app.text_area[0].value == ""
    _confirm(app).click().run()
    assert not app.exception
    assert any("toelichting" in message.value for message in app.error)
    with db.unit_of_work() as uow:
        assert uow.no_show_revocations.for_no_show(remaining_id) is None


def test_revocation_success_does_not_guess_missing_person_name(rendered_app, monkeypatch):
    app, db = rendered_app
    original_query = NoShowApplicationService.revocable_no_shows

    def without_person_context(self, **kwargs):
        return tuple(replace(row, assignment=replace(row.assignment, person_name=None))
                     for row in original_query(self, **kwargs))

    monkeypatch.setattr(NoShowApplicationService, "revocable_no_shows", without_person_context)
    app.run()
    no_show_id = _revocation_selector(app).value
    with db.unit_of_work() as uow:
        person_id = uow.no_shows.get(no_show_id).person_id
    app.text_area[0].set_value("Expliciet besluit")
    _confirm(app).click().run()
    assert not app.exception
    message = next(message.value for message in app.success if "No-show ingetrokken" in message.value)
    assert message == "No-show ingetrokken. Actuele no-showteller voor dit lid (naam onbekend) in seizoen 2026/2027: 1."
    assert person_id not in message
    assert "Jeugdlid Thuis" not in message
