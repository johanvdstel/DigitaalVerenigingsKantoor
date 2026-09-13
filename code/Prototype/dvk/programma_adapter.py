from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from .real_data_import import DataQualitySignal, Provenance
from .workstream_model import Match


PROGRAMMA_ENDPOINT = "https://data.sportlink.com/programma"
PROGRAMMA_FIELDS = (
    "wedstrijddatum,wedstrijdcode,wedstrijdnummer,teamnaam,"
    "thuisteamclubrelatiecode,uitteamclubrelatiecode,thuisteamid,thuisteam,"
    "uitteamid,uitteam,teamvolgorde,competitiesoort,competitie,klasse,poule,"
    "aanvangstijd,status,accommodatie,veld,locatie,plaats"
)


@dataclass(frozen=True)
class ProgramMatchRecord:
    match: Match
    source_status: str | None
    source_accommodation: str | None
    home_team_name: str
    away_team_name: str


@dataclass(frozen=True)
class ProgramImportResult:
    matches: tuple[Match, ...]
    records: tuple[ProgramMatchRecord, ...]
    excluded_records: tuple[ProgramMatchRecord, ...]
    provenance: tuple[Provenance, ...]
    signals: tuple[DataQualitySignal, ...]
    retrieved_at: datetime


class SportlinkProgrammaAdapter:
    """Read-only mapping from Sportlink Programma rows to canonical DVK Match objects."""

    NON_OPERATIONAL_STATUS_MARKERS = (
        "afgelast", "vervallen", "gestaakt", "uitgesteld",
        "niet gespeeld", "geannuleerd", "annul",
    )

    def __init__(self, *, club_relation_code: str, timezone_name: str = "Europe/Amsterdam"):
        self.club_relation_code = club_relation_code.strip()
        self.timezone_name = timezone_name

    def build_url(self, *, client_id: str, days: int = 60, max_rows: int = 500) -> str:
        params = {
            "aantaldagen": int(days),
            "aantalregels": int(max_rows),
            "client_id": client_id,
            "eigenwedstrijden": "JA",
            "thuis": "JA",
            "uit": "JA",
            "gebruiklokaleteamgegevens": "NEE",
            "fields": PROGRAMMA_FIELDS,
        }
        return f"{PROGRAMMA_ENDPOINT}?{urlencode(params)}"

    def import_rows(self, rows: Iterable[dict[str, object]], *,
                    retrieved_at: datetime | None = None) -> ProgramImportResult:
        retrieved_at = retrieved_at or datetime.now(timezone.utc)
        matches: list[Match] = []
        records: list[ProgramMatchRecord] = []
        excluded: list[ProgramMatchRecord] = []
        provenance: list[Provenance] = []
        signals: list[DataQualitySignal] = []

        for index, row in enumerate(rows, 1):
            key = self._record_key(row, index)
            home_is_ckc = self._value(row, "thuisteamclubrelatiecode") == self.club_relation_code
            away_is_ckc = self._value(row, "uitteamclubrelatiecode") == self.club_relation_code
            if home_is_ckc == away_is_ckc:
                signals.append(DataQualitySignal(
                    "PROGRAM_MATCH_CLUB_SIDE_UNRESOLVED", "ERROR", "programma", key,
                    "Wedstrijd heeft niet exact één CKC-zijde op basis van clubrelatiecode",
                ))
                continue

            home_away = "HOME" if home_is_ckc else "AWAY"
            team_id_field = "thuisteamid" if home_is_ckc else "uitteamid"
            team_name_field = "thuisteam" if home_is_ckc else "uitteam"
            team_id = self._value(row, team_id_field)
            team_name = self._value(row, team_name_field)
            if not team_id:
                team_id = self._strip_ckc_prefix(team_name)
                signals.append(DataQualitySignal(
                    "PROGRAM_MATCH_TEAM_ID_FALLBACK", "WARNING", "programma", key,
                    "Sportlink team-id ontbreekt; teamnaam gebruikt als fallback",
                ))
            if not team_id:
                signals.append(DataQualitySignal(
                    "PROGRAM_MATCH_TEAM_UNRESOLVED", "ERROR", "programma", key,
                    "CKC-team kon niet worden bepaald",
                ))
                continue

            raw_datetime = self._value(row, "wedstrijddatum")
            try:
                starts_at = self._parse_sportlink_datetime(raw_datetime)
            except ValueError as exc:
                signals.append(DataQualitySignal(
                    "INVALID_PROGRAM_MATCH_DATETIME", "ERROR", "programma", key, str(exc)
                ))
                continue

            match_id = self._value(row, "wedstrijdcode") or self._value(row, "wedstrijdnummer")
            if not match_id:
                signals.append(DataQualitySignal(
                    "MISSING_PROGRAM_MATCH_ID", "ERROR", "programma", key,
                    "Wedstrijdcode en wedstrijdnummer ontbreken",
                ))
                continue

            status = self._value(row, "status") or None
            if status is None:
                signals.append(DataQualitySignal(
                    "MISSING_PROGRAM_MATCH_STATUS", "WARNING", "programma", match_id,
                    "Sportlink wedstrijdstatus ontbreekt; wedstrijd blijft operationeel tenzij anders bekend",
                ))

            match = Match(match_id, team_id, starts_at, home_away)
            record = ProgramMatchRecord(
                match, status, self._value(row, "accommodatie") or None,
                self._value(row, "thuisteam"), self._value(row, "uitteam"),
            )
            records.append(record)
            operational = self._is_operational(status)
            provenance.append(Provenance(
                "Sportlink", "programma", match_id, retrieved_at,
                kind="SOURCE_FACT", source_field="status", source_value=status,
                normalized_value="OPERATIONAL" if operational else "NON_OPERATIONAL",
            ))
            if operational:
                matches.append(match)
            else:
                excluded.append(record)
                signals.append(DataQualitySignal(
                    "NON_OPERATIONAL_PROGRAM_MATCH", "INFO", "programma", match_id,
                    f"Wedstrijd niet als normale kandidaatscontext gebruikt vanwege status {status!r}",
                ))

        return ProgramImportResult(
            tuple(matches), tuple(records), tuple(excluded), tuple(provenance), tuple(signals), retrieved_at
        )

    def _parse_sportlink_datetime(self, value: str) -> datetime:
        if not value:
            raise ValueError("Sportlink wedstrijddatum ontbreekt")
        normalized = value.strip().replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(f"Ongeldige Sportlink wedstrijddatum: {value!r}") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(ZoneInfo(self.timezone_name))

    @classmethod
    def _is_operational(cls, status: str | None) -> bool:
        if not status:
            return True
        normalized = status.strip().casefold()
        return not any(marker in normalized for marker in cls.NON_OPERATIONAL_STATUS_MARKERS)

    @staticmethod
    def _strip_ckc_prefix(team_name: str) -> str:
        value = team_name.strip()
        if value.casefold().startswith("ckc "):
            return value[4:].strip()
        return value

    @staticmethod
    def _record_key(row: dict[str, object], index: int) -> str:
        for field in ("wedstrijdcode", "wedstrijdnummer"):
            value = str(row.get(field) or "").strip()
            if value:
                return value
        return str(index)

    @staticmethod
    def _value(row: dict[str, object], field: str) -> str:
        return str(row.get(field) or "").strip()
