"""Development regressions for the accepted round-2 rules, not release acceptance."""
import csv
from dataclasses import replace
from datetime import date

import pytest

from dvk.member_duty import canonical_address, family_criteria
from dvk.model import DutyPolicy, Membership, Person, RoleAssignment
from dvk.real_data_import import CommitteeMembership, RealDataImportResult, SportlinkRealDataAdapter

TODAY = date(2026, 10, 6)


def person(pid, born=date(1990, 1, 1), **kwargs):
    return Person(pid, f"Lid {pid}", born, postal_code="8000 AA", house_number="17", **kwargs)


def source(*persons, roles=(), committees=(), memberships=None):
    memberships = memberships or tuple(Membership(p.person_id, "Definitief", "Bondslid", plays_football=True)
                                       for p in persons)
    return RealDataImportResult(tuple(persons), memberships, (), roles, committees, (), (), (), ())


def outcomes(data, when=TODAY, policy=None):
    return {r.person_id: r for r in data.derive_member_duties(when, policy)}


def codes(result):
    return {g.code for g in result.grounds}


@pytest.mark.parametrize("postcode,number,addition,expected", [
    (" 8000 aa ", "17 ", None, ("8000AA", "17", "")),
    ("8000AA", "17", " A ", ("8000AA", "17", "A")),
    (None, "17", None, None), ("8000 AA", None, None, None),
    (" ", "17", None, None), ("8000AA", " ", None, None),
])
def test_canonical_address(postcode, number, addition, expected):
    p = Person("P", "Lid", postal_code=postcode, house_number=number, house_number_addition=addition)
    assert canonical_address(p) == expected


def test_free_address_and_conflicting_address_do_not_prove_household():
    assert canonical_address(Person("P", "Lid", address="8000 AA 17")) is None
    assert canonical_address(replace(person("P"), address_conflicting=True)) is None


@pytest.mark.parametrize("left,right,match", [
    (("Ouder A", "Ouder B"), ("Ouder B", "Ouder A"), True),
    (("Ouder A", None), (None, "Ouder A"), True),
    (("Ouder A", None), ("Ouder A", "Ouder B"), False),
    (("Ouder A", "Ouder B"), ("Ouder A", "Ouder C"), False),
    ((None, None), (None, None), False),
    (("Anna Gelijk", None), ("Ben Gelijk", None), False),
])
def test_complete_parent_registration(left, right, match):
    a = person("A", parent_names=left)
    b = replace(person("B", parent_names=right), house_number="18")
    assert ("parents" in family_criteria(a, b)) is match


def test_address_is_independent_and_addition_distinguishes():
    a, b = person("A"), person("B", parent_names=("Ouder", None))
    assert family_criteria(a, b) == ("address",)
    assert family_criteria(a, replace(b, house_number_addition="A")) == ()


@pytest.mark.parametrize("role", ["Hoofdtrainer Sen.", "Verzorger", "Erelid", "Lid van verdienste"])
def test_paid_functions_and_titles_only_exempt_self(role):
    data = source(person("A"), person("B"), roles=(RoleAssignment("A", role),))
    r = outcomes(data)
    assert r["A"].expected_required_hours == 0
    assert "personal_function" in codes(r["A"])
    assert r["B"].expected_required_hours == 10


def test_household_function_has_separate_supporting_ground():
    data = source(person("A"), person("B"), roles=(approved_volunteer("A"), approved_volunteer("B")))
    r = outcomes(data)
    assert {"personal_function", "household_function"} <= codes(r["B"])
    assert all(g.registrations for g in r["B"].grounds if "function" in g.code)
    b = replace(person("B"), house_number_addition="A")
    assert outcomes(source(person("A"), b, roles=(approved_volunteer("A"),)))["B"].expected_required_hours == 10


def approved_volunteer(pid):
    from dvk.function_classification import FunctionClassifier
    rule = next(r for r in FunctionClassifier().rules.values() if r.dataset == "functies" and r.rights.household_exempt)
    return RoleAssignment(pid, rule.title)


@pytest.mark.parametrize("missing_holder", [False, True])
def test_missing_household_address_is_unknown_not_ten_hours(missing_holder):
    a, b = person("A"), person("B")
    if missing_holder:
        a = replace(a, postal_code=None)
    else:
        b = replace(b, house_number=None)
    r = outcomes(source(a, b, roles=(approved_volunteer("A"),)))["B"]
    assert r.status == "niet betrouwbaar beoordeelbaar"
    assert r.expected_required_hours is None
    assert "household_address_insufficient" in codes(r)


def test_oldest_and_eighteenth_birthday_are_recomputed_without_rewriting():
    a = person("A", date(2008, 10, 7))
    b = person("B", date(2012, 1, 1))
    data = source(a, b)
    previous = outcomes(data)
    assert previous["A"].expected_required_hours == 10
    assert previous["B"].expected_required_hours == 0
    assert "younger_minor" in codes(previous["B"])
    next_day = outcomes(data, date(2026, 10, 7))
    assert next_day["A"].expected_required_hours == next_day["B"].expected_required_hours == 10
    assert previous["B"].expected_required_hours == 0


def test_membership_end_moves_family_duty_on_exact_date():
    a, b = person("A", date(2010, 1, 1)), person("B", date(2012, 1, 1))
    data = source(a, b, memberships=(Membership("A", "Afgemeld", "Bondslid", end_date=TODAY, plays_football=True),
                                    Membership("B", "Definitief", "Bondslid", plays_football=True)))
    assert outcomes(data, date(2026, 10, 5))["B"].expected_required_hours == 0
    assert outcomes(data)["B"].expected_required_hours == 10


def test_oldest_function_exempts_household_instead_of_shifting_duty():
    a, b = person("A", date(2010, 1, 1)), person("B", date(2012, 1, 1))
    r = outcomes(source(a, b, roles=(approved_volunteer("A"),)))
    assert r["A"].expected_required_hours == r["B"].expected_required_hours == 0
    assert {"household_function", "younger_minor"} <= codes(r["B"])


def test_nontransitive_pair_comparison():
    a = person("A", date(2010, 1, 1), parent_names=("Ouder A", None))
    b = person("B", date(2012, 1, 1), parent_names=("Ouder A", None))
    c = replace(person("C", date(2014, 1, 1), parent_names=("Ouder C", None)), house_number="18")
    b = replace(b, house_number="18")
    assert family_criteria(a, b) == ("parents",)
    assert family_criteria(b, c) == ("address",)
    assert family_criteria(a, c) == ()
    r = outcomes(source(a, b, c))
    ground = next(g for g in r["C"].grounds if g.code == "younger_minor")
    assert ground.supporting_person_id == "B"


def test_missing_parents_do_not_create_persons_and_address_can_match():
    a, b = person("A", date(2010, 1, 1)), person("B", date(2012, 1, 1), contact_via_parent=True)
    assert outcomes(source(a, b))["B"].expected_required_hours == 0
    b = replace(b, postal_code=None)
    r = outcomes(source(b))["B"]
    assert r.expected_required_hours is None
    assert "family_data_insufficient" in codes(r)


def test_policy_hours_remain_configuration():
    r = outcomes(source(person("A")), policy=DutyPolicy(12, "test-season"))["A"]
    assert r.expected_required_hours == 12
    assert r.policy_version == "test-season"


def test_function_and_committee_peildatum():
    from dvk.function_classification import FunctionClassifier
    rule = next(r for r in FunctionClassifier().rules.values() if r.dataset == "commissies" and r.rights.household_exempt)
    fact = CommitteeMembership("A", rule.committee, rule.title, start_date=date(2026, 10, 7))
    data = source(person("A"), person("B"), committees=(fact,))
    assert outcomes(data)["B"].expected_required_hours == 10
    assert outcomes(data, date(2026, 10, 7))["B"].expected_required_hours == 0
    data = replace(data, committees=(), roles=(replace(approved_volunteer("A"), end_date=date(2026, 10, 5)),))
    assert outcomes(data)["B"].expected_required_hours == 10


def test_missing_birth_date_and_unknown_function_are_explicit():
    assert outcomes(source(person("A", None)))["A"].expected_required_hours is None
    r = outcomes(source(person("A"), roles=(RoleAssignment("A", "Onbekend"),)))["A"]
    assert "function_classification_unknown" in codes(r)
    assert r.expected_required_hours is None


def write_export(tmp_path, name, rows, fields):
    path = tmp_path / name
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.mark.parametrize("conflict", [None, "Huisnummer", "Naam ouder/verzorger 2"])
def test_actual_member_headers_provenance_duplicates_and_no_hours_export(tmp_path, conflict):
    row = {"Rel. code": "M1", "Naam": "Synthetisch lid", "Geb.dat.": "01-01-2012",
           "Lidstatus": "Definitief", "Lidsoort": "Bondslid", "Status lidmaatschap": "",
           "Straatnaam": "Teststraat", "Huisnummer": "17", "Toevoeging": " A ", "Postcode": "8000 aa",
           "Plaats": "Testplaats", "Contact via ouder/verzorger": "Ja",
           "Naam ouder/verzorger 1": "Ouder A", "Naam ouder/verzorger 2": "Ouder B"}
    rows = [row]
    if conflict:
        rows.append({**row, conflict: "Afwijkend"})
    adapter = SportlinkRealDataAdapter()
    members = write_export(tmp_path, "members.csv", rows, list(row))
    others = {k: write_export(tmp_path, k + ".csv", [], sorted(adapter.REQUIRED_COLUMNS[k]))
              for k in ("functies", "commissies", "teams")}
    data = adapter.load_exports(members_path=members, functions_path=others["functies"],
                                committees_path=others["commissies"], teams_path=others["teams"], duty_path=None)
    p, = data.persons
    assert p.parent_names == ("Ouder A", "Ouder B")
    assert p.contact_via_parent is True
    assert p.street_name == "Teststraat" and p.city == "Testplaats"
    assert len(data.persons) == 1 and not data.duty_records
    assert p.address_conflicting is (conflict == "Huisnummer")
    assert p.parent_data_conflicting is (conflict == "Naam ouder/verzorger 2")
    assert any(p.source_field == "Toevoeging" and p.source_value == " A " for p in data.provenance)
    assert {p.source_field for p in data.provenance} >= set(row) - {"Rel. code", "Naam", "Lidstatus", "Lidsoort", "Status lidmaatschap"}


def test_unknown_membership_of_older_child_cannot_imply_independent_duty():
    a, b = person("A", date(2010, 1, 1)), person("B", date(2012, 1, 1))
    data = source(a, b, memberships=(Membership("A", "Onbekend", "Bondslid", plays_football=True),
                                    Membership("B", "Definitief", "Bondslid", plays_football=True)))
    r = outcomes(data)["B"]
    assert r.expected_required_hours is None
    assert "family_membership_unknown" in codes(r)


def test_equal_birth_dates_use_b10_uncertainty_without_selecting_a_child():
    r = outcomes(source(person("A", date(2010, 1, 1)), person("B", date(2010, 1, 1))))
    assert all(item.expected_required_hours is None for item in r.values())
    assert all("oldest_minor_undetermined" in codes(item) for item in r.values())


def test_conflicting_parent_data_cannot_prove_parent_match_but_address_still_can():
    a = person("A", date(2010, 1, 1), parent_names=("Ouder A", None))
    b = person("B", date(2012, 1, 1), parent_names=("Ouder A", None), parent_data_conflicting=True)
    assert family_criteria(a, b) == ("address",)
    assert outcomes(source(a, b))["B"].expected_required_hours == 0
    b = replace(b, house_number="18")
    assert outcomes(source(a, b))["B"].expected_required_hours is None


def test_unknown_household_function_and_separate_source_facts():
    a, b = person("A"), person("B")
    r = outcomes(source(a, b, roles=(RoleAssignment("A", "Onbekend"),)))["B"]
    assert r.expected_required_hours is None
    assert "household_function_classification_unknown" in codes(r)
    assert a in r.source_facts and b in r.source_facts
    assert r.kind == "DERIVED"


def test_different_full_addresses_and_parent_registrations_prove_no_family_match():
    a = person("A", date(2010, 1, 1), parent_names=("Ouder A", "Ouder B"))
    b = replace(person("B", date(2012, 1, 1), parent_names=("Ouder A", "Ouder C")), house_number="18")
    assert outcomes(source(a, b))["B"].expected_required_hours == 10


def test_nonplaying_older_child_does_not_take_family_duty():
    a, b = person("A", date(2010, 1, 1)), person("B", date(2012, 1, 1))
    data = source(a, b, memberships=(Membership("A", "Definitief", "Bondslid", plays_football=False),
                                    Membership("B", "Definitief", "Bondslid", plays_football=True)))
    assert outcomes(data)["B"].expected_required_hours == 10


@pytest.mark.parametrize("status,end_date,expected", [("Afgemeld", TODAY, 10), ("Onbekend", None, None)])
def test_household_function_requires_current_member(status, end_date, expected):
    a, b = person("A"), person("B")
    data = source(a, b, roles=(approved_volunteer("A"),),
                  memberships=(Membership("A", status, "Bondslid", end_date=end_date),
                               Membership("B", "Definitief", "Bondslid", plays_football=True)))
    assert outcomes(data)["B"].expected_required_hours == expected


def test_import_to_round2_with_actual_headers_and_teams(tmp_path):
    adapter = SportlinkRealDataAdapter()
    member_fields = ["Rel. code", "Naam", "Geb.dat.", "Lidstatus", "Lidsoort", "Status lidmaatschap",
                     "Straatnaam", "Huisnummer", "Toevoeging", "Postcode", "Plaats",
                     "Contact via ouder/verzorger", "Naam ouder/verzorger 1", "Naam ouder/verzorger 2"]
    base = {f: "" for f in member_fields}
    base.update({"Lidstatus": "Definitief", "Lidsoort": "Bondslid", "Postcode": "8000 aa",
                 "Huisnummer": "17", "Contact via ouder/verzorger": "Ja"})
    rows = [{**base, "Rel. code": "A", "Naam": "Oudste", "Geb.dat.": "01-01-2010"},
            {**base, "Rel. code": "B", "Naam": "Jongste", "Geb.dat.": "01-01-2012"}]
    members = write_export(tmp_path, "members.csv", rows, member_fields)
    functions = write_export(tmp_path, "functions.csv", [{"Rel. code": "A", "Functie": approved_volunteer("A").role}],
                             sorted(adapter.REQUIRED_COLUMNS["functies"]))
    committees = write_export(tmp_path, "committees.csv", [], sorted(adapter.REQUIRED_COLUMNS["commissies"]))
    team_rows = [{"Rel. code": pid, "Team": "JO17", "Teamrol": "Teamspeler", "Functie": "",
                  "Spelend lid": "Ja", "Teamsoort": "Bond"} for pid in ("A", "B")]
    teams = write_export(tmp_path, "teams.csv", team_rows, list(team_rows[0]))
    data = adapter.load_exports(members_path=members, functions_path=functions, committees_path=committees,
                                teams_path=teams, duty_path=None)
    r = outcomes(data)
    assert {"household_function", "younger_minor"} <= codes(r["B"])
    assert r["B"].expected_required_hours == 0
    assert any(getattr(f, "source_field", None) == "Huisnummer" for f in r["B"].source_facts)
    ground = next(g for g in r["B"].grounds if g.code == "household_function")
    assert ground.registrations[0].source.provenance.kind == "SOURCE_FACT"
    assert len(data.persons) == 2
    assert data.duty_records == ()
