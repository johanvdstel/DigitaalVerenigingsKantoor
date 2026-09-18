from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"

def test_gate10_ui_exposes_human_confirmed_replacement_flow():
    text = SOURCE.read_text()
    assert '### Vervangende inzet' in text
    assert 'Vervangende inzet koppelen' in text
    assert 'Uitgevoerd bevestigen' in text
    assert 'No-show vastleggen voor vervangende inzet' in text
    assert 'Actieve no-showteller is teruggezet naar 0' in text

def test_v13_ui_does_not_claim_linking_alone_resets_counter():
    text = SOURCE.read_text()
    assert 'De actieve teller blijft 1 totdat uitvoering is bevestigd.' in text
