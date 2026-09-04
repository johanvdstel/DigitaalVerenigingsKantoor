from pprint import pformat

from dvk.cases import CASES, TODAY
from dvk.engine import RuleEngine

engine = RuleEngine()

# Sommige mastercases bewijzen juist dat iets niet van toepassing is. Die besluiten
# moeten in de menselijke acceptatierapportage zichtbaar blijven.
ACCEPTANCE_NOT_APPLICABLE = {
    "C07": {"membership", "ledendienst"},
}


def print_mapping(label, value, indent="    "):
    if not value:
        return
    formatted = pformat(value, width=100, sort_dicts=True)
    lines = formatted.splitlines()
    print(f"{indent}{label}: {lines[0]}")
    for line in lines[1:]:
        print(f"{indent}{' ' * (len(label) + 2)}{line}")


def is_relevant(case_id, decision):
    return decision.status != "not_applicable" or decision.code in ACCEPTANCE_NOT_APPLICABLE.get(case_id, set())


print("DVK Prototype v0.2 — functionele acceptatierapportage")
print(f"Peildatum: {TODAY.isoformat()}")
print(f"Aantal mastercases: {len(CASES)}")
print("=" * 78)

for case in CASES:
    decisions = engine.evaluate(case, TODAY)
    relevant = [d for d in decisions if is_relevant(case.case_id, d)]
    signal_count = sum(len(d.signals) for d in relevant)
    action_count = sum(len(d.actions) for d in relevant)

    print(f"\n{case.case_id} — {case.description}")
    print(f"  Onderwerp: {case.person.person_id} — {case.person.name}")
    print(f"  Samenvatting: {len(relevant)} relevante besluiten, {signal_count} signalering(en), {action_count} actie(s)")

    for decision in relevant:
        print(f"  [{decision.code}] status={decision.status}")
        print(f"    Uitkomst: {decision.message}")
        print_mapping("Feiten", decision.facts)
        for signal in decision.signals:
            print(f"    Signalering: {signal.code} ({signal.severity}) — {signal.message}")
            print_mapping("Signaalfeiten", signal.facts, indent="      ")
        for action in decision.actions:
            owner = f"; verantwoordelijke={action.responsible_role}" if action.responsible_role else ""
            print(f"    Actie: {action.action_type} [{action.status}]{owner}")
            if action.reason:
                print(f"      Reden: {action.reason}")
            print_mapping("Actiefeiten", action.facts, indent="      ")

print("\n" + "=" * 78)
print(f"Uitgevoerd: {len(CASES)} cases. De inhoudelijke verwachtingen worden afgedwongen door tests/test_cases.py.")
