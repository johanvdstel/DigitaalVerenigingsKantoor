from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


from test_candidate_context_ui_v05 import candidate_buttons, operational_page


def test_proposal_identity_is_stable_across_streamlit_reruns(operational_page):
    app, _, _ = operational_page
    keys = [button.key for button in candidate_buttons(app)]
    assert keys
    for _ in range(2):
        app.run()
        assert [button.key for button in candidate_buttons(app)] == keys


def test_no_show_selector_uses_planner_friendly_service_details():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'service_info.service_type' in source
    assert 'person_name' in source
    assert 'assignment_options[assignment_id] = f"{assignment_id}' not in source
