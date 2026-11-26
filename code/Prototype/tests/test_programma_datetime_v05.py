from datetime import timezone
import re

import pytest

import dvk.programma_adapter as programma
from dvk.programma_adapter import SportlinkProgrammaAdapter
from dvk.programma_team_adapter import CkcProgrammaAdapter
from dvk.real_data_import import RealTeamMembership


# Synthetic instants, including both occurrences of 02:30 at the DST boundary.
CASES = [
    ("2026-10-24T10:00:00+0200", "2026-10-24T10:00:00+02:00", "2026-10-24T08:00:00+00:00"),
    ("2026-11-24T10:00:00+0100", "2026-11-24T10:00:00+01:00", "2026-11-24T09:00:00+00:00"),
    ("2026-10-24T10:00:00+02:00", "2026-10-24T10:00:00+02:00", "2026-10-24T08:00:00+00:00"),
    ("2026-11-24T10:00:00+01:00", "2026-11-24T10:00:00+01:00", "2026-11-24T09:00:00+00:00"),
    ("2026-10-24T00:15:00+0200", "2026-10-24T00:15:00+02:00", "2026-10-23T22:15:00+00:00"),
    ("2026-11-24T00:15:00+0100", "2026-11-24T00:15:00+01:00", "2026-11-23T23:15:00+00:00"),
    ("2026-10-23T22:30:00Z", "2026-10-24T00:30:00+02:00", "2026-10-23T22:30:00+00:00"),
    ("2026-11-23T23:30:00+00:00", "2026-11-24T00:30:00+01:00", "2026-11-23T23:30:00+00:00"),
    ("2026-10-25T02:30:00+0200", "2026-10-25T02:30:00+02:00", "2026-10-25T00:30:00+00:00"),
    ("2026-10-25T02:30:00+0100", "2026-10-25T02:30:00+01:00", "2026-10-25T01:30:00+00:00"),
]


@pytest.mark.parametrize("source,local,utc", CASES)
def test_timezone_aware_instants_keep_local_date_time_and_utc_instant(source, local, utc):
    parsed = SportlinkProgrammaAdapter(club_relation_code="BBDZ08H")._parse_sportlink_datetime(source)
    assert parsed.isoformat() == local
    assert parsed.astimezone(timezone.utc).isoformat() == utc
    assert parsed.tzinfo.key == "Europe/Amsterdam"


@pytest.mark.parametrize("source,local,utc", CASES)
def test_compact_offsets_also_work_with_pre_311_fromisoformat(monkeypatch, source, local, utc):
    # Python 3.9 rejects compact offsets. Exercise that restriction in newer CI
    # interpreters as well, so a removed compatibility fix cannot pass unnoticed.
    original = programma.datetime
    class LegacyDatetime(original):
        @classmethod
        def fromisoformat(cls, value):
            if re.search(r"[+-]\d{4}$", value):
                raise ValueError("compact offsets unsupported by this interpreter")
            return original.fromisoformat(value)
    monkeypatch.setattr(programma, "datetime", LegacyDatetime)
    parsed = SportlinkProgrammaAdapter(club_relation_code="BBDZ08H")._parse_sportlink_datetime(source)
    assert parsed.isoformat() == local
    assert parsed.astimezone(timezone.utc).isoformat() == utc


def test_146_synthetic_linked_matches_are_operational_with_mixed_offset_forms():
    adapter = CkcProgrammaAdapter(team_memberships=[
        RealTeamMembership("SYNTHETIC-P1", "O17-1", "Teamspeler", True, "Bond"),
    ])
    rows = [{
        "wedstrijdcode": f"SYNTHETIC-DATE-{index}",
        "wedstrijddatum": CASES[index % len(CASES)][0],
        "thuisteamclubrelatiecode": "BBDZ08H", "uitteamclubrelatiecode": "OTHER",
        "thuisteam": "CKC O17-1", "thuisteamid": "-1", "uitteam": "Andere club",
        "competitiesoort": "regulier", "status": "Te spelen",
    } for index in range(146)]
    result = adapter.import_rows(rows)
    assert len(result.links) == len(result.matches) == 146
    assert all(link.status == "matched" and link.identity.name == "O17-1" for link in result.links)
    assert not any(signal.code == "INVALID_PROGRAM_MATCH_DATETIME" for signal in result.signals)
    assert [m.starts_at.isoformat() for m in result.matches] == [CASES[i % len(CASES)][1] for i in range(146)]
    assert [link.original_team_name for link in result.links] == ["CKC O17-1"] * 146


@pytest.mark.parametrize("value", ["", "not-a-date", "2026-99-24T10:00:00+0200", "2026-10-24T10:00:00+9900"])
def test_invalid_dates_are_still_rejected(value):
    with pytest.raises(ValueError):
        SportlinkProgrammaAdapter(club_relation_code="BBDZ08H")._parse_sportlink_datetime(value)


def test_timezone_naive_legacy_input_still_means_utc():
    parsed = SportlinkProgrammaAdapter(club_relation_code="BBDZ08H")._parse_sportlink_datetime("2026-11-24T10:00:00")
    assert parsed.isoformat() == "2026-11-24T11:00:00+01:00"
