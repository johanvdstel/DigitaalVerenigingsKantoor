"""BL-22 demonstrations: fixed synthetic outcomes, including evidence and order."""
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from dvk.duty_control_presenter import present_controls
from dvk.function_classification import FunctionClassifier
from dvk.model import RoleAssignment, SportlinkDutyRegistration, DutyPosition
from dvk.real_data_import import DutyImportRecord, Provenance, RealTeamMembership
from test_member_duty_v05 import person, source, outcomes, TODAY


def test_multiple_exemptions_keep_order_evidence_and_explanation():
    a, b = person('A'), person('B')
    roles = (RoleAssignment('A', 'Assistenttrainer'), RoleAssignment('A', 'Hoofdtrainer Sen.'),
             RoleAssignment('B', 'Assistenttrainer'), RoleAssignment('B', 'Onbekend synthetisch'))
    provenance = Provenance('Sportlink', 'leden', 'B:1', datetime(2026, 10, 6, tzinfo=timezone.utc))
    team = RealTeamMembership('B', 'Synthetisch team', 'Teamspeler', True, 'Bond')
    data = replace(source(a, b, roles=roles), team_memberships=(team,), provenance=(provenance,))
    result = outcomes(data)['A']
    assert (result.status, result.expected_required_hours) == ('vrijgesteld', 0)
    assert [(g.code, g.supporting_person_id, g.criteria) for g in result.grounds] == [
        ('personal_function', 'A', ()), ('personal_function', 'A', ()),
        ('household_function', 'B', ('address',)),
        ('household_function_classification_unknown', 'B', ())]
    classified = FunctionClassifier().classify_many(roles).registrations
    assert [g.registrations for g in result.grounds] == [(classified[0],), (classified[1],),
                                                       (classified[2],), (classified[3],)]
    assert result.source_facts == (a, b, *data.memberships, team, provenance)
    assert result.as_of == TODAY and result.kind == 'DERIVED'
    row = next(r for r in present_controls(data, data.compare_required_hours(TODAY)).rows if r.person_id == 'A')
    assert row.why == ('Persoonlijke vrijstelling wegens functie: Assistenttrainer; '
                       'Persoonlijke vrijstelling wegens functie: Hoofdtrainer Sen.; '
                       'Huishoudvrijstelling wegens functie van Lid B: Assistenttrainer; '
                       'Onbekende functieclassificatie bij huishoudlid Lid B: Onbekend synthetisch; '
                       'Urenpositie ontbreekt of kan niet betrouwbaar gekoppeld worden')


@pytest.mark.parametrize('conflicting', [False, True])
@pytest.mark.parametrize('role,hours,codes', [
    (None, None, ['household_address_insufficient']),
    ('Hoofdtrainer Sen.', 0, ['personal_function', 'household_address_insufficient']),
])
def test_proven_personal_exemption_precedes_address_uncertainty(conflicting, role, hours, codes):
    a = replace(person('A'), address_conflicting=conflicting,
                postal_code='8000AA' if conflicting else None)
    data = source(a, roles=() if role is None else (RoleAssignment('A', role),))
    result = outcomes(data)['A']
    assert result.expected_required_hours == hours
    assert result.status == ('vrijgesteld' if role else 'niet betrouwbaar beoordeelbaar')
    assert [g.code for g in result.grounds] == codes
    assert result.source_facts == (a, *data.memberships)


@pytest.mark.parametrize('when,expected', [
    (date(2026, 10, 6), (10, 0)), (date(2026, 10, 7), (10, 10)),
])
def test_eighteenth_birthday_keeps_child_evidence_and_does_not_transfer_hours(when, expected):
    a, b = person('A', date(2008, 10, 7)), person('B', date(2012, 1, 1))
    records = tuple(DutyImportRecord(SportlinkDutyRegistration(pid, 10, 0, completed, 0),
                                    10-completed, DutyPosition(10, 0, completed, 0))
                    for pid, completed in [('A', 4), ('B', 0)])
    data = replace(source(a, b), duty_records=records)
    controls = data.compare_required_hours(when)
    assert tuple(c.expected_required_hours for c in controls) == expected
    assert tuple(c.registered_required_hours for c in controls) == (10, 10)
    assert tuple(r.registration.completed_hours for r in data.duty_records) == (4, 0)
    assert tuple(c.status for c in controls) == ('overeenkomst', 'afwijking' if expected[1] == 0 else 'overeenkomst')
    if expected[1] == 0:
        assert [(g.code, g.supporting_person_id) for g in controls[1].expectation.grounds] == [('younger_minor', 'A')]


@pytest.mark.parametrize('role,household_hours', [('Assistenttrainer', 0), ('Hoofdtrainer Sen.', 10)])
def test_paid_and_unpaid_functions_demonstrate_different_household_effect(role, household_hours):
    result = outcomes(source(person('A'), person('B'), roles=(RoleAssignment('A', role),)))
    assert result['A'].expected_required_hours == 0
    assert result['B'].expected_required_hours == household_hours
    assert [g.code for g in result['B'].grounds] == ['household_function' if household_hours == 0 else 'no_exemption_found']
