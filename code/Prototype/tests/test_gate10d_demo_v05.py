from datetime import date
from pathlib import Path

from streamlit_app import _demo_data, _demo_proposals

SOURCE = Path(__file__).parents[1] / "streamlit_app.py"


def test_demo_uses_real_team_memberships_without_gate10_eligibility_override():
    text = SOURCE.read_text()
    assert 'W_CASE_BY_ID["W08"].person.person_id: "Senioren 1"' in text
    assert 'Demo-only: keep W08 available across services' not in text
    assert 'service.service_id == "BAR-WO-1"' not in text


def test_senioren_1_home_match_without_overlap_is_offered_by_real_gate8_rules():
    services, needs, matches, _ = _demo_data(date(2026, 9, 14))
    bar_za = next(s for s in services if s.service_id == "BAR-ZA-1")
    need = next(n for n in needs if n.service_id == "BAR-ZA-1")
    cases, planned = _demo_proposals(bar_za, need, matches, proposal_run_id="test")
    senior_1_id = next(c.person.person_id for c in cases if c.case_id == "W08")
    proposal = next(item.proposal for item in planned if item.proposal.person_id == senior_1_id)
    assert proposal.team_id == "Senioren 1"
    assert proposal.home_away == "home"
    assert proposal.match_relation == "home_match_same_day"
