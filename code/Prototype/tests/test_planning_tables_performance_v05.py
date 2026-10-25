"""Native-table interactions, synthetic sources and isolated SQLite only."""
import ast
import json
from pathlib import Path

from test_candidate_context_ui_v05 import operational_page
from test_candidate_context_v05 import IDENTITY
from dvk.application_services import PlanningApplicationService
from ui_table_events import table, edit, pick, choose_service


def active(db):
    with db.unit_of_work() as uow:
        return PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_service_checkbox_switches_directly_and_deselects_previous(operational_page):
    app, db, observed = operational_page
    services = table(app, "services_editor-")
    ids = services.value.service_id.tolist()
    choose_service(app, 0)
    assert "selected_service_id" not in app.session_state
    choose_service(app, 0)
    assert app.session_state["selected_service_id"] == ids[0]
    first_proposals = table(app).value.proposal_id.tolist()
    pick(app)  # Choose a candidate, but do not confirm.
    choose_service(app, 1)
    assert not app.exception
    assert app.session_state["selected_service_id"] == ids[1]
    assert table(app, "services_editor-").value.Kies.tolist() == ["☐", "☑"] + ["☐"] * (len(ids)-2)
    assert table(app).value.proposal_id.tolist() != first_proposals
    assert next(b for b in app.button if b.label == "Selectie bevestigen").disabled
    assert not active(db)
    assert len(observed) == 1  # No CSV/API reload on table interaction.
    app.run()
    assert (table(app, "services_editor-").value.Kies == "☑").sum() == 1


def test_service_table_native_options_and_compact_numbers(operational_page):
    app, _, _ = operational_page
    services = table(app, "services_editor-")
    config = json.loads(services.proto.columns)
    assert config["Kies"]["pinned"] is True
    for label in ("Min", "Max", "Tijdelijk DVK", "DVK-bezetting", "Open minimum", "Vrije capaciteit"):
        assert config[label]["width"] == 65
        assert config[label]["help"] == label
        assert config[label]["alignment"] == "right"
        assert config[label]["disabled"] is True
    assert services.proto.row_height == 32
    assert config["Sportlink"]["width"] == 320
    assert table(app).proto.row_height == 32


def test_candidate_detail_selects_another_person_without_planning(operational_page):
    app, db, _ = operational_page
    detail = next(s for s in app.selectbox if s.label == "Kandidaat voor toelichting")
    assert detail.options
    detail.select_index(len(detail.options)-1).run()
    assert not app.exception
    assert any("Taakplicht:" in c.value for c in app.caption)
    assert len([s for s in app.selectbox if s.label == "Reden"]) == 1
    assert not active(db)


def test_version_feature_fallback_uses_only_supported_arguments():
    # Exercise pure presentation helpers against 1.40-shaped public signatures.
    from types import SimpleNamespace
    source = Path(__file__).parents[1] / "streamlit_app.py"
    tree = ast.parse(source.read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
                 {"_table_column_options", "_table_width_options"}]
    import inspect
    def old_column(label=None, *, width=None, help=None):
        pass
    def old_editor(data, *, width=None, use_container_width=None):
        pass
    scope = {"inspect": inspect, "st": SimpleNamespace(data_editor=old_editor)}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), "exec"), scope)
    assert scope["_table_column_options"](old_column, pinned=True, alignment="right") == {}
    assert scope["_table_width_options"]() == {"use_container_width": True}


def test_many_candidates_use_one_editor_and_one_exception_form(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_candidate_context_v05 import context, exports
    app, db, _ = operational_page
    members = [dict(pid=f"SYNTH-{i}", born="01-01-1990", team="O17-1", number=str(i+1)) for i in range(250)]
    ctx = replace(context(exports(members=members)), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    app.button(key="load-candidate-sources").click().run()
    assert len(table(app).value) == 250
    assert table(app).value.Rang.tolist() == list(range(1, 251))
    assert len([t for t in app.dataframe if t.key and t.key.startswith("candidate-table-")]) == 1
    assert len([b for b in app.button if b.label == "Uitzondering vastleggen"]) == 1
    pick(app, index=249)
    assert not next(b for b in app.button if b.label == "Selectie bevestigen").disabled
    assert not active(db)


def test_changed_candidate_rows_discard_old_positional_edits(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_planning_acceptance_abc_v05 import many
    app, db, _ = operational_page
    ctx = replace(many(), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    app.button(key="load-candidate-sources").click().run()
    old_key = table(app).key
    pick(app)
    original = CandidateContextApplicationService.propose
    def changed(*a, **kw):
        result = original(*a, **kw)
        return replace(result, planned=tuple(reversed(result.planned)))
    monkeypatch.setattr(CandidateContextApplicationService, "propose", changed)
    app.run()
    assert table(app).key != old_key
    assert next(b for b in app.button if b.label == "Selectie bevestigen").disabled
    assert not active(db)


def test_shared_exception_form_targets_chosen_candidate(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from dvk.application_services import ProposalDecisionApplicationService
    from test_planning_acceptance_abc_v05 import many
    app, db, _ = operational_page
    ctx = replace(many(), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    app.button(key="load-candidate-sources").click().run()
    next(s for s in app.selectbox if s.label == "Kandidaat voor toelichting").select_index(5).run()
    observed = []
    original = ProposalDecisionApplicationService.reject
    def reject(self, proposal, case, **kwargs):
        observed.append((proposal.person_id, kwargs))
        return original(self, proposal, case, **kwargs)
    monkeypatch.setattr(ProposalDecisionApplicationService, "reject", reject)
    next(t for t in app.text_input if t.label == "Toelichting").input("Synthetische bijzonderheid")
    next(b for b in app.button if b.label == "Uitzondering vastleggen").click().run()
    assert not app.exception
    assert observed == [("M5", {"reason_category": "personal_circumstance", "reason": "Synthetische bijzonderheid"})]
    assert any("Uitzondering vastgelegd" in w.value for w in app.warning)
    assert not active(db)
