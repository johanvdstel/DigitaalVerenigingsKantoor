from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path

from .model import Membership, Person, PrototypeCase, RoleAssignment, SportlinkDutyRegistration
from .workstream_model import DutyService, Match, TeamMembership


@dataclass(frozen=True)
class ImportedWorkstreamData:
    persons: tuple[Person, ...]
    memberships: tuple[Membership, ...]
    roles: tuple[RoleAssignment, ...]
    duty_registrations: tuple[SportlinkDutyRegistration, ...]
    team_memberships: tuple[TeamMembership, ...]
    matches: tuple[Match, ...]
    services: tuple[DutyService, ...]

    def case_for_person(self, person_id: str, case_id: str = "IMPORT") -> PrototypeCase:
        person = next(p for p in self.persons if p.person_id == person_id)
        membership = next(m for m in self.memberships if m.person_id == person_id)
        duty = next((d for d in self.duty_registrations if d.person_id == person_id), None)
        roles = tuple(r for r in self.roles if r.person_id == person_id)
        return PrototypeCase(
            case_id,
            f"Imported source data for {person_id}",
            person,
            membership,
            roles=roles,
            sportlink_duty=duty,
        )


class SportlinkCsvImportAdapter:
    """Map Sportlink-like CSV source representations to canonical DVK objects.

    This layer knows CSV column names. It deliberately contains no CKC duty,
    selection or prioritisation policy.
    """

    MEMBER_COLUMNS = {
        "person_id", "name", "birth_date", "membership_status", "membership_kind",
        "plays_football", "recreational", "honorary", "roles",
    }
    DUTY_COLUMNS = {"person_id", "required_hours", "correction_hours", "completed_hours", "scheduled_hours"}
    TEAM_COLUMNS = {"person_id", "team_id", "start_date", "end_date"}
    MATCH_COLUMNS = {"match_id", "team_id", "date", "start_time", "home_away"}
    SERVICE_COLUMNS = {
        "service_id", "service_type", "date", "start_time", "end_time", "location", "required_staff",
    }

    def load_directory(self, directory: str | Path) -> ImportedWorkstreamData:
        root = Path(directory)
        member_rows = self._read(root / "members.csv", self.MEMBER_COLUMNS)
        duty_rows = self._read(root / "duty_hours.csv", self.DUTY_COLUMNS)
        team_rows = self._read(root / "teams.csv", self.TEAM_COLUMNS)
        match_rows = self._read(root / "matches.csv", self.MATCH_COLUMNS)
        service_rows = self._read(root / "services.csv", self.SERVICE_COLUMNS)

        persons: list[Person] = []
        memberships: list[Membership] = []
        roles: list[RoleAssignment] = []
        for row in member_rows:
            person_id = row["person_id"].strip()
            persons.append(Person(person_id, row["name"].strip(), self._date(row["birth_date"])))
            memberships.append(
                Membership(
                    person_id,
                    row["membership_status"].strip(),
                    row["membership_kind"].strip(),
                    plays_football=self._bool(row["plays_football"]),
                    recreational=self._bool(row["recreational"]),
                    honorary=self._bool(row["honorary"]),
                )
            )
            for role in (part.strip() for part in row["roles"].split(";") if part.strip()):
                roles.append(RoleAssignment(person_id, role))

        duties = tuple(
            SportlinkDutyRegistration(
                row["person_id"].strip(),
                required_hours=self._int_or_none(row["required_hours"]),
                correction_hours=self._int(row["correction_hours"]),
                completed_hours=self._int(row["completed_hours"]),
                scheduled_hours=self._int(row["scheduled_hours"]),
            )
            for row in duty_rows
        )
        teams = tuple(
            TeamMembership(
                row["person_id"].strip(),
                row["team_id"].strip(),
                self._date(row["start_date"]),
                self._date(row["end_date"]),
            )
            for row in team_rows
        )
        matches = tuple(
            Match(
                row["match_id"].strip(),
                row["team_id"].strip(),
                self._datetime(row["date"], row["start_time"]),
                row["home_away"].strip(),
            )
            for row in match_rows
        )
        services = tuple(
            DutyService(
                row["service_id"].strip(),
                row["service_type"].strip(),
                self._datetime(row["date"], row["start_time"]),
                self._datetime(row["date"], row["end_time"]),
                row["location"].strip(),
                self._int(row["required_staff"]),
            )
            for row in service_rows
        )
        return ImportedWorkstreamData(
            tuple(persons), tuple(memberships), tuple(roles), duties, teams, matches, services
        )

    @staticmethod
    def _read(path: Path, required_columns: set[str]) -> list[dict[str, str]]:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = set(reader.fieldnames or ())
            missing = required_columns - columns
            if missing:
                raise ValueError(f"{path.name}: missing columns: {', '.join(sorted(missing))}")
            return list(reader)

    @staticmethod
    def _date(value: str) -> date | None:
        value = value.strip()
        return date.fromisoformat(value) if value else None

    @staticmethod
    def _datetime(date_value: str, time_value: str) -> datetime:
        return datetime.combine(date.fromisoformat(date_value.strip()), time.fromisoformat(time_value.strip()))

    @staticmethod
    def _bool(value: str) -> bool:
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "ja", "y"}:
            return True
        if normalized in {"0", "false", "no", "nee", "n", ""}:
            return False
        raise ValueError(f"Invalid boolean source value: {value!r}")

    @staticmethod
    def _int(value: str) -> int:
        return int(value.strip() or "0")

    @staticmethod
    def _int_or_none(value: str) -> int | None:
        value = value.strip()
        return int(value) if value else None
