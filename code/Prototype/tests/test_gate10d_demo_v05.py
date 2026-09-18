from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"

def test_gate10_demo_offers_same_candidate_for_second_service_without_changing_domain_rules():
    text = SOURCE.read_text()
    assert 'Demo-only: keep W08 available across services' in text
    assert 'service.service_id == "BAR-WO-1"' in text
    assert 'Production eligibility remains entirely in assess_candidate' in text
