"""Optional historical-source UI behaviour; all files use synthetic HOME."""

from dvk.historical_backlog import HISTORICAL_FILENAME
from dvk.sportlink_exports import default_export_directory
from test_candidate_context_ui_v05 import candidate_buttons, candidate_checks, operational_page, refresh_candidate_sources
from test_historical_backlog_v05 import history_row, history_text
from test_volunteer_planning_integration_v05 import snapshot


def test_missing_then_valid_then_invalid_history_refresh_keeps_planning(operational_page):
    app, db, _ = operational_page
    assert any('Historische urenbron:' in w.value and 'ontbreekt' in w.value for w in app.warning)
    before = snapshot(db)
    assert candidate_buttons(app)
    path = default_export_directory() / HISTORICAL_FILENAME
    path.write_text(history_text([history_row(value=6)]))
    refresh_candidate_sources(app)
    assert not app.exception
    candidate_buttons(app)[0].click().run()
    assert any('vorig seizoen: 6.' in c.value for c in app.markdown)
    assert snapshot(db)==before
    candidate_checks(app)[0].check().run()
    app.button(key='planner-assign').click().run()
    assert not app.exception
    after = snapshot(db)
    assert after != before
    path.write_text(history_text([history_row(),history_row()]))
    refresh_candidate_sources(app)
    assert not app.exception
    assert any('onbetrouwbare' in w.value for w in app.warning)
    assert any('Melding' in t.value and any('achterstand niet gebruikt' in message
               for message in t.value['Melding']) for t in app.table)
    assert snapshot(db)==after
    # Undo still works after historical-source quality changes.
    next(b for b in app.button if (b.key or '').startswith('planner-undo-duty-')).click().run()
    assert not app.exception
    assert candidate_buttons(app)
    candidate_buttons(app)[0].click().run()
    assert any('geen vastgestelde nulachterstand' in c.value for c in app.markdown)
    assert not any('Geen historische achterstand: 0 uur.' in c.value for c in app.markdown)
    path.write_text('Relatiecode;Niet ingedeeld\nM1;6')
    refresh_candidate_sources(app)
    assert not app.exception and candidate_buttons(app)
    assert any('structureel ongeldig' in w.value for w in app.warning)
