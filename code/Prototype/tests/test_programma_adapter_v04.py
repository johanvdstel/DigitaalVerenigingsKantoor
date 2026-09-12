from __future__ import annotations

from datetime import datetime
from urllib.parse import parse_qs, urlparse

from dvk.programma_adapter import SportlinkProgrammaAdapter


CKC = "BBDZ08H"
OTHER = "OTHER"


def adapter():
    return SportlinkProgrammaAdapter(club_relation_code=CKC)


def row(**overrides):
    data = {
        "wedstrijddatum": "2026-09-12T12:30:00Z",
        "wedstrijdcode": "W-100",
        "wedstrijdnummer": "100",
        "thuisteamclubrelatiecode": CKC,
        "uitteamclubrelatiecode": OTHER,
        "thuisteamid": "TEAM-CKC-8",
        "thuisteam": "CKC Senioren 8",
        "uitteamid": "TEAM-OTHER",
        "uitteam": "Tegenstander 1",
        "status": "Te spelen",
        "accommodatie": "Sportpark 't Veer",
    }
    data.update(overrides)
    return data


def test_r10_programma_url_uses_verified_ckc_selection_parameters():
    url = adapter().build_url(client_id="test-client", days=60, max_rows=500)
    query = parse_qs(urlparse(url).query)
    assert query["eigenwedstrijden"] == ["JA"]
    assert query["thuis"] == ["JA"]
    assert query["uit"] == ["JA"]
    assert query["gebruiklokaleteamgegevens"] == ["NEE"]
    assert query["aantaldagen"] == ["60"]
    assert query["aantalregels"] == ["500"]


def test_r10_maps_home_and_away_ckc_matches_explicitly():
    result = adapter().import_rows([
        row(),
        row(
            wedstrijdcode="W-101",
            wedstrijdnummer="101",
            thuisteamclubrelatiecode=OTHER,
            uitteamclubrelatiecode=CKC,
            thuisteamid="TEAM-OTHER-2",
            thuisteam="Tegenstander 2",
            uitteamid="TEAM-CKC-9",
            uitteam="CKC Senioren 9",
        ),
    ], retrieved_at=datetime(2026, 9, 12, 13, 0))

    assert [(m.match_id, m.team_id, m.home_away) for m in result.matches] == [
        ("W-100", "TEAM-CKC-8", "HOME"),
        ("W-101", "TEAM-CKC-9", "AWAY"),
    ]
    assert result.matches[0].starts_at.isoformat() == "2026-09-12T14:30:00+02:00"


def test_r10_does_not_treat_rooster2_hometeam_label_as_canonical_semantics():
    result = adapter().import_rows([
        row(
            wedstrijdcode="W-102",
            thuisteamclubrelatiecode=OTHER,
            uitteamclubrelatiecode=CKC,
            thuisteam="Andere Club 1",
            uitteamid="TEAM-CKC-JO19",
            uitteam="CKC JO19-1",
        )
    ])
    match = result.matches[0]
    assert match.team_id == "TEAM-CKC-JO19"
    assert match.home_away == "AWAY"


def test_r11_cancelled_match_is_retained_for_audit_but_excluded_from_matches():
    result = adapter().import_rows([row(status="Afgelast")])
    assert not result.matches
    assert len(result.records) == 1
    assert len(result.excluded_records) == 1
    assert result.excluded_records[0].source_status == "Afgelast"
    assert any(s.code == "NON_OPERATIONAL_PROGRAM_MATCH" for s in result.signals)
    assert result.provenance[0].source_value == "Afgelast"
    assert result.provenance[0].normalized_value == "NON_OPERATIONAL"


def test_programma_unresolved_ckc_side_is_not_silently_imported():
    result = adapter().import_rows([
        row(thuisteamclubrelatiecode=OTHER, uitteamclubrelatiecode=OTHER)
    ])
    assert not result.matches
    assert any(s.code == "PROGRAM_MATCH_CLUB_SIDE_UNRESOLVED" for s in result.signals)


def test_programma_missing_team_id_uses_visible_fallback_with_signal():
    result = adapter().import_rows([row(thuisteamid="")])
    assert result.matches[0].team_id == "Senioren 8"
    assert any(s.code == "PROGRAM_MATCH_TEAM_ID_FALLBACK" for s in result.signals)
