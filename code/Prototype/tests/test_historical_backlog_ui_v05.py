"""Optional historical-source UI behaviour; all files use synthetic HOME."""
from ui_table_events import table, pick

from dvk.historical_backlog import HISTORICAL_FILENAME
from dvk.sportlink_exports import default_export_directory
from test_candidate_context_ui_v05 import operational_page
from test_historical_backlog_v05 import history_row, history_text
from test_volunteer_planning_integration_v05 import snapshot


def test_missing_then_valid_then_invalid_history_refresh_keeps_planning(operational_page):
    app, db, _ = operational_page
    assert any('Historische urenbron ontbreekt' in w.value for w in app.warning)
    before = snapshot(db)
    assert not table(app).value.empty
    path = default_export_directory() / HISTORICAL_FILENAME
    path.write_text(history_text([history_row(value=6)]))
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    pick(app)
    assert any('vorig seizoen: 6.' in c.value for c in app.caption)
    assert snapshot(db)==before
    next(b for b in app.button if b.label=='Selectie bevestigen').click().run()
    assert not app.exception
    after = snapshot(db)
    assert after != before
    path.write_text(history_text([history_row(),history_row()]))
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception
    assert any('onbetrouwbare' in w.value for w in app.warning)
    assert any('Melding' in t.value and any('achterstand niet gebruikt' in message
               for message in t.value['Melding']) for t in app.table)
    assert snapshot(db)==after
    # Undo still works after historical-source quality changes.
    next(b for b in app.button if b.label=='Tijdelijke inroostering ongedaan maken').click().run()
    assert not app.exception
    assert not table(app).value.empty
    pick(app)
    assert any('geen vastgestelde nulachterstand' in c.value for c in app.caption)
    assert not any('Geen historische achterstand: 0 uur.' in c.value for c in app.caption)
    path.write_text('Relatiecode;Niet ingedeeld\nM1;6')
    app.button(key='load-candidate-sources').click().run()
    assert not app.exception and not table(app).value.empty
    assert any('structureel ongeldig' in w.value for w in app.warning)
