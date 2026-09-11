from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
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

    def load_exports(self, *, members_path, functions_path, committees_path, duty_path, teams_path,
                     imported_at=None, source_period=None, expected_required_hours=None) -> RealDataImportResult:
        imported_at = imported_at or datetime.now()
        expected_required_hours = expected_required_hours or {}
        signals: list[DataQualitySignal] = []
        provenance: list[Provenance] = []

        member_rows = self.read_rows(members_path, "leden")
        function_rows = self.read_rows(functions_path, "functies")
        committee_rows = self.read_rows(committees_path, "commissies")
        duty_rows = self.read_rows(duty_path, "vrijwilligers_periode")
        team_rows = self.read_rows(teams_path, "teams")

        grouped: dict[str, list[dict[str, str]]] = {}
        for row in member_rows:
            pid = self.value(row, "Rel. code")
            if not pid:
                signals.append(DataQualitySignal("MISSING_PERSON_ID", "ERROR", "leden", None, "Ledenregel zonder Rel. code"))
                continue
            grouped.setdefault(pid, []).append(row)

        persons, memberships, football = [], [], []
        for pid, variants in grouped.items():
            if len(variants) > 1:
                signals.append(DataQualitySignal("DUPLICATE_PERSON_SOURCE_RECORD", "WARNING", "leden", pid,
                                                 f"{len(variants)} bronregels met dezelfde Rel. code"))
            identities = {(self.value(r, "Naam"), self.value(r, "Geboortedatum")) for r in variants}
            if len(identities) > 1:
                signals.append(DataQualitySignal("CONFLICTING_DUPLICATE_IDENTITY", "ERROR", "leden", pid,
                                                 "Dubbele Rel. code heeft conflicterende naam/geboortedatum"))
                continue
            row = max(variants, key=self._member_score)
            local_status = self.value(row, "Status lidmaatschap")
            activity = self.value(row, "Spelactiviteiten (bond)")
            plays = bool(activity) or local_status.lower() == "spelend lid"
            persons.append(Person(pid, self.value(row, "Naam"), self.parse_date(self.value(row, "Geboortedatum"))))
            memberships.append(Membership(pid, self.value(row, "Lidstatus"), self.value(row, "Lidsoort"),
                                          plays_football=plays,
                                          recreational=local_status.lower() == "recreatief",
                                          honorary=local_status.lower() in {"erelid", "ere lid"}))
            football.append(FootballParticipation(pid, local_status, activity or None, plays))
            provenance.append(self.prov("leden", pid, imported_at, source_period))

        person_ids = {p.person_id for p in persons}
        roles: list[RoleAssignment] = []
        for i, row in enumerate(function_rows, 1):
            pid = self.value(row, "Rel. code")
            if not self.known_person(pid, person_ids, "functies", str(i), signals):
                continue
            role = self.value(row, "Functie")
            if role:
                roles.append(RoleAssignment(pid, self.normalize_role(role)))
            else:
                signals.append(DataQualitySignal("UNKNOWN_FUNCTION", "WARNING", "functies", pid, "Lege functienaam"))
            provenance.append(self.prov("functies", f"{pid}:{i}", imported_at, source_period))

        committees: list[CommitteeMembership] = []
        for i, row in enumerate(committee_rows, 1):
            pid = self.value(row, "Rel. code")
            if not self.known_person(pid, person_ids, "commissies", str(i), signals):
                continue
            committees.append(CommitteeMembership(pid, self.value(row, "Commissie"), self.value(row, "Functie")))
            provenance.append(self.prov("commissies", f"{pid}:{i}", imported_at, source_period))

        teams: list[RealTeamMembership] = []
        for i, row in enumerate(team_rows, 1):
            pid = self.value(row, "Rel. code")
            if not self.known_person(pid, person_ids, "teams", str(i), signals):
                continue
            team = self.value(row, "Team")
            if not team:
                signals.append(DataQualitySignal("UNMATCHED_TEAM_REFERENCE", "WARNING", "teams", f"{pid}:{i}", "Team ontbreekt"))
                continue
            teams.append(RealTeamMembership(pid, team, self.value(row, "Teamrol") or None,
                                            self.value(row, "Functie") or None,
                                            self.optional_bool(self.value(row, "Spelend lid"))))
            provenance.append(self.prov("teams", f"{pid}:{i}", imported_at, source_period))

        duties: list[DutyImportRecord] = []
        for i, row in enumerate(duty_rows, 1):
            pid = self.value(row, "Relatiecode")
            if not self.known_person(pid, person_ids, "vrijwilligers_periode", str(i), signals):
                continue
            a = self.whole_number(self.value(row, "Verplichte punten"))
            b = self.whole_number(self.value(row, "Gecorrigeerde punten"))
            c = self.whole_number(self.value(row, "Voldaan"))
            d = self.whole_number(self.value(row, "Nog ingedeeld"))
            source_e = self.whole_number(self.value(row, "Niet ingedeeld"))
            registration = SportlinkDutyRegistration(pid, a, b, c, d)
            record = DutyImportRecord(registration, source_e, DutyPosition(a, b, c, d), expected_required_hours.get(pid))
            duties.append(record)
            if not record.source_formula_matches:
                signals.append(DataQualitySignal("DUTY_REMAINING_MISMATCH", "ERROR", "vrijwilligers_periode", pid,
                                                 f"Sportlink E={source_e} maar A-B-C-D={record.position.E}"))
            if record.required_hours_mismatch:
                signals.append(DataQualitySignal("REQUIRED_HOURS_MISMATCH", "WARNING", "vrijwilligers_periode", pid,
                                                 f"Sportlink A={a} maar DVK verwacht A={record.expected_required_hours}"))
            provenance.append(self.prov("vrijwilligers_periode", pid, imported_at, source_period))

        return RealDataImportResult(tuple(persons), tuple(memberships), tuple(football), tuple(roles),
                                    tuple(committees), tuple(teams), tuple(duties), tuple(provenance), tuple(signals))

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
    def _member_score(row):
        return ((row.get("Lidstatus") or "").strip().lower() != "afgemeld",
                (row.get("Status lidmaatschap") or "").strip().lower() != "oud lid")

    @staticmethod
    def normalize_role(role: str) -> str:
        cleaned = " ".join(role.strip().split())
        lower = cleaned.lower().replace("-", " ")
        if lower in {"vice voorzitter", "vicevoorzitter"}:
            return "Vice voorzitter"
        if lower.startswith("trainer ") or lower == "hoofdtrainer":
            return "Trainer"
        return cleaned

    @staticmethod
    def known_person(pid, person_ids, dataset, key, signals) -> bool:
        if not pid or pid not in person_ids:
            signals.append(DataQualitySignal("UNMATCHED_PERSON_REFERENCE", "ERROR", dataset, key,
                                             f"Rel. code {pid or '(leeg)'} niet gevonden in ledenexport"))
            return False
        return True

    @staticmethod
    def value(row: dict[str, str], column: str) -> str:
        return (row.get(column) or "").strip()

    @staticmethod
    def parse_date(value: str) -> date | None:
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                pass
        raise ValueError(f"Invalid date source value: {value!r}")

    @staticmethod
    def optional_bool(value: str) -> bool | None:
        normalized = value.strip().lower()
        if not normalized:
            return None
        if normalized in {"ja", "yes", "true", "1", "y"}:
            return True
        if normalized in {"nee", "no", "false", "0", "n"}:
            return False
        return None

    @staticmethod
    def whole_number(value: str) -> int:
        normalized = value.strip().replace(",", ".")
        if not normalized:
            return 0
        number = float(normalized)
        if not number.is_integer():
            raise ValueError(f"Expected whole duty points/hours, got {value!r}")
        return int(number)

    @staticmethod
    def prov(dataset, key, imported_at, source_period):
        return Provenance("Sportlink", dataset, key, imported_at, source_period)
