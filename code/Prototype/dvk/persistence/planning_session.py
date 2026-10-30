"""Single typed session record in the existing PK-protected local record store."""
import json
from datetime import date

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
                               date.fromisoformat(data['end'])), data['source_revision'])

    def save(self, session):
        payload = dict(session_id=session.session_id, start=session.period.start.isoformat(),
                       end=session.period.end.isoformat(), source_revision=session.source_revision)
        self._connection.execute('INSERT OR REPLACE INTO dvk_records VALUES (?, ?)', (KEY, json.dumps(payload)))

    def remove(self):
        self._connection.execute('DELETE FROM dvk_records WHERE record_id=?', (KEY,))
