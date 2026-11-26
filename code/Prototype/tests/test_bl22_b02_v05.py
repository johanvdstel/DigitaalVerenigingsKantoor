"""B-02: one registration, two distinct applications, synthetic sources only."""
import pytest

from dvk.football_participation import is_bond_team_player
from dvk.team_matchday import other_weekend_persons, TeamMatchdayError
from test_candidate_person_issues_v05 import rows, write_rows
from test_iteration1_candidates_v05 import team_data, plan, slot
from test_candidate_context_v05 import context


@pytest.mark.parametrize('team_type,type_ok', [
    ('Bond', True), ('bOnD', True), ('Vereniging', False),
    (None, False), ('', False), (' Bond ', False),
])
@pytest.mark.parametrize('team_role,role_ok', [
    ('Teamspeler', True), ('tEaMsPeLeR', True), ('Trainer', False),
    (None, False), ('', False), (' Teamspeler ', False),
])
@pytest.mark.parametrize('playing_member', [True, False, None])
def test_b02_truth_table(team_type, type_ok, team_role, role_ok, playing_member):
    assert is_bond_team_player(team_type, team_role, playing_member) is (
        type_ok and role_ok and playing_member is True)


@pytest.mark.parametrize('team_type,role,playing,qualifies,signals', [
    ('Bond', 'Teamspeler', 'Ja', True, []),
    (' bOnD ', ' tEaMsPeLeR ', 'yes', True, []),
    ('Vereniging', 'Teamspeler', 'Ja', False, []),
    ('Bond', 'Trainer', 'Ja', False, []),
    ('Bond', 'Teamspeler', 'Nee', False, []),
    ('Bond', 'Teamspeler', '', False, []),
    ('', 'Teamspeler', 'Ja', False, ['MISSING_TEAM_TYPE']),
    ('Onbekend', 'Teamspeler', 'Ja', False, ['UNKNOWN_TEAM_TYPE']),
    ('Bond', 'Teamspeler', 'Onbekend', False, ['UNKNOWN_PLAYING_MEMBER_VALUE']),
])
def test_import_booleans_signals_and_weekend_outcome(team_type, role, playing, qualifies, signals):
    data = team_data(['Algemeen/Zondag'])
    teams = rows(data, 'teams')
    teams[0].update({'Teamsoort': team_type, 'Teamrol': role, 'Spelend lid': playing})
    write_rows(data, 'teams', teams)
    imported = context(data).source
    assert imported.memberships[0].plays_football is qualifies
    assert imported.football_participations[0].plays_football is qualifies
    assert len(imported.team_memberships) == 1
    assert [s.code for s in imported.signals if s.dataset == 'teams'] == signals
    assert other_weekend_persons(imported.team_memberships, slot(5)) == (
        frozenset({'M1'}) if qualifies else frozenset())
    assert any(p.source_dataset == 'teams' and p.source_value == playing for p in imported.provenance)


def test_distributed_conditions_do_not_qualify_in_either_application():
    data = team_data(['Algemeen/Zaterdag'])
    team, = rows(data, 'teams')
    write_rows(data, 'teams', [dict(team, Team='A', Teamrol='Trainer'),
                              dict(team, Team='B', Teamsoort='Vereniging')])
    imported = context(data).source
    assert not imported.memberships[0].plays_football
    assert not imported.football_participations[0].plays_football
    assert len(imported.team_memberships) == 2
    assert not other_weekend_persons(imported.team_memberships, slot(6))
    # Sportlink duty still permits planning despite the separate exemption.
    result, _, _ = plan(data, 6)
    assert result.planned[0].staffing_purpose == 'minimum_coverage'
    assert result.controls[0].expectation.expected_required_hours == 0


@pytest.mark.parametrize('reverse', [False, True])
def test_saturday_player_plus_sunday_trainer_does_not_gain_sunday_player_rights(reverse):
    data = team_data(['Algemeen/Zaterdag'])
    team, = rows(data, 'teams')
    teams = [team, dict(team, Team='Trainerteam', Speeldag='Algemeen/Zondag', Teamrol='Trainer')]
    write_rows(data, 'teams', teams[::-1] if reverse else teams)
    imported = context(data).source
    assert imported.memberships[0].plays_football
    assert imported.football_participations[0].plays_football
    assert other_weekend_persons(imported.team_memberships, slot(5)) == frozenset()
    assert other_weekend_persons(imported.team_memberships, slot(6)) == frozenset({'M1'})
    assert plan(data, 6)[0].planned[0].staffing_purpose == 'emergency_minimum_coverage'
    # Programma retains every team link, including the trainer registration.
    assert {m.team_id for m in context(data).program.team_memberships} == {team['Team'], 'Trainerteam'}


def test_nonplayer_matchday_validation_remains_before_weekday_shortcut():
    from dvk.real_data_import import RealTeamMembership
    invalid = RealTeamMembership('M1', 'Trainerteam', 'Trainer', False, 'Bond', '')
    with pytest.raises(TeamMatchdayError, match='Speeldag'):
        other_weekend_persons((invalid,), slot(0))
