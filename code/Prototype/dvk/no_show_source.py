"""Independent, read-only Sportlink consultation. Never publishes planning state."""
from dataclasses import dataclass
from datetime import datetime

from .no_show import TZ, registration_period
from .security import Authorizer, Permission
from .vrijwilligers_adapter import SportlinkVrijwilligersAdapter


@dataclass(frozen=True)
class NoShowSource:
    bookings: tuple
    signals: tuple
    period: object
    fetched_at: datetime


def booking_revision(booking):
    # Fetch timestamps and row order are not source changes. Identity/context are.
    return (booking.assignment_id, booking.person_id, booking.person_name,
            booking.volunteer_name, booking.location, booking.service,
            booking.identity_issues,
            booking.provenance.source_value if booking.provenance else None)


class NoShowSourceApplicationService:
    def __init__(self, identity, client, client_id, catalog, persons):
        self.identity, self.client, self.client_id = identity, client, client_id
        self.catalog, self.persons = catalog, tuple(persons)

    def consult(self, now, *, task_codes=None):
        Authorizer().require(self.identity, Permission.MANAGE_NO_SHOWS)
        from .volunteer_planning import request_window
        period = registration_period(now)
        window = request_window(period, now.astimezone(TZ).date())
        codes = self.catalog.task_codes if task_codes is None else tuple(task_codes)
        if not codes or any(code not in {d.task_code for d in self.catalog.definitions} for code in codes):
            raise ValueError("Geen bekende taakcodes beschikbaar voor bronraadpleging")
        bookings, signals = [], []
        for code in codes:
            fetched = self.client.fetch_rows(client_id=self.client_id, task_code=code,
                                             days=window.days, weekoffset=window.weekoffset)
            result = SportlinkVrijwilligersAdapter().import_rows(
                task_code=code, rows=fetched.rows, services=(), persons=self.persons,
                imported_at=now, period=period, planning_definitions=self.catalog.definitions, strict_local_times=True)
            bookings.extend(result.bookings)
            signals.extend(result.signals)
        if any(s.severity == "ERROR" for s in signals):
            raise ValueError("Sportlink-bron kan niet betrouwbaar worden gebruikt: " +
                             "; ".join(sorted({s.message for s in signals if s.severity == "ERROR"})))
        return NoShowSource(tuple(bookings), tuple(signals), period, now)

    def verify(self, selected, now):
        # One task request on actual confirmation; no calls on ordinary UI reruns.
        current = self.consult(now, task_codes=(selected.task_code,))
        matches = tuple(b for b in current.bookings if b.assignment_id == selected.assignment_id)
        if len(matches) != 1 or not matches[0].can_register_no_show or booking_revision(matches[0]) != booking_revision(selected):
            raise ValueError("Sportlink-inroostering is gewijzigd, verdwenen of niet betrouwbaar; raadpleeg de bron opnieuw.")
        return matches[0]
