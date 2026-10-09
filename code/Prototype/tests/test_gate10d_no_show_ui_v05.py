from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"

def test_no_show_confirmation_uses_assignment_service_time():
    text = SOURCE.read_text()
    assert 'Datum no-show' not in text
    assert 'No-show bevestigen' in text
    assert 'occurred_at = service_info.starts_at' in text
    assert 'season_id(occurred_at.date())' in text
