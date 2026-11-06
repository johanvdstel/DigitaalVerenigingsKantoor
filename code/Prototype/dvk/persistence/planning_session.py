"""Single typed session record in the existing PK-protected local record store."""
import json
from datetime import date, time
from dataclasses import asdict

from ..shift_catalog import ShiftCatalog, ShiftDefinition, StaffingRule, WeeklySlot

from ..planning import PlanningPeriod
from ..planning_session import PlanningSession

KEY = 'active-planning-session'


class SQLitePlanningSessionRepository:
    def __init__(self, connection):
        self._connection = connection

    def get(self):
        row = self._connection.execute('SELECT payload FROM dvk_records WHERE record_id=?', (KEY,)).fetchone()
        if row is None:
            return None
        data = json.loads(row[0])
        return PlanningSession(data['session_id'], PlanningPeriod(date.fromisoformat(data['start']),
                               date.fromisoformat(data['end'])), data['source_revision'], _catalog(data.get('catalog')))

    def save(self, session):
        payload = dict(session_id=session.session_id, start=session.period.start.isoformat(),
                       end=session.period.end.isoformat(), source_revision=session.source_revision,
                       catalog=asdict(session.catalog) if session.catalog else None)
        self._connection.execute('INSERT OR REPLACE INTO dvk_records VALUES (?, ?)', (KEY, json.dumps(payload, default=lambda value: value.isoformat())))

    def remove(self):
        self._connection.execute('DELETE FROM dvk_records WHERE record_id=?', (KEY,))


def _catalog(data):
    if data is None:
        return None
    definitions = tuple(ShiftDefinition(**dict(d, staffing_rules=tuple(StaffingRule(**r) for r in d['staffing_rules'])))
                        for d in data['definitions'])
    slots = tuple(WeeklySlot(s['weekday'], time.fromisoformat(s['starts_at']), time.fromisoformat(s['ends_at']),
                            s['task_code'], date.fromisoformat(s['date_from']) if s.get('date_from') else None,
                            date.fromisoformat(s['date_to']) if s.get('date_to') else None) for s in data['slots'])
    return ShiftCatalog(definitions, slots)
