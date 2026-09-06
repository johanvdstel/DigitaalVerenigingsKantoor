from __future__ import annotations

from datetime import date

from .model import Membership, Person, PrototypeCase, SportlinkDutyRegistration

TODAY = date(2026, 9, 4)

W_CASES = (
    PrototypeCase(
        "W01",
        "Taakplicht automatisch afgeleid",
        Person("W01P", "Senior Taakplicht", date(1990, 5, 1)),
        Membership("W01P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W02",
        "Afwijkende Sportlink-administratie",
        Person("W02P", "Senior Afwijking", date(1991, 6, 1)),
        Membership("W02P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration("W02P", required_hours=None),
    ),
    PrototypeCase(
        "W07",
        "Urenpositie A=10 B=0 C=4 D=3",
        Person("W07P", "Senior Urenpositie", date(1989, 7, 1)),
        Membership("W07P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration(
            "W07P", required_hours=10, correction_hours=0, completed_hours=4, scheduled_hours=3
        ),
    ),
)

W_CASE_BY_ID = {case.case_id: case for case in W_CASES}
