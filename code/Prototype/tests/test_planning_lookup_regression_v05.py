"""Lookup optimization preserves facts, ordering, uncertainty and freshness."""
from dataclasses import replace
from datetime import date

from dvk import member_duty
from dvk.model import Person
from test_candidate_context_v05 import exports, context, DAY


def test_large_population_normalizes_each_address_once(monkeypatch):
    members = [dict(pid=f"S{i}",born="01-01-2011" if i%3==0 else "01-01-1990",team="O17-1",number=str(i+1)) for i in range(300)]
    src = context(exports(members=members)).source
    calls=[]
    original = member_duty.canonical_address
    def address(person):
        calls.append(person.person_id)
        return original(person)
    monkeypatch.setattr(member_duty, "canonical_address", address)
    results = src.compare_required_hours(DAY)
    assert len(results) == 300
    assert sorted(calls) == sorted(p.person_id for p in src.persons)
    assert all(r.status == "overeenkomst" and r.expected_required_hours == 10 for r in results)


def test_source_evidence_and_signals_retain_original_order():
    members = [dict(pid=f"S{i}",born="01-01-2011",team="O17-1",number=str(i//2+1)) for i in range(12)]
    functions=[{"Rel. code":"S0","Functie":"Trainer Senioren"},
               {"Rel. code":"S7","Functie":"Synthetische onbekende functie"}]
    src=context(exports(members=members,functions=functions)).source
    # Deliberately interleave source records; lookup order must not leak into results.
    src=replace(src,provenance=tuple(reversed(src.provenance)),team_memberships=tuple(reversed(src.team_memberships)))
    for result in src.compare_required_hours(DAY):
        expectation=result.expectation
        support={fact.person_id for fact in expectation.source_facts if isinstance(fact,Person)}
        expected_teams=tuple(f for f in src.team_memberships if f.person_id in support)
        actual_teams=tuple(f for f in expectation.source_facts if f in src.team_memberships)
        assert actual_teams == expected_teams
        expected_provenance=tuple(f for f in src.provenance if f.source_dataset == "leden" and f.source_record_key.split(":",1)[0] in support)
        assert tuple(f for f in expectation.source_facts if f in src.provenance) == expected_provenance
        expected_signals=tuple(signal for signal in src.signals if signal.record_key is None or
                              signal.record_key.split(":",1)[0] in ({result.person_id} if signal.dataset == "vrijwilligers_periode" else support))
        assert result.signals[:len(expected_signals)] == expected_signals
        assert result.provenance == tuple(f for f in src.provenance if f.source_dataset == "vrijwilligers_periode" and f.source_record_key.split(":",1)[0] == result.person_id)


def test_lookup_tables_are_rebuilt_for_changed_date_and_sources():
    members=[dict(pid="OLDER",born="25-10-2008",team="O17-1",number="7"),
             dict(pid="YOUNGER",born="01-01-2011",team="O17-1",number="7")]
    src=context(exports(members=members)).source
    before={r.person_id:r for r in src.compare_required_hours(date(2026,10,24))}
    after={r.person_id:r for r in src.compare_required_hours(date(2026,10,25))}
    assert before["YOUNGER"].expected_required_hours == 0
    assert after["YOUNGER"].expected_required_hours == 10
    changed=replace(src, persons=tuple(replace(p, house_number="8") if p.person_id=="YOUNGER" else p for p in src.persons))
    assert next(r for r in changed.compare_required_hours(DAY) if r.person_id=="YOUNGER").expected_required_hours == 10
