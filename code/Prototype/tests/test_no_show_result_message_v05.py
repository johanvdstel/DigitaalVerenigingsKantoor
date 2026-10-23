"""One-shot registration feedback must not replace durable No-Show history."""
from datetime import timedelta

import pytest
from streamlit.testing.v1 import AppTest

from dvk.application_services import NoShowApplicationService
from dvk.planning import PlanningPeriod
from dvk.shift_catalog import load_shift_catalog
from test_planning_ui_names_v05 import page
from test_volunteer_planning_integration_v05 import IDENTITY, PERIOD, people, row, sync

FIRST = 'Eerste no-show: waarschuwing. Betrokkene moet zelf een vervangende inzet regelen.'
COMMUNICATION = 'Communicatie hierover is vereist.'


def submit(app):
    next(b for b in app.button if b.label == 'No-show bevestigen').click().run()
    assert not app.exception


def assert_no_registration_feedback(app):
    assert not any(w.value.startswith(('Eerste no-show:', 'No-show 2:')) for w in app.warning)
    assert not any(COMMUNICATION in i.value for i in app.info)


def setup(app, db):
    catalog = load_shift_catalog()
    first = catalog.bindings(PERIOD)[0]
    later = next(b for b in catalog.bindings(PERIOD) if b.service.starts_at.date() > first.service.starts_at.date())
    payload = {}
    for b in (first, later):
        payload.setdefault(b.task_code, []).append(row(b.service, people()[0]))
    assert sync(db, catalog, payload)[0] is None
    app.run()
    return catalog


@pytest.mark.parametrize('action', ['rerun', 'navigation', 'new_browser', 'synchronize', 'period_and_synchronize'])
def test_first_feedback_is_shown_once_and_history_survives_later_screen_views(tmp_path, action):
    app, db = page(tmp_path)
    catalog = setup(app, db)
    submit(app)
    assert any(w.value == FIRST for w in app.warning)
    assert any(COMMUNICATION in i.value for i in app.info)
    assert 'last-no-show' not in app.session_state
    with db.unit_of_work() as u:
        fact, = u.no_shows.all()
        original = u.sanctions.get(fact.no_show_id)
    if action == 'rerun':
        app.run()
    elif action == 'navigation':
        app.button(key='nav-home').click().run()
        app.button(key='nav-planning').click().run()
    elif action == 'new_browser':
        app = AppTest.from_file(str(tmp_path / 'streamlit_app.py'), default_timeout=20).run()
        app.button(key='nav-planning').click().run()
        app.button(key='resume-planning').click().run()
    elif action == 'synchronize':
        assert sync(db, catalog, {})[0] is None
        app.run()
    else:
        new_period = PlanningPeriod(PERIOD.start+timedelta(days=7), PERIOD.end+timedelta(days=7))
        app.date_input(key='planning-from').set_value(new_period.start).run()
        assert_no_registration_feedback(app)
        app.button(key='confirm-period-change').click().run()
        assert_no_registration_feedback(app)
        assert sync(db, catalog, {}, period=new_period)[0] is None
        app.run()
    assert not app.exception
    assert_no_registration_feedback(app)
    with db.unit_of_work() as u:
        assert u.no_shows.all() == (fact,)
        assert u.sanctions.get(fact.no_show_id) == original
        assert NoShowApplicationService(u, IDENTITY).current_state(fact.person_id, fact.season).counter == 1
        assert not u.no_show_revocations.for_no_show(fact.no_show_id)


def test_second_feedback_duplicate_protection_and_revocation_keep_existing_semantics(tmp_path):
    app, db = page(tmp_path)
    setup(app, db)
    submit(app)
    with db.unit_of_work() as u:
        first, = u.no_shows.all()
        other = next(b for b in u.sportlink_bookings.all() if b.assignment_id != first.assignment_id)
    next(s for s in app.selectbox if s.label == 'Inroostering').select(other.assignment_id)
    submit(app)
    assert any(w.value == 'No-show 2: gele kaart, €75 boete en 1 wedstrijd(en) schorsing.' for w in app.warning)
    assert any(COMMUNICATION in i.value for i in app.info)
    with db.unit_of_work() as u:
        history = u.no_shows.all()
        assert len(history) == 2
        assert NoShowApplicationService(u, IDENTITY).current_state(first.person_id, first.season).counter == 2
    submit(app)  # Duplicate submission may report an error, never repeat the success feedback.
    assert any('al een no-show geregistreerd' in e.value for e in app.error)
    assert_no_registration_feedback(app)
    with db.unit_of_work() as u:
        assert u.no_shows.all() == history
    next(s for s in app.selectbox if s.label == 'No-show intrekken').select(first.no_show_id)
    app.text_area(key='no-show-revocation-reason').set_value('Synthetic correction')
    next(b for b in app.button if b.label == 'Intrekking bevestigen').click().run()
    assert not app.exception
    assert_no_registration_feedback(app)
    with db.unit_of_work() as u:
        assert u.no_shows.all() == history
        assert u.no_show_revocations.for_no_show(first.no_show_id).reason == 'Synthetic correction'
        assert NoShowApplicationService(u, IDENTITY).current_state(first.person_id, first.season).counter == 1
