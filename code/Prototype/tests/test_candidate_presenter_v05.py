"""Presentation checks on synthetic calculated outcomes, without changing policy."""
from types import SimpleNamespace

import pytest

from dvk.candidate_presenter import priority_explanation


@pytest.mark.parametrize('preference,expected', [
    ('neutral', 'Wedstrijdcontext geeft geen voorkeur.'),
    ('preferred', 'voorrang bij gelijke urenprioriteit'),
    ('avoid', 'minder voorkeur bij gelijke urenprioriteit'),
])
@pytest.mark.parametrize('backlog,expected_backlog', [
    ('achterstand vorig seizoen niet beschikbaar: BL-03', 'zijn nog niet beschikbaar en tellen niet mee'),
    ('achterstand vorig seizoen niet meegewogen vanaf 1 december', 'tellen vanaf 1 december niet mee'),
    ('achterstand vorig seizoen=4', 'vorig seizoen: 4. Deze tellen mee'),
])
def test_priority_translation(preference, expected, backlog, expected_backlog):
    p = SimpleNamespace(E=10, previous_season_backlog=4,
                        applied_priority_rules=('actuele E=10', backlog, f'wedstrijdvoorkeur={preference}'))
    result = priority_explanation(p)
    assert result.startswith('Openstaande uren: 10.')
    assert expected in result and expected_backlog in result
    for internal in ('BL-03', 'E=', 'neutral', 'preferred', 'avoid', 'wedstrijdvoorkeur='):
        assert internal not in result
