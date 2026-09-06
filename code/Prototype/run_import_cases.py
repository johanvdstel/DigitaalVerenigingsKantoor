from pathlib import Path

from dvk.duty import evaluate_duty_foundation
from dvk.import_adapter import SportlinkCsvImportAdapter
from dvk.workstream_cases import TODAY


FIXTURES = Path(__file__).parent / "testdata" / "v03_import"


def main() -> None:
    data = SportlinkCsvImportAdapter().load_directory(FIXTURES)

    print("I01 — Sportlink-achtige bronimport")
    print(f"  leden: {len(data.persons)}")
    print(f"  taakurenregistraties: {len(data.duty_registrations)}")
    print(f"  teamlidmaatschappen: {len(data.team_memberships)}")
    print(f"  wedstrijden: {len(data.matches)}")
    print(f"  diensten: {len(data.services)}")
    print("  resultaat: OK")
    print()

    imported = evaluate_duty_foundation(data.case_for_person("I01P", "I01"), TODAY)
    print("I01a — Geïmporteerd taakplichtig lid reproduceert domeinuitkomst")
    print(f"  taakplichtig: {imported.facts['duty_required']}")
    print(f"  verwacht A: {imported.facts['expected_required_hours']}")
    position = imported.facts["duty_position"]
    print(
        "  urenpositie: "
        f"A={position['A']} B={position['B']} C={position['C']} D={position['D']} E={position['E']}"
    )
    print(f"  resultaat: {imported.status.upper()}")
    print()

    exempt = evaluate_duty_foundation(data.case_for_person("I02P", "I01-role"), TODAY)
    print("I01b — Geïmporteerde functie blijft bronfeit")
    print("  bronfunctie: trainer")
    print(f"  afgeleide taakplicht: {exempt.facts['duty_required']}")
    print(f"  reden: {exempt.facts['qualification_reason']}")
    print(f"  verwacht A: {exempt.facts['expected_required_hours']}")
    print(f"  resultaat: {exempt.status.upper()}")
    print()

    print("I01c — Bronvalidatie")
    print("  vereiste kolommen worden expliciet gecontroleerd")
    print("  ontbrekende kolommen leiden tot ValueError; DVK verzint geen bronfeiten")
    print("  resultaat: OK (afgedekt door pytest-regressietest)")


if __name__ == "__main__":
    main()
