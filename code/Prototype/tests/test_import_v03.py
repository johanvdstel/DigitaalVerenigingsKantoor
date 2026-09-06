from pathlib import Path

import pytest

from dvk.duty import evaluate_duty_foundation
from dvk.import_adapter import SportlinkCsvImportAdapter
from dvk.workstream_cases import TODAY


FIXTURES = Path(__file__).parents[1] / "testdata" / "v03_import"


def test_i01_sportlink_like_csv_import_produces_canonical_objects():
    data = SportlinkCsvImportAdapter().load_directory(FIXTURES)

    assert [person.person_id for person in data.persons] == ["I01P", "I02P"]
    assert data.team_memberships[0].team_id == "SEN-1"
    assert data.matches[0].home_away == "home"
    assert data.services[0].service_type == "bardienst"
    assert data.services[0].duration_hours == 3


def test_i01_imported_member_reproduces_domain_duty_and_position():
    data = SportlinkCsvImportAdapter().load_directory(FIXTURES)
    decision = evaluate_duty_foundation(data.case_for_person("I01P", "I01"), TODAY)

    assert decision.status == "ok"
    assert decision.facts["duty_required"] is True
    assert decision.facts["expected_required_hours"] == 10
    assert decision.facts["duty_position"] == {"A": 10, "B": 0, "C": 4, "D": 3, "E": 3}


def test_i01_imported_role_is_source_fact_not_import_policy():
    data = SportlinkCsvImportAdapter().load_directory(FIXTURES)
    decision = evaluate_duty_foundation(data.case_for_person("I02P", "I01-role"), TODAY)

    assert decision.status == "ok"
    assert decision.facts["duty_required"] is False
    assert decision.facts["qualification_reason"] == "function:trainer"
    assert decision.facts["expected_required_hours"] == 0


def test_import_rejects_missing_required_source_column(tmp_path):
    for source in FIXTURES.iterdir():
        target = tmp_path / source.name
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "members.csv").write_text("person_id,name\nP1,Incomplete\n", encoding="utf-8")

    with pytest.raises(ValueError, match="members.csv: missing columns"):
        SportlinkCsvImportAdapter().load_directory(tmp_path)
