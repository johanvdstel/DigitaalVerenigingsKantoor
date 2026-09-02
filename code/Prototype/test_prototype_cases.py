from dvk.cases import CASE_BY_ID, TODAY
from dvk.engine import RuleEngine


engine = RuleEngine()


def run(case_id: str):
    return engine.evaluate(CASE_BY_ID[case_id], today=TODAY)


def test_c01_active_adult_member_has_six_hours_remaining():
    result = run("C01")
    assert result["membership"].status == "ok"
    assert result["ledendienst"].status == "attention"
    assert result["ledendienst"].facts["remaining_hours"] == 6
    assert result["ledendienst"].facts["actor"] == "lid"


def test_c02_ledendienst_is_complete():
    result = run("C02")
    assert result["ledendienst"].status == "ok"
    assert result["ledendienst"].facts["remaining_hours"] == 0


def test_c03_minor_shifts_execution_to_parent_or_guardian():
    result = run("C03")
    assert result["ledendienst"].status == "attention"
    assert result["ledendienst"].facts["actor"] == "ouder/verzorger namens minderjarig lid"
    assert result["ledendienst"].facts["remaining_hours"] == 10


def test_c04_younger_minor_is_exempt_via_broederdienst():
    result = run("C04")
    assert result["ledendienst"].status == "ok"
    assert result["ledendienst"].facts["exempt_reason"] == "broederdienst"


def test_c05_playing_trainer_is_member_and_function_exempt():
    result = run("C05")
    assert result["membership"].status == "ok"
    assert result["ledendienst"].status == "ok"
    assert "trainer" in result["ledendienst"].facts["exempt_roles"]


def test_c06_committee_member_is_active_member_and_function_exempt():
    result = run("C06")
    assert result["membership"].status == "ok"
    assert result["ledendienst"].status == "ok"
    assert "commissielid" in result["ledendienst"].facts["exempt_roles"]


def test_c07_one_off_bar_volunteer_is_not_a_member():
    result = run("C07")
    assert result["membership"].status == "not_applicable"
    assert result["ledendienst"].status == "not_applicable"


def test_c08_honorary_member_is_exempt():
    result = run("C08")
    assert result["membership"].status == "ok"
    assert result["ledendienst"].status == "ok"
    assert result["ledendienst"].facts["exempt_reason"] == "erelid"


def test_c09_recreational_member_is_still_an_active_member():
    result = run("C09")
    assert result["membership"].status == "ok"
    assert result["membership"].facts["recreational"] is True
    assert result["ledendienst"].facts["remaining_hours"] == 8


def test_c10_ended_member_with_unreturned_clothing_requires_attention():
    result = run("C10")
    assert result["membership"].status == "attention"
    assert result["ledendienst"].status == "not_applicable"
    assert result["clothing"].status == "attention"
    assert result["clothing"].facts["outstanding"] == [
        {"article": "wedstrijdshirt", "size": "M"}
    ]


def test_c11_clothing_tool_manager_has_access_management_rights():
    result = run("C11")
    assert result["clothing_access"].status == "ok"
    assert set(result["clothing_access"].facts["levels"]) == {
        "read",
        "update",
        "manage_access",
    }
