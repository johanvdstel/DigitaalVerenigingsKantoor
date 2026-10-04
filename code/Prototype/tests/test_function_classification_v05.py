from datetime import date, datetime
import json
from pathlib import Path

import pytest

from dvk.duty import derive_duty_qualification
from dvk.function_classification import ClassificationRule, FunctionClassifier
from dvk.model import FunctionExemptionPolicy, Membership, Person, PrototypeCase, RoleAssignment
from dvk.real_data_import import CommitteeMembership, SportlinkRealDataAdapter
from test_real_data_import_v04 import exports, write_csv


# Exact approved workbook keys, independent of the runtime configuration.
APPROVED = json.loads((Path(__file__).parents[1] / "testdata/v05_function_classification/approved_keys.json").read_text())


@pytest.mark.parametrize("title", APPROVED["functions"])
def test_all_27_approved_functions(title):
    item = FunctionClassifier().classify(RoleAssignment("P1", title))
    paid = title in {"Hoofdtrainer Sen.", "Verzorger"}
    assert item.known and item.self_exempt
    assert item.household_exempt is not paid
    assert item.rule.category == ("Betaalde functie – CKC-afspraak" if paid else "Erkende onbetaalde vrijwilligersfunctie")


@pytest.mark.parametrize("committee,title", APPROVED["committees"])
def test_all_62_approved_combinations(committee, title):
    item = FunctionClassifier().classify(CommitteeMembership("P1", committee, title))
    honorary = (committee, title) == ("lid van verdienste", "lid van verdienste")
    assert item.known and item.self_exempt
    assert item.household_exempt is not honorary
    assert item.rule.category == ("Eretitel" if honorary else "Erkende onbetaalde vrijwilligersfunctie")


def test_configuration_contains_exactly_approved_keys_and_explicit_policy_titles():
    assert len(set(APPROVED["functions"])) == 27
    assert len({tuple(key) for key in APPROVED["committees"]}) == 62
    expected = {("functies", "", title) for title in APPROVED["functions"] + ["Erelid", "Lid van verdienste"]}
    expected.update(("commissies", committee, title) for committee, title in APPROVED["committees"])
    assert set(FunctionClassifier().rules) == expected


@pytest.mark.parametrize("title", ["Hoofdtrainer Sen.", "Verzorger", "Lid van verdienste", "Erelid"])
def test_personal_only_exceptions_have_no_person_specific_override(title):
    result = FunctionClassifier().classify_many([RoleAssignment(pid, title) for pid in ("P1", "P2")])
    assert all(p.self_exempt and not p.household_exempt for p in result.persons)


def test_overlap_keeps_every_fact_and_grants_rights_only_once_per_person():
    sources = [RoleAssignment("P1", "Hoofdtrainer Sen."), RoleAssignment("P1", "Trainer Pupillen"),
               CommitteeMembership("P1", "Bestuur", "CKC 100"), RoleAssignment("P1", "Trainer Pupillen")]
    result = FunctionClassifier().classify_many(sources)
    assert len(result.persons) == 1
    assert result.persons[0].self_exempt and result.persons[0].household_exempt
    assert tuple(r.source for r in result.registrations) == tuple(sources)
    assert len(result.persons[0].registrations) == 4
    assert not result.signals


def test_unknown_values_are_counted_by_exact_source_key_and_not_fuzzy_matched():
    sources = [RoleAssignment("P1", "Nieuwe functie"), RoleAssignment("P2", " Nieuwe   functie "),
               CommitteeMembership("P1", "Bestuur", "CKC100"),
               CommitteeMembership("P2", "Bestuur", "CKC100"),
               CommitteeMembership("P2", "Andere commissie", "CKC100")]
    result = FunctionClassifier().classify_many(sources)
    assert all(not r.known and not r.self_exempt and not r.household_exempt for r in result.registrations)
    assert all(not p.self_exempt and not p.household_exempt for p in result.persons)
    assert {(s.facts["dataset"], s.facts["committee"], s.facts["title"], s.facts["registration_count"])
            for s in result.signals} == {("functies", "", "Nieuwe functie", 2),
                                        ("commissies", "Bestuur", "CKC100", 2),
                                        ("commissies", "Andere commissie", "CKC100", 1)}


def test_known_nonexempt_is_distinct_from_unknown_and_configuration_duplicates_fail():
    rule = ClassificationRule("functies", "", "Niet vrijstellend", "Niet-vrijstellende functie",
                              FunctionExemptionPolicy("Niet vrijstellend", False, False))
    result = FunctionClassifier([rule]).classify_many([RoleAssignment("P1", "Niet vrijstellend"),
                                                      RoleAssignment("P2", "Onbekend")])
    assert result.registrations[0].known
    assert not result.registrations[0].self_exempt
    assert not result.registrations[0].household_exempt
    assert not result.registrations[1].known
    assert len(result.signals) == 1
    with pytest.raises(ValueError, match="Duplicate"):
        FunctionClassifier([rule, rule])


def test_import_preserves_names_dates_and_linked_provenance_without_duty_integration(tmp_path):
    paths = exports(tmp_path)
    paths["functions_path"] = write_csv(tmp_path, "functies.csv", ["Rel. code", "Functie", "Begindatum", "Einddatum"],
                                        [["P1", " Trainer   Pupillen ", "01-09-2026", "30-06-2027"],
                                         ["P1", "Hoofdtrainer Sen.", "", ""]])
    paths["committees_path"] = write_csv(tmp_path, "commissies.csv", ["Rel. code", "Commissie", "Functie", "Begindatum", "Einddatum"],
                                         [["P1", "Bestuur", "CKC 100", "01-09-2026", "30-06-2027"]])
    imported_at = datetime(2026, 10, 4, 12)
    result = SportlinkRealDataAdapter().load_exports(**paths, imported_at=imported_at, source_period="2026-2027")
    role = result.roles[0]
    assert role.role == "Trainer Pupillen" and role.source_role == " Trainer   Pupillen "
    assert role.provenance.source_value == role.source_role
    assert (role.start_date, role.end_date) == (date(2026, 9, 1), date(2027, 6, 30))
    assert result.roles[1].start_date is None and result.roles[1].end_date is None
    committee = result.committees[0]
    assert (committee.committee, committee.committee_role) == ("Bestuur", "CKC 100")
    assert (committee.start_date, committee.end_date) == (role.start_date, role.end_date)
    for source in (role, committee):
        assert source.provenance in result.provenance
        assert source.provenance.source_system == "Sportlink"
        assert source.provenance.imported_at == imported_at
        assert source.provenance.source_period == "2026-2027"
        assert source.provenance.kind == "SOURCE_FACT"
    classified = result.function_classification
    assert classified.registrations[0].source is role
    assert classified.registrations[0].kind == "DERIVED"
    assert classified.registrations[0].configuration_version == "ckc-v05-step2-round1"
    assert classified.persons[0].household_exempt
    person = result.persons[0]
    case = PrototypeCase("S2", "synthetic", person,
                         Membership("P1", "active", "member", plays_football=True), roles=result.roles)
    assert derive_duty_qualification(case, date(2026, 10, 4)).reason == "playing_member"
    assert not classified.signals


def test_import_exposes_bundled_unknown_classification(tmp_path):
    result = SportlinkRealDataAdapter().load_exports(**exports(tmp_path))
    assert result.function_classification.signals[0].facts == {
        "dataset": "commissies", "committee": "Jeugdcommissie", "title": "commissielid", "registration_count": 1}


def test_address_and_parent_preparation_is_backward_compatible_and_creates_no_relationships():
    legacy = Person("P1", "Synthetic", address="legacy address")
    assert legacy.postal_code is None and legacy.house_number is None
    assert legacy.house_number_addition is None and legacy.parent_names == (None, None)
    prepared = Person("P2", "Synthetic", postal_code="1234 AB", house_number="10",
                      house_number_addition="A", parent_names=("Synthetic parent", None))
    assert prepared.address is None
    assert prepared.parent_names == ("Synthetic parent", None)


@pytest.mark.parametrize("dataset,column,code", [
    ("functions_path", "Begindatum", "INVALID_FUNCTION_DATE"),
    ("functions_path", "Einddatum", "INVALID_FUNCTION_DATE"),
    ("committees_path", "Begindatum", "INVALID_COMMITTEE_START_DATE"),
    ("committees_path", "Einddatum", "INVALID_COMMITTEE_END_DATE"),
])
def test_invalid_source_dates_are_signalled_not_repaired(tmp_path, dataset, column, code):
    paths = exports(tmp_path)
    path = paths[dataset]
    if dataset == "functions_path":
        write_csv(tmp_path, path.name, ["Rel. code", "Functie", column], [["P1", "Trainer Pupillen", "geen datum"]])
    else:
        write_csv(tmp_path, path.name, ["Rel. code", "Commissie", "Functie", column],
                  [["P1", "Bestuur", "CKC 100", "geen datum"]])
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert any(s.code == code and s.severity == "ERROR" for s in result.signals)
    assert not (result.roles if dataset == "functions_path" else result.committees)
