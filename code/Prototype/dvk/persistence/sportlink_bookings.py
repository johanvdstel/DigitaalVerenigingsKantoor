"""Current read-only Sportlink bookings; independent of temporary DVK work."""
import json
from datetime import datetime

from ..real_data_import import Provenance
from ..vrijwilligers_adapter import VolunteerBooking
from ..workstream_model import DutyService
from .planning_records import _dump


def booking_from_dict(data):
    data = dict(data)
    for key in ("starts_at", "ends_at"):
        data[key] = datetime.fromisoformat(data[key])
    if data.get("provenance"):
        provenance = dict(data["provenance"])
        provenance["imported_at"] = datetime.fromisoformat(provenance["imported_at"])
        data["provenance"] = Provenance(**provenance)
    if data.get("service"):
        service = dict(data["service"])
        for key in ("starts_at", "ends_at"):
            service[key] = datetime.fromisoformat(service[key])
        data["service"] = DutyService(**service)
    return VolunteerBooking(**data)


class SQLiteSportlinkBookingRepository:
    def __init__(self, connection):
        self._connection = connection

    def replace_all(self, bookings):
        self._connection.execute("DELETE FROM sportlink_bookings")
        self._connection.executemany("INSERT INTO sportlink_bookings VALUES (?, ?)",
                                     [(b.assignment_id, _dump(b)) for b in bookings])

    def get(self, assignment_id):
        row = self._connection.execute("SELECT payload FROM sportlink_bookings WHERE assignment_id=?", (assignment_id,)).fetchone()
        return None if row is None else booking_from_dict(json.loads(row[0]))

    def recent(self, limit=50):
        rows = self._connection.execute("SELECT payload FROM sportlink_bookings ORDER BY rowid DESC LIMIT ?", (limit,)).fetchall()
        return tuple(booking_from_dict(json.loads(row[0])) for row in rows)
