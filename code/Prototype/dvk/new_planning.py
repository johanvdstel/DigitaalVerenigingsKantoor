"""Initial source cycle for an explicitly started, empty planningssessie."""
from datetime import datetime

from .candidate_context import CandidateContextApplicationService, CandidateSourceError
from .duty_control_presenter import validate_season
from .local_csv_sources import LocalCsvSourceApplicationService
from .planning_session import PlanningCandidateSources, PlanningSessionApplicationService
from .sportlink_exports import ExportFileError
from .vrijwilligers_adapter import SportlinkVrijwilligersAdapter
from .vrijwilligers_client import SportlinkVrijwilligersClient
from .volunteer_planning import VolunteerPlanningApplicationService


class NewPlanningApplicationService:
    def __init__(self, database, identity):
        self.database = database
        self.identity = identity

    def start(self, *, period, catalog, source_period, client_id, progress):
        source_period = validate_season(source_period)
        catalog.bindings(period)
        # The session service rejects an existing planning under the write lock.
        # Source collection starts only after this attempt owns the new session.
        with self.database.unit_of_work() as uow:
            session = PlanningSessionApplicationService(uow, self.identity).start(period, catalog=catalog)

        sources = self._load(session, catalog, source_period, client_id, progress)
        with self.database.unit_of_work() as uow:
            PlanningSessionApplicationService(uow, self.identity).save_candidate_sources(session.session_id, sources)
        return session

    def _load(self, session, catalog, source_period, client_id, progress):
        period = session.period
        progress("Lokale Sportlink-exports lezen en controleren…")
        local = LocalCsvSourceApplicationService()
        try:
            members_text = local.read_members()
        except ExportFileError as exc:
            return PlanningCandidateSources(
                error=str(exc), initial_volunteer_error="Vrijwilligers is niet opgehaald. Controleer eerst Leden.csv.",
            )

        context = candidate_error = volunteer_error = None
        try:
            context = CandidateContextApplicationService(self.identity).load(
                period=period, source_period=source_period, client_id=client_id,
                local_sources=local, members_text=members_text,
                before_programma=lambda: progress("Wedstrijdprogramma ophalen bij Sportlink…"),
            )
        except CandidateSourceError as exc:
            candidate_error = str(exc)

        try:
            persons = local.volunteer_persons(members_text=members_text)
        except ValueError as exc:
            return PlanningCandidateSources(
                context, candidate_error, f"Vrijwilligers is niet opgehaald. Controleer Leden.csv. {exc}",
            )

        progress("Feitelijke vrijwilligersinroosteringen ophalen en controleren…")
        try:
            with self.database.unit_of_work() as uow:
                if PlanningSessionApplicationService(uow, self.identity).current() != session:
                    raise ValueError("De planningssessie is tijdens het laden gewijzigd.")
                volunteer_error = VolunteerPlanningApplicationService(uow, self.identity, catalog).synchronize(
                    period=period, client=SportlinkVrijwilligersClient(SportlinkVrijwilligersAdapter()),
                    client_id=client_id, persons=persons, imported_at=datetime.now().astimezone(),
                )
        except ValueError as exc:
            volunteer_error = str(exc)
        return PlanningCandidateSources(context, candidate_error, volunteer_error)
