"""Round-3 development regressions; synthetic source data only."""
from datetime import date

import pytest

from dvk.real_data_import import SportlinkRealDataAdapter
from test_member_duty_v05 import write_export

TODAY = date(2026, 10, 6)
FIELDS = ["Relatiecode", "Verplichte punten", "Gecorrigeerde punten", "Voldaan", "Nog ingedeeld", "Niet ingedeeld"]


def load(tmp_path, values=(10, 0, 9, 0, 1), pid="M1", unknown=False, extra=False, duplicate=False):
    adapter = SportlinkRealDataAdapter()
    member = {"Rel. code": "M1", "Naam": "Synthetisch lid", "Geb.dat.": "01-01-1990",
              "Lidstatus": "Definitief", "Lidsoort": "Bondslid", "Status lidmaatschap": "",
              "Postcode": "8000AA", "Huisnummer": "17", "Toevoeging": ""}
    members = write_export(tmp_path, "members.csv", [member], list(member))
    function_rows = [{"Rel. code": "M1", "Functie": "Onbekend"}] if unknown else []
    functions = write_export(tmp_path, "functions.csv", function_rows, ["Rel. code", "Functie"])
    committees = write_export(tmp_path, "committees.csv", [], sorted(adapter.REQUIRED_COLUMNS["commissies"]))
    team = {"Rel. code": "M1", "Team": "Senioren", "Teamsoort": "Bond", "Teamrol": "Teamspeler",
            "Spelend lid": "Ja"}
    teams = write_export(tmp_path, "teams.csv", [team], list(team))
    row = dict(zip(FIELDS, [pid, *values]))
    if extra:
        row.update({"Volledige naam": "Andere naam", "Overbodig": "genegeerd"})
    duties = write_export(tmp_path, "hours.csv", [row, row] if duplicate else [row], list(row))
    return adapter.load_exports(members_path=members, functions_path=functions, committees_path=committees,
                                teams_path=teams, duty_path=duties, source_period="2026-2027")


@pytest.mark.parametrize("values", [(10, 0, 9, 0, 1), (0, 0, 2, 0, -2), (10, 0, 2, 3, 5),
                                    (10, 3, 2, 1, 4), (10, 2, 9, 0, -1), (10, -2, 9, 0, 3)])
def test_actual_mapping_and_formula(tmp_path, values):
    data = load(tmp_path, values)
    record, = data.duty_records
    assert record.registration.person_id == data.persons[0].person_id == "M1"
    assert (record.position.A, record.position.B, record.position.C, record.position.D,
            record.source_remaining_hours) == values
    assert record.position.E == values[-1] and record.source_formula_matches
    assert not data.signals
    facts = {p.source_field: p.source_value for p in data.provenance if p.source_dataset == "vrijwilligers_periode"}
    assert facts == dict(zip(FIELDS, ["M1", *map(str, values)]))


def test_incorrect_e_preserves_both_values_and_is_not_reliably_assessed(tmp_path):
    data = load(tmp_path, (10, 0, 9, 0, 7))
    record, = data.duty_records
    assert record.source_remaining_hours == 7 and record.position.E == 1
    assert any(s.code == "DUTY_REMAINING_MISMATCH" for s in data.signals)
    assert next(p for p in data.provenance if p.source_field == "Niet ingedeeld").normalized_value == "7"
    assert data.compare_required_hours(TODAY)[0].status == "niet betrouwbaar beoordeelbaar"


@pytest.mark.parametrize("a,status", [(10, "overeenkomst"), (0, "afwijking")])
def test_round2_expectation_is_used_for_a_control(tmp_path, a, status):
    data = load(tmp_path, (a, 0, 0, 0, a), extra=True)
    control, = data.compare_required_hours(TODAY)
    assert control.status == status
    assert control.expected_required_hours == 10 and control.registered_required_hours == a
    assert control.expectation == data.derive_member_duties(TODAY)[0]
    assert control.expectation.grounds and control.expectation.source_facts
    assert control.provenance and control.kind == "DERIVED"
    assert data.duty_records[0].registration.required_hours == a
    assert (any(s.code == "REQUIRED_HOURS_REASSESSMENT" for s in control.signals)) == (a != 10)


def test_unknown_round2_result_cannot_be_compared(tmp_path):
    control, = load(tmp_path, unknown=True).compare_required_hours(TODAY)
    assert control.expected_required_hours is None
    assert control.registered_required_hours == 10
    assert control.status == "niet betrouwbaar beoordeelbaar"
    assert any(g.code == "function_classification_unknown" for g in control.expectation.grounds)


@pytest.mark.parametrize("index", range(5))
@pytest.mark.parametrize("invalid", ["", "tekst", "NaN", "Infinity", "1.5"])
def test_invalid_numeric_values_are_explicit(tmp_path, index, invalid):
    values = [10, 0, 9, 0, 1]
    values[index] = invalid
    data = load(tmp_path, values)
    assert not data.duty_records
    control, = data.compare_required_hours(TODAY)
    assert control.status == "niet betrouwbaar beoordeelbaar"
    assert any(s.code == "INVALID_DUTY_VALUE" for s in control.signals)
    assert any(p.source_field == FIELDS[index + 1] and p.source_value == invalid for p in control.provenance)


@pytest.mark.parametrize("pid", ["", "ONBEKEND"])
def test_no_guessed_link(tmp_path, pid):
    data = load(tmp_path, pid=pid, extra=True)
    assert not data.duty_records
    assert any(s.code == "UNMATCHED_PERSON_REFERENCE" for s in data.signals)
    assert data.compare_required_hours(TODAY)[0].status == "niet betrouwbaar beoordeelbaar"


def test_duplicate_positions_do_not_choose_a_row(tmp_path):
    control, = load(tmp_path, duplicate=True).compare_required_hours(TODAY)
    assert control.status == "niet betrouwbaar beoordeelbaar"
    assert control.registered_required_hours is None and len(control.duty_records) == 2
    assert any(s.code == "AMBIGUOUS_DUTY_POSITION" for s in control.signals)


def test_missing_required_hours_header_fails_explicitly():
    with pytest.raises(ValueError, match="missing columns"):
        SportlinkRealDataAdapter.read_rows_text("Relatiecode;Verplichte punten\nM1;10", "vrijwilligers_periode")


def test_configured_policy_is_used_without_altering_registration(tmp_path):
    from dvk.model import DutyPolicy
    data = load(tmp_path, (12, 0, 0, 0, 12))
    control, = data.compare_required_hours(TODAY, DutyPolicy(12, "seizoen-test"))
    assert control.status == "overeenkomst"
    assert control.expectation.policy_version == "seizoen-test"
    assert data.compare_required_hours(TODAY)[0].status == "afwijking"


def test_decimal_notation_and_large_whole_numbers_preserve_exact_value(tmp_path):
    data = load(tmp_path, ("9007199254740993", "1,0", 0, 0, "9007199254740992"))
    record, = data.duty_records
    assert record.position.A == 9007199254740993
    assert record.source_formula_matches


def test_missing_export_does_not_create_zero_position(tmp_path):
    from dataclasses import replace
    data = replace(load(tmp_path), duty_records=(), provenance=())
    control, = data.compare_required_hours(TODAY)
    assert control.registered_required_hours is None
    assert control.status == "niet betrouwbaar beoordeelbaar"
    assert any(s.code == "MISSING_DUTY_POSITION" for s in control.signals)


def test_importer_preserves_source_a_without_policy_comparison(tmp_path):
    data = load(tmp_path, (3, 1, 1, 0, 1))
    record, = data.duty_records
    assert (record.position.A, record.position.B, record.position.C, record.position.D) == (3, 1, 1, 0)
    assert record.source_remaining_hours == record.position.E == 1
    assert data.signals == ()
    control, = data.compare_required_hours(TODAY)
    assert control.expected_required_hours == 10 and control.registered_required_hours == 3
    assert control.status == "afwijking"
    assert [s.code for s in control.signals] == ["REQUIRED_HOURS_REASSESSMENT"]
    assert data.signals == ()  # The read-only domain control does not mutate imported facts/signals.


def test_import_api_has_no_external_expectation_route():
    from dataclasses import fields
    from inspect import signature
    from dvk.real_data_import import DutyImportRecord
    assert "expected_required_hours" not in signature(SportlinkRealDataAdapter.load_exports).parameters
    assert "expected_required_hours" not in {field.name for field in fields(DutyImportRecord)}
    assert not hasattr(DutyImportRecord, "required_hours_mismatch")
