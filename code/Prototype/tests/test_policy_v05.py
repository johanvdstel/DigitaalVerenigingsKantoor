from datetime import date, datetime

from dvk.duty import HOUSEHOLD_EXEMPTION_EXPLANATION, derive_duty_qualification, evaluate_duty_foundation
from dvk.model import DutyPolicy, FunctionExemptionPolicy, Membership, Person, PrototypeCase, RoleAssignment
from dvk.shift_catalog import ShiftDefinition
from dvk.staffing import calculate_staffing_need
from dvk.vrijwilligers_adapter import VolunteerBooking
from dvk.workstream_model import DutyService

TODAY = date(2026, 9, 17)
POLICY = DutyPolicy(10, "v0.5-test", (FunctionExemptionPolicy("trainer", True, True), FunctionExemptionPolicy("hoofdtrainer", True, False)))


def case(subject_address="Straat 1", household_address="Straat 1", household_role="trainer"):
    subject = Person("P1", "Spelend lid", date(1990, 1, 1), address=subject_address)
    household = Person("P2", "Gezinslid", date(1988, 1, 1), address=household_address)
    return PrototypeCase("V05-1", "gezinsvrijstelling", subject, Membership("P1", "active", "member", plays_football=True), persons=(household,), roles=(RoleAssignment("P2", household_role),))


def test_household_member_with_qualifying_function_exempts_same_address_playing_member():
    qualification = derive_duty_qualification(case(), TODAY, POLICY)
    assert qualification.duty_required is False
    assert qualification.reason == "household_function:P2:trainer"
    decision = evaluate_duty_foundation(case(), TODAY, POLICY)
    assert decision.facts["exemption_explanation"] == HOUSEHOLD_EXEMPTION_EXPLANATION
    assert decision.facts["policy_version"] == "v0.5-test"
    assert decision.facts["expected_required_hours"] == 0


def test_same_source_role_can_change_outcome_under_different_policy_version():
    no_household = DutyPolicy(10, "v0.5-no-household", (FunctionExemptionPolicy("trainer", True, False),))
    assert derive_duty_qualification(case(), TODAY, POLICY).duty_required is False
    assert derive_duty_qualification(case(), TODAY, no_household).duty_required is True


def test_hoofdtrainer_is_self_exempt_but_does_not_exempt_adult_child():
    child_case = case(household_role="hoofdtrainer")
    assert derive_duty_qualification(child_case, TODAY, POLICY).duty_required is True
    head_coach = Person("P2", "Betaalde hoofdtrainer", date(1980, 1, 1), address="Straat 1")
    own_case = PrototypeCase("V05-H", "hoofdtrainer zelf", head_coach, Membership("P2", "active", "member", plays_football=True), roles=(RoleAssignment("P2", "hoofdtrainer"),))
    qualification = derive_duty_qualification(own_case, TODAY, POLICY)
    assert qualification.duty_required is False
    assert qualification.reason == "function:hoofdtrainer"


def test_same_surname_or_relationship_is_not_invented_different_address_does_not_exempt():
    qualification = derive_duty_qualification(case(household_address="Andere straat 9"), TODAY, POLICY)
    assert qualification.duty_required is True


def test_missing_address_never_guesses_household_exemption_and_yields_quality_attention():
    c = case(subject_address=None)
    assert derive_duty_qualification(c, TODAY, POLICY).duty_required is True
    assert any(signal.code == "household_exemption_address_missing" for signal in evaluate_duty_foundation(c, TODAY, POLICY).signals)


def test_missing_address_of_function_holder_also_yields_quality_attention():
    c = case(household_address=None)
    assert derive_duty_qualification(c, TODAY, POLICY).duty_required is True
    assert any(signal.code == "household_exemption_address_missing" for signal in evaluate_duty_foundation(c, TODAY, POLICY).signals)


def test_unconfigured_household_role_does_not_exempt():
    assert derive_duty_qualification(case(household_role="supporter"), TODAY, POLICY).duty_required is True


def _service_and_times(required_staff=2):
    start = datetime(2026, 9, 19, 10); end = datetime(2026, 9, 19, 12)
    return DutyService("S1", "bar", start, end, "clubhuis", required_staff), start, end


def test_candidate_capacity_continues_after_minimum_until_maximum():
    service, start, end = _service_and_times()
    definition = ShiftDefinition("BAR", "bar", 2.0, 2, 4)
    bookings = (VolunteerBooking("BAR", "S1", "P1", start, end, "clubhuis"), VolunteerBooking("BAR", "S1", "P2", start, end, "clubhuis"))
    need = calculate_staffing_need(service=service, definition=definition, bookings=bookings)
    assert need.open_need == 0
    assert need.remaining_capacity == 2
    assert need.minimum_coverage_slots == 0
    assert need.optional_capacity_slots == 2
    assert need.candidate_slots == 2


def test_candidate_capacity_stops_at_maximum():
    service, start, end = _service_and_times()
    definition = ShiftDefinition("BAR", "bar", 2.0, 2, 3)
    bookings = tuple(VolunteerBooking("BAR", "S1", f"P{i}", start, end, "clubhuis") for i in range(3))
    need = calculate_staffing_need(service=service, definition=definition, bookings=bookings)
    assert need.open_need == 0
    assert need.remaining_capacity == 0
    assert need.candidate_slots == 0
