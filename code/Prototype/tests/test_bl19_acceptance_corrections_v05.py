"""BL-19-02/03/05 and synthetic technical acceptance; never live sources."""
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import NoShowApplicationService
from dvk.local_csv_sources import LocalCsvSourceApplicationService
from dvk.model import Person
from dvk.no_show import NoShowEvent, assess_sanction, season_id, MANUAL_DECLARATION
from dvk.no_show_presenter import history_page, person_labels
from dvk.persistence import SQLiteDatabase
from dvk.vrijwilligers_client import SportlinkVrijwilligersClient
from test_bl19_no_show_management_v05 import (
    NOW, PERSONS, CATALOG, Client, app, inputs, db,
)
from test_schema_validation_v05 import contents

PERIOD_TEXT = 'Een No-show kan worden geregistreerd vanaf 14 kalenderdagen geleden tot en met vandaag, mits de dienst al is begonnen.'


def browser(tmp_path, monkeypatch, persons=PERSONS, client=None):
    script = tmp_path/'streamlit_app.py'
    script.write_text((Path(__file__).parents[1]/'streamlit_app.py').read_text().replace(
        'datetime.now(TZ)', 'datetime(2026, 11, 1, 12, tzinfo=TZ)'))
    monkeypatch.setattr(LocalCsvSourceApplicationService, 'volunteer_persons', lambda self: persons)
    monkeypatch.setattr('dvk.shift_catalog.load_shift_catalog', lambda: CATALOG)
    original = NoShowApplicationService.__init__
    def init(self, *args, **kw):
        kw.setdefault('clock', lambda: NOW)
        original(self, *args, **kw)
    monkeypatch.setattr(NoShowApplicationService, '__init__', init)
    if client:
        monkeypatch.setattr(SportlinkVrijwilligersClient, 'fetch_rows', lambda self, **kw: client.fetch_rows(**kw))
    database = SQLiteDatabase(tmp_path/'dvk_v05.sqlite')
    ui = AppTest.from_file(str(script), default_timeout=20).run()
    ui.button(key='nav-no-shows').click().run()
    assert not ui.exception
    return ui, database


def select(ui, label):
    return next(s for s in ui.selectbox if s.label == label)


def button(ui, label):
    return next(b for b in ui.button if b.label == label)


def history_table(ui):
    return next(t.value for t in ui.dataframe if 'Geregistreerd' in t.value.columns)


def text(ui):
    return '\n'.join(m.value for m in ui.markdown)


def seed_history(database, count=25):
    with database.unit_of_work() as u:
        for i in range(count):
            person = PERSONS[i % 3 == 0]
            start = (NOW-timedelta(days=12 if i == 0 else i % 12+1)).replace(hour=10, minute=i % 60)
            context = app(u).manual_context(**inputs(start=start, end=start+timedelta(hours=1),
                person_id=person.person_id, explanation=f'Toelichting {i}', location=f'Locatie {i}'))
            recorded = NOW - timedelta(minutes=1 if i in (1,2) else i)
            event = NoShowEvent(f'H{i:02}', f'M{i:02}', person.person_id, start, recorded,
                                'historische-planner', season_id(start.date()), manual=context)
            prior = u.no_shows.for_person_season(event.person_id, event.season)
            u.no_shows.add(event)
            u.sanctions.add(assess_sanction(event, prior))
        u.commit()
        app(u).revoke('H00', reason='Historische correctie', revoked_at=NOW+timedelta(minutes=1))
        return app(u).history()


def test_person_label_order_is_stable_and_preserves_namesakes():
    names = {'Z':'Zoë', 'B':'Alex', 'A':'Alex', 'C':'anna'}
    assert list(person_labels(names).items()) == [
        ('A','Alex (relatie A)'), ('B','Alex (relatie B)'), ('C','anna'), ('Z','Zoë')]
    assert person_labels(dict(reversed(tuple(names.items())))) == person_labels(names)


def test_both_person_widgets_are_alphabetical_and_keep_identity(tmp_path, monkeypatch):
    persons = (Person('Z','Zoë'),Person('B','Alex'),Person('C','anna'),Person('A','Alex'))
    ui, database = browser(tmp_path, monkeypatch, persons)
    expected = ['Alex (relatie A)','Alex (relatie B)','anna','Zoë']
    assert select(ui,'Persoonfilter').options == ['Alle personen', *expected]
    next(r for r in ui.radio if r.label == 'Registratievorm').set_value('Handmatig').run()
    assert select(ui,'Persoon').options == expected
    select(ui,'Persoon').select('B').run()
    select(ui,'Persoonfilter').select('A').run()
    assert select(ui,'Persoon').value == 'B'
    assert select(ui,'Persoonfilter').value == 'A'
    assert any(c.value == PERIOD_TEXT for c in ui.caption)
    with database.unit_of_work() as u:
        assert not u.no_shows.all() and u.planning_sessions.get() is None


def test_page_order_uses_recording_instant_not_service_date_and_has_stable_ties(db):
    history = seed_history(db)
    before = contents(db.path)
    first = history_page(history)
    assert (first.total,first.count,first.number,len(first.rows)) == (25,3,1,10)
    assert [e.no_show_id for e,r in first.rows[:3]] == ['H00','H02','H01']
    assert first.rows[0][0].occurred_at < first.rows[2][0].occurred_at
    assert history_page(tuple(reversed(history))).rows == first.rows
    assert len(history_page(history,2).rows) == 10
    assert len(history_page(history,3).rows) == 5
    assert history_page(history,99).number == 3
    assert contents(db.path) == before


def test_recording_order_compares_explicit_offsets_as_absolute_instants(db):
    from dataclasses import replace
    history = seed_history(db,2)
    a,b = (row[0] for row in history)
    a=replace(a,recorded_at=datetime.fromisoformat('2026-10-25T02:45:00+02:00'))
    b=replace(b,recorded_at=datetime.fromisoformat('2026-10-25T02:15:00+01:00'))
    assert history_page(((a,None),(b,None))).rows[0][0] == b


def test_browser_pages_single_details_and_preserves_entire_history(tmp_path, monkeypatch):
    database=SQLiteDatabase(tmp_path/'dvk_v05.sqlite')
    history=seed_history(database)
    before=contents(database.path)
    ui, _=browser(tmp_path,monkeypatch)
    assert len(history_table(ui)) == 10
    assert history_table(ui).iloc[0]['Locatie'] == 'Locatie 0'
    assert history_table(ui).iloc[0]['Status'] == 'Ingetrokken'
    assert select(ui,'Details van No-show').value == 'H00'
    assert 'Historische correctie' in text(ui) and 'historische-planner' in text(ui)
    assert 'Taakcode: 741' in text(ui)
    assert text(ui).count('##### Details geselecteerde No-show') == 1
    assert not any(e.label.startswith('Historie:') for e in ui.expander)
    button(ui,'Volgende pagina').click().run()
    assert len(history_table(ui)) == 10
    select(ui,'Details van No-show').select('H13').run()
    assert 'Toelichting 13' in text(ui) and 'Locatie: Locatie 13' in text(ui)
    assert 'Toelichting 0' not in text(ui)
    button(ui,'Volgende pagina').click().run()
    assert len(history_table(ui)) == 5
    assert button(ui,'Volgende pagina').disabled
    button(ui,'Vorige pagina').click().run()
    assert ui.session_state['no-show-history-page'] == 2
    with database.unit_of_work() as u:
        assert app(u).history() == history
        assert len(u.no_shows.all()) == 25
        assert app(u).current_state('P1','2026/2027').counter == 16
    assert contents(database.path) == before


@pytest.mark.parametrize('label,value', [('Persoonfilter','P1'),('Status','Actief'),('Seizoen','2025/2026')])
def test_each_filter_resets_page_to_one(tmp_path,monkeypatch,label,value):
    database=SQLiteDatabase(tmp_path/'dvk_v05.sqlite'); seed_history(database)
    # A historical season remains selectable without any source reconstruction.
    with database.unit_of_work() as u:
        old=NOW.replace(year=2025)-timedelta(days=1)
        app(u,old+timedelta(hours=1)).register_manual(**inputs(start=old,end=old+timedelta(hours=1)))
    ui,_=browser(tmp_path,monkeypatch)
    button(ui,'Volgende pagina').click().run()
    assert ui.session_state['no-show-history-page'] == 2
    select(ui,label).select(value).run()
    assert not ui.exception
    assert ui.session_state['no-show-history-page'] == 1
    assert any(c.value.startswith('Pagina 1 van') for c in ui.caption)
    if label == 'Status': assert set(history_table(ui)['Status']) == {'Actief'}


def test_revoked_details_and_current_sanction_are_independent_of_page(tmp_path,monkeypatch):
    database=SQLiteDatabase(tmp_path/'dvk_v05.sqlite')
    with database.unit_of_work() as u:
        a=app(u)
        a.register_manual(**inputs(start=NOW-timedelta(days=2)))
        a.register_manual(**inputs(start=NOW-timedelta(days=1)))
        facts=u.no_shows.all()
        assert a.current_state('P1','2026/2027').assessment.fine_eur == 75
        a.revoke(facts[0].no_show_id,reason='Gecontroleerde intrekking',revoked_at=NOW)
    ui,_=browser(tmp_path,monkeypatch)
    select(ui,'Status').select('Ingetrokken').run()
    assert 'Gecontroleerde intrekking' in text(ui)
    assert 'Actuele seizoensteller: 1' in text(ui)
    assert 'Actuele sanctie: waarschuwing' in text(ui)
    select(ui,'Status').select('Actief').run()
    assert 'Gecontroleerde intrekking' not in text(ui)
    assert 'Actuele seizoensteller: 1' in text(ui)
    with database.unit_of_work() as u:
        assert u.no_shows.all() == facts
        assert u.no_show_revocations.for_no_show(facts[0].no_show_id)
        assert u.sanctions.get(facts[1].no_show_id).counter == 2


def test_manual_browser_requires_description_declaration_and_acknowledgment(tmp_path,monkeypatch):
    ui,database=browser(tmp_path,monkeypatch)
    next(r for r in ui.radio if r.label == 'Registratievorm').set_value('Handmatig').run()
    select(ui,'Oorspronkelijke dienst').select('Andere dienst').run()
    assert not any(b.label == 'No-show bevestigen' for b in ui.button)
    next(c for c in ui.checkbox if c.label == MANUAL_DECLARATION).check().run()
    assert any('omschrijving' in e.value for e in ui.error)
    next(t for t in ui.text_input if t.label == 'Dienstomschrijving (verplicht)').set_value('Oude dienst').run()
    button(ui,'No-show bevestigen').click().run()
    with database.unit_of_work() as u:
        first,=u.no_shows.all()
        assert first.manual.task_code is None and first.manual.declaration_confirmed
    assert "Taakcode:" not in text(ui)
    assert "None" not in text(ui)
    # Same person/day with unverified task identity is a possible duplicate.
    ui.run()
    assert any('Mogelijk duplicaat' in w.value for w in ui.warning)
    button(ui,'No-show bevestigen').click().run()
    assert any('Mogelijk duplicaat' in e.value for e in ui.error)
    next(c for c in ui.checkbox if c.label.startswith('Ik heb deze mogelijke')).check().run()
    button(ui,'No-show bevestigen').click().run()
    with database.unit_of_work() as u:
        assert len(u.no_shows.all()) == 2


def test_regular_browser_preserves_source_details_and_blocks_duplicate_and_failure(tmp_path,monkeypatch):
    client=Client()
    ui,database=browser(tmp_path,monkeypatch,client=client)
    button(ui,'Sportlink-diensten raadplegen').click().run()
    chosen=select(ui,'Inroostering').value
    button(ui,'No-show bevestigen').click().run()
    assert not ui.exception and not ui.error
    with database.unit_of_work() as u:
        fact,=u.no_shows.all()
        assert fact.person_id == 'P1' and fact.assignment_id == chosen
        assert fact.booking.starts_at == NOW-timedelta(days=1,hours=2)
        assert fact.booking.ends_at == NOW-timedelta(days=1)+timedelta(hours=2)
        assert u.planning_sessions.get() is None and not u.temporary_planning.all()
    assert 'Bron: Sportlink — Vrijwilligers' in text(ui)
    assert PERSONS[0].sportlink_name in text(ui)
    assert 'Begin: 31-10-2026 10:00' in text(ui)
    ui.run()
    assert button(ui,'No-show bevestigen').disabled
    assert any('al een no-show' in e.value for e in ui.error)
    client.fail=True
    button(ui,'Sportlink-diensten raadplegen').click().run()
    assert any('Sportlink' in e.value for e in ui.error)
    next(r for r in ui.radio if r.label == 'Registratievorm').set_value('Handmatig').run()
    assert select(ui,'Persoon')
    with database.unit_of_work() as u: assert u.no_shows.all() == (fact,)


def test_synthetic_manual_sanctions_remain_season_independent(db):
    with db.unit_of_work() as u:
        a=app(u)
        assert a.register_manual(**inputs(start=NOW-timedelta(days=2))).counter == 1
        second=a.register_manual(**inputs(start=NOW-timedelta(days=1)))
        assert (second.counter,second.card,second.fine_eur,second.suspension_matches) == (2,'yellow',75,1)
        old=NOW.replace(year=2025)-timedelta(days=1)
        assert app(u,old+timedelta(hours=1)).register_manual(**inputs(start=old,end=old+timedelta(hours=1))).counter == 1
        assert a.current_state('P1','2026/2027').counter == 2
        assert a.current_state('P1','2025/2026').counter == 1


def test_manual_catalog_browser_blocks_exact_active_duplicate(tmp_path,monkeypatch):
    ui,database=browser(tmp_path,monkeypatch)
    next(r for r in ui.radio if r.label == 'Registratievorm').set_value('Handmatig').run()
    next(c for c in ui.checkbox if c.label == MANUAL_DECLARATION).check().run()
    button(ui,'No-show bevestigen').click().run()
    assert not ui.exception and not ui.error
    ui.run()
    assert any('al een no-show' in e.value for e in ui.error)
    assert button(ui,'No-show bevestigen').disabled
    with database.unit_of_work() as u:
        assert len(u.no_shows.all()) == 1
        assert app(u).current_state('P1','2026/2027').counter == 1
