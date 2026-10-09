"""FB-01: synthetic explanation regressions; baseline hours remain unchanged."""
from dataclasses import replace
from datetime import date

import pytest

from dvk.duty_control_presenter import present_controls
from dvk.model import Membership, RoleAssignment
from test_member_duty_v05 import person, source, outcomes, codes, TODAY


SCENARIOS = ('single', 'two', 'former', 'different_names', 'household',
             'different_address', 'nonplaying', 'adult', 'personal')


def fb01_source(scenario):
    a = person('A', date(2010, 1, 1))
    b = person('B', date(2012, 1, 1))
    if scenario == 'single':
        return source(a)
    if scenario == 'former':
        c = person('C', date(2000, 1, 1))
        return source(a, b, c, memberships=(
            Membership('A', 'Definitief', 'Bondslid', plays_football=True),
            Membership('B', 'Afgemeld', 'Bondslid', end_date=date(2017, 1, 1), plays_football=True),
            Membership('C', 'Afgemeld', 'Bondslid', end_date=date(2017, 1, 1), plays_football=True)))
    if scenario == 'different_names':
        a, b = replace(a, name='Anna Voorbeeld'), replace(b, name='Ben Anders')
    if scenario == 'different_address':
        b = replace(b, house_number='18')
    if scenario == 'adult':
        b = replace(b, birth_date=date(1990, 1, 1))
    if scenario == 'nonplaying':
        return source(a, b, memberships=(
            Membership('A', 'Definitief', 'Bondslid', plays_football=True),
            Membership('B', 'Definitief', 'Bondslid', plays_football=False)))
    roles = ((RoleAssignment('A', 'Assistenttrainer'),) if scenario == 'household' else
             (RoleAssignment('A', 'Hoofdtrainer Sen.'),) if scenario == 'personal' else ())
    return source(a, b, roles=roles)


@pytest.mark.parametrize('scenario', SCENARIOS)
def test_fb01_hours_and_motivation(scenario):
    data = fb01_source(scenario)
    results = outcomes(data)
    rows = {r.person_id: r for r in present_controls(data, data.compare_required_hours(TODAY)).rows}
    expected_a = 0 if scenario in ('household', 'personal') else 10
    assert results['A'].expected_required_hours == expected_a
    if scenario == 'single':
        assert len(results) == 1
    elif scenario == 'former':
        assert results['B'].expected_required_hours == results['C'].expected_required_hours == 0
    else:
        expected_b = 10 if scenario in ('different_address', 'adult') else 0
        assert results['B'].expected_required_hours == expected_b

    if scenario in ('two', 'different_names'):
        assert codes(results['A']) == {'oldest_minor'}
        assert 'oudste kwalificerende minderjarige' in rows['A'].why
        assert 'younger_minor' in codes(results['B'])
        assert 'jonger kind' in rows['B'].why and data.persons[0].name in rows['B'].why
    elif scenario in ('household', 'personal'):
        assert 'personal_function' in codes(results['A'])
        assert 'oldest_minor' not in codes(results['A'])
        assert 'Persoonlijke vrijstelling' in rows['A'].why
        if scenario == 'household':
            assert 'household_function' in codes(results['B'])
            assert 'Huishoudvrijstelling' in rows['B'].why
            assert results['B'].status == 'vrijgesteld'
    else:
        assert codes(results['A']) == {'no_exemption_found'}
        assert 'Geen vrijstellingsgrond gevonden' in rows['A'].why
        assert 'Gezinsregel minderjarigen' not in rows['A'].why
