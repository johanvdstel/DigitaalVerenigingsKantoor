from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any


def canonical_json(value: Any) -> str:
    """Serialize versioned content deterministically before hashing/persisting."""
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_json_default)


def content_hash(content_json: str) -> str:
    return hashlib.sha256(content_json.encode("utf-8")).hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Unsupported version content: {type(value)!r}")


@dataclass(frozen=True)
class PolicyVersion:
    version_id: str
    content_json: str
    content_hash: str
    created_at: datetime
    created_by: str
    effective_from: date

    @classmethod
    def create(cls, version_id: str, content: Any, *, created_at: datetime, created_by: str, effective_from: date) -> "PolicyVersion":
        serialized = canonical_json(content)
        return cls(version_id, serialized, content_hash(serialized), created_at, created_by, effective_from)

    def __post_init__(self) -> None:
        _validate_common(self.version_id, self.content_json, self.content_hash, self.created_by)


@dataclass(frozen=True)
class ConfigVersion:
    version_id: str
    content_json: str
    content_hash: str
    created_at: datetime
    created_by: str
    effective_from: date

    @classmethod
    def create(cls, version_id: str, content: Any, *, created_at: datetime, created_by: str, effective_from: date) -> "ConfigVersion":
        serialized = canonical_json(content)
        return cls(version_id, serialized, content_hash(serialized), created_at, created_by, effective_from)

    def __post_init__(self) -> None:
        _validate_common(self.version_id, self.content_json, self.content_hash, self.created_by)


@dataclass(frozen=True)
class SoftwareVersion:
    version_id: str
    release_label: str
    git_commit_sha: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.version_id.strip() or not self.release_label.strip():
            raise ValueError("software version_id and release_label are required")
        if not re.fullmatch(r"[0-9a-f]{40}", self.git_commit_sha):
            raise ValueError("git_commit_sha must be a full 40-character hexadecimal Git commit id")


def _validate_common(version_id: str, content_json: str, expected_hash: str, created_by: str) -> None:
    if not version_id.strip() or not created_by.strip():
        raise ValueError("version_id and created_by are required")
    if content_hash(content_json) != expected_hash:
        raise ValueError("content_hash does not match canonical content")
