from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

from ..no_show import NoShowEvent, NoShowRevocation, SanctionAssessment


class SQLiteNoShowRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, event: NoShowEvent) -> None:
        self._connection.execute(
            "INSERT INTO no_show_events VALUES (?, ?, ?, ?, ?, ?)",
            (event.no_show_id, event.assignment_id, event.person_id, event.season,
             event.occurred_at.isoformat(), json.dumps(asdict(event), default=str)),
        )

    def all(self) -> tuple[NoShowEvent, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM no_show_events ORDER BY occurred_at, no_show_id"
        ).fetchall()
        return tuple(_event(json.loads(row[0])) for row in rows)

    def get(self, no_show_id: str) -> NoShowEvent | None:
        row = self._connection.execute("SELECT payload FROM no_show_events WHERE no_show_id=?", (no_show_id,)).fetchone()
        return None if row is None else _event(json.loads(row[0]))

    def for_assignment(self, assignment_id: str) -> NoShowEvent | None:
        row = self._connection.execute(
            "SELECT payload FROM no_show_events WHERE assignment_id=?", (assignment_id,)
        ).fetchone()
        return None if row is None else _event(json.loads(row[0]))

    def for_person_season(self, person_id: str, season: str) -> tuple[NoShowEvent, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM no_show_events WHERE person_id=? AND season=? ORDER BY occurred_at, no_show_id",
            (person_id, season),
        ).fetchall()
        return tuple(_event(json.loads(row[0])) for row in rows)


class SQLiteNoShowRevocationRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, revocation: NoShowRevocation) -> None:
        self._connection.execute(
            "INSERT INTO no_show_revocations VALUES (?, ?, ?, ?, ?)",
            (revocation.revocation_id, revocation.no_show_id, revocation.reason,
             revocation.revoked_at.isoformat(), revocation.revoked_by),
        )

    def for_no_show(self, no_show_id: str) -> NoShowRevocation | None:
        row = self._connection.execute(
            "SELECT * FROM no_show_revocations WHERE no_show_id=?", (no_show_id,)
        ).fetchone()
        return None if row is None else _revocation(row)

    def for_person_season(self, person_id: str, season: str) -> tuple[NoShowRevocation, ...]:
        rows = self._connection.execute(
            """SELECT r.* FROM no_show_revocations r
               JOIN no_show_events n ON n.no_show_id=r.no_show_id
               WHERE n.person_id=? AND n.season=? ORDER BY r.revoked_at, r.revocation_id""",
            (person_id, season),
        ).fetchall()
        return tuple(_revocation(row) for row in rows)


class SQLiteSanctionAssessmentRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, assessment: SanctionAssessment) -> None:
        self._connection.execute(
            "INSERT INTO sanction_assessments VALUES (?, ?, ?, ?, ?)",
            (assessment.no_show_id, assessment.person_id, assessment.season,
             assessment.counter, json.dumps(asdict(assessment))),
        )

    def get(self, no_show_id: str) -> SanctionAssessment | None:
        row = self._connection.execute(
            """SELECT s.payload FROM sanction_assessments s
               JOIN no_show_events n ON n.no_show_id=s.no_show_id
               WHERE s.no_show_id=? AND NOT EXISTS (
                   SELECT 1 FROM no_show_revocations r WHERE r.no_show_id=n.no_show_id
               )""", (no_show_id,)
        ).fetchone()
        return None if row is None else SanctionAssessment(**json.loads(row[0]))


def _event(data: dict) -> NoShowEvent:
    # Valid legacy payloads stay byte-for-byte intact during migration.
    # Their obsolete mutable-model fields are not part of the new fact model.
    for key in ("status", "correction_reason", "corrected_at", "corrected_by"):
        data.pop(key, None)
    for key in ("occurred_at", "recorded_at"):
        if data.get(key):
            data[key] = datetime.fromisoformat(data[key])
    return NoShowEvent(**data)


def _revocation(row) -> NoShowRevocation:
    return NoShowRevocation(row[0], row[1], row[2], datetime.fromisoformat(row[3]), row[4])
