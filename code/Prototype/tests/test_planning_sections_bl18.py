"""Planner panel placement and source controls with synthetic data."""
from dataclasses import replace

from dvk.candidate_context import CandidateContextApplicationService, CandidateSourceError
from dvk.shift_catalog import load_shift_catalog
from test_candidate_context_ui_v05 import candidate_buttons, operational_page, refresh_candidate_sources
from test_candidate_context_v05 import context
from test_candidate_person_issues_v05 import data_with_two, rows, write_rows
from test_planning_ui_names_v05 import page
from test_volunteer_planning_integration_v05 import sync


def test_dashboard_panels_and_external_controls(operational_page):
    app, _, _ = operational_page
    assert [item.value for item in app.markdown if item.value in {
        "### Rooster Ledendiensten", "### Kandidaten", "### Wedstrijden", "### Kandidaatdetails",
    }] == ["### Rooster Ledendiensten", "### Kandidaten", "### Wedstrijden", "### Kandidaatdetails"]
    assert app.button(key="nav-sources") and app.button(key="nav-no-shows")
    assert app.button(key="planner-assign") and app.button(key="planner-review")
    assert not any(button.key in {"load-candidate-sources", "reload-catalog"} for button in app.button)
    assert not any(button.label == "Sportlink-inroosteringen synchroniseren" for button in app.button)


def test_source_warning_stays_visible_while_detail_is_collapsed(operational_page, monkeypatch):
    app, _, _ = operational_page
    data = data_with_two()
    members = rows(data, "leden")
    members[1]["Lidstatus"] = "Onbekende synthetische status"
    write_rows(data, "leden", members)
    ctx = replace(context(data), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *args, **kwargs: ctx)
    refresh_candidate_sources(app)
    details = next(item for item in app.expander if item.label == "Bronstatus bekijken")
    assert not app.exception and not details.proto.expanded
    diagnostic = next(node.value for node in details.dataframe if "Relatiecode" in node.value.columns)
    assert diagnostic.Relatiecode.tolist() == ["M2"]
    assert sum("de overige kandidaten worden normaal beoordeeld" in item.value.lower() for item in app.info) >= 2


def test_full_program_remains_available_in_collapsed_section(operational_page, monkeypatch):
    from test_candidate_context_v05 import row
    app, _, _ = operational_page
    ctx = replace(context(rows=[row("CKC O17-1", wedstrijddatum="2026-10-24T11:00:00+02:00")]), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *args, **kwargs: ctx)
    refresh_candidate_sources(app)
    assert not app.exception
    program = next(section for section in app.expander if section.label.startswith("Volledig programma"))
    assert not program.proto.expanded
    assert any("O17-1" in item.value for item in program.markdown)


def test_unknown_occupancy_points_to_manual_sync_and_tracks_source(tmp_path):
    app, db = page(tmp_path)
    assert any("De Sportlink-bezetting is onbekend" in item.value and "Databronnen" in item.value for item in app.warning)
    assert not any(b.label == "Sportlink-inroosteringen synchroniseren" for b in app.button)
    app.button(key="nav-sources").click().run()
    assert any(b.label == "Sportlink-inroosteringen synchroniseren" for b in app.button)
    app.button(key="nav-planning").click().run()
    assert sync(db, load_shift_catalog(), {})[0] is None
    app.run()
    assert not app.exception
    assert not any("De Sportlink-bezetting is onbekend" in item.value for item in app.warning)


def test_catalog_controls_confirmation_and_cancel_do_not_fetch(operational_page):
    app, db, observed = operational_page
    app.button(key="nav-sources").click().run()
    catalog = next(section for section in app.expander if section.label == "Dienstencatalogus")
    assert catalog.button(key="reload-catalog").label == "Dienstencatalogus (roosterindeling) opnieuw laden"
    assert any("vervalt de tijdelijke planning" in entry.value for entry in catalog.caption)
    before = len(observed)
    with db.unit_of_work() as uow:
        session = uow.planning_sessions.get()
    app.button(key="reload-catalog").click().run()
    assert app.button(key="confirm-reload-catalog")
    app.button(key="cancel-reload-catalog").click().run()
    assert not app.exception and len(observed) == before
    with db.unit_of_work() as uow:
        assert uow.planning_sessions.get() == session


def test_stale_demo_widget_cannot_select_demo_or_avoid_source_validation(operational_page, monkeypatch):
    app, _, _ = operational_page
    app.session_state["planning-source-mode"] = "Demonstratie"

    def failure(*args, **kwargs):
        raise CandidateSourceError("Synthetische bronfout; geen demonstratieterugval")

    monkeypatch.setattr(CandidateContextApplicationService, "load", failure)
    refresh_candidate_sources(app)
    assert not app.exception
    assert not any(widget.label == "Gegevens" for widget in app.radio)
    assert any("geen demonstratieterugval" in error.value for error in app.error)
    assert not candidate_buttons(app)
