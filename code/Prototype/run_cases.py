from dvk.cases import CASES, TODAY
from dvk.engine import RuleEngine

engine = RuleEngine()

for case in CASES:
    print(f"\n{case.case_id} — {case.description}")
    for decision in engine.evaluate(case, TODAY):
        if decision.status != "not_applicable":
            print(f"  {decision.code}: {decision.status} — {decision.message}")
            for action in decision.actions:
                print(f"    action: {action.action_type} — {action.reason or ''}")
