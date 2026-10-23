"""BL-04 navigation tests; only temporary databases and synthetic state."""
from datetime import date
from pathlib import Path

from streamlit.testing.v1 import AppTest

from dvk.persistence import SQLiteDatabase

APP = Path(__file__).parents[1] / 'streamlit_app.py'


def app_at(tmp_path):
    path = tmp_path / 'streamlit_app.py'
    path.write_text(APP.read_text())
    return AppTest.from_file(str(path), default_timeout=20).run()


def test_home_default_and_honest_module_statuses(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Home must not initialize the database')
    monkeypatch.setattr(SQLiteDatabase, 'initialize', forbidden)
    app = app_at(tmp_path)
    assert not app.exception
    assert any('Welkom' in x.value for x in app.subheader)
    assert not app.get('file_uploader')
    assert not app.metric
    assert not (tmp_path / 'dvk_v05.sqlite').exists()
    assert [x.value for x in app.sidebar.subheader] == [
        'Ledendiensten & Vrijwilligersbeleid', 'Overige werkgebieden', 'DVK Beheer']
    future = [x for x in app.sidebar.button if x.disabled and x.key != 'nav-rooster']
    assert len(future) == 5
    assert all('niet beschikbaar' in x.label for x in future)
    rooster = app.sidebar.button(key='nav-rooster')
    assert rooster.disabled
    assert rooster.label == 'Rooster Generator — extern, nog niet geïntegreerd'
    assert not app.sidebar.caption
    assert not app.sidebar.get('link_button')
    assert any('Rooster Generator' in x.value and 'nog niet geïntegreerd' in x.value
               for x in app.markdown)
    assert not (tmp_path / 'dvk_v05.sqlite').exists()


def test_available_screens_and_roundtrip_leave_database_unchanged(tmp_path):
    db = tmp_path / 'dvk_v05.sqlite'
    SQLiteDatabase(db).initialize()
    before = db.read_bytes()
    app = app_at(tmp_path)
    for _ in range(2):
        app.button(key='nav-planning').click().run()
        assert not app.exception
        assert any(x.label == 'Diensten' for x in app.metric)
        assert not any(x.key and x.key.startswith('duty-control-') for x in app.get('file_uploader'))
        app.button(key='nav-control').click().run()
        assert not app.exception
        assert len(app.get('file_uploader')) == 5
        assert not app.metric
        assert not any(x.value == '### No-shows' for x in app.markdown)
        app.button(key='nav-home').click().run()
        assert any('Welkom' in x.value for x in app.subheader)
        assert not app.get('file_uploader')
        assert db.read_bytes() == before


def test_scalar_controls_survive_screen_cleanup(tmp_path):
    app = app_at(tmp_path)
    app.button(key='nav-control').click().run()
    app.date_input(key='duty-control-date').set_value(date(2025, 8, 1)).run()
    app.text_input(key='duty-control-period').set_value('2025-2026').run()
    app.radio(key='duty-control-filter').set_value('Alleen afwijkingen').run()
    upload_keys = [x.key for x in app.get('file_uploader')]
    app.button(key='nav-home').click().run()
    assert not app.get('file_uploader')
    assert all(key not in app.session_state for key in upload_keys)
    app.button(key='nav-control').click().run()
    assert app.date_input(key='duty-control-date').value == date(2025, 8, 1)
    assert app.text_input(key='duty-control-period').value == '2025-2026'
    assert app.radio(key='duty-control-filter').value == 'Alleen afwijkingen'
    # Empty uploader widgets are recreated without a retained file.
    assert all(app.session_state[key] is None for key in upload_keys)
    app.button(key='nav-planning').click().run()
    app.radio(key='planning-mode').set_value('Dag').run()
    app.date_input(key='planning-from').set_value(date(2026, 9, 14)).run()
    app.button(key='nav-home').click().run()
    app.button(key='nav-planning').click().run()
    assert not app.exception
    assert app.radio(key='planning-mode').value == 'Dag'
    assert app.date_input(key='planning-from').value == date(2026, 9, 14)


def test_uploaded_files_require_reselection_after_leaving_control(tmp_path):
    import pytest
    from test_duty_control_dashboard_v05 import uploads
    from test_hours_control_v05 import TODAY

    files = uploads(tmp_path)
    app = app_at(tmp_path)
    app.button(key='nav-control').click().run()
    if not hasattr(app.get('file_uploader')[0], 'set_value'):
        pytest.skip('Installed Streamlit AppTest does not support file uploads')
    app.date_input(key='duty-control-date').set_value(TODAY).run()
    app.text_input(key='duty-control-period').set_value('2026-2027').run()
    for widget in app.get('file_uploader'):
        dataset = widget.key.removeprefix('duty-control-')
        widget.set_value((dataset + '.csv', files[dataset], 'text/csv'))
    app.run()
    assert not app.exception
    assert any(x.label == 'Totaal' and x.value == '1' for x in app.metric)
    app.radio(key='duty-control-filter').set_value('Alleen afwijkingen').run()
    assert all(app.session_state['duty-control-' + key] is not None for key in files)
    app.button(key='nav-home').click().run()
    app.button(key='nav-control').click().run()
    assert not app.exception
    assert not app.metric
    assert all(app.session_state['duty-control-' + key] is None for key in files)
    assert any('Selecteer alle vijf' in x.value for x in app.info)


def test_home_uses_one_consistent_line_per_function(tmp_path):
    app = app_at(tmp_path)
    groups = {}
    current = None
    for item in app.main.markdown:
        if item.value.startswith('### '):
            current = item.value.removeprefix('### ')
            groups[current] = []
        elif current and item.value.startswith('**'):
            groups[current].append(item.value)
    assert groups == {
        'Ledendiensten & Vrijwilligersbeleid': [
            '**Ledendienst Planning** — beschikbaar als prototype v0.5, in ontwikkeling.',
            '**Taakplichtcontrole** — beschikbare read-only functie binnen Ledendienst Planning.',
            '**Rooster Generator** — operationele externe toepassing, nog niet geïntegreerd in DVK.'],
        'Overige werkgebieden': [
            '**Ledenadministratie** — toekomstig, niet beschikbaar.',
            '**Wedstrijdsecretariaat** — toekomstig, niet beschikbaar.',
            '**Kledingadministratie** — toekomstig, niet beschikbaar.'],
        'DVK Beheer': [
            '**Toegangsbeheer** — toekomstig, niet beschikbaar.',
            '**Tabelonderhoud** — toekomstig, niet beschikbaar.'],
    }


def test_function_settings_are_directly_under_main_screen_title(tmp_path):
    app = app_at(tmp_path)
    app.button(key='nav-planning').click().run()
    assert not app.exception
    children = list(app.main.children.values())
    assert [x.type for x in children[:4]] == ['title', 'subheader', 'radio', 'date_input']
    assert app.main.radio(key='planning-mode').value == 'Week'
    assert app.main.date_input(key='planning-from').value == date.today()
    app.main.radio(key='planning-mode').set_value('Aangepast').run()
    assert app.main.date_input(key='planning-until').value > app.main.date_input(key='planning-from').value
    assert not app.sidebar.radio and not app.sidebar.date_input
    app.button(key='nav-control').click().run()
    assert not app.exception
    children = list(app.main.children.values())
    assert [x.type for x in children[:4]] == ['title', 'markdown', 'date_input', 'text_input']
    assert children[1].value == '### Taakplichtcontrole — read-only'
    assert app.main.date_input(key='duty-control-date').value == date.today()
    assert not app.sidebar.date_input and not app.sidebar.text_input
    assert [x.value for x in app.sidebar.header] == ['DVK']
