from __future__ import annotations

from typing import Protocol

from .repositories import RecordRepository


class UnitOfWork(Protocol):
    """Transaction boundary exposed to application services."""

    records: RecordRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, exc_type, exc_value, traceback) -> bool | None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
