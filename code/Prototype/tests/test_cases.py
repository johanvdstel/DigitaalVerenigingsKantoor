from dvk.cases import CASE_BY_ID, CASES, TODAY
from dvk.engine import RuleEngine

engine = RuleEngine()


def result(cid, code):
    return next(x for x in engine.evaluate(CASE_BY_ID[cid], TODAY) if x.code == code)


def test_masterset_has_22_cases():
    assert [c.case_id for c in CASES] == [f"C{i:02d}" for i in range(1, 23)]


def test_c01_open_hours(): assert result("C01","ledendienst").facts["remaining_hours"] == 6
def test_c02_completed(): assert result("C02","ledendienst").status == "ok"
def test_c03_parent_executes(): assert result("C03","ledendienst").facts["actor"] == "P03O"
def test_c04_no_second_family_duty(): assert result("C04","ledendienst").facts["exempt_reason"] == "gezinsverplichting"
def test_c05_trainer_exempt(): assert "trainer" in result("C05","ledendienst").facts["exempt_roles"]
def test_c06_committee_exempt(): assert "commissielid" in result("C06","ledendienst").facts["exempt_roles"]
def test_c07_not_member(): assert result("C07","membership").status == "not_applicable"
def test_c08_honorary_exempt(): assert result("C08","ledendienst").facts["exempt_reason"] == "erelid"
def test_c09_recreational_exempt(): assert result("C09","ledendienst").facts["exempt_reason"] == "recreatief"

def test_c10_clothing_blocks_transfer():
    r=result("C10","clothing"); assert r.status == "blocked" and r.facts["transfer_release_blocked"] is True
    assert {a.action_type for a in r.actions} == {"send_email","block_transfer_release"}

def test_c11_correct_manager_access(): assert result("C11","authorization").status == "ok"
def test_c12_manage_access_excess(): assert "manage_access" in result("C12","authorization").facts["excess"]["CKC Kleding Beheer Tool"]
def test_c13_correct_member_admin_access(): assert result("C13","authorization").status == "ok"
def test_c14_old_board_access_revoke(): assert "revoke_access" in {a.action_type for a in result("C14","authorization").actions}
def test_c15_new_officer_missing_access(): assert "grant_access" in {a.action_type for a in result("C15","authorization").actions}
def test_c16_unexplained_access(): assert result("C16","authorization").facts["excess"]
def test_c17_two_roles_combined(): assert result("C17","authorization").status == "ok" and len(result("C17","authorization").facts["required"]) == 2
def test_c18_trainer_without_vog(): assert result("C18","compliance").facts["vog_valid"] is False
def test_c19_bar_update_is_excess(): assert "update" in result("C19","authorization").facts["excess"]["kassasysteem"]
def test_c20_minor_without_parent(): assert result("C20","relationships").status == "error"
def test_c21_nine_digit_mobile_invalid(): assert any(s.code == "invalid_mobile" for s in result("C21","data_quality").signals)

def test_c22_different_addresses_not_error():
    r=result("C22","data_quality"); assert r.status == "ok" and r.facts["address_difference_possible"] is True
