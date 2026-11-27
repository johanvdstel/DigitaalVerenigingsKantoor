"""Native-table interactions, synthetic sources and isolated SQLite only."""

from test_candidate_context_ui_v05 import candidate_buttons, candidate_checks, duty_buttons, operational_page, refresh_candidate_sources
from test_candidate_context_v05 import IDENTITY
from dvk.application_services import PlanningApplicationService


def active(db):
    with db.unit_of_work() as uow:
        return PlanningApplicationService(IDENTITY, uow=uow).active_planning()


def test_service_selection_switches_directly_and_can_be_cleared(operational_page):
    app, db, observed = operational_page
    duties = duty_buttons(app)
    duties[0].click().run()
    assert "selected_service_id" not in app.session_state
    duty_buttons(app)[0].click().run()
    first_keys = [button.key for button in candidate_buttons(app)]
    candidate_checks(app)[0].check().run()
    duty_buttons(app)[1].click().run()
    assert app.session_state["selected_service_id"] == duties[1].key.removeprefix("planner-duty-")
    assert [button.key for button in candidate_buttons(app)] != first_keys
    assert app.button(key="planner-assign").disabled
    assert not active(db) and len(observed) == 1
    app.run()
    assert app.session_state["selected_service_id"] == duties[1].key.removeprefix("planner-duty-")


def test_service_counts_expose_maximum_and_hide_minimum(operational_page):
    app, _, _ = operational_page
    app.button(key="planner-review").click().run()
    roster = next(node.value for node in app.dataframe if "Max." in node.value.columns)
    assert roster.columns.tolist() == ["Datum", "Tijd", "Dienst", "Max.", "SL", "DVK", "Vrij"]
    assert roster.Tijd.str.match(r"^[0-9]{2}:[0-9]{2}–[0-9]{2}:[0-9]{2}$").all()


def test_candidate_detail_can_be_opened_and_closed_without_planning(operational_page):
    app, db, _ = operational_page
    name = candidate_buttons(app)[0].label
    candidate_buttons(app)[0].click().run()
    assert any(item.value == f"**{name}**" for item in app.markdown)
    candidate_buttons(app)[0].click().run()
    assert not any(item.value == f"**{name}**" for item in app.markdown)
    assert not any(check.value for check in candidate_checks(app))
    assert not active(db)


def test_many_candidates_remain_reachable_in_service_order(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_candidate_context_v05 import context, exports
    app, db, _ = operational_page
    members = [dict(pid=f"SYNTH-{i}", born="01-01-1990", team="O17-1", number=str(i+1)) for i in range(250)]
    ctx = replace(context(exports(members=members)), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    refresh_candidate_sources(app)
    assert len(candidate_buttons(app)) == 24
    while len(candidate_buttons(app)) < 250:
        next(button for button in app.button if button.label.startswith("Meer kandidaten")).click().run()
    assert len({button.label for button in candidate_buttons(app)}) == 250
    assert not any(b.label == "Uitzondering vastleggen" for b in app.button)
    last = candidate_buttons(app)[249].label
    candidate_buttons(app)[249].click().run()
    assert any(item.value == f"**{last}**" for item in app.markdown)
    assert any("Rang 250" in item.value for item in app.caption)
    assert app.button(key="planner-assign").disabled
    assert not active(db)


def test_changed_candidate_rows_discard_old_positional_edits(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_planning_acceptance_abc_v05 import many
    app, db, _ = operational_page
    ctx = replace(many(), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    refresh_candidate_sources(app)
    old_key = candidate_checks(app)[0].key
    candidate_checks(app)[0].check().run()
    original = CandidateContextApplicationService.propose
    def changed(*a, **kw):
        result = original(*a, **kw)
        return replace(result, planned=tuple(reversed(result.planned)))
    monkeypatch.setattr(CandidateContextApplicationService, "propose", changed)
    app.run()
    assert candidate_checks(app)[0].key != old_key
    assert not any("DVK-beleidscontrole taakplicht:" in c.value for c in app.caption)
    assert app.button(key="planner-assign").disabled
    assert not active(db)


def test_shared_candidate_detail_never_records_an_exception(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from dvk.application_services import ProposalDecisionApplicationService
    from test_planning_acceptance_abc_v05 import many
    app, db, _ = operational_page
    ctx = replace(many(), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    refresh_candidate_sources(app)
    candidate_buttons(app)[5].click().run()
    observed = []
    original = ProposalDecisionApplicationService.reject
    def reject(self, proposal, case, **kwargs):
        observed.append((proposal.person_id, kwargs))
        return original(self, proposal, case, **kwargs)
    monkeypatch.setattr(ProposalDecisionApplicationService, "reject", reject)
    app.run()
    assert not app.exception
    assert observed == []
    assert not any(t.label == "Toelichting" for t in app.text_input)
    assert not any(b.label == "Uitzondering vastleggen" for b in app.button)
    assert any("Openstaande uren:" in c.value for c in app.markdown)
    assert not active(db)


def test_multiple_selected_details_and_deselect_preserve_storage(operational_page, monkeypatch):
    from dataclasses import replace
    from dvk.candidate_context import CandidateContextApplicationService
    from test_planning_acceptance_abc_v05 import many
    from test_volunteer_planning_integration_v05 import snapshot
    app, db, _ = operational_page
    ctx = replace(many(), period=app.session_state["candidate-context"].period)
    monkeypatch.setattr(CandidateContextApplicationService, "load", lambda *a, **k: ctx)
    refresh_candidate_sources(app)
    names = [button.label for button in candidate_buttons(app)]
    before = snapshot(db)
    candidate_checks(app)[0].check().run()
    candidate_checks(app)[1].check().run()
    candidate_buttons(app)[1].click().run()
    candidate_checks(app)[0].uncheck().run()
    assert any(item.value == f"**{names[1]}**" for item in app.markdown)
    assert [check.value for check in candidate_checks(app)][:2] == [False, True]
    assert snapshot(db) == before
