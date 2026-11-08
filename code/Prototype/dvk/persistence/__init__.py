"""Persistence boundary for DVK Prototype v0.5.

The domain and application layers should depend on repository and unit-of-work
contracts, never on SQLite directly.
"""

from .repositories import RecordRepository
from .sqlite import SQLiteDatabase
from .unit_of_work import UnitOfWork

__all__ = ["RecordRepository", "SQLiteDatabase", "UnitOfWork"]
