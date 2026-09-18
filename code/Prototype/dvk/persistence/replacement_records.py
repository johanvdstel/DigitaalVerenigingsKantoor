from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime

from ..replacement_duty import ReplacementDuty


class SQLiteReplacementDutyRepository:
    def __init__(self, connection):
        self._connection = connection

    def add(self, replacement: ReplacementDuty) -> None:
        self._connection.execute(
            """INSERT INTO replacement_duties
               (replacement_id, no_show_id, assignment_id, person_id, season, completed_at, payload)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                replacement.replacement_id, replacement.no_show_id, replacement.assignment_id,
                replacement.person_id, replacement.season,
                None if replacement.completed_at is None else replacement.completed_at.isoformat(),
                json.dumps(asdict(replacement), default=str),
            ),
        )

    def update(self, replacement: ReplacementDuty) -> None:
        self._connection.execute(
            "UPDATE replacement_duties SET completed_at=?, payload=? WHERE replacement_id=?",
            (
                None if replacement.completed_at is None else replacement.completed_at.isoformat(),
                json.dumps(asdict(replacement), default=str), replacement.replacement_id,
            ),
        )

    def get(self, replacement_id: str) -> ReplacementDuty | None:
        row = self._connection.execute(
            "SELECT payload FROM replacement_duties WHERE replacement_id=?", (replacement_id,)
        ).fetchone()
        return None if row is None else _replacement(json.loads(row[0]))

    def for_no_show(self, no_show_id: str) -> ReplacementDuty | None:
        row = self._connection.execute(
            "SELECT payload FROM replacement_duties WHERE no_show_id=?", (no_show_id,)
        ).fetchone()
        return None if row is None else _replacement(json.loads(row[0]))

    def for_person_season(self, person_id: str, season: str) -> tuple[ReplacementDuty, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM replacement_duties WHERE person_id=? AND season=? ORDER BY rowid",
            (person_id, season),
        ).fetchall()
        return tuple(_replacement(json.loads(row[0])) for row in rows)


def _replacement(data: dict) -> ReplacementDuty:
    for key in ("registered_at", "completed_at"):
        if data.get(key):
            data[key] = datetime.fromisoformat(data[key])
    return ReplacementDuty(**data)
