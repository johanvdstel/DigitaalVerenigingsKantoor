from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def test_demo_proposal_ids_include_a_run_specific_component():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'proposal_run_id or uuid4()' in source
    assert 'f"DEMO-{service.service_id}-{case.person.person_id}-{proposal_run_id or uuid4()}"' in source
