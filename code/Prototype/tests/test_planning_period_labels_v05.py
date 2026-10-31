"""UI clarification only: display the same period used to start the session."""
from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod


@pytest.mark.parametrize('mode,end,expected,label', [
    ('Dag', None, PlanningPeriod(date(2026,10,31),date(2026,10,31)), 'Vanaf'),
    ('Week', None, PlanningPeriod(date(2026,10,26),date(2026,11,1)), 'Week waarin datum valt'),
    ('Aangepast', date(2026,11,15), PlanningPeriod(date(2026,10,31),date(2026,11,15)), 'Vanaf'),
])
def test_period_label_and_immediate_range_match_actual_session(tmp_path,mode,end,expected,label):
    script=tmp_path/'streamlit_app.py'
    script.write_text((Path(__file__).parents[1]/'streamlit_app.py').read_text())
    app=AppTest.from_file(str(script),default_timeout=20)
    app.session_state['dvk-screen']='planning'
    app.session_state['planning-mode']=mode
    app.session_state['planning-from']=date(2026,10,31)
    if end: app.session_state['planning-until']=end
    app.run()
    assert not app.exception
    assert app.date_input(key='planning-from').label==label
    assert app.radio(key='planning-mode').options==['Dag','Week','Aangepast']
    if mode=='Aangepast': assert app.date_input(key='planning-until').label=='Tot en met'
    assert not any(w.label=='Aantal weken' for w in app.number_input)
    caption=f'**Roosterperiode: {expected.start:%d-%m-%Y} t/m {expected.end:%d-%m-%Y}**'
    assert caption in [w.value for w in app.markdown]
    # Range is displayed before any source fetch or session activation.
    db=SQLiteDatabase(tmp_path/'dvk_v05.sqlite')
    with db.unit_of_work() as u:
        assert u.planning_sessions.get() is None
        assert u.sportlink_bookings.refresh_state() is None
    app.button(key='activate-planning').click().run()
    assert not app.exception
    with db.unit_of_work() as u:
        assert u.planning_sessions.get().period==expected
        assert u.sportlink_bookings.refresh_state() is None
