from __future__ import annotations

import json
from dataclasses import asdict, fields
from datetime import datetime

from ..workstream_model import AssignmentProposal, DutyAssignment, DutyService, HumanDecision
from ..planning_workqueue import TemporaryPlanning


def _dump(value) -> str:
    return json.dumps(asdict(value), default=lambda item: item.isoformat() if isinstance(item, datetime) else item, sort_keys=True)


def _load(model, payload: str):
    values = json.loads(payload)
    if model is AssignmentProposal:
        values["applied_priority_rules"] = tuple(values["applied_priority_rules"])
        values["uncertainties"] = tuple(values["uncertainties"])
        values["snapshot_ids"] = tuple(values["snapshot_ids"])
        if values["match_starts_at"] is not None:
            values["match_starts_at"] = datetime.fromisoformat(values["match_starts_at"])
    elif model is DutyAssignment:
        values["snapshot_ids"] = tuple(values["snapshot_ids"])
        if values["decided_at"] is not None:
            values["decided_at"] = datetime.fromisoformat(values["decided_at"])
    elif model is HumanDecision and values["decided_at"] is not None:
        values["decided_at"] = datetime.fromisoformat(values["decided_at"])
    elif model is DutyService:
        values["starts_at"] = datetime.fromisoformat(values["starts_at"])
        values["ends_at"] = datetime.fromisoformat(values["ends_at"])
    return model(**{field.name: values[field.name] for field in fields(model)})


class SQLiteAssignmentProposalRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, proposal: AssignmentProposal) -> None:
        self._connection.execute(
            "INSERT INTO assignment_proposals(proposal_id, engine_run_id, payload) VALUES (?, ?, ?)",
            (proposal.proposal_id, proposal.engine_run_id, _dump(proposal)),
        )
    def get(self, proposal_id: str) -> AssignmentProposal | None:
        row = self._connection.execute("SELECT payload FROM assignment_proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
        return None if row is None else _load(AssignmentProposal, row[0])


class SQLiteHumanDecisionRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, decision: HumanDecision) -> None:
        self._connection.execute(
            "INSERT INTO human_decisions(proposal_id, payload) VALUES (?, ?)",
            (decision.proposal_id, _dump(decision)),
        )
    def get(self, proposal_id: str) -> HumanDecision | None:
        row = self._connection.execute("SELECT payload FROM human_decisions WHERE proposal_id=?", (proposal_id,)).fetchone()
        return None if row is None else _load(HumanDecision, row[0])


class SQLiteDutyAssignmentRepository:
    def __init__(self, connection): self._connection = connection
    def add(self, assignment: DutyAssignment) -> None:
        self._connection.execute(
            "INSERT INTO duty_assignments(assignment_id, proposal_id, engine_run_id, payload) VALUES (?, ?, ?, ?)",
            (assignment.assignment_id, assignment.proposal_id, assignment.engine_run_id, _dump(assignment)),
        )
    def get(self, assignment_id: str) -> DutyAssignment | None:
        row = self._connection.execute("SELECT payload FROM duty_assignments WHERE assignment_id=?", (assignment_id,)).fetchone()
        return None if row is None else _load(DutyAssignment, row[0])
    def recent(self, limit: int = 50) -> tuple[DutyAssignment, ...]:
        rows = self._connection.execute(
            "SELECT payload FROM duty_assignments ORDER BY rowid DESC LIMIT ?", (limit,)
        ).fetchall()
        return tuple(_load(DutyAssignment, row[0]) for row in rows)


class SQLiteTemporaryPlanningRepository:
    def __init__(self, connection): self._connection = connection

    def add(self, entry: TemporaryPlanning) -> None:
        self._connection.execute(
            "INSERT INTO temporary_planning VALUES (?, ?, ?)",
            (entry.assignment.assignment_id, _dump(entry.assignment), _dump(entry.service)),
        )

    def all(self) -> tuple[TemporaryPlanning, ...]:
        rows = self._connection.execute(
            "SELECT assignment_payload, service_payload FROM temporary_planning ORDER BY rowid"
        ).fetchall()
        return tuple(TemporaryPlanning(_load(DutyAssignment, row[0]), _load(DutyService, row[1])) for row in rows)

    def remove(self, assignment_id: str) -> bool:
        return self._connection.execute(
            "DELETE FROM temporary_planning WHERE assignment_id=?", (assignment_id,)
        ).rowcount == 1
