"""Connect existing v0.5 sources and domain services; no new selection policy."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime

from .duty_control_presenter import EXPORTS, load_duty_dashboard, present_controls, validate_season
from .model import DutyQualification, PrototypeCase
from .no_show import season_id
from .planning import PlanningPeriod
from .prioritization import prioritize_candidates
from .programma_client import ProgrammaFetchError, ProgrammaFetchStats, SportlinkProgrammaClient
from .programma_team_adapter import CkcProgrammaAdapter, LinkedProgramImportResult
from .proposal_planning import plan_proposals
from .proposals import create_assignment_proposal
from .real_data_import import RealDataImportResult
from .security import Authorizer, Permission
from .sportlink_exports import read_export_text


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
                exports = {dataset: read_export_text(dataset).encode("utf-8") for dataset in EXPORTS}
            # Reuse the existing strict CSV boundary and complete household context.
            source = load_duty_dashboard(exports, as_of=period.start,
                                         source_period=source_period).source
        except (ValueError, OSError):
            raise CandidateSourceError(
                "Kandidaatbronnen niet geladen. Controleer de vijf lokale CSV-bestanden, "
                "hun verplichte kolommen, leesbaarheid en geldige bronwaarden."
            ) from None
        now = datetime.now().astimezone()
        if any(signal.severity == "ERROR" for signal in source.signals):
            return CandidateContext(period, source_period, source, None, now, ProgrammaFetchStats(),
                                    "CSV-bronproblemen: beoordeel de bronmeldingen en vernieuw de exports vóór kandidaatselectie.")
        adapter = CkcProgrammaAdapter(team_memberships=source.team_memberships)
        client = client_factory(adapter)
        try:
            fetched = client.fetch_rows(client_id=client_id)
        except (ProgrammaFetchError, ValueError):
            return CandidateContext(period, source_period, source, None, now, client.stats,
                                    "Programma API niet beschikbaar: de aanvraag is mislukt of de respons is ongeldig. "
                                    "Wedstrijdcontext is onbekend; laad de kandidaatbronnen opnieuw.")
        program = adapter.import_rows(fetched.rows, retrieved_at=now)
        error = None
        if any(signal.severity == "ERROR" for signal in program.signals):
            error = "Wedstrijdcontext niet bruikbaar: controleer de teamkoppeling en wedstrijdbronmeldingen."
        return CandidateContext(period, source_period, source, program, now, client.stats, error)

    def propose(self, context, *, service, need, planning_app, proposal_run_id):
        self.authorizer.require(self.identity, Permission.VIEW_PLANNING)
        if context.error or context.program is None:
            raise CandidateSourceError(context.error or "Wedstrijdcontext is niet geladen.")
        if not context.period.contains(service.starts_at):
            raise CandidateSourceError("Laad de kandidaatbronnen voor de gekozen planningsperiode opnieuw.")
        if context.source_period != season_id(service.starts_at.date()).replace("/", "-"):
            raise CandidateSourceError("Het opgegeven CSV-seizoen hoort niet bij deze dienst; controleer de urenexport.")
        source = context.source
        controls = source.compare_required_hours(service.starts_at.date())
        members = {member.person_id: member for member in source.memberships}
        persons = {person.person_id: person for person in source.persons}
        # Exclusions and uncertainty come from the accepted v0.5 source derivation.
        usable = tuple(control for control in controls
                       if control.status != "niet betrouwbaar beoordeelbaar"
                       and control.expectation.status == "taakplichtig")
        cases = tuple(PrototypeCase(
            f"CKC-{control.person_id}", "Actuele CKC-bronnen", persons[control.person_id],
            members[control.person_id], persons=source.persons, memberships=source.memberships,
            roles=source.roles, sportlink_duty=control.duty_records[0].registration,
            context_date=service.starts_at.date(),
            context={"duty_expectation": control.expectation, "hours_control": control},
        ) for control in usable)
        qualifications = {control.person_id: DutyQualification(
            control.person_id, True, ", ".join(ground.code for ground in control.expectation.grounds),
            control.person_id,
        ) for control in usable}
        matches = context.program.matches
        assessments = planning_app.assess_candidates(
            cases=cases, service=service, team_memberships=context.program.team_memberships,
            matches=matches, today=service.starts_at.date(), duty_qualifications=qualifications,
        )
        priorities = prioritize_candidates(assessments, cases, service.starts_at.date(),
                                          apply_previous_season=False)
        by_case = {case.person.person_id: case for case in cases}
        by_assessment = {assessment.person_id: assessment for assessment in assessments}
        proposals = tuple(create_assignment_proposal(
            f"CKC-{service.service_id}-{priority.person_id}-{proposal_run_id}", service,
            by_case[priority.person_id], by_assessment[priority.person_id], priority, matches,
        ) for priority in priorities)
        return CandidateProposals(cases, plan_proposals(proposals, need), controls, assessments, priorities,
                                  present_controls(source, controls).rows)
