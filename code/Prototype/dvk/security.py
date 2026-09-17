from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Permission(str, Enum):
    VIEW_PLANNING = "view_planning"
    VIEW_PERSONAL_DATA = "view_personal_data"
    PREVIEW_IMPORT = "preview_import"
    CONFIRM_IMPORT = "confirm_import"
    RECORD_ENGINE_RUN = "record_engine_run"
    DECIDE_PROPOSAL = "decide_proposal"
    VIEW_AUDIT = "view_audit"
    ADMINISTER_SECURITY = "administer_security"


@dataclass(frozen=True)
class Identity:
    subject_id: str
    display_name: str
    permissions: frozenset[Permission]

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("subject_id is required")


class AuthorizationError(PermissionError):
    pass


class Authorizer:
    """Server-side authorization boundary based on explicit permissions."""

    def require(self, identity: Identity, permission: Permission) -> None:
        if permission not in identity.permissions:
            raise AuthorizationError(
                f"{identity.subject_id} is not authorized for {permission.value}"
            )
