from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from itertools import permutations

import pytest

from dvk.candidate_selection import assess_candidate
from dvk.programma_team_adapter import CkcProgrammaAdapter, UnresolvedProgramTeamsError
from dvk.real_data_import import RealTeamMembership, SportlinkRealDataAdapter
from dvk.team_linking import CkcTeamIdentity, link_program_team
from dvk.workstream_model import DutyService
from dvk.workstream_cases import W_CASE_BY_ID
from test_real_data_import_v04 import exports, write_csv


def team(name, matchday=None, person="SYNTHETIC-P1"):
    return RealTeamMembership(person, name, "Teamspeler", True, "Bond", matchday)


def row(name="CKC O17-1", **overrides):
    result = {
        "wedstrijdcode": "SYNTHETIC-W1", "wedstrijddatum": "2026-11-01T12:30:00Z",
        "thuisteamclubrelatiecode": "BBDZ08H", "uitteamclubrelatiecode": "OTHER",
        "thuisteam": name, "uitteam": "Andere vereniging O17-1",
        "thuisteamid": "COMPETITION-A", "uitteamid": "OTHER-ID",
        "competitiesoort": "regulier", "competitie": "", "status": "Te spelen",
    }
    result.update(overrides)
    return result


def adapter(*teams):
    return CkcProgrammaAdapter(team_memberships=teams or [team("O17-1")])


@pytest.mark.parametrize("source_id", ["COMPETITION-A", "COMPETITION-B", "-1", ""])
@pytest.mark.parametrize("kind", ["regulier", "beker", "Rijnmond Cup"])
def test_competition_ids_never_determine_shared_identity(source_id, kind):
    result = adapter().import_rows([row(thuisteamid=source_id, competitiesoort=kind)])
    assert result.matches[0].team_id == result.team_memberships[0].team_id == "O17-1"
    assert result.links[0].source_team_id == source_id


@pytest.mark.parametrize("home,away", [("OTHER", "OTHER"), ("BBDZ08H", "BBDZ08H"), ("", "OTHER")])
def test_only_club_code_may_identify_ckc_and_prefix_is_not_processed_before_it(home, away):
    result = adapter().import_rows([row(thuisteamclubrelatiecode=home, uitteamclubrelatiecode=away)])
    assert result.links[0].normalized_name is None
    assert result.links[0].original_team_name is None
    assert not result.links[0].normalizations
    assert result.links[0].home_team_name == "CKC O17-1"
    assert result.signals[0].code == "PROGRAM_TEAM_UNMATCHED"
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.matches
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.team_memberships


def test_ckc_away_side_and_original_values_are_preserved_without_mutating_input():
    source = row("CKC Verkeerd", thuisteamclubrelatiecode="OTHER", uitteamclubrelatiecode="BBDZ08H",
                 uitteam=" CKC O17-1 ", uitteamid="COMPETITION-C")
    original = deepcopy(source)
    result = adapter().import_rows([source])
    assert source == original
    assert result.matches[0].home_away == "AWAY"
    link = result.links[0]
    assert link.original_team_name == " CKC O17-1 "
    assert link.normalized_name == "O17-1"
    assert link.normalizations == ("trim_outer_whitespace", "remove_CKC_prefix")
    assert result.program.records[0].away_team_name == "CKC O17-1"


CUP_EXAMPLES = [
    ("CKC JO O13", "O13-1"), ("CKC MO17", "MO17-1"), ("CKC O10", "O10-1"),
    ("CKC O14", "O14-1"), ("CKC O23", "O23-1"), ("CKC O17-1", "O17-1"),
]


@pytest.mark.parametrize("kind", ["Rijnmond Cup", "Rijnmondcup"])
@pytest.mark.parametrize("source,target", CUP_EXAMPLES)
def test_six_approved_cup_names_link_to_existing_export_teams_only(source, target, kind):
    result = adapter(team(target)).import_rows([row(source, competitiesoort=kind, thuisteamid="-1")])
    assert result.matches[0].team_id == target
    assert result.links[0].original_team_name == source
    assert result.links[0].competition_type == kind
    assert result.links[0].identity.name == target
    assert ("Rijnmond_add_team_number_1" in result.links[0].normalizations) == (source != "CKC O17-1")


def test_existing_team_number_is_kept():
    result = adapter(team("O13-2")).import_rows([row("CKC O13-2", competitiesoort="Rijnmond Cup")])
    assert result.matches[0].team_id == "O13-2"
    assert result.links[0].normalizations == ("remove_CKC_prefix",)


@pytest.mark.parametrize("name,kind", [
    ("CKC O13", "regulier"), ("CKC JO O13", "beker"),
    ("CKC JO13", "Rijnmond Cup"), ("ckc O13-1", "regulier"),
    ("CKC o13-1", "regulier"), ("CKC O13", "Andere cup"),
])
def test_no_fuzzy_or_unapproved_conversions(name, kind):
    result = adapter(team("O13-1")).import_rows([row(name, competitiesoort=kind)])
    assert result.links[0].status == "unmatched"
    assert any(s.code == "PROGRAM_TEAM_UNMATCHED" for s in result.signals)
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.matches


def test_missing_target_cannot_invent_cup_team_or_publish_partial_planning_context():
    result = adapter().import_rows([row(), row("CKC O99", wedstrijdcode="SYNTHETIC-W2", competitiesoort="Rijnmond Cup")])
    assert [link.status for link in result.links] == ["matched", "unmatched"]
    assert result.links[1].normalized_name == "O99-1"
    assert len(result.program.records) == 1  # audit of the successfully parsed row remains accessible
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.matches


def test_fifteen_team_2_matches_use_competition_description_not_calendar_day():
    sat, sun = team("2", "Algemeen/Zaterdag"), team("2", "Algemeen/Zondag", "SYNTHETIC-P2")
    # Synthetic fixtures: 8 Saturday competition, 6 Sunday competition, 1 Sunday cup.
    descriptions = ["0213 Mannen Zaterdag reserve (A-cat)"] * 8 + ["0519 Mannen Zondag reserve"] * 6 + ["B1620 Mannen beker reserve zondag 2e ronde"]
    rows = [row("CKC 2", wedstrijdcode=f"SYNTHETIC-2-{i}", competitie=description,
                competitiesoort="beker" if i == 14 else "regulier", thuisteamid=f"COMP-{i}",
                wedstrijddatum="2026-11-01T12:30:00Z" if i < 8 else "2026-10-31T12:30:00Z")
            for i, description in enumerate(descriptions)]
    result = adapter(sat, sun).import_rows(rows)
    assert len(result.matches) == 15
    assert [m.team_id for m in result.matches] == ["2 / Algemeen/Zaterdag"] * 8 + ["2 / Algemeen/Zondag"] * 7
    assert {m.team_id for m in result.matches} == {m.team_id for m in result.team_memberships}
    assert [link.competition for link in result.links] == descriptions


@pytest.mark.parametrize("description", ["", "Reserve", "Zaterdag en zondag"])
def test_team_2_missing_or_ambiguous_competition_is_explicit_and_not_first_match(description):
    result = adapter(team("2", "Algemeen/Zaterdag"), team("2", "Algemeen/Zondag")).import_rows([
        row("CKC 2", competitie=description),
    ])
    assert result.links[0].status == "ambiguous"
    assert result.signals[0].code == "PROGRAM_TEAM_AMBIGUOUS"
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.matches


def test_team_2_requires_matching_export_matchday_even_if_only_one_team_is_available():
    result = adapter(team("2", "Algemeen/Zaterdag")).import_rows([row("CKC 2", competitie="Mannen zondag")])
    assert result.links[0].status == "unmatched"
    result = adapter(team("2")).import_rows([])
    assert result.signals[0].code == "CKC_TEAM_MEMBERSHIP_UNRESOLVED"
    with pytest.raises(UnresolvedProgramTeamsError):
        _ = result.team_memberships


def test_other_names_do_not_require_matchday_and_duplicate_member_rows_are_one_candidate():
    source = team("O17-1", "niet relevant")
    result = adapter(source, source, team("O17-1", "Algemeen/Zondag", "SYNTHETIC-P2")).import_rows([row()])
    assert result.matches[0].team_id == "O17-1"
    assert len(result.links[0].candidates) == 1
    assert len(result.team_memberships) == 3  # no change to multiple-membership policy


def test_all_team_and_match_permutations_have_same_links():
    teams = [team("O13-1"), team("2", "Algemeen/Zaterdag"), team("2", "Algemeen/Zondag")]
    rows = [row("CKC JO O13", competitiesoort="Rijnmondcup"),
            row("CKC 2", competitie="Mannen zaterdag", wedstrijdcode="SYNTHETIC-SAT"),
            row("CKC 2", competitie="Mannen zondag", wedstrijdcode="SYNTHETIC-SUN")]
    expected = None
    for ordered_teams in permutations(teams):
        for ordered_rows in permutations(rows):
            result = adapter(*ordered_teams).import_rows(iter(ordered_rows))
            actual = {link.record_key: link for link in result.links}
            if expected is None:
                expected = actual
            assert actual == expected


def test_unknown_team_results_are_order_independent_too():
    catalog = [CkcTeamIdentity("2", "Algemeen/Zaterdag"), CkcTeamIdentity("2", "Algemeen/Zondag")]
    for ordered in permutations(catalog):
        link = link_program_team(row("CKC 2"), ordered, record_key="synthetic")
        assert link.status == "ambiguous"
        assert link.candidates == tuple(sorted(catalog))


def test_import_preserves_original_csv_name_and_matchday_without_changing_old_team_id(tmp_path):
    paths = exports(tmp_path)
    paths['teams_path'] = write_csv(tmp_path, "teams.csv",
        ["Rel. code", "Team", "Speeldag", "Teamsoort", "Teamrol", "Spelend lid"],
        [["P1", " 2 ", "Algemeen/Zondag", "Bond", "Teamspeler", "Ja"]])
    source = SportlinkRealDataAdapter().load_exports(**paths)
    membership, = source.team_memberships
    assert membership.team_id == "2"  # retained source name, never a competition ID
    assert membership.source_team_name == " 2 "
    assert membership.matchday == "Algemeen/Zondag"
    result = adapter(membership).import_rows([row("CKC 2", competitie="Mannen zondag")])
    assert result.team_memberships[0].team_id == result.matches[0].team_id == "2 / Algemeen/Zondag"


def test_existing_status_time_and_audit_semantics_remain_available():
    result = adapter().import_rows([row(status="Afgelast")], retrieved_at=datetime(2026, 10, 24))
    assert not result.matches
    assert result.program.excluded_records[0].source_status == "Afgelast"
    assert result.program.records[0].match.starts_at.isoformat() == "2026-11-01T13:30:00+01:00"
    assert result.program.provenance[0].source_value == "Afgelast"


def test_resolved_identity_reaches_existing_candidate_selection_without_rule_changes():
    case = W_CASE_BY_ID["W08"]
    result = adapter(team("O17-1", person=case.person.person_id)).import_rows([
        row(thuisteamclubrelatiecode="OTHER", uitteamclubrelatiecode="BBDZ08H",
            uitteam="CKC O17-1", uitteamid="DIFFERENT-COMPETITION-ID")])
    service = DutyService("SYNTHETIC-SERVICE", "bar", result.matches[0].starts_at,
                          result.matches[0].starts_at.replace(hour=15), "synthetic", 1)
    assessed = assess_candidate(case, service, result.team_memberships, result.matches, date(2026, 11, 1))
    assert not assessed.eligible
    assert assessed.match_relation == "away_match_overlaps_service"


@pytest.mark.parametrize("name,matchday,competition,exit_code", [
    ("O17-1", "", "", 0),
    ("2", "Algemeen/Zaterdag", "Mannen zaterdag", 0),
    ("2", "Algemeen/Zaterdag", "", 2),
    ("2", "", "Mannen zaterdag", 2),
])
def test_local_validation_command_is_read_only_and_prints_no_personal_values(
    tmp_path, monkeypatch, capsys, name, matchday, competition, exit_code,
):
    from types import SimpleNamespace
    import run_programma_team_validation as command
    path = write_csv(tmp_path, "synthetic-teams.csv",
        ["Rel. code", "Team", "Speeldag", "Teamrol", "Spelend lid", "Naam"],
        [["PRIVATE-SYNTHETIC-ID", name, matchday, "Teamspeler", "Ja", "Fictieve Persoon"]])
    original = path.read_bytes()
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "SYNTHETIC-SECRET")
    monkeypatch.setattr(command, "SportlinkProgrammaClient", lambda adapter: SimpleNamespace(
        fetch_rows=lambda **kwargs: SimpleNamespace(rows=[row("CKC " + name, competitie=competition)])))
    assert command.main(["--teams", str(path)]) == exit_code
    output = capsys.readouterr().out
    assert "PRIVATE-SYNTHETIC-ID" not in output
    assert "Fictieve Persoon" not in output
    assert "SYNTHETIC-SECRET" not in output
    assert path.read_bytes() == original


def test_transport_error_does_not_print_credentials(tmp_path, monkeypatch, capsys):
    import run_programma_team_validation as command
    from dvk.programma_client import ProgrammaFetchError
    path = write_csv(tmp_path, "synthetic-teams.csv", ["Rel. code", "Team", "Teamrol", "Spelend lid"],
                     [["SYNTHETIC-P1", "O17-1", "Teamspeler", "Ja"]])
    monkeypatch.setenv("SPORTLINK_CLIENT_ID", "SYNTHETIC-SECRET")
    def fail(**kwargs):
        raise ProgrammaFetchError("request?client_id=SYNTHETIC-SECRET")
    monkeypatch.setattr(command.SportlinkProgrammaClient, "fetch_rows", lambda self, **kwargs: fail())
    assert command.main(["--teams", str(path)]) == 1
    assert "SYNTHETIC-SECRET" not in capsys.readouterr().out
