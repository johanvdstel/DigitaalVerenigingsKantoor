"""BL-18 presentation and preserved native service selection; synthetic only."""
from dataclasses import replace

from test_candidate_context_ui_v05 import operational_page
from test_candidate_context_v05 import context
from test_candidate_person_issues_v05 import data_with_two, rows, write_rows
from dvk.candidate_context import CandidateContextApplicationService
from ui_table_events import table, choose_service, pick


HEADINGS = [f"## {i} — {name}" for i, name in enumerate(
    ("Instellingen", "Databronnen", "Diensten", "Kandidaten", "Wedstrijden"), 1)]


def sections(app):
    return [block for block in app.main.children.values()
            if block.type == "expander" and block.markdown and block.markdown[0].value in HEADINGS]


def test_five_sections_and_controls_in_agreed_order(operational_page):
    app, _, _ = operational_page
    settings, sources, duties, candidates, fixtures = sections(app)
    assert [block.markdown[0].value for block in sections(app)] == HEADINGS
    assert settings.radio(key="planning-mode")
    assert settings.date_input(key="planning-from")
    assert settings.text_input(key="candidate-season")
    assert all(block.proto.expanded is False for block in sections(app))
    assert sources.radio(key="planning-source-mode")
    assert sources.button(key="load-candidate-sources")
    assert any(m.value == "### Datakwaliteit" for m in sources.markdown)
    assert any(e.label == "Bronstatus en actualiteit" for e in sources.expander)
    assert any(b.label == "Sportlink-inroosteringen synchroniseren" for b in duties.button)
    assert table(duties, "services_editor-")
    assert table(candidates)
    assert any(m.value == "### Actieve tijdelijke DVK-inroosteringen" for m in candidates.markdown)
    assert candidates.get("divider")
    assert any(m.value == "### No-shows" for m in candidates.markdown)
    assert not fixtures.button
    assert fixtures.label == "Wedstrijden"
    assert fixtures.proto.expanded is False


def test_source_warning_stays_visible_while_detail_is_collapsed(operational_page, monkeypatch):
    app, _, _ = operational_page
    data = data_with_two()
    members = rows(data, "leden")
    members[1]["Lidstatus"] = "Onbekende synthetische status"
    write_rows(data, "leden", members)
    ctx = replace(context(data), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    app.button(key="load-candidate-sources").click().run()
    assert not app.exception
    _, sources, _, _, _ = sections(app)
    detail = next(e for e in sources.expander if e.label == "Bronmeldingen kandidaatcontext")
    assert detail.proto.expanded is False
    assert detail.dataframe[0].value.Relatiecode.tolist() == ["M2"]
    # Direct child: important summary is outside every collapsed expander.
    assert any(child.type == "info" and "de overige kandidaten" in child.value
               for child in sources.children.values())


def test_service_context_and_widget_identity_survive_actions(operational_page):
    app, _, observed = operational_page
    original = table(app, "services_editor-").proto.id
    for index in (1, 2, 0):
        choose_service(app, index)
        selected = app.session_state["selected_service_id"]
        assert table(app, "services_editor-").proto.id == original
        assert table(app).key.startswith(f"candidate-table-{selected}-")
        pick(app)
        assert not next(b for b in app.button if b.label == "Selectie bevestigen").disabled
    choose_service(app, 0)
    assert "selected_service_id" not in app.session_state
    assert not any(t.key and t.key.startswith("candidate-table-") for t in app.dataframe)
    assert observed == [app.session_state["candidate-context"].period]
    assert not app.exception


def test_matches_table_remains_available_in_collapsed_section(operational_page):
    app, _, _ = operational_page
    app.radio(key="planning-source-mode").set_value("Demonstratie").run()
    assert not app.exception
    fixtures = sections(app)[4]
    expander = fixtures
    assert expander.proto.expanded is False
    assert set(expander.dataframe[0].value.columns) == {"Datum", "Tijd", "Team", "Thuis/uit"}
    assert len(expander.dataframe[0].value) > 0
