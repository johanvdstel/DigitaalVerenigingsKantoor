from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from .vrijwilligers_adapter import VolunteerBooking


def season_id(day: date) -> str:
    """CKC/KNVB/Sportlink season: 1 July through 30 June."""
    start_year = day.year if day.month >= 7 else day.year - 1
    return f"{start_year}/{start_year + 1}"


TZ = ZoneInfo("Europe/Amsterdam")
MANUAL_DECLARATION = "Ik bevestig dat dit lid oorspronkelijk voor deze dienst was ingeroosterd en niet is verschenen."


def registration_period(now):
    from .planning import PlanningPeriod
    today = now.astimezone(TZ).date()
    return PlanningPeriod(today - timedelta(days=14), today)


def validate_registration_time(start, end, now):
    for moment in (start, end, now):
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("Tijdstippen vereisen een expliciete tijdzone")
        # An aware datetime can still represent an imaginary wall time.
        if moment.astimezone(timezone.utc).astimezone(moment.tzinfo).replace(tzinfo=None) != moment.replace(tzinfo=None):
            raise ValueError("Niet-bestaande lokale tijd")
    if end.astimezone(timezone.utc) <= start.astimezone(timezone.utc):
        raise ValueError("Eindtijd moet strikt na begintijd liggen")
    if not registration_period(now).contains(start.astimezone(TZ)):
        raise ValueError("Dienst valt buiten vandaag min 14 kalenderdagen tot en met vandaag")
    if start.astimezone(timezone.utc) > now.astimezone(timezone.utc):
        raise ValueError("Registratie kan pas vanaf dienstaanvang")


@dataclass(frozen=True)
class ManualServiceContext:
    person_id: str
    person_name: str
    task_code: str | None
    task_identity_verified: bool
    description: str
    starts_at: datetime
    ends_at: datetime
    location: str = ""
    explanation: str = ""
    declaration: str = MANUAL_DECLARATION
    declaration_confirmed: bool = False

    @property
    def service(self):
        from .workstream_model import DutyService
        return DutyService("manual", self.description, self.starts_at, self.ends_at, self.location, 0)


@dataclass(frozen=True)
class NoShowEvent:
    no_show_id: str
    assignment_id: str
    person_id: str
    occurred_at: datetime
    recorded_at: datetime
    recorded_by: str
    season: str
    booking: VolunteerBooking | None = None
    manual: ManualServiceContext | None = None

    @property
    def registration_mode(self):
        return "Handmatig" if self.manual is not None else "Sportlink"

    @property
    def context(self):
        return self.manual if self.manual is not None else self.booking

    def __post_init__(self) -> None:
        if self.booking is not None and self.manual is not None:
            raise ValueError("Een registratie heeft één herkomst")
        if self.manual is not None and (not self.manual.declaration_confirmed or
                self.manual.declaration != MANUAL_DECLARATION or self.manual.person_id != self.person_id or
                self.manual.starts_at != self.occurred_at):
            raise ValueError("Handmatige registratie vereist consistente identiteit en bevestigde verklaring")
        if self.season != season_id(self.occurred_at.date()):
            raise ValueError("no-show season must match occurrence date")


@dataclass(frozen=True)
class NoShowRevocation:
    revocation_id: str
    no_show_id: str
    reason: str
    revoked_at: datetime
    revoked_by: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("revocation reason is required")


@dataclass(frozen=True)
class SanctionAssessment:
    no_show_id: str
    person_id: str
    season: str
    counter: int
    card: str | None
    fine_eur: int
    suspension_matches: int
    replacement_service_required: bool
    board_follow_up: bool
    communication_required: bool = True


def assess_sanction(
    event: NoShowEvent, prior_events: tuple[NoShowEvent, ...],
    revocations: tuple[NoShowRevocation, ...] = (),
) -> SanctionAssessment:
    revoked_ids = {revocation.no_show_id for revocation in revocations}
    if event.no_show_id in revoked_ids:
        raise ValueError("a revoked no-show cannot produce a sanction")
    prior_count = sum(
        1 for prior in prior_events
        if prior.person_id == event.person_id and prior.season == event.season
        and prior.no_show_id not in revoked_ids and prior.occurred_at < event.occurred_at
    )
    return _sanction_at_counter(event, prior_count + 1)


def _sanction_at_counter(event: NoShowEvent, counter: int) -> SanctionAssessment:
    if counter == 1:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, None, 0, 0, True, False)
    if counter == 2:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 1, False, False)
    if counter == 3:
        return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "yellow", 75, 2, False, False)
    return SanctionAssessment(event.no_show_id, event.person_id, event.season, counter, "red", 100, 3, False, True)


@dataclass(frozen=True)
class CurrentSanctionState:
    person_id: str
    season: str
    counter: int
    assessment: SanctionAssessment | None


def current_sanction_state(
    person_id: str, season: str, no_shows: tuple[NoShowEvent, ...],
    revocations: tuple[NoShowRevocation, ...] = (),
) -> CurrentSanctionState:
    """Current season state, independent of historical registration assessments."""
    revoked_ids = {revocation.no_show_id for revocation in revocations}
    valid = tuple(event for event in no_shows
                  if event.person_id == person_id and event.season == season
                  and event.no_show_id not in revoked_ids)
    latest = max(valid, key=lambda event: (event.occurred_at, event.no_show_id)) if valid else None
    assessment = _sanction_at_counter(latest, len(valid)) if latest else None
    return CurrentSanctionState(person_id, season, len(valid), assessment)


def exact_service_identity(context):
    if context is None or not context.task_code:
        return None
    if isinstance(context, ManualServiceContext) and not context.task_identity_verified:
        return None
    return (context.person_id, context.task_code,
            context.starts_at.astimezone(timezone.utc), context.ends_at.astimezone(timezone.utc))


def duplicate_events(context, events, revocations):
    revoked = {r.no_show_id for r in revocations}
    exact, possible = [], []
    key = exact_service_identity(context)
    for event in events:
        if event.no_show_id in revoked or event.person_id != context.person_id:
            continue
        if key is not None and key == exact_service_identity(event.context):
            exact.append(event)
        elif event.occurred_at.astimezone(TZ).date() == context.starts_at.astimezone(TZ).date():
            possible.append(event)
    return tuple(exact), tuple(possible)
