from pathlib import Path

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"

def test_no_show_confirmation_uses_assignment_service_time():
    text = SOURCE.read_text()
    assert 'Datum no-show' not in text
    assert 'No-show bevestigen' in text
    assert 'app.register_booking(selected, source=source' in text
    services = (SOURCE.parent / 'dvk' / 'application_services.py').read_text()
    assert 'booking.starts_at.astimezone(TZ), self.clock()' in services
    assert 'season_id(booking.starts_at.astimezone(TZ).date())' in services
