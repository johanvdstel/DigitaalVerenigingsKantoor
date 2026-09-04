from dvk.cases import CASE_BY_ID, CASES, TODAY
from dvk.engine import RuleEngine

engine = RuleEngine()


def result(cid, code):
    return next(x for x in engine.evaluate(CASE_BY_ID[cid], TODAY) if x.code == code)


def signal_codes(decision):
    return {s.code for s in decision.signals}


def action_types(decision):
    return {a.action_type for a in decision.actions}


def test_masterset_has_22_cases():
    assert [c.case_id for c in CASES] == [f"C{i:02d}" for i in range(1, 23)]


def test_c01_open_hours_and_scheduling_proposal():
    assert result("C01", "membership").status == "ok"
    r = result("C01", "ledendienst")
    assert r.status == "attention"
    assert r.facts == {"required_hours": 10, "completed_hours": 4, "remaining_hours": 6, "actor": "P01"}
    assert action_types(r) == {"propose_duty_scheduling"}
    action = r.actions[0]
    assert action.responsible_role == "vrijwilligerscommissie"
    assert action.facts == {"remaining_hours": 6}
    assert "verantwoordelijkheid" in (action.reason or "")


def test_c02_completed():
    r = result("C02", "ledendienst")
    assert r.status == "ok"
    assert r.facts == {"required_hours": 10, "completed_hours": 10, "remaining_hours": 0, "actor": "P02"}
    assert not r.actions and not r.signals


def test_c03_parent_executes():
    assert result("C03", "relationships").facts["parent_guardians"] == ["P03O"]
    r = result("C03", "ledendienst")
    assert r.facts == {"required_hours": 10, "completed_hours": 0, "remaining_hours": 10, "actor": "P03O"}


def test_c04_no_second_family_duty():
    r = result("C04", "ledendienst")
    assert r.status == "ok"
    assert r.facts["exempt_reason"] == "gezinsverplichting"
    assert r.facts["actor"] == "P04O"
    assert r.facts["family_duty_subject"] == "P04A"


def test_c05_trainer_exempt():
    assert result("C05", "membership").facts["plays_football"] is True
    assert "trainer" in result("C05", "ledendienst").facts["exempt_roles"]
    assert result("C05", "compliance").facts["vog_valid"] is True


def test_c06_committee_exempt():
    assert result("C06", "membership").status == "ok"
    assert result("C06", "membership").facts["kind"] == "verenigingslid"
    assert "commissielid" in result("C06", "ledendienst").facts["exempt_roles"]


def test_c07_not_member_and_no_own_duty():
    membership = result("C07", "membership")
    duty = result("C07", "ledendienst")
    assert membership.status == "not_applicable"
    assert membership.message == "Persoon heeft geen CKC-lidmaatschap."
    assert duty.status == "not_applicable"
    assert duty.message == "Geen urenplicht bij niet-actief lidmaatschap."


def test_c08_honorary_exempt():
    assert result("C08", "membership").facts["honorary"] is True
    assert result("C08", "ledendienst").facts["exempt_reason"] == "erelid"


def test_c09_recreational_exempt():
    assert result("C09", "membership").facts["recreational"] is True
    r = result("C09", "ledendienst")
    assert r.status == "ok"
    assert r.facts == {"exempt_reason": "recreatief"}


def test_c10_clothing_blocks_transfer_and_email_explains_block():
    assert result("C10", "membership").status == "attention"
    r = result("C10", "clothing")
    assert r.status == "blocked"
    assert r.facts["transfer_release_blocked"] is True
    assert r.facts["outstanding"] == [{"article": "wedstrijdshirt", "size": "M"}]
    assert "outstanding_clothing" in signal_codes(r)
    assert action_types(r) == {"send_email", "block_transfer_release"}
    email = next(a for a in r.actions if a.action_type == "send_email")
    assert "restwaarde" in (email.reason or "")
    assert "geen vrijgave voor overschrijving" in (email.reason or "")


def test_c11_correct_manager_access():
    r = result("C11", "authorization")
    expected = ["manage_access", "read", "update"]
    assert r.status == "ok"
    assert r.facts["required"]["CKC Kleding Beheer Tool"] == expected
    assert r.facts["actual"]["CKC Kleding Beheer Tool"] == expected
    assert r.facts["authority_ids"]["CKC Kleding Beheer Tool"] == ["A11"]


def test_c12_manage_access_excess():
    r = result("C12", "authorization")
    assert r.status == "blocked"
    assert r.facts["required"]["CKC Kleding Beheer Tool"] == ["read"]
    assert r.facts["excess"]["CKC Kleding Beheer Tool"] == ["manage_access"]
    assert "excess_authorization" in signal_codes(r)
    assert "revoke_access" in action_types(r)


def test_c13_correct_member_admin_access():
    r = result("C13", "authorization")
    assert r.status == "ok"
    assert r.facts["required"]["ledenadministratie"] == ["read", "update"]
    assert r.facts["actual"]["ledenadministratie"] == ["read", "update"]
    assert not r.facts["missing"] and not r.facts["excess"] and not r.facts["unexplained"]


def test_c14_old_board_access_revoke():
    r = result("C14", "authorization")
    assert r.status == "blocked"
    assert r.facts["required"] == {}
    assert r.facts["excess"]["bestuursresource"] == ["read", "update"]
    assert "excess_authorization" in signal_codes(r)
    assert "revoke_access" in action_types(r)


def test_c15_new_officer_missing_access():
    r = result("C15", "authorization")
    assert r.status == "blocked"
    assert r.facts["missing"]["ledenadministratie"] == ["read", "update"]
    assert "missing_authorization" in signal_codes(r)
    assert "grant_access" in action_types(r)


def test_c16_unexplained_access_requires_investigation_not_immediate_revocation():
    r = result("C16", "authorization")
    assert r.status == "attention"
    assert r.facts["unexplained"]["ledenadministratie"] == ["read"]
    assert not r.facts["excess"]
    assert "unexplained_authorization" in signal_codes(r)
    assert "investigate_authorization" in action_types(r)
    assert "revoke_access" not in action_types(r)


def test_c17_two_roles_combined():
    r = result("C17", "authorization")
    assert r.status == "ok"
    assert r.facts["required"] == {"ledenadministratie": ["read", "update"], "bestuursresource": ["read"]}
    assert r.facts["actual"] == r.facts["required"]


def test_c18_trainer_without_vog():
    r = result("C18", "compliance")
    assert r.status == "error"
    assert r.facts["vog_valid"] is False
    assert "missing_vog" in signal_codes(r)
    assert "start_vog_followup" in action_types(r)


def test_c19_bar_update_is_excess():
    r = result("C19", "authorization")
    assert r.status == "blocked"
    assert r.facts["required"]["kassasysteem"] == ["read", "use"]
    assert r.facts["excess"]["kassasysteem"] == ["update"]
    assert "revoke_access" in action_types(r)


def test_c20_minor_without_parent_requires_member_admin_followup():
    r = result("C20", "relationships")
    assert r.status == "error"
    assert r.facts["parent_guardians"] == []
    assert "missing_parent_guardian" in signal_codes(r)
    assert action_types(r) == {"investigate_parent_guardian"}
    assert r.actions[0].responsible_role == "ledenadministrateur"
    duty = result("C20", "ledendienst")
    assert duty.facts["actor"] is None


def test_c21_nine_digit_mobile_invalid():
    r = result("C21", "data_quality")
    assert r.status == "error"
    assert "invalid_mobile" in signal_codes(r)
    assert "request_data_correction" in action_types(r)


def test_c22_same_parent_two_children_different_addresses_not_error():
    relationships = result("C22", "relationships")
    assert relationships.facts["parent_guardians"] == ["P22O"]
    assert relationships.facts["parent_guardian_links"] == [
        {"parent_guardian": "P22O", "child": "P22A"},
        {"parent_guardian": "P22O", "child": "P22B"},
    ]
    r = result("C22", "data_quality")
    assert r.status == "ok"
    assert r.facts["address_difference_possible"] is True
    assert not r.signals and not r.actions
