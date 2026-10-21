"""One planner, one active period; catalog supply and Sportlink facts stay separate."""
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .application_services import NoShowApplicationService
from .planning import PlanningSourceStatus
from .security import Authorizer, Permission
from .staffing import calculate_staffing_need
from .vrijwilligers_client import VrijwilligersFetchError
from .vrijwilligers_adapter import same_task_group, overlaps_service_date

TZ = ZoneInfo("Europe/Amsterdam")


@dataclass(frozen=True)
class VolunteerWindow:
    days: int
    weekoffset: int


def request_window(period, today: date) -> VolunteerWindow:
    """Keep the accepted -1/60 window unless a wider window is necessary.

    Sportlink documents weekoffset as weeks relative to the current week/day.
    Start at least a full week before the selected date. Count days through the
    end from that Monday, which also covers a day-relative server anchor.
    No form input can narrow this application-owned request.
    """
    monday = today - timedelta(days=today.weekday())
    offset = min(-1, (period.start - monday).days // 7 - 1)
    earliest = monday + timedelta(weeks=offset)
    return VolunteerWindow(max(60, (period.end - earliest).days + 1), offset)


class VolunteerPlanningApplicationService:
    def __init__(self, uow, identity, catalog):
        self.uow, self.identity, self.catalog = uow, identity, catalog

    def source(self, period):
        Authorizer().require(self.identity, Permission.VIEW_PLANNING)
        success = self.uow.sportlink_bookings.refresh_state()
        failure = self.uow.sportlink_bookings.refresh_state("attempt")
        matching = success is not None and (success["start"], success["end"], tuple(success["codes"])) == (
            period.start.isoformat(), period.end.isoformat(), self.catalog.task_codes)
        return success, failure, matching

    def planning_data(self, period):
        success, _, matching = self.source(period)
        bindings = self.catalog.bindings(period)
        bookings = self.uow.sportlink_bookings.all() if matching else ()
        definitions = {d.task_code: d for d in self.catalog.definitions}
        needs = tuple(calculate_staffing_need(
            service=b.service, definition=definitions[b.task_code],
            # Derived view only: one person per slot, even with multiple source
            # bookings/codes. Stored source IDs, task codes and intervals stay intact.
            bookings=tuple(replace(x, service_id=b.service.service_id) for x in
                           {x.person_id: x for x in bookings if x.person_id
                            and same_task_group(x.task_code, b.task_code)
                            and overlaps_service_date(x.starts_at, x.ends_at, b.service)}.values()),
            condition="vrijdag" if b.service.starts_at.weekday() == 4 else None) for b in bindings)
        statuses = (PlanningSourceStatus("Sportlink Vrijwilligers", None if success is None else
                    datetime.fromisoformat(success["fetched_at"]), "Opgehaald" if matching else
                    "Geen gevalideerde bron voor de gekozen periode"),)
        return tuple(b.service for b in bindings), needs, (), statuses

    def synchronize(self, *, period, client, client_id, persons, imported_at):
        Authorizer().require(self.identity, Permission.MANAGE_NO_SHOWS)
        if imported_at.tzinfo is None:
            raise ValueError("Ophaaltijd vereist een tijdzone")
        window = request_window(period, imported_at.astimezone(TZ).date())
        bindings = self.catalog.bindings(period)
        state = dict(start=period.start.isoformat(), end=period.end.isoformat(),
                     fetched_at=imported_at.isoformat(), codes=list(self.catalog.task_codes),
                     days=window.days, weekoffset=window.weekoffset,
                     tasks=[dict(task_code=d.task_code, description=d.service_type,
                                 services=sum(b.task_code == d.task_code for b in bindings),
                                 status="Geslaagd") for d in self.catalog.definitions])
        attempt_tasks = [dict(row, status="Niet uitgevoerd") for row in state["tasks"]]
        class TrackingClient:
            def fetch_rows(self, **kwargs):
                task = next(t for t in attempt_tasks if t["task_code"] == kwargs["task_code"])
                task["status"] = "Mislukt"
                result = client.fetch_rows(**kwargs)
                task["status"] = "Geslaagd"
                return result
        try:
            signals = NoShowApplicationService(self.uow, self.identity).synchronize(
                client=TrackingClient(), client_id=client_id, bindings=bindings, persons=persons,
                imported_at=imported_at, days=window.days, weekoffset=window.weekoffset,
                task_codes=self.catalog.task_codes, period=period, refresh_state=state, catalog_overlap=True)
        except VrijwilligersFetchError as exc:
            # Client messages are fixed categories: never persist exception URLs.
            category = str(exc)
            if "HTTP " in category:
                message = "Sportlink weigert de uitvraag; controleer toegang en lokale instellingen."
            elif "connection failure" in category or "transport failure" in category:
                message = "Sportlink is niet bereikbaar of antwoordt niet op tijd; probeer later opnieuw."
            else:
                message = "Sportlink gaf geen geldige bronrespons; de verversing is niet gepubliceerd."
            self._attempt(state, "Mislukt", message, attempt_tasks)
            return message
        if signals:
            message = "; ".join(sorted({s.message for s in signals}))
            self._attempt(state, "Mislukt", message, attempt_tasks)
            return message
        self._attempt(state, "Geslaagd", "", attempt_tasks)
        return None

    def _attempt(self, state, status, message, tasks):
        self.uow.sportlink_bookings.save_refresh_state(
            dict(start=state["start"], end=state["end"], at=state["fetched_at"],
                 status=status, message=message, codes=state["codes"], tasks=tasks), "attempt")
        self.uow.commit()
