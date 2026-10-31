"""Durable single-session lifecycle; no browser/process lifetime business rules."""
from dataclasses import dataclass
from uuid import uuid4
from zoneinfo import ZoneInfo

from .planning import PlanningPeriod
from .security import Authorizer, Permission
from .shift_catalog import ShiftCatalog

TZ = ZoneInfo('Europe/Amsterdam')


@dataclass(frozen=True)
class PlanningSession:
    session_id: str
    period: PlanningPeriod
    source_revision: str | None = None
    catalog: ShiftCatalog | None = None


def active_source(uow, period=None):
    """One shared definition of a validated active source for all consumers."""
    session = uow.planning_sessions.get()
    success = uow.sportlink_bookings.refresh_state()
    if not session or not session.source_revision or not success:
        return None
    if period is not None and session.period != period:
        return None
    if (success.get('session_id'), success.get('source_revision'), success.get('start'), success.get('end')) != (
            session.session_id, session.source_revision, session.period.start.isoformat(), session.period.end.isoformat()):
        return None
    if success.get('status') not in ('Geslaagd', 'Geslaagd, met aandachtspunten'):
        return None
    return session


def booking_in_period(booking, period):
    return period.start <= booking.starts_at.astimezone(TZ).date() <= period.end


class PlanningSessionApplicationService:
    def __init__(self, uow, identity):
        self.uow, self.identity = uow, identity

    def catalog(self):
        """The session owns its loaded configuration, without versions or comparisons."""
        Authorizer().require(self.identity, Permission.VIEW_PLANNING)
        session = self.uow.planning_sessions.get()
        if session and session.catalog is not None:
            return session.catalog
        from .shift_catalog import load_shift_catalog
        return load_shift_catalog()

    def reload_catalog(self, period, *, confirmed=False, expected_session_id=None, catalog=None):
        Authorizer().require(self.identity, Permission.DECIDE_PROPOSAL)
        from .shift_catalog import load_shift_catalog
        catalog = load_shift_catalog() if catalog is None else catalog
        # Validate every concrete boundary before any session/work is removed.
        catalog.bindings(period)
        if not confirmed:
            raise ValueError('Bevestig Reload catalog; de huidige sessie en tijdelijke indelingen vervallen.')
        return self.start(period, confirmed=True, expected_session_id=expected_session_id, catalog=catalog)

    def current(self):
        Authorizer().require(self.identity, Permission.VIEW_PLANNING)
        return self.uow.planning_sessions.get()

    def start(self, period, *, confirmed=False, expected_session_id=None, catalog=None):
        Authorizer().require(self.identity, Permission.DECIDE_PROPOSAL)
        self.uow.begin_planning_write()
        current = self.uow.planning_sessions.get()
        if current and (not confirmed or current.session_id != expected_session_id):
            raise ValueError('Bevestig het afsluiten van de huidige planning; tijdelijke indelingen vervallen.')
        if not current and expected_session_id is not None:
            raise ValueError('De planning is gewijzigd; open de planning opnieuw.')
        try:
            self._clear()
            session = PlanningSession(str(uuid4()), period, catalog=catalog if catalog is not None else (current.catalog if current else None))
            self.uow.planning_sessions.save(session)
            self.uow.commit()
        except BaseException:
            self.uow.rollback()
            raise
        return session

    def close(self, *, confirmed=False, expected_session_id=None):
        Authorizer().require(self.identity, Permission.DECIDE_PROPOSAL)
        self.uow.begin_planning_write()
        current = self.uow.planning_sessions.get()
        if not current or not confirmed or current.session_id != expected_session_id:
            raise ValueError('Bevestig het afsluiten van de huidige planning.')
        try:
            self._clear()
            self.uow.planning_sessions.remove()
            self.uow.commit()
        except BaseException:
            self.uow.rollback()
            raise

    def _clear(self):
        for entry in self.uow.temporary_planning.all():
            self.uow.temporary_planning.remove(entry.assignment.assignment_id)
        self.uow.sportlink_bookings.replace_all(())
        self.uow.sportlink_bookings.clear_refresh_state()
