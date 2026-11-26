from __future__ import annotations

from datetime import date, datetime

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
        teams_path=write_csv(tmp_path, "teams.csv", ["Rel. code", "Team", "Teamsoort", "Teamrol", "Spelend lid"], [["P1", "Senioren 8", "Bond", "Teamspeler", "Ja"]]),
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
    assert {r.role for r in result.roles} == {"Trainer Pupillen", "Vice-voorzitter"}


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
    result = SportlinkRealDataAdapter().load_exports(**paths)
    record = result.duty_records[0]
    assert record.registration.required_hours == 10
    control, = result.compare_required_hours(date(2026, 10, 6))
    assert control.expected_required_hours == 0
    assert control.registered_required_hours == 10
    assert control.status == "afwijking"
    assert any(s.code == "REQUIRED_HOURS_REASSESSMENT" for s in control.signals)
    assert not any(s.code == "REQUIRED_HOURS_MISMATCH" for s in result.signals)


def test_conflicting_duplicate_identity_is_blocked(tmp_path):
    rows = [
        ["P1", "Jan Smit", "01-01-2000", "Definitief", "Lid", "spelend lid", "Veld - Algemeen", "x"],
        ["P1", "Piet Smit", "01-01-2000", "Definitief", "Lid", "spelend lid", "Veld - Algemeen", "x"],
    ]
    result = load(tmp_path, member_rows=rows)
    assert not result.persons
    assert any(s.code == "CONFLICTING_DUPLICATE_IDENTITY" for s in result.signals)


def test_blank_duty_value_is_not_silently_zero(tmp_path):
    result = load(tmp_path, duty_rows=[["P1", "10", "0", "", "3", "7"]])
    assert not result.duty_records
    assert any(s.code == "INVALID_DUTY_VALUE" and "Voldaan" in s.message for s in result.signals)


def test_non_numeric_duty_value_is_explicit_data_quality_error(tmp_path):
    result = load(tmp_path, duty_rows=[["P1", "10", "0", "twee", "3", "5"]])
    assert not result.duty_records
    assert any(s.code == "INVALID_DUTY_VALUE" for s in result.signals)


def test_unknown_playing_member_value_is_signalled(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text(
        "Rel. code;Team;Teamrol;Spelend lid\nP1;Senioren 8;Teamspeler;Onbekend",
        encoding="utf-8",
    )
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert result.team_memberships[0].playing_member is None
    assert any(s.code == "UNKNOWN_PLAYING_MEMBER_VALUE" for s in result.signals)


def test_role_provenance_keeps_source_and_normalized_value(tmp_path):
    result = load(tmp_path)
    trainer_provenance = next(
        p for p in result.provenance
        if p.source_dataset == "functies" and p.source_value == "Trainer Pupillen"
    )
    assert trainer_provenance.source_field == "Functie"
    assert trainer_provenance.normalized_value == "Trainer Pupillen"


def test_v02_real_birth_date_column_and_conflicting_termination_dates(tmp_path):
    paths = exports(tmp_path)
    member = paths["members_path"]
    member.write_text("Rel. code;Naam;Geb.dat.;Lidstatus;Lidsoort;Status lidmaatschap;Afmelddatum\nP1;Jan Smit;01-01-2000;Definitief;Verenigingslid;spelend lid;\nP1;Jan Smit;01-01-2000;Definitief;Verenigingslid;spelend lid;01-12-2026", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert not result.persons
    assert any(signal.code == "CONFLICTING_DUPLICATE_MEMBERSHIP" for signal in result.signals)


def test_v03_distinct_trainer_roles_are_preserved(tmp_path):
    paths = exports(tmp_path)
    paths["functions_path"].write_text("Rel. code;Functie\nP1;Trainer Pupillen\nP1;Hoofdtrainer Sen.", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert {role.role for role in result.roles} == {"Trainer Pupillen", "Hoofdtrainer Sen."}


def test_v01_bond_conditions_must_match_same_team_row(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text("Rel. code;Team;Teamsoort;Teamrol;Spelend lid\nP1;Recreatief;Recreatief;Teamspeler;Ja\nP1;Senioren;Bond;Trainer;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert not result.memberships[0].plays_football
    assert not result.football_participations[0].plays_football


def test_v01_additional_trainer_role_does_not_cancel_bond_player(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text("Rel. code;Team;Teamsoort;Teamrol;Spelend lid\nP1;Senioren;Bond;Trainer;Ja\nP1;Senioren;Bond;Teamspeler;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert result.memberships[0].plays_football
    assert len(result.team_memberships) == 2


def test_v01_missing_team_type_is_signalled_not_assumed(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text("Rel. code;Team;Teamrol;Spelend lid\nP1;Senioren;Teamspeler;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert not result.memberships[0].plays_football
    assert any(s.code == "MISSING_TEAM_TYPE" for s in result.signals)


def test_v03_committee_start_date_is_preserved(tmp_path):
    paths = exports(tmp_path)
    paths["committees_path"].write_text("Rel. code;Commissie;Functie;Begindatum\nP1;Jeugdcommissie;Lid;01-09-2026", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert result.committees[0].start_date.isoformat() == "2026-09-01"


def test_v02_membership_end_date_is_first_nonmember_day(tmp_path):
    paths = exports(tmp_path)
    paths["members_path"].write_text("Rel. code;Naam;Geb.dat.;Lidstatus;Lidsoort;Status lidmaatschap;Afmelddatum\nP1;Jan Smit;01-01-2000;Definitief;Verenigingslid;spelend lid;01-12-2026", encoding="utf-8")
    before = SportlinkRealDataAdapter().load_exports(**paths, as_of=date(2026, 11, 30))
    on_day = SportlinkRealDataAdapter().load_exports(**paths, as_of=date(2026, 12, 1))
    assert before.memberships[0].end_date == date(2026, 12, 1)
    assert not any(s.code == "MEMBERSHIP_ENDED_AS_OF" for s in before.signals)
    assert any(s.code == "MEMBERSHIP_ENDED_AS_OF" for s in on_day.signals)


def test_v02_missing_termination_date_is_not_guessed(tmp_path):
    paths = exports(tmp_path)
    paths["members_path"].write_text("Rel. code;Naam;Geb.dat.;Lidstatus;Lidsoort;Status lidmaatschap;Afmelddatum\nP1;Jan Smit;01-01-2000;Afgemeld;Verenigingslid;oud lid;", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert any(s.code == "MISSING_TERMINATION_DATE" for s in result.signals)


def test_v02_per_source_dates_are_retained(tmp_path):
    dates = {"leden": date(2026, 10, 1), "teams": date(2026, 9, 30)}
    result = SportlinkRealDataAdapter().load_exports(**exports(tmp_path), source_dates=dates)
    assert dict(result.source_dates) == dates


def test_v02_actual_team_type_vereniging_is_known_but_not_bond(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text("Rel. code;Team;Teamsoort;Teamrol;Spelend lid\nP1;Lokale selectie;Vereniging;Teamspeler;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert not result.memberships[0].plays_football
    assert not any(s.code == "UNKNOWN_TEAM_TYPE" for s in result.signals)


def test_v02_teams_import_does_not_require_banking_columns(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"].write_text("Rel. code;Team;Teamsoort;Teamrol;Spelend lid\nP1;Senioren 1;Bond;Teamspeler;Ja", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert result.memberships[0].plays_football
    assert not any(signal.dataset == "teams" for signal in result.signals)


def test_v02_derived_membership_respects_first_nonmember_day(tmp_path):
    paths = exports(tmp_path)
    paths["members_path"].write_text("Rel. code;Naam;Geb.dat.;Lidstatus;Lidsoort;Status lidmaatschap;Afmelddatum\nP1;Jan Smit;01-01-2000;Definitief;Verenigingslid;spelend lid;01-12-2026", encoding="utf-8")
    adapter = SportlinkRealDataAdapter()
    assert dict(adapter.load_exports(**paths, as_of=date(2026, 11, 30)).membership_as_of) == {"P1": True}
    assert dict(adapter.load_exports(**paths, as_of=date(2026, 12, 1)).membership_as_of) == {"P1": False}


def test_v02_ambiguous_membership_is_not_assumed_active(tmp_path):
    paths = exports(tmp_path)
    paths["members_path"].write_text("Rel. code;Naam;Geb.dat.;Lidstatus;Lidsoort;Status lidmaatschap;Afmelddatum\nP1;Jan Smit;01-01-2000;Afgemeld;Verenigingslid;oud lid;", encoding="utf-8")
    result = SportlinkRealDataAdapter().load_exports(**paths, as_of=date(2026, 10, 2))
    assert dict(result.membership_as_of) == {"P1": None}


def test_v02_warns_on_source_dates_not_refreshed_since_previous_planning(tmp_path):
    result = SportlinkRealDataAdapter().load_exports(**exports(tmp_path),
        source_dates={"teams": date(2026, 9, 30)}, previous_planning_date=date(2026, 10, 1),
        previous_source_dates={"teams": date(2026, 9, 30)})
    assert {"SOURCE_PREDATES_PREVIOUS_PLANNING", "SOURCE_NOT_REFRESHED"} <= {s.code for s in result.signals}


def test_v05_minimal_teams_export_without_function(tmp_path):
    paths = exports(tmp_path)
    paths["teams_path"] = write_csv(tmp_path, "teams.csv",
        ["Rel. code", "Naam", "Team", "Teamsoort", "Teamrol", "Spelend lid"],
        [["P1", "Jan Smit", "Senioren 8", "Bond", "Teamspeler", "Ja"]])
    result = SportlinkRealDataAdapter().load_exports(**paths)
    team = result.team_memberships[0]
    assert (team.person_id, team.team_id, team.team_type, team.team_role, team.playing_member) == (
        "P1", "Senioren 8", "Bond", "Teamspeler", True)
    assert result.memberships[0].plays_football
    assert result.football_participations[0].plays_football
    assert not any(signal.dataset == "teams" for signal in result.signals)


@pytest.mark.parametrize("column", ["Teamrol", "Spelend lid"])
def test_v05_missing_required_team_column_is_rejected(tmp_path, column):
    paths = exports(tmp_path)
    row = {"Rel. code": "P1", "Team": "Senioren 8", "Teamsoort": "Bond",
           "Teamrol": "Teamspeler", "Spelend lid": "Ja"}
    del row[column]
    paths["teams_path"] = write_csv(tmp_path, "teams.csv", list(row), [list(row.values())])
    with pytest.raises(ValueError, match=f"missing columns: {column}"):
        SportlinkRealDataAdapter().load_exports(**paths)


@pytest.mark.parametrize("value, code", [("", "MISSING_TEAM_TYPE"), ("Onbekend", "UNKNOWN_TEAM_TYPE")])
def test_v05_invalid_team_type_without_function_is_signalled(tmp_path, value, code):
    paths = exports(tmp_path)
    paths["teams_path"] = write_csv(tmp_path, "teams.csv",
        ["Rel. code", "Team", "Teamsoort", "Teamrol", "Spelend lid"],
        [["P1", "Senioren 8", value, "Teamspeler", "Ja"]])
    result = SportlinkRealDataAdapter().load_exports(**paths)
    assert not result.memberships[0].plays_football
    assert any(signal.dataset == "teams" and signal.code == code for signal in result.signals)
