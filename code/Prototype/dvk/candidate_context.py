"""Operational Sportlink candidate basis and confirmed Iteration 1 filters."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime

from .duty_control_presenter import EXPORTS, load_duty_dashboard, present_controls, validate_season
from .model import DutyQualification, PrototypeCase
from .no_show import season_id
from .planning import PlanningPeriod
from .prioritization import prioritize_candidates
from .programma_client import ProgrammaFetchError, ProgrammaFetchStats, SportlinkProgrammaClient
from .programma_team_adapter import CkcProgrammaAdapter, LinkedProgramImportResult
from .team_matchday import (TeamMatchdayError, validate_source_team_matchdays,
                            other_weekend_persons, plan_matchday_proposals)
from .proposals import create_assignment_proposal
from .real_data_import import RealDataImportResult
from .security import Authorizer, Permission
from .local_csv_sources import LocalCsvSourceApplicationService
from .sportlink_exports import EXPORT_FILENAMES
from .source_diagnostics import source_diagnostics
from .historical_backlog import HistoricalBacklogSource


class CandidateSourceError(ValueError):
    """An explicit source problem, never an apparently empty candidate list."""


@dataclass(frozen=True)
class CandidateContext:
    period: PlanningPeriod
    source_period: str
    source: RealDataImportResult
    program: LinkedProgramImportResult | None
    fetched_at: datetime
    stats: ProgrammaFetchStats
    error: str | None = None
    source_files: tuple[str, ...] = ()
    historical_backlog: HistoricalBacklogSource | None = None

    @property
    def diagnostic_details(self):
        return source_diagnostics(self.source, self.program)

    @property
    def signal_counts(self):
        signals = self.source.signals + (self.program.signals if self.program else ())
        return dict(Counter(signal.code for signal in signals))


@dataclass(frozen=True)
class CandidateProposals:
    cases: tuple
    planned: tuple
    controls: tuple
    assessments: tuple
    priorities: tuple
    explanations: tuple


class CandidateContextApplicationService:
    """Read-only source boundary; approval stays in ProposalDecisionApplicationService."""

    def __init__(self, identity):
        self.identity = identity
        self.authorizer = Authorizer()

    def load(self, *, period, source_period, client_id, exports=None,
             client_factory=SportlinkProgrammaClient):
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        try:
            source_period = validate_season(source_period)
        except ValueError as exc:
            raise CandidateSourceError(str(exc)) from None
        try:
            if exports is None:
                exports = LocalCsvSourceApplicationService().load().exports
            # Reuse the existing strict CSV boundary and complete household context.
            source = load_duty_dashboard(exports, as_of=period.start,
                                         source_period=source_period, isolate_person_errors=True).source
        except (ValueError, OSError) as exc:
            raise CandidateSourceError(
                "Kandidaatbronnen niet geladen. Controleer de vijf lokale CSV-bestanden, "
                f"hun verplichte kolommen, leesbaarheid en geldige bronwaarden. {exc}"
            ) from None
        try:
            validate_source_team_matchdays(source)
        except TeamMatchdayError as exc:
            raise CandidateSourceError(str(exc)) from None
        now = datetime.now().astimezone()
        history = LocalCsvSourceApplicationService().historical_backlog(
            person_ids=(p.person_id for p in source.persons))
        adapter = CkcProgrammaAdapter(team_memberships=source.team_memberships)
        client = client_factory(adapter)
        try:
            fetched = client.fetch_rows(client_id=client_id)
        except (ProgrammaFetchError, ValueError):
            return CandidateContext(period, source_period, source, None, now, client.stats,
                                    "Programma API niet beschikbaar: de aanvraag is mislukt of de respons is ongeldig. "
                                    "Wedstrijdcontext is onbekend; laad de kandidaatbronnen opnieuw.",
                                    tuple(EXPORT_FILENAMES.values()), history)
        program = adapter.import_rows(fetched.rows, retrieved_at=now)
        error = None
        if any(signal.severity == "ERROR" for signal in program.signals):
            error = "Wedstrijdcontext niet bruikbaar: controleer de teamkoppeling en wedstrijdbronmeldingen."
        return CandidateContext(period, source_period, source, program, now, client.stats, error,
                                tuple(EXPORT_FILENAMES.values()), history)

    def propose(self, context, *, service, need, planning_app, proposal_run_id):
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        if context.error or context.program is None:
            raise CandidateSourceError(context.error or "Wedstrijdcontext is niet geladen.")
        if not context.period.contains(service.starts_at):
            raise CandidateSourceError("Laad de kandidaatbronnen voor de gekozen planningsperiode opnieuw.")
        if context.source_period != season_id(service.starts_at.date()).replace("/", "-"):
            raise CandidateSourceError("Het opgegeven CSV-seizoen hoort niet bij deze dienst; controleer de urenexport.")
        source = context.source
        # Orphan rows have no matched person. Keep their diagnostics in the raw
        # context, but do not interpret their CSV row number as a relation code
        # (or a missing code as a fault of every imported person).
        assessment_source = replace(source, signals=tuple(
            signal for signal in source.signals
            if signal.code not in {"MISSING_PERSON_ID", "UNMATCHED_PERSON_REFERENCE"}
        ))
        controls = assessment_source.compare_required_hours(service.starts_at.date())
        members = {member.person_id: member for member in source.memberships}
        persons = {person.person_id: person for person in source.persons}
        # Planning trusts Sportlink A, not the policy comparison or household evidence.
        # Keep policy-only date errors in controls without overruling Sportlink A.
        # All other source-error checks continue to protect reliable planning.
        def usable_for_planning(control):
            pid = control.person_id
            member = members[pid]
            if (member.status.strip().casefold() != "definitief"
                    or (member.end_date is not None and member.end_date <= service.starts_at.date())
                    or persons[pid].birth_date is None
                    or len(control.duty_records) != 1):
                return False
            if any(((signal.severity == "ERROR" and signal.code not in {
                       "INVALID_FUNCTION_DATE", "INVALID_COMMITTEE_START_DATE",
                       "INVALID_COMMITTEE_END_DATE"}) or signal.code in {
                       "UNKNOWN_PLAYING_MEMBER_VALUE", "MISSING_TEAM_TYPE",
                       "UNKNOWN_TEAM_TYPE", "UNMATCHED_TEAM_REFERENCE"})
                   and (signal.record_key is None or signal.record_key.split(":", 1)[0] == pid)
                   for signal in assessment_source.signals):
                return False
            record = control.duty_records[0]
            return (record.source_formula_matches
                    and record.registration.required_hours is not None
                    and record.registration.required_hours > 0)

        usable = tuple(control for control in controls if usable_for_planning(control))
        try:
            other_weekend = other_weekend_persons(source.team_memberships, service)
        except TeamMatchdayError as exc:
            raise CandidateSourceError(str(exc)) from None
        need, = planning_app.staffing_needs(services=(service,), source_needs=(need,))
        cases = tuple(PrototypeCase(
            f"CKC-{control.person_id}", "Actuele CKC-bronnen", persons[control.person_id],
            members[control.person_id], persons=source.persons, memberships=source.memberships,
            roles=source.roles, sportlink_duty=control.duty_records[0].registration,
            context_date=service.starts_at.date(),
            context={"duty_expectation": control.expectation, "hours_control": control},
        ) for control in usable)
        qualifications = {control.person_id: DutyQualification(
            control.person_id, True, "Sportlink geregistreerde taakplicht",
            control.person_id,
        ) for control in usable}
        matches = context.program.matches
        assessments = planning_app.assess_candidates(
            cases=cases, service=service, team_memberships=context.program.team_memberships,
            matches=matches, today=service.starts_at.date(), duty_qualifications=qualifications,
        )
        history = context.historical_backlog
        priorities = prioritize_candidates(assessments, cases, service.starts_at.date(),
                                          history.values if history and history.available else {},
                                          apply_previous_season=bool(history and history.available))
        by_case = {case.person.person_id: case for case in cases}
        by_assessment = {assessment.person_id: assessment for assessment in assessments}
        proposals = tuple(create_assignment_proposal(
            f"CKC-{service.service_id}-{priority.person_id}-{proposal_run_id}", service,
            by_case[priority.person_id], by_assessment[priority.person_id], priority, matches,
        ) for priority in priorities)
        return CandidateProposals(cases, plan_matchday_proposals(proposals, need, other_weekend), controls, assessments, priorities,
                                  present_controls(source, controls).rows)
