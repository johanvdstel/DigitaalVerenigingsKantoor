from __future__ import annotations

from datetime import datetime

import pytest

from dvk.real_data_import import SportlinkRealDataAdapter


def write_csv(tmp_path, name, header, rows):
    path = tmp_path / name
    lines = [";".join(header)] + [";".join(row) for row in rows]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def exports(tmp_path, member_rows=None, duty_rows=None):
    member_rows = member_rows or [["P1", "Jan Smit", "01-01-2000", "Definitief", "Verenigingslid", "spelend lid", "Veld - Algemeen", "extra"]]
    duty_rows = duty_rows or [["P1", "10", "0", "2", "3", "5"]]
    return dict(
        members_path=write_csv(tmp_path, "leden.csv",
            ["Rel. code", "Naam", "Geboortedatum", "Lidstatus", "Lidsoort", "Status lidmaatschap", "Spelactiviteiten (bond)", "Extra kolom"], member_rows),
        functions_path=write_csv(tmp_path, "functies.csv", ["Rel. code", "Functie"], [["P1", "Trainer Pupillen"], ["P1", "Vice-voorzitter"]]),
        committees_path=write_csv(tmp_path, "commissies.csv", ["Rel. code", "Commissie", "Functie"], [["P1", "Jeugdcommissie", "commissielid"]]),
        duty_path=write_csv(tmp_path, "duty.csv", ["Relatiecode", "Verplichte punten", "Gecorrigeerde punten", "Voldaan", "Nog ingedeeld", "Niet ingedeeld"], duty_rows),
        teams_path=write_csv(tmp_path, "teams.csv", ["Rel. code", "Team", "Teamrol", "Functie", "Spelend lid"], [["P1", "Senioren 8", "Teamspeler", "Aanvaller", "Ja"]]),
    )


def load(tmp_path, **kwargs):
    paths = exports(tmp_path, **kwargs)
    return SportlinkRealDataAdapter().load_exports(**paths, imported_at=datetime(2026, 9, 11, 20, 0), source_period="2026-2027")


def test_r01_imports_one_canonical_person_per_relation_code(tmp_path):
    result = load(tmp_path)
    assert [p.person_id for p in result.persons] == ["P1"]
    assert result.memberships[0].plays_football is True


def test_r02_duplicate_relation_code_is_consolidated_and_signalled(tmp_path):
    rows = [
        ["MGCD323", "Mes, N.J.E.F.", "24-01-2001", "Afgemeld", "Oud bondslid", "oud lid", "", "x"],
        ["MGCD323", "Mes, N.J.E.F.", "24-01-2001", "Afgemeld", "Oud relatie", "oud lid", "", "x"],
    ]
    paths = exports(tmp_path, member_rows=rows)
    for key in ("functions_path", "committees_path", "duty_path", "teams_path"):
        path = paths[key]
        text = path.read_text().replace("P1", "MGCD323")
        path.write_text(text)
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert len(result.persons) == 1
    assert any(s.code == "DUPLICATE_PERSON_SOURCE_RECORD" for s in result.signals)


def test_r03_unknown_extra_columns_are_tolerated(tmp_path):
    assert len(load(tmp_path).persons) == 1


def test_r04_missing_required_column_fails_explicitly(tmp_path):
    paths = exports(tmp_path)
    paths["members_path"].write_text("Rel. code;Naam\nP1;Jan Smit", encoding="utf-8")
    with pytest.raises(ValueError, match="missing columns"):
        SportlinkRealDataAdapter().load_exports(**paths)


def test_r05_preserves_multi_relation_cardinalities(tmp_path):
    result = load(tmp_path)
    assert len(result.roles) == 2
    assert len(result.committees) == 1
    assert len(result.team_memberships) == 1


def test_r06_role_variants_are_normalized_without_policy_decision(tmp_path):
    result = load(tmp_path)
    assert {r.role for r in result.roles} == {"Trainer", "Vice voorzitter"}


def test_r07_abcd_e_is_reconciled(tmp_path):
    record = load(tmp_path).duty_records[0]
    assert (record.position.A, record.position.B, record.position.C, record.position.D, record.position.E) == (10, 0, 2, 3, 5)
    assert record.source_formula_matches


def test_r08_negative_e_is_retained(tmp_path):
    result = load(tmp_path, duty_rows=[["P1", "10", "0", "8", "5", "-3"]])
    assert result.duty_records[0].position.E == -3
    assert not any(s.code == "DUTY_REMAINING_MISMATCH" for s in result.signals)


def test_r09_expected_a_mismatch_is_signalled_not_corrected(tmp_path):
    paths = exports(tmp_path)
    result = SportlinkRealDataAdapter().load_exports(**paths, expected_required_hours={"P1": 0})
    record = result.duty_records[0]
    assert record.registration.required_hours == 10
    assert record.expected_required_hours == 0
    assert any(s.code == "REQUIRED_HOURS_MISMATCH" for s in result.signals)


def test_conflicting_duplicate_identity_is_blocked(tmp_path):
    rows = [
        ["P1", "Jan Smit", "01-01-2000", "Definitief", "Lid", "spelend lid", "Veld - Algemeen", "x"],
        ["P1", "Piet Smit", "01-01-2000", "Definitief", "Lid", "spelend lid", "Veld - Algemeen", "x"],
    ]
    result = load(tmp_path, member_rows=rows)
    assert not result.persons
    assert any(s.code == "CONFLICTING_DUPLICATE_IDENTITY" for s in result.signals)
