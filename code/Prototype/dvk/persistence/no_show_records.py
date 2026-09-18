from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

from ..no_show import NoShowEvent, SanctionAssessment


class SQLiteNoShowRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, event: NoShowEvent) -> None:
        self._connection.execute(
            "INSERT INTO no_show_events VALUES (?, ?, ?, ?, ?, ?, ?)",
            (event.no_show_id, event.assignment_id, event.person_id, event.season,
             event.occurred_at.isoformat(), event.status, json.dumps(asdict(event), default=str)),
        )

    def update(self, event: NoShowEvent) -> None:
        self._connection.execute(
            "UPDATE no_show_events SET status=?, payload=? WHERE no_show_id=?",
            (event.status, json.dumps(asdict(event), default=str), event.no_show_id),
        )

    def get(self, no_show_id: str) -> NoShowEvent | None:
        row = self._connection.execute("SELECT payload FROM no_show_events WHERE no_show_id=?", (no_show_id,)).fetchone()
        return None if row is None else _event(json.loads(row[0]))

    def for_person_season(self, person_id: str, season: str) -> tuple[NoShowEvent, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM no_show_events WHERE person_id=? AND season=? ORDER BY occurred_at, no_show_id",
            (person_id, season),
        ).fetchall()
        return tuple(_event(json.loads(row[0])) for row in rows)


class SQLiteSanctionAssessmentRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, assessment: SanctionAssessment) -> None:
        self._connection.execute(
            "INSERT INTO sanction_assessments VALUES (?, ?, ?, ?, ?)",
            (assessment.no_show_id, assessment.person_id, assessment.season,
             assessment.counter, json.dumps(asdict(assessment))),
        )

    def get(self, no_show_id: str) -> SanctionAssessment | None:
        row = self._connection.execute("SELECT payload FROM sanction_assessments WHERE no_show_id=?", (no_show_id,)).fetchone()
        return None if row is None else SanctionAssessment(**json.loads(row[0]))


def _event(data: dict) -> NoShowEvent:
    for key in ("occurred_at", "recorded_at", "corrected_at"):
        if data.get(key):
            data[key] = datetime.fromisoformat(data[key])
    return NoShowEvent(**data)
