"""CKC classification of source facts; no duty or household decisions."""
from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from importlib.resources import files
from typing import Iterable

from .model import FunctionExemptionPolicy, RoleAssignment, Signal
from .real_data_import import CommitteeMembership

CONFIGURATION_VERSION = "ckc-v05-step2-round1"
SourceRegistration = RoleAssignment | CommitteeMembership


def clean_text(value: str) -> str:
    return " ".join(value.split())


@dataclass(frozen=True)
class ClassificationRule:
    dataset: str
    committee: str
    title: str
    category: str
    rights: FunctionExemptionPolicy


@dataclass(frozen=True)
class ClassifiedFunction:
    source: SourceRegistration
    rule: ClassificationRule | None
    configuration_version: str
    kind: str = "DERIVED"

    @property
    def known(self) -> bool:
        return self.rule is not None

    @property
    def self_exempt(self) -> bool:
        return self.rule is not None and self.rule.rights.self_exempt

    @property
    def household_exempt(self) -> bool:
        return self.rule is not None and self.rule.rights.household_exempt


@dataclass(frozen=True)
class PersonFunctionRights:
    person_id: str
    self_exempt: bool
    household_exempt: bool
    # Keep every supporting source fact, even when rights overlap.
    registrations: tuple[ClassifiedFunction, ...]


@dataclass(frozen=True)
class FunctionClassificationResult:
    registrations: tuple[ClassifiedFunction, ...]
    persons: tuple[PersonFunctionRights, ...]
    signals: tuple[Signal, ...]


class FunctionClassifier:
    def __init__(self, rules: Iterable[ClassificationRule] | None = None,
                 version: str = CONFIGURATION_VERSION):
        self.version = version
        self.rules = {}
        if rules is None:
            with files("dvk").joinpath("configuration/function_classification.csv").open(encoding="utf-8", newline="") as handle:
                rules = tuple(ClassificationRule(
                    row["dataset"], row["committee"], row["title"], row["category"],
                    FunctionExemptionPolicy(row["title"], self._bool(row["self_exempt"]),
                                            self._bool(row["household_exempt"])))
                    for row in csv.DictReader(handle))
        for rule in rules:
            key = (rule.dataset, clean_text(rule.committee), clean_text(rule.title))
            if key in self.rules:
                raise ValueError(f"Duplicate classification key: {key!r}")
            self.rules[key] = rule

    @staticmethod
    def _bool(value: str) -> bool:
        if value not in {"true", "false"}:
            raise ValueError(f"Invalid classification right: {value!r}")
        return value == "true"

    @staticmethod
    def key(source: SourceRegistration) -> tuple[str, str, str]:
        if isinstance(source, RoleAssignment):
            return ("functies", "", clean_text(source.source_role if source.source_role is not None else source.role))
        return ("commissies", clean_text(source.committee), clean_text(source.committee_role))

    def classify(self, source: SourceRegistration) -> ClassifiedFunction:
        return ClassifiedFunction(source, self.rules.get(self.key(source)), self.version)

    def classify_many(self, sources: Iterable[SourceRegistration]) -> FunctionClassificationResult:
        registrations = tuple(self.classify(source) for source in sources)
        grouped: dict[str, list[ClassifiedFunction]] = {}
        unknown = Counter()
        for item in registrations:
            grouped.setdefault(item.source.person_id, []).append(item)
            if not item.known:
                unknown[self.key(item.source)] += 1
        persons = tuple(PersonFunctionRights(pid, any(r.self_exempt for r in items),
                                            any(r.household_exempt for r in items), tuple(items))
                        for pid, items in sorted(grouped.items()))
        signals = tuple(Signal("unknown_function_classification",
                               f"Onbekende CKC-classificatie: {committee + ' / ' if committee else ''}{title!r} ({count} registraties)",
                               facts={"dataset": dataset, "committee": committee, "title": title,
                                      "registration_count": count})
                        for (dataset, committee, title), count in sorted(unknown.items()))
        return FunctionClassificationResult(registrations, persons, signals)
