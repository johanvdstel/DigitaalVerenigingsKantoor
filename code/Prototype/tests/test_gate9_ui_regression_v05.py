from datetime import date

from streamlit_app import _demo_data, _demo_proposals


def test_demo_proposal_ids_are_unique_between_planning_runs():
    services, needs, matches, _ = _demo_data(date(2026, 9, 18))
    first = _demo_proposals(services[0], needs[0], matches)[1]
    second = _demo_proposals(services[0], needs[0], matches)[1]
    first_ids = {item.proposal.proposal_id for item in first}
    second_ids = {item.proposal.proposal_id for item in second}
    assert first_ids.isdisjoint(second_ids)
