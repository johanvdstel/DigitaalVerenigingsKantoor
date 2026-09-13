from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

from .real_data_import import DataQualitySignal, Provenance
from .workstream_model import DutyService


VRIJWILLIGERS_ENDPOINT = "https://data.sportlink.com/vrijwilligers"
VRIJWILLIGERS_FIELDS = "naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag"
TZ = ZoneInfo("Europe/Amsterdam")


@dataclass(frozen=True)
class ServiceBinding:
    task_code: str
    service: DutyService


@dataclass(frozen=True)
class VolunteerBooking:
    task_code: str
    service_id: str
    volunteer_name: str
    starts_at: datetime
    ends_at: datetime
    location: str


@dataclass(frozen=True)
class OperationalService:
    """Concrete Sportlink service period plus DVK planning segments.

    The full Sportlink interval remains the source fact. Segments are derived
    planning boundaries only; they never replace or shorten that interval.
    """

    task_code: str
    starts_at: datetime
    ends_at: datetime
    location: str
    segments: tuple[tuple[datetime, datetime], ...]
    deviates_from_catalog: bool


@dataclass(frozen=True)
class VolunteerImportResult:
    bookings: tuple[VolunteerBooking, ...]
    provenance: tuple[Provenance, ...]
    signals: tuple[DataQualitySignal, ...]


class SportlinkVrijwilligersAdapter:
    """Normalize Sportlink volunteer registrations and link them to a known DutyService."""

    @staticmethod
    def build_url(*, client_id: str, task_code: str, days: int = 60, weekoffset: int = -1) -> str:
        params = {
            "vrijwilligerstaakcode": task_code,
            "aantaldagen": str(days),
            "client_id": client_id,
            "weekoffset": str(weekoffset),
            "fields": VRIJWILLIGERS_FIELDS,
        }
        return f"{VRIJWILLIGERS_ENDPOINT}?{urlencode(params, quote_via=quote)}"

    @staticmethod
    def derive_operational_service(
        *,
        task_code: str,
        starts_at: datetime,
        ends_at: datetime,
        location: str,
        catalog_boundaries: Iterable[datetime] = (),
    ) -> OperationalService:
        """Keep a concrete Sportlink interval intact and derive planning segments.

        Known catalog boundaries strictly inside the actual interval are reused.
        The actual start/end are always boundaries themselves, so a previously
        unknown edge such as Tuesday 17:00 is represented instead of discarded.
        """
        if ends_at <= starts_at:
            raise ValueError("Operational service requires ends_at > starts_at")

        start = starts_at.astimezone(TZ)
        end = ends_at.astimezone(TZ)
        internal = sorted({
            boundary.astimezone(TZ)
            for boundary in catalog_boundaries
            if start < boundary.astimezone(TZ) < end
        })
        points = (start, *internal, end)
        segments = tuple((left, right) for left, right in zip(points, points[1:]))
        deviates = start not in {b.astimezone(TZ) for b in catalog_boundaries} or end not in {
            b.astimezone(TZ) for b in catalog_boundaries
        }
        return OperationalService(task_code, start, end, location, segments, deviates)

    def import_rows(
        self,
        *,
        task_code: str,
        rows: Iterable[dict[str, object]],
        services: Iterable[ServiceBinding],
        imported_at: datetime,
    ) -> VolunteerImportResult:
        bindings = tuple(binding for binding in services if binding.task_code == task_code)
        bookings: list[VolunteerBooking] = []
        provenance: list[Provenance] = []
        signals: list[DataQualitySignal] = []

        for index, row in enumerate(rows, 1):
            key = f"{task_code}:{index}"
            name = self._pick(row, "naam", "Naam", "Vrijwilliger", "vrijwilliger", "vrijwilligerNaam", "displayName")
            raw_date_from = self._pick(row, "datumvanaf", "Datum vanaf", "DatumVanaf", "start", "Start", "startDatumTijd", "startDateTime")
            raw_date_to = self._pick(row, "datumtot", "Datum tot", "DatumTot", "eind", "Eind", "eindDatumTijd", "endDateTime")
            raw_time_from = self._pick(row, "tijdvanaf", "Tijd vanaf", "startTijd", "starttijd", "StartTijd")
            raw_time_to = self._pick(row, "tijdtot", "Tijd tot", "eindtijd", "EindTijd", "endTijd", "TijdTot")
            location = self._pick(row, "lokatie", "Lokatie", "locatie", "Locatie")

            if not name or not raw_date_from:
                signals.append(DataQualitySignal(
                    "INVALID_VOLUNTEER_RECORD", "ERROR", "sportlink_vrijwilligers", key,
                    "Vrijwilligersrecord mist naam of begindatum",
                ))
                continue

            try:
                starts_at = self._parse_datetime(raw_date_from, raw_time_from)
                ends_at = self._parse_datetime(raw_date_to or raw_date_from, raw_time_to) if raw_time_to or raw_date_to else starts_at
            except ValueError:
                signals.append(DataQualitySignal(
                    "INVALID_VOLUNTEER_DATETIME", "ERROR", "sportlink_vrijwilligers", key,
                    "Begindatum/-tijd of einddatum/-tijd is niet herkenbaar",
                ))
                continue

            matches = [binding.service for binding in bindings if self._same_service_time(binding.service, starts_at, ends_at)]
            if len(matches) == 0:
                signals.append(DataQualitySignal(
                    "VOLUNTEER_SERVICE_NOT_FOUND", "ERROR", "sportlink_vrijwilligers", key,
                    f"Geen DutyService gevonden voor taakcode {task_code} op {starts_at.isoformat()}",
                ))
                continue
            if len(matches) > 1:
                signals.append(DataQualitySignal(
                    "VOLUNTEER_SERVICE_AMBIGUOUS", "ERROR", "sportlink_vrijwilligers", key,
                    f"Meer dan één DutyService past bij taakcode {task_code} op {starts_at.isoformat()}",
                ))
                continue

            service = matches[0]
            booking = VolunteerBooking(task_code, service.service_id, name, starts_at, ends_at, location)
            bookings.append(booking)
            provenance.append(Provenance(
                "Sportlink", "Vrijwilligers", key, imported_at,
                kind="SOURCE_FACT",
                source_value=str(dict(row)),
                normalized_value=str(booking),
            ))

        return VolunteerImportResult(tuple(bookings), tuple(provenance), tuple(signals))

    @staticmethod
    def _same_service_time(service: DutyService, starts_at: datetime, ends_at: datetime) -> bool:
        if service.starts_at.astimezone(TZ) != starts_at:
            return False
        if ends_at > starts_at and service.ends_at.astimezone(TZ) != ends_at:
            return False
        return True

    @staticmethod
    def _parse_datetime(date_value: str, time_value: str) -> datetime:
        value = date_value.strip()
        if "T" in value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(TZ) if parsed.tzinfo else parsed.replace(tzinfo=TZ)
        date_formats = ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y")
        parsed_date = None
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(value, fmt).date()
                break
            except ValueError:
                pass
        if parsed_date is None:
            raise ValueError(value)
        time_text = (time_value or "00:00").strip()
        parsed_time = None
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                parsed_time = datetime.strptime(time_text, fmt).time()
                break
            except ValueError:
                pass
        if parsed_time is None:
            raise ValueError(time_text)
        return datetime.combine(parsed_date, parsed_time, tzinfo=TZ)

    @staticmethod
    def _pick(row: dict[str, object], *names: str) -> str:
        lower = {str(key).lower(): key for key in row}
        for name in names:
            key = name if name in row else lower.get(name.lower())
            if key is not None:
                value = row.get(key)
                if value is not None:
                    return str(value).strip()
        return ""
