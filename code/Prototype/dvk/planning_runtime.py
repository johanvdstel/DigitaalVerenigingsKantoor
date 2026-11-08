"""Compatibility entry points backed by durable session storage, never module state."""
from .planning_session import PlanningSessionApplicationService
from .security import Identity, Permission

_RUNTIME_IDENTITY = Identity('planning-runtime', 'Planner', frozenset({Permission.DECIDE_PROPOSAL}))


def prepare_planning(database):
    """Opening/navigating/restarting is strictly read-only for planning work."""
    with database.unit_of_work() as uow:
        session = uow.planning_sessions.get()
        return session.period if session else None


def choose_period(database, requested, *, discard=False):
    with database.unit_of_work() as uow:
        current = uow.planning_sessions.get()
        if current and current.period == requested:
            return True
        if current and not discard:
            return False
        PlanningSessionApplicationService(uow, _RUNTIME_IDENTITY).start(
            requested, confirmed=discard, expected_session_id=current.session_id if current else None)
        return True
