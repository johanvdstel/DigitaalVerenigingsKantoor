from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


# DVK Prototype v0.2 — canoniek prototype-model
#
# Dit model is bewust klein. Het volgt de begrippenscheiding uit
# docs/informatiemodel/Canoniek_Informatiemodel.md en bevat alleen de
# bronobjecten en resultaatobjecten die nodig zijn om de masterset C01-C22
# in volgende implementatiestappen te kunnen dragen.
#
# In deze stap worden nog geen nieuwe rules of cases geïmplementeerd.


@dataclass(frozen=True)
class Person:
    """Natuurlijke persoon; rollen en lidmaatschap zijn afzonderlijke relaties."""

    person_id: str
    name: str
    birth_date: date | None = None
    mobile_number: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class Membership:
    """Formele CKC-lidmaatschapsrelatie, los van functie en voetbaldeelname."""

    person_id: str
    status: str  # active | ended | none
    kind: str
    start_date: date | None = None
    end_date: date | None = None
    plays_football: bool = False
    recreational: bool = False
    honorary: bool = False


@dataclass(frozen=True)
class PersonRelationship:
    """Tijdgebonden relatie tussen personen, bv. ouder/verzorger -> kind."""

    from_person_id: str
    to_person_id: str
    relationship_type: str  # parent_guardian
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True


@dataclass(frozen=True)
class RoleAssignment:
    """Tijdgebonden vervulling van een CKC-functie door een persoon."""

    person_id: str
    role: str
    start_date: date | None = None
    end_date: date | None = None
    active: bool = True


@dataclass(frozen=True)
class Resource:
    """Door of namens CKC beheerd object waarop handelingen mogelijk zijn."""

    resource_id: str
    name: str
    resource_type: str = "information_system"


@dataclass(frozen=True)
class AuthorityGrant:
    """Geldige bevoegdheidsgrond/delegatie voor handelingen op een resource.

    Bij voorkeur wordt de bevoegdheid aan een functie toegekend. Voor het
    prototype kan zij zo nodig rechtstreeks aan een persoon worden gekoppeld.
    """

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
    """Afgeleide gewenste autorisatie uit geldige functie/bevoegdheid.

    Dit object is opgenomen als expliciet resultaatbegrip; het hoort niet als
    voorgekookt bronfeit in een testcase te worden gebruikt.
    """

    person_id: str
    resource_id: str
    actions: frozenset[str]
    authority_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class AccessGrant:
    """Feitelijke toegang: wat een persoon technisch daadwerkelijk kan."""

    person_id: str
    system: str
    levels: frozenset[str]
    delegated_by: str | None = None
    granted_by: str | None = None

    @property
    def resource_id(self) -> str:
        """v0.2-alias; houdt bestaande v0.1-cases/rules compatibel."""

        return self.system


@dataclass(frozen=True)
class DutyRegistration:
    """Registratie van ledendiensturen bij de verplichting van een lid.

    required_hours blijft tijdelijk optioneel beschikbaar voor compatibiliteit
    met v0.1-cases. In v0.2 behoort de omvang waar mogelijk uit beleid te
    worden afgeleid.
    """

    person_id: str
    required_hours: int | None = None
    completed_hours: int = 0


@dataclass(frozen=True)
class ClothingIssue:
    """Aan een persoon/lid uitgegeven CKC-kleding."""

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
    """Minimaal compliancefeit, in v0.2 primair bedoeld voor VOG."""

    person_id: str
    compliance_type: str  # bv. VOG
    valid: bool
    valid_from: date | None = None
    valid_until: date | None = None


@dataclass(frozen=True)
class Signal:
    """Expliciete signalering voor menselijke aandacht."""

    code: str
    message: str
    severity: str = "attention"
    subject_id: str | None = None
    facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    """Door het DVK bepaalde vervolgactie; v0.2 voert deze nog niet extern uit."""

    action_type: str
    subject_id: str | None = None
    responsible_role: str | None = None
    reason: str | None = None
    status: str = "proposed"
    facts: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Decision:
    """Uitlegbaar rule-resultaat met afgeleide feiten, signalen en acties."""

    code: str
    status: str  # ok | attention | error | blocked | not_applicable
    message: str
    facts: dict[str, Any] = field(default_factory=dict)
    signals: tuple[Signal, ...] = ()
    actions: tuple[Action, ...] = ()


@dataclass(frozen=True)
class PrototypeCase:
    """Kleine relevante werkelijkheid voor één mastercase.

    v0.2 kan meerdere personen en relaties bevatten. De enkelvoudige velden
    person en membership blijven in deze stap bestaan zodat C01-C11 en de
    huidige rules niet onnodig tegelijk hoeven te worden herschreven.
    """

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
        """Geeft de primaire persoon plus eventuele overige personen uniek terug."""

        seen: set[str] = set()
        result: list[Person] = []
        for person in (self.person, *self.persons):
            if person.person_id not in seen:
                seen.add(person.person_id)
                result.append(person)
        return tuple(result)

    @property
    def all_memberships(self) -> tuple[Membership, ...]:
        """Geeft primair lidmaatschap plus overige lidmaatschappen uniek terug."""

        result = [self.membership]
        result.extend(
            membership
            for membership in self.memberships
            if membership is not self.membership
        )
        return tuple(result)

    @property
    def all_duties(self) -> tuple[DutyRegistration, ...]:
        """Compatibele toegang tot enkelvoudige en meervoudige urenregistraties."""

        if self.duty is None:
            return self.duties
        return (self.duty, *self.duties)
