"""Presentation-oriented demonstration of the accepted DVK Prototype v0.4.

This is deliberately not a replacement for pytest. It calls the accepted DVK
production components and renders their input, derivations, human decision and
output in a form intended for project demonstrations.
"""

from dataclasses import replace
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from dvk.assignments import apply_assignment_to_case, create_duty_assignment
from dvk.candidate_selection import assess_candidate
from dvk.duty import duty_position_from_registration
from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.proposals import assess_proposal, create_assignment_proposal
from dvk.prioritization import prioritize_candidates
from dvk.shift_catalog import ShiftCatalogAdapter
from dvk.staffing import calculate_staffing_need, staffing_provenance
from dvk.task_code_resolution import resolve_task_code
from dvk.vrijwilligers_adapter import ServiceBinding, SportlinkVrijwilligersAdapter
from dvk.workstream_cases import TODAY, W_CASE_BY_ID
from dvk.workstream_model import TeamMembership


IMPORTED_AT = datetime(2026, 9, 13, 10, 0, tzinfo=timezone.utc)
LOCAL = ZoneInfo("Europe/Amsterdam")
WIDTH = 72


def title(text):
    print("\n" + "=" * WIDTH)
    print(f" {text}")
    print("=" * WIDTH)


def section(text):
    print("\n" + text)
    print("-" * WIDTH)


def field(label, value):
    print(f"{label:<30} {value}")


def local(dt):
    return dt.astimezone(LOCAL).strftime("%d-%m-%Y %H:%M")


def position(pos):
    return f"A={pos.A}, B={pos.B}, C={pos.C}, D={pos.D}, E={pos.E}"


def build_happy_flow():
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
        task_code="701", rows=(), services=(ServiceBinding("701", service),),
        imported_at=IMPORTED_AT,
    )
    need = calculate_staffing_need(service=service, definition=definition,
                                   bookings=volunteer_result.bookings)
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
    proposal = create_assignment_proposal("P-R17", service, case, assessment, priority,
                                          program_result.matches)
    return shift_result, volunteer_result, need, program_result, case, service, assessment, priority, proposal


def scenario_1_approval():
    title("SCENARIO 1 — Van brondata naar goedgekeurde ledendienst")
    shift, volunteers, need, program, case, service, assessment, priority, proposal = build_happy_flow()
    definition = shift.definitions[0]
    match = program.matches[0]

    section("1. INPUT — CKC ShiftCatalog (CONFIGURATION)")
    field("Taakcode", definition.task_code)
    field("Dienst", definition.service_type)
    field("Duur", f"{definition.duration_hours:g} uur")
    field("Minimum bezetting", definition.minimum_staff)
    field("Maximum bezetting", definition.maximum_staff)

    section("2. INPUT — Concrete dienst + Sportlink Vrijwilligers")
    field("Dienst-ID", service.service_id)
    field("Diensttijd", f"{local(service.starts_at)} – {local(service.ends_at).split()[-1]}")
    field("Locatie", service.location)
    field("Bevestigde vrijwilligers", len(volunteers.bookings))
    field("DVK: minimum nodig", need.minimum_staff)
    field("DVK: open behoefte", need.open_need)

    section("3. INPUT — Sportlink Programma (SOURCE_FACT)")
    field("Wedstrijd-ID", match.match_id)
    field("Team", match.team_id)
    field("Aanvang", local(match.starts_at))
    field("Thuis/uit", match.home_away)
    field("Status bronrecord", "Te spelen")

    section("4. INPUT — Kandidaat")
    before = duty_position_from_registration(case.sportlink_duty)
    field("Naam", case.person.name)
    field("Team", "Senioren 8")
    field("Urenpositie vóór voorstel", position(before))
    field("DVK kandidaatstatus", "GESCHIKT" if assessment.eligible else "NIET GESCHIKT")

    section("4a. DVK-UITLEG — Waarom deze kandidaat?")
    field("DVK rangorde", priority.rank)
    field("Nog in te plannen", f"{priority.remaining_hours:g} uur")
    field("Achterstand vorig seizoen", f"{priority.previous_season_backlog:g} uur ({'meegewogen' if priority.previous_season_considered else 'niet meegewogen'})")
    preference = {
        "preferred": "GUNSTIG",
        "neutral": "NEUTRAAL",
        "avoid": "ONGUNSTIG",
    }.get(priority.match_preference, str(priority.match_preference).upper())
    field("Wedstrijdvoorkeur", preference)
    reason_parts = [f"{priority.remaining_hours:g} uur openstaand"]
    if priority.match_preference == "preferred" and proposal.match_starts_at is not None:
        reason_parts.append(f"thuiswedstrijd om {proposal.match_starts_at.astimezone(LOCAL).strftime('%H:%M')}")
    field("Reden", "; ".join(reason_parts))

    section("5. DVK-VOORSTEL")
    field("Voorstel-ID", proposal.proposal_id)
    field("Kandidaat", case.person.name)
    field("Wedstrijdcontext", f"{proposal.home_away.upper()} om {local(proposal.match_starts_at)}")
    field("Status", proposal.status.upper())
    print("\nDVK heeft hiermee een voorstel gemaakt; er is nog geen indeling.")

    section("6. MENSELIJKE BESLISSING")
    decision = assess_proposal(proposal, "approved", "Vrijwilligerscommissie")
    field("Beslisser", "Vrijwilligerscommissie")
    field("Besluit", "GOEDGEKEURD")
    assignment = create_duty_assignment("A-R17", proposal, decision, service)
    updated = apply_assignment_to_case(case, assignment)
    after = duty_position_from_registration(updated.sportlink_duty)

    section("7. OUTPUT — DutyAssignment en urenpositie")
    field("Assignment-ID", assignment.assignment_id)
    field("Persoon", case.person.name)
    field("Dienst", definition.service_type)
    field("Urenpositie vóór", position(before))
    field("Urenpositie na", position(after))
    field("Effect", f"Tijdelijke DVK-planning: {assignment.scheduled_hours} uur; Sportlink A/B/C/D/E ongewijzigd")

    section("8. PROVENANCE — Wat is feit, configuratie en afleiding?")
    field("ShiftCatalog", next(iter({p.kind for p in shift.provenance})))
    field("Sportlink Programma", next(iter({p.kind for p in program.provenance})))
    field("Sportlink Vrijwilligers", "SOURCE_FACT (0 records in dit scenario)")
    field("Open behoefte", staffing_provenance(need, derived_at=IMPORTED_AT).kind)
    field("Voorstel", "DVK-afleiding / voorstel")
    field("Goedkeuring", "MENSELIJKE BESLISSING")
    return after == before and assignment.scheduled_hours == 1


def scenario_2_rejection():
    title("SCENARIO 2 — Mens wijst DVK-voorstel af")
    _, _, _, _, case, service, _, _, proposal = build_happy_flow()
    before = duty_position_from_registration(case.sportlink_duty)
    section("INPUT")
    field("Voorstel", proposal.proposal_id)
    field("Kandidaat", case.person.name)
    field("Urenpositie", position(before))
    section("MENSELIJKE BESLISSING")
    decision = assess_proposal(proposal, "rejected", "Vrijwilligerscommissie",
                               "planning", "Andere inzet gekozen")
    assignment = create_duty_assignment("A-R17-X", proposal, decision, service)
    field("Besluit", "AFGEWEZEN")
    field("Reden", "Andere inzet gekozen")
    section("OUTPUT")
    field("DutyAssignment", "GEEN" if assignment is None else assignment.assignment_id)
    field("Urenpositie gewijzigd", "NEE")
    print("\nEen DVK-voorstel is dus nadrukkelijk niet hetzelfde als een CKC-besluit.")
    return assignment is None


def scenario_3_unknown_task_code():
    title("SCENARIO 3 — Onbekende taakcode: DVK gokt niet")
    catalog = ShiftCatalogAdapter().import_rows((
        {"task_code": "701", "service_type": "Bar korte inzet", "duration_hours": "1", "minimum_staff": "1", "maximum_staff": "2"},
        {"task_code": "741", "service_type": "Bar weekend", "duration_hours": "2.5", "minimum_staff": "2", "maximum_staff": "4"},
    ), imported_at=IMPORTED_AT)
    source_code = "999"
    result = resolve_task_code(source_code, catalog.definitions)
    section("INPUT")
    field("Taakcode uit bron", source_code)
    field("Bekende cataloguscodes", ", ".join(d.task_code for d in catalog.definitions))
    section("DVK-VERWERKING")
    field("Automatische mapping", "GEEN")
    field("Gekozen ShiftDefinition", result.definition or "GEEN")
    section("OUTPUT — Datakwaliteit")
    for signal in result.signals:
        field("Signaal", signal.code)
        field("Ernst", signal.severity)
        field("Melding", signal.message)
    print("\nDVK trimt, vertaalt of fuzzy-matcht een onbekende taakcode niet.")
    return result.definition is None and result.signals[0].code == "UNKNOWN_TASK_CODE"


def scenario_4_irregular_service():
    title("SCENARIO 4 — Afwijkende concrete diensttijd blijft bronfeit")
    adapter = SportlinkVrijwilligersAdapter()
    start = datetime(2026, 9, 15, 17, 0, tzinfo=LOCAL)
    end = datetime(2026, 9, 15, 22, 30, tzinfo=LOCAL)
    boundaries = tuple(datetime(2026, 9, 15, h, 0, tzinfo=LOCAL) for h in (18, 19, 20)) + (
        datetime(2026, 9, 15, 22, 30, tzinfo=LOCAL),
    )
    operational = adapter.derive_operational_service(
        task_code="761", starts_at=start, ends_at=end, location="CKC",
        catalog_boundaries=boundaries,
    )
    section("INPUT — Concrete Sportlink-dienst")
    field("Taakcode", operational.task_code)
    field("Werkelijke periode", f"{local(operational.starts_at)} – {local(operational.ends_at).split()[-1]}")
    field("Locatie", operational.location)
    section("DVK-AFLEIDING — Planbare segmenten")
    for index, (left, right) in enumerate(operational.segments, 1):
        field(f"Segment {index}", f"{left.strftime('%H:%M')} – {right.strftime('%H:%M')}")
    section("OUTPUT")
    field("Volledige bronperiode behouden", "JA")
    field("Afwijking van catalogus", "JA" if operational.deviates_from_catalog else "NEE")
    print("\nDe segmenten helpen bij planning; ze vervangen of verkorten het bronfeit niet.")
    return operational.deviates_from_catalog and operational.starts_at == start and operational.ends_at == end


def main():
    title("DVK PROTOTYPE v0.4 — PRESENTATIERUN")
    print("Doel: zichtbaar maken welke input DVK ontvangt, wat DVK afleidt,")
    print("waar de mens beslist en welke output daarna ontstaat.")
    results = (
        ("1. Goedkeuring end-to-end", scenario_1_approval()),
        ("2. Afwijzing zonder assignment", scenario_2_rejection()),
        ("3. Onbekende taakcode", scenario_3_unknown_task_code()),
        ("4. Afwijkende diensttijd", scenario_4_irregular_service()),
    )
    title("SAMENVATTING PRESENTATIERUN")
    for name, ok in results:
        field(name, "OK" if ok else "MISLUKT")
    print("\nDeze presentatierun vervangt de formele pytest-suite niet.")
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
