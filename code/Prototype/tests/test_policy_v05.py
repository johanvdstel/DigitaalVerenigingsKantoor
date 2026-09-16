from datetime import date, datetime

from dvk.duty import HOUSEHOLD_EXEMPTION_EXPLANATION, derive_duty_qualification, evaluate_duty_foundation
from dvk.model import Membership, Person, PrototypeCase, RoleAssignment
from dvk.shift_catalog import ShiftDefinition
from dvk.staffing import calculate_staffing_need
from dvk.vrijwilligers_adapter import VolunteerBooking
from dvk.workstream_model import DutyService

TODAY = date(2026, 9, 17)


def case(subject_address="Straat 1", household_address="Straat 1"):
    subject = Person("P1", "Spelend lid", date(1990, 1, 1), address=subject_address)
    household = Person("P2", "Gezinslid", date(1988, 1, 1), address=household_address)
    return PrototypeCase("V05-1", "gezinsvrijstelling", subject, Membership("P1", "active", "member", plays_football=True), persons=(household,), roles=(RoleAssignment("P2", "trainer"),))


def test_household_member_with_qualifying_function_exempts_same_address_playing_member():
    qualification = derive_duty_qualification(case(), TODAY)
    assert qualification.duty_required is False
    assert qualification.reason == "household_function:P2:trainer"
    decision = evaluate_duty_foundation(case(), TODAY)
    assert decision.facts["exemption_explanation"] == HOUSEHOLD_EXEMPTION_EXPLANATION
    assert decision.facts["expected_required_hours"] == 0


def test_same_surname_or_relationship_is_not_invented_different_address_does_not_exempt():
    qualification = derive_duty_qualification(case(household_address="Andere straat 9"), TODAY)
    assert qualification.duty_required is True
    assert qualification.reason == "playing_member"


def test_missing_address_never_guesses_household_exemption_and_yields_quality_attention():
    c = case(subject_address=None, household_address="Straat 1")
    assert derive_duty_qualification(c, TODAY).duty_required is True
    decision = evaluate_duty_foundation(c, TODAY)
    assert any(signal.code == "household_exemption_address_missing" for signal in decision.signals)


def test_non_qualifying_household_role_does_not_exempt():
    c = case()
    c = PrototypeCase(c.case_id, c.description, c.person, c.membership, persons=c.persons, roles=(RoleAssignment("P2", "supporter"),))
    assert derive_duty_qualification(c, TODAY).duty_required is True


def test_candidate_capacity_continues_after_minimum_until_maximum():
    service = DutyService("S1", "bar", datetime(2026, 9, 19, 10), datetime(2026, 9, 19, 12), 2)
    definition = ShiftDefinition("bar", "Bar", 2, 4)
    bookings = (VolunteerBooking("B1", "S1", "P1"), VolunteerBooking("B2", "S1", "P2"))
    need = calculate_staffing_need(service=service, definition=definition, bookings=bookings)
    assert need.open_need == 0
    assert need.remaining_capacity == 2
    assert need.minimum_coverage_slots == 0
    assert need.optional_capacity_slots == 2
    assert need.candidate_slots == 2


def test_candidate_capacity_stops_at_maximum():
    service = DutyService("S1", "bar", datetime(2026, 9, 19, 10), datetime(2026, 9, 19, 12), 2)
    definition = ShiftDefinition("bar", "Bar", 2, 3)
    bookings = tuple(VolunteerBooking(f"B{i}", "S1", f"P{i}") for i in range(3))
    need = calculate_staffing_need(service=service, definition=definition, bookings=bookings)
    assert need.open_need == 0
    assert need.remaining_capacity == 0
    assert need.candidate_slots == 0
