"""One active planning period per application process and SQLite database.

Imported module state survives Streamlit script reruns and browser sessions.
Only active work is removed; durable facts and historical records are untouched.
"""
from pathlib import Path
from threading import RLock

from .planning import PlanningPeriod

_lock = RLock()
_periods: dict[Path, PlanningPeriod | None] = {}


def _clear_work(uow):
    for entry in uow.temporary_planning.all():
        uow.temporary_planning.remove(entry.assignment.assignment_id)


def prepare_planning(database) -> PlanningPeriod | None:
    """Discard previous-process work once, before allowing planning access.

    Failed initialization is not remembered. A new connection/database object
    is not a new process and must not discard current-process work.
    """
    key = database.path.resolve()
    with _lock:
        if key not in _periods:
            with database.unit_of_work() as uow:
                uow.begin_planning_write()
                _clear_work(uow)
                uow.commit()
            _periods[key] = None
        return _periods[key]


def choose_period(database, requested: PlanningPeriod, *, discard: bool = False) -> bool:
    """Activate a period, or request confirmation while retaining old state.

    The UI supplies explicit confirmation through discard. Deletion and commit
    must succeed before the in-process period changes.
    """
    key = database.path.resolve()
    with _lock:
        current = prepare_planning(database)
        if current == requested:
            return True
        with database.unit_of_work() as uow:
            uow.begin_planning_write()
            active = uow.temporary_planning.all()
            if active and not discard:
                return False
            if active:
                _clear_work(uow)
            uow.commit()
        _periods[key] = requested
        return True
