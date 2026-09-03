from __future__ import annotations

from datetime import date

from .model import Decision, PrototypeCase
from .rules import (
    evaluate_authorization,
    evaluate_clothing,
    evaluate_compliance,
    evaluate_data_quality,
    evaluate_ledendienst,
    evaluate_membership,
    evaluate_relationships,
)


class RuleEngine:
    def evaluate(self, case: PrototypeCase, today: date | None = None) -> tuple[Decision, ...]:
        on_date = today or case.context_date or date.today()
        return (
            evaluate_membership(case, on_date),
            evaluate_relationships(case, on_date),
            evaluate_ledendienst(case, on_date),
            evaluate_clothing(case, on_date),
            evaluate_authorization(case, on_date),
            evaluate_compliance(case, on_date),
            evaluate_data_quality(case, on_date),
        )
