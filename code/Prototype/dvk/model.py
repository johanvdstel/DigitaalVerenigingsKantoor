from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(frozen=True)
class Person:
    person_id: str
    name: str
    birth_date: date | None = None
    mobile_number: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class Membership:
    person_id: str
    status: str
    kind: str
    start_date: date | None = None
    end_date: date | None = None
    plays_football: bool = False
    recreational: bool = False
    honorary: bool = False


@dataclass(frozen=True)
class PersonRelationship:
    from_person_id: str
    to_person_id: str
    relationship_type: str
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True


@dataclass(frozen=True)
class RoleAssignment:
    person_id: str
    role: str
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True


@dataclass(frozen=True)
class Resource:
    resource_id: str
    name: str
    resource_type: str = "information_system"


@dataclass(frozen=True)
class AuthorityGrant:
    authority_id: str
    resource_id: str
    actions: frozenset[str]
    granted_by: str
    role: str | None = None
    person_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True


@dataclass(frozen=True)
class RequiredAuthorization:
    person_id: str
    resource_id: str
    actions: frozenset[str]
    authority_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccessGrant:
    person_id: str
    system: str
    levels: frozenset[str]
    delegated_by: str | None = None
    granted_by: str | None = None

    @property
    def resource_id(self) -> str:
        return self.system


@dataclass(frozen=True)
class DutyRegistration:
    person_id: str
    required_hours: int | None = None
    completed_hours: int = 0


@dataclass(frozen=True)
class ClothingIssue:
    person_id: str
    article: str
    size: str | None = None
    returned: bool = False
    financially_settled: bool = False

    @property
    def resolved(self) -> bool:
        return self.returned or self.financially_settled


@dataclass(frozen=True)
class ComplianceFact:
    person_id: str
    compliance_type: str
    valid: bool
    valid_from: date | None = None
    valid_until: date | None = None


@dataclass(frozen=True)
class Signal:
    code: str
    message: str
    severity: str = "attention"
    subject_id: str | None = None
    facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    action_type: str
    subject_id: str | None = None
    responsible_role: str | None = None
    reason: str | None = None
    status: str = "proposed"
    facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    code: str
    status: str
    message: str
    facts: dict[str, Any] = field(default_factory=dict)
    signals: tuple[Signal, ...] = ()
    actions: tuple[Action, ...] = ()


@dataclass(frozen=True)
class PrototypeCase:
    case_id: str
    description: str
    person: Person
    membership: Membership
    persons: tuple[Person, ...] = ()
    memberships: tuple[Membership, ...] = ()
    relationships: tuple[PersonRelationship, ...] = ()
    roles: tuple[RoleAssignment, ...] = ()
    authorities: tuple[AuthorityGrant, ...] = ()
    resources: tuple[Resource, ...] = ()
    access: tuple[AccessGrant, ...] = ()
    duty: DutyRegistration | None = None
    duties: tuple[DutyRegistration, ...] = ()
    clothing: tuple[ClothingIssue, ...] = ()
    compliance: tuple[ComplianceFact, ...] = ()
    context_date: date | None = None
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def all_persons(self) -> tuple[Person, ...]:
        result: dict[str, Person] = {self.person.person_id: self.person}
        result.update({p.person_id: p for p in self.persons})
        return tuple(result.values())

    @property
    def all_memberships(self) -> tuple[Membership, ...]:
        return (self.membership, *self.memberships)

    @property
    def all_duties(self) -> tuple[DutyRegistration, ...]:
        return ((self.duty,) if self.duty else ()) + self.duties
