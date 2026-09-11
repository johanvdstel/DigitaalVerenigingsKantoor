from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .model import DutyPosition, Membership, Person, RoleAssignment, SportlinkDutyRegistration


@dataclass(frozen=True)
class Provenance:
    source_system: str
    source_dataset: str
    source_record_key: str
    imported_at: datetime
    source_period: str | None = None
    kind: str = "SOURCE_FACT"


@dataclass(frozen=True)
class DataQualitySignal:
    code: str
    severity: str
    dataset: str
    record_key: str | None
    message: str


@dataclass(frozen=True)
class FootballParticipation:
    person_id: str
    source_status: str
    bond_activity: str | None
    plays_football: bool


@dataclass(frozen=True)
class CommitteeMembership:
    person_id: str
    committee: str
    committee_role: str


@dataclass(frozen=True)
class RealTeamMembership:
    person_id: str
    team_id: str
    team_role: str | None
    team_function: str | None
    playing_member: bool | None


@dataclass(frozen=True)
class DutyImportRecord:
    registration: SportlinkDutyRegistration
    source_remaining_hours: int
    position: DutyPosition
    expected_required_hours: int | None = None

    @property
    def source_formula_matches(self) -> bool:
        return self.source_remaining_hours == self.position.E

    @property
    def required_hours_mismatch(self) -> bool:
        return self.expected_required_hours is not None and self.registration.required_hours != self.expected_required_hours


@dataclass(frozen=True)
class RealDataImportResult:
    persons: tuple[Person, ...]
    memberships: tuple[Membership, ...]
    football_participations: tuple[FootballParticipation, ...]
    roles: tuple[RoleAssignment, ...]
    committees: tuple[CommitteeMembership, ...]
    team_memberships: tuple[RealTeamMembership, ...]
    duty_records: tuple[DutyImportRecord, ...]
    provenance: tuple[Provenance, ...]
    signals: tuple[DataQualitySignal, ...]


class SportlinkRealDataAdapter:
    """Read-only v0.4 adapter. Sportlink field names live only in this layer."""

    REQUIRED_COLUMNS = {
        "leden": {"Rel. code", "Naam", "Geboortedatum", "Lidstatus", "Lidsoort", "Status lidmaatschap"},
        "functies": {"Rel. code", "Functie"},
        "commissies": {"Rel. code", "Commissie", "Functie"},
        "vrijwilligers_periode": {"Relatiecode", "Verplichte punten", "Gecorrigeerde punten", "Voldaan", "Nog ingedeeld", "Niet ingedeeld"},
        "teams": {"Rel. code", "Team", "Teamrol", "Functie", "Spelend lid"},
    }

    @classmethod
    def read_rows(cls, path: str | Path, dataset: str) -> list[dict[str, str]]:
        path = Path(path)
        text = path.read_text(encoding="utf-8-sig")
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=";,\t").delimiter
        except csv.Error:
            delimiter = ";"
        reader = csv.DictReader(text.splitlines(), delimiter=delimiter)
        missing = cls.REQUIRED_COLUMNS[dataset] - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path.name}: missing columns: {', '.join(sorted(missing))}")
        return list(reader)

    @staticmethod
    def value(row: dict[str, str], column: str) -> str:
        return (row.get(column) or "").strip()

    @staticmethod
    def whole_number(value: str) -> int:
        normalized = value.strip().replace(",", ".")
        if not normalized:
            return 0
        number = float(normalized)
        if not number.is_integer():
            raise ValueError(f"Expected whole duty points/hours, got {value!r}")
        return int(number)
