from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def test_demo_proposal_run_id_is_stable_across_streamlit_reruns():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'proposal_run_key = f"proposal-run-{selected_service_id}"' in source
    assert 'proposal_run_id=st.session_state[proposal_run_key]' in source
    assert 'st.session_state[proposal_run_key] = str(uuid4())' in source


def test_no_show_selector_uses_planner_friendly_service_details():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'service_info.service_type' in source
    assert 'person_name' in source
    assert 'assignment_options[assignment_id] = f"{assignment_id}' not in source
