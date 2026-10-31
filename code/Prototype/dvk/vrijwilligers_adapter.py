from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
from typing import Iterable
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo

from .real_data_import import DataQualitySignal, Provenance
from .workstream_model import DutyService
from .model import Person


VRIJWILLIGERS_ENDPOINT = "https://data.sportlink.com/vrijwilligers"
VRIJWILLIGERS_FIELDS = "naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag"
TZ = ZoneInfo("Europe/Amsterdam")
BAR_TASK_CODES = frozenset({"701", "741", "761"})
IDENTITY_MESSAGES = {
    "VOLUNTEER_PERSON_NOT_FOUND": "Geen overeenkomstig lid gevonden",
    "VOLUNTEER_PERSON_AMBIGUOUS": "Meerdere Rel. codes mogelijk",
    "VOLUNTEER_PERSON_DUPLICATE": "Dubbele ledenregels met dezelfde Rel. code",
    "VOLUNTEER_PERSON_CONFLICT": "Tegenstrijdige ledengegevens bij dezelfde Rel. code",
}


def booking_identity_report(bookings):
    """Local-only planner report; names never enter transport errors or logs."""
    bookings = tuple(bookings)
    details = []
    for code, message in IDENTITY_MESSAGES.items():
        affected = tuple(b for b in bookings if code in b.identity_issues)
        for name in sorted({b.volunteer_name for b in affected}):
            details.append(dict(category=code, name=name, problem=message,
                                bookings=sum(b.volunteer_name == name for b in affected)))
    return dict(total=len(bookings), shielded=sum(b.volunteer_name.strip() == "Afgeschermd" for b in bookings),
                unlinked=sum(not b.can_register_no_show for b in bookings),
                problem_names=len({d["name"] for d in details}), details=details,
                categories=[dict(category=code, problem=message,
                                 bookings=sum(code in b.identity_issues for b in bookings),
                                 names=len({b.volunteer_name for b in bookings if code in b.identity_issues}))
                            for code, message in IDENTITY_MESSAGES.items()
                            if any(code in b.identity_issues for b in bookings)])


def same_task_group(source_code: str, catalog_code: str) -> bool:
    """Confirmed CKC grouping; unknown codes retain exact comparison."""
    return source_code == catalog_code or source_code in BAR_TASK_CODES and catalog_code in BAR_TASK_CODES


def overlaps_service_date(starts_at: datetime, ends_at: datetime, service: DutyService) -> bool:
    """Rooster2 fill_names: any positive overlap counts, only on the source date.

    Partial overlap counts as occupancy, not as proof of full-slot attendance.
    Merely touching endpoints does not count. Compare absolute UTC instants.
    """
    if starts_at.astimezone(TZ).date() != service.starts_at.astimezone(TZ).date():
        return False
    start, end = starts_at.astimezone(timezone.utc), ends_at.astimezone(timezone.utc)
    slot_start = service.starts_at.astimezone(timezone.utc)
    slot_end = service.ends_at.astimezone(timezone.utc)
    return max(start, slot_start) < min(end, slot_end)


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
    person_id: str | None = None
    person_name: str | None = None
    provenance: Provenance | None = None
    service: DutyService | None = None
    identity_issues: tuple[str, ...] = ()

    @property
    def can_register_no_show(self) -> bool:
        return bool(self.person_id) and self.volunteer_name.strip() != "Afgeschermd" and not any(
            issue in {"VOLUNTEER_PERSON_NOT_FOUND", "VOLUNTEER_PERSON_AMBIGUOUS", "VOLUNTEER_PERSON_CONFLICT"}
            for issue in self.identity_issues)

    @property
    def assignment_id(self) -> str:
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Sportlink booking key requires explicit timezones")
        interval = (self.task_code, self.starts_at.astimezone(timezone.utc).isoformat(),
                    self.ends_at.astimezone(timezone.utc).isoformat())
        # Keep all existing linked booking keys, including durable no-show references.
        key = (self.person_id, *interval) if self.person_id else (self.volunteer_name, *interval, self.location)
        prefix = "SL-" if self.person_id else "SLU-"
        return prefix + hashlib.sha256(json.dumps(key, ensure_ascii=False).encode()).hexdigest()


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
        persons: Iterable[Person] | None = None,
        period=None,
        catalog_overlap: bool = False,
        planning_definitions=(),
    ) -> VolunteerImportResult:
        bindings = tuple(binding for binding in services if
                         (same_task_group(task_code, binding.task_code) if catalog_overlap else binding.task_code == task_code))
        bookings: list[VolunteerBooking] = []
        provenance: list[Provenance] = []
        signals: list[DataQualitySignal] = []
        persons = None if persons is None else tuple(persons)

        for index, row in enumerate(rows, 1):
            key = f"{task_code}:{index}"
            name = self._pick(row, "naam", "Naam", "Vrijwilliger", "vrijwilliger", "vrijwilligerNaam", "displayName", strip=False)
            match_name = name.strip()
            raw_date_from = self._pick(row, "datumvanaf", "Datum vanaf", "DatumVanaf", "start", "Start", "startDatumTijd", "startDateTime")
            raw_date_to = self._pick(row, "datumtot", "Datum tot", "DatumTot", "eind", "Eind", "eindDatumTijd", "endDateTime")
            raw_time_from = self._pick(row, "tijdvanaf", "Tijd vanaf", "startTijd", "starttijd", "StartTijd")
            raw_time_to = self._pick(row, "tijdtot", "Tijd tot", "eindtijd", "EindTijd", "endTijd", "TijdTot")
            location = self._pick(row, "lokatie", "Lokatie", "locatie", "Locatie")

            if not match_name or not raw_date_from:
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

            if period is not None and not period.contains(starts_at.astimezone(TZ)):
                continue

            if planning_definitions:
                from .shift_catalog import concrete_service
                definition = next((d for d in planning_definitions if d.task_code == task_code), None)
                if definition is None:
                    signals.append(DataQualitySignal("UNKNOWN_VOLUNTEER_TASK_CODE", "ERROR", "sportlink_vrijwilligers", key, "Onbekende Sportlink-taakcode"))
                    continue
                if ends_at.astimezone(timezone.utc) <= starts_at.astimezone(timezone.utc):
                    signals.append(DataQualitySignal("INVALID_VOLUNTEER_INTERVAL", "ERROR", "sportlink_vrijwilligers", key, "Feitelijke inroostering vereist einde na begin"))
                    continue
                # Planning accepts every actual interval; legacy exact/overlap paths stay intact.
                actual_service = concrete_service(definition, starts_at, ends_at, location)
                matches = [actual_service]
            else:
                matches = [binding.service for binding in bindings if
                       (overlaps_service_date(starts_at, ends_at, binding.service) if catalog_overlap
                        else self._same_service_time(binding.service, starts_at, ends_at))]
            if len(matches) == 0:
                signals.append(DataQualitySignal(
                    "VOLUNTEER_SERVICE_NOT_FOUND", "ERROR", "sportlink_vrijwilligers", key,
                    f"Geen DutyService gevonden voor taakcode {task_code} op {starts_at.isoformat()}",
                ))
                continue
            if (len(matches) > 1 and not catalog_overlap) or len({s.service_id for s in matches}) != len(matches):
                signals.append(DataQualitySignal(
                    "VOLUNTEER_SERVICE_AMBIGUOUS", "ERROR", "sportlink_vrijwilligers", key,
                    f"Meer dan één DutyService past bij taakcode {task_code} op {starts_at.isoformat()}",
                ))
                continue

            # Only an anchor for the existing source context, never a split source
            # booking. Occupancy is projected independently onto every matching slot.
            service = min(matches, key=lambda s: (s.starts_at, s.service_id))
            person = None
            issues = []
            if persons is not None:
                # Never attempt to reconstruct an identity behind the privacy marker.
                candidates = () if match_name == "Afgeschermd" else tuple(p for p in persons if p.sportlink_name == match_name and p.person_id)
                ids = {p.person_id for p in candidates}
                if match_name != "Afgeschermd":
                    if not ids:
                        issues.append("VOLUNTEER_PERSON_NOT_FOUND")
                    elif len(ids) > 1:
                        issues.append("VOLUNTEER_PERSON_AMBIGUOUS")
                    else:
                        related = tuple(p for p in persons if p.person_id in ids)
                        if len(related) > 1:
                            issues.append("VOLUNTEER_PERSON_DUPLICATE")
                        if any(p.volunteer_identity_conflicting for p in related) or any(p != related[0] for p in related):
                            issues.append("VOLUNTEER_PERSON_CONFLICT")
                        else:
                            person = candidates[0]
                for issue in issues:
                    signals.append(DataQualitySignal(issue, "WARNING", "sportlink_vrijwilligers", key,
                                                     IDENTITY_MESSAGES[issue]))
                if not planning_definitions and ends_at <= starts_at:
                    signals.append(DataQualitySignal("INVALID_VOLUNTEER_INTERVAL", "ERROR", "sportlink_vrijwilligers", key,
                                                     "Feitelijke inroostering vereist volledige begin- en eindtijd"))
                    continue
            booking = VolunteerBooking(task_code, service.service_id, name, starts_at, ends_at, location,
                                       None if person is None else person.person_id,
                                       None if person is None else person.name, service=service,
                                       identity_issues=tuple(issues))
            if persons is not None:
                booking = replace(booking, service=replace(service, starts_at=starts_at, ends_at=ends_at, location=location))
                key = booking.assignment_id
                if any(b.assignment_id == key for b in bookings):
                    signals.append(DataQualitySignal("DUPLICATE_VOLUNTEER_BOOKING", "ERROR", "sportlink_vrijwilligers", key,
                                                     "Dezelfde feitelijke inroostering komt meermaals voor"))
                    continue
            source_provenance = Provenance(
                "Sportlink", "Vrijwilligers", key, imported_at,
                kind="SOURCE_FACT", source_value=str(dict(row)),
                normalized_value=str(booking))
            booking = replace(booking, provenance=source_provenance)
            bookings.append(booking)
            provenance.append(source_provenance)

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
        date_tz = TZ
        if "T" in value:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if not time_value:
                return parsed.astimezone(TZ) if parsed.tzinfo else parsed.replace(tzinfo=TZ)
            # Sportlink supplies the calendar date and duty time separately.
            parsed_date = parsed.date()
            date_tz = parsed.tzinfo or TZ
        else:
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
        return datetime.combine(parsed_date, parsed_time, tzinfo=date_tz)

    @staticmethod
    def _pick(row: dict[str, object], *names: str, strip: bool = True) -> str:
        lower = {str(key).lower(): key for key in row}
        for name in names:
            key = name if name in row else lower.get(name.lower())
            if key is not None:
                value = row.get(key)
                if value is not None:
                    return str(value).strip() if strip else str(value)
        return ""
