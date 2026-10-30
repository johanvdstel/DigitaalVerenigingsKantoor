"""Complete and functionally ordered No-Show choices; synthetic SQLite only."""
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from dvk.application_services import NoShowApplicationService
from dvk.persistence import SQLiteDatabase
from dvk.planning import PlanningPeriod
from dvk.planning_session import PlanningSessionApplicationService, TZ
from sportlink_fixtures import booking, seed_bookings
from test_planning_session_source_v05 import IDENTITY, event


def source(person, day=19, hour=10, *, description='Bardienst', name='Synthetic volunteer'):
    b = booking(person, when=datetime(2026, 10, day, hour))
    return replace(b, volunteer_name=name, person_name='Different synthetic member label',
                   service=replace(b.service, service_type=description))


def database(tmp_path, values):
    db = SQLiteDatabase(tmp_path / 'choices.sqlite')
    with db.unit_of_work() as u:
        seed_bookings(u, values)
    return db


def test_all_eligible_choices_beyond_fifty_reach_public_contexts_without_writes(tmp_path):
    eligible = tuple(source(f'MEMBER{i:03}', name=f'Synthetic volunteer {i:03}') for i in range(73))
    excluded = (replace(source('SHIELDED'), volunteer_name='Afgeschermd'),
                replace(source('UNLINKED'), person_id=None),
                replace(source('AMBIGUOUS'), identity_issues=('VOLUNTEER_PERSON_AMBIGUOUS',)))
    db = database(tmp_path, tuple(reversed(eligible)) + excluded)
    with db.unit_of_work() as u:
        before = u._connection.total_changes
        app = NoShowApplicationService(u, IDENTITY)
        assert app.available_assignments() == eligible
        contexts = app.assignment_contexts()
        assert tuple(c.assignment for c in contexts) == eligible
        assert all(c.source_revision == u.planning_sessions.get().source_revision for c in contexts)
        assert u._connection.total_changes == before


@pytest.mark.parametrize('reverse', [False, True])
def test_shuffled_source_is_sorted_by_date_time_description_original_name_then_key(tmp_path, reverse):
    # Deliberately opposing member labels must not replace original source names.
    a = source('Z', description='Bar', name='Anna')
    b = source('A', description='Bar', name='Zoe')
    c = source('C', description='Commissiekamer', name='Aaron')
    later = source('D', hour=11, description='A', name='Aaron')
    next_day = source('E', day=20, hour=9, description='A', name='Aaron')
    # Identical human data: only the stable technical key breaks the tie.
    twin = source('TWIN', description='Bar', name='Anna')
    same_human = sorted((a, twin), key=lambda x:x.assignment_id)
    expected = (*same_human, b, c, later, next_day)
    shuffled = (next_day, c, twin, later, b, a)
    db = database(tmp_path, tuple(reversed(shuffled)) if reverse else shuffled)
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        assert app.available_assignments() == expected
        assert tuple(c.assignment for c in app.assignment_contexts()) == expected
        assert app.available_assignments(limit=2) == expected[:2]
        assert tuple(c.assignment for c in app.assignment_contexts(limit=2)) == expected[:2]


def test_chronology_uses_dutch_local_date_and_time_across_utc_midnight(tmp_path):
    first = source('FIRST').starts_at.replace(hour=0, minute=30)
    a = replace(source('FIRST'), starts_at=first.astimezone(timezone.utc), ends_at=first+timedelta(hours=1))
    b = replace(source('SECOND'), starts_at=first.replace(hour=1), ends_at=first.replace(hour=2))
    db = database(tmp_path, (b, a))
    with db.unit_of_work() as u:
        assert a.starts_at.date() < a.starts_at.astimezone(TZ).date()
        assert NoShowApplicationService(u, IDENTITY).available_assignments() == (a, b)


@pytest.mark.parametrize('change', ['wrong_period', 'unvalidated', 'replaced', 'closed'])
def test_complete_choices_keep_active_source_period_and_registration_guards(tmp_path, change):
    old = source('OLD')
    db = database(tmp_path, (old,))
    with db.unit_of_work() as u:
        app = NoShowApplicationService(u, IDENTITY)
        choice, = app.assignment_contexts()
        active = u.planning_sessions.get()
        if change == 'wrong_period':
            wrong = PlanningPeriod(active.period.start, active.period.end+timedelta(days=1))
            assert not app.assignment_contexts(period=wrong)
            with pytest.raises(ValueError):
                app.register(event(old), source_revision=choice.source_revision, period=wrong)
            return
        if change == 'unvalidated':
            u.sportlink_bookings.clear_refresh_state(); u.commit()
        elif change == 'replaced':
            seed_bookings(u, (source('NEW', name='New synthetic volunteer'),))
        else:
            PlanningSessionApplicationService(u, IDENTITY).close(confirmed=True, expected_session_id=active.session_id)
        assert tuple(c.assignment for c in app.assignment_contexts()) == ((source('NEW', name='New synthetic volunteer'),) if change=='replaced' else ())
        with pytest.raises(ValueError, match='actieve gevalideerde bron'):
            app.register(event(old), source_revision=choice.source_revision)
        assert not u.no_shows.all()
