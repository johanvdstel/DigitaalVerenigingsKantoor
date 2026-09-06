from dvk.duty import evaluate_duty_foundation
from dvk.workstream_cases import TODAY, W_CASES


def _format_value(value):
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


def main():
    print("DVK Prototype v0.3 - Werkstroom Ledendiensten, Fase 1")
    print("=" * 62)

    for case in W_CASES:
        decision = evaluate_duty_foundation(case, TODAY)
        facts = decision.facts

        print(f"\n{case.case_id} - {case.description}")
        print(f"  status: {decision.status.upper()}")
        print(f"  taakplichtig: {_format_value(facts.get('duty_required'))}")
        print(f"  reden: {_format_value(facts.get('qualification_reason'))}")
        print(f"  administratief subject: {_format_value(facts.get('administrative_subject'))}")
        print(f"  uitvoerdercategorie: {_format_value(facts.get('executor_category'))}")
        print(f"  beleidsnorm uren: {_format_value(facts.get('policy_required_hours'))}")
        print(f"  verwacht A: {_format_value(facts.get('expected_required_hours'))}")

        if facts.get("sportlink_comparison_performed"):
            print(f"  Sportlink A: {_format_value(facts.get('sportlink_required_hours'))}")
        else:
            print("  Sportlink vergelijking: niet uitgevoerd")

        duty_position = facts.get("duty_position")
        if duty_position:
            print(
                "  urenpositie: "
                f"A={duty_position['A']} B={duty_position['B']} "
                f"C={duty_position['C']} D={duty_position['D']} E={duty_position['E']}"
            )

        if decision.signals:
            print("  signalen: " + ", ".join(signal.code for signal in decision.signals))
        else:
            print("  signalen: geen")


if __name__ == "__main__":
    main()
