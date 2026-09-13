from dataclasses import replace
from datetime import date, datetime, timezone

from dvk.assignments import apply_assignment_to_case, create_duty_assignment
from dvk.candidate_selection import assess_candidate
from dvk.duty import duty_position_from_registration
from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.shift_catalog import ShiftCatalogAdapter
from dvk.staffing import calculate_staffing_need, staffing_provenance
from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import TeamMembership


IMPORTED_AT = datetime(2026, 9, 13, 10, 0, tzinfo=timezone.utc)


def _integrated_fixture():
    shift_result = ShiftCatalogAdapter().import_rows(({
        "task_code": "701",
        "service_type": "Bar korte inzet",
        "duration_hours": "1",
        "minimum_staff": "1",
        "maximum_staff": "2",
    },), imported_at=IMPORTED_AT)
    definition = shift_result.definitions[0]
    service = ShiftCatalogAdapter.create_service(
        definition,
        service_id="S-R17",
        starts_at=datetime(2026, 9, 12, 11, 0, tzinfo=timezone.utc),
        location="CKC",
    )

    volunteer_result = SportlinkVrijwilligersAdapter().import_rows(
        task_code="701",
        rows=(),
        services=(ServiceBinding("701", service),),
        imported_at=IMPORTED_AT,
    )
    need = calculate_staffing_need(
        service=service,
        definition=definition,
        bookings=volunteer_result.bookings,
    )

    program_result = SportlinkProgrammaAdapter(club_relation_code="CKC").import_rows(({
        "wedstrijddatum": "2026-09-12T14:30:00+02:00",
        "wedstrijdcode": "M-R17",
        "thuisteamclubrelatiecode": "CKC",
        "uitteamclubrelatiecode": "OTHER",
        "thuisteamid": "Senioren 8",
        "thuisteam": "CKC Senioren 8",
        "uitteamid": "OTHER-1",
        "uitteam": "Tegenstander 1",
        "status": "Te spelen",
        "accommodatie": "CKC",
    },), retrieved_at=IMPORTED_AT)

    base = W_CASE_BY_ID["W08"]
    case = replace(base, person=replace(base.person, name="Jan Smit"))
    teams = (TeamMembership("W08P", "Senioren 8", date(2026, 7, 1), date(2027, 6, 30)),)
    assessment = assess_candidate(case, service, teams, program_result.matches, TODAY)
    priority = prioritize_candidates((assessment,), (case,), service.starts_at.date())[0]
    proposal = create_assignment_proposal(
        "P-R17", service, case, assessment, priority, program_result.matches
    )
    return shift_result, volunteer_result, need, program_result, case, service, proposal


def test_r16_provenance_distinguishes_source_configuration_and_derivation():
    shift_result, volunteer_result, need, program_result, _, _, _ = _integrated_fixture()
    derived = staffing_provenance(need, derived_at=IMPORTED_AT)

    assert {row.kind for row in shift_result.provenance} == {"CONFIGURATION"}
    assert {row.kind for row in program_result.provenance} == {"SOURCE_FACT"}
    assert all(row.kind == "SOURCE_FACT" for row in volunteer_result.provenance)
    assert derived.kind == "DERIVED"
    assert derived.source_system == "DVK"
    assert derived.source_dataset == "staffing"


def test_r17_integrated_weekend_reaches_proposal_human_decision_and_assignment():
    _, _, need, program_result, case, service, proposal = _integrated_fixture()

    assert need.open_need == 1
    assert proposal.person_id == "W08P"
    assert proposal.home_away == "HOME"
    assert proposal.match_starts_at == program_result.matches[0].starts_at
    assert proposal.status == "proposed"

    before = duty_position_from_registration(case.sportlink_duty)
    decision = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    assert case.sportlink_duty.scheduled_hours == before.D

    assignment = create_duty_assignment("A-R17", proposal, decision, service)
    assert assignment is not None
    assert assignment.approved_by == "Vrijwilligerscommissie"

    updated_case = apply_assignment_to_case(case, assignment)
    after = duty_position_from_registration(updated_case.sportlink_duty)
    assert (after.A, after.B, after.C) == (before.A, before.B, before.C)
    assert after.D == before.D + 1
    assert after.E == before.E - 1


def test_r17_rejection_never_creates_assignment_or_mutates_source_position():
    _, _, _, _, case, service, proposal = _integrated_fixture()
    before = case.sportlink_duty
    decision = assess_proposal(
        proposal,
        "rejected",
        "Vrijwilligerscommissie",
        "planning",
        "Andere inzet gekozen",
    )
    assert create_duty_assignment("A-R17-X", proposal, decision, service) is None
    assert case.sportlink_duty == before
