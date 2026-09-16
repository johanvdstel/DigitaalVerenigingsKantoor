from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .migrations import migrate


class SQLiteRecordRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def add(self, record_id: str, payload: str) -> None:
        self._connection.execute(
            "INSERT INTO dvk_records(record_id, payload) VALUES (?, ?)",
            (record_id, payload),
        )

    def get(self, record_id: str) -> dict[str, Any] | None:
        row = self._connection.execute(
            "SELECT record_id, payload FROM dvk_records WHERE record_id = ?",
            (record_id,),
        ).fetchone()
        if row is None:
            return None
        return {"record_id": row[0], "payload": row[1]}


class SQLiteUnitOfWork:
    def __init__(self, database_path: str | Path) -> None:
        self._database_path = str(database_path)
        self._connection: sqlite3.Connection | None = None
        self.records: SQLiteRecordRepository
        self._committed = False

    def __enter__(self) -> "SQLiteUnitOfWork":
        self._connection = sqlite3.connect(self._database_path)
        migrate(self._connection)
        self.records = SQLiteRecordRepository(self._connection)
        self._committed = False
        return self

    def commit(self) -> None:
        if self._connection is None:
            raise RuntimeError("Unit of work is not active")
        self._connection.commit()
        self._committed = True

    def rollback(self) -> None:
        if self._connection is not None:
            self._connection.rollback()

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if self._connection is None:
            return False
        try:
            if exc_type is not None or not self._committed:
                self._connection.rollback()
        finally:
            self._connection.close()
            self._connection = None
        return False


class SQLiteDatabase:
    """SQLite infrastructure adapter; callers receive a transaction boundary."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def initialize(self) -> int:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            return migrate(connection)

    def unit_of_work(self) -> SQLiteUnitOfWork:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        return SQLiteUnitOfWork(self.path)
