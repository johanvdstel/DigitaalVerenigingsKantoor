from __future__ import annotations

from typing import Any, Protocol


class RecordRepository(Protocol):
    """Minimal persistence port used to prove the Gate 1 boundary.

    Gate 1 deliberately stores generic records only. Domain-specific repositories
    are introduced in later gates when their persisted concepts are implemented.
    """

    def add(self, record_id: str, payload: str) -> None: ...

    def get(self, record_id: str) -> dict[str, Any] | None: ...
