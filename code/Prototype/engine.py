from __future__ import annotations

from datetime import date
from collections.abc import Callable

from .model import Decision, PrototypeCase
from .rules import (
    evaluate_clothing,
    evaluate_clothing_access,
    evaluate_ledendienst,
    evaluate_membership,
)

Rule = Callable[[PrototypeCase, date], Decision]


class RuleEngine:
    def __init__(self, rules: tuple[Rule, ...] | None = None) -> None:
        self.rules = rules or (
            evaluate_membership,
            evaluate_ledendienst,
            evaluate_clothing,
            evaluate_clothing_access,
        )

    def evaluate(
        self,
        case: PrototypeCase,
        *,
        today: date,
    ) -> dict[str, Decision]:
        decisions = [rule(case, today) for rule in self.rules]
        return {decision.code: decision for decision in decisions}
