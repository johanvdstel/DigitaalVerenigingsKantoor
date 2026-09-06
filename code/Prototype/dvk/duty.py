from __future__ import annotations

from datetime import date

from .model import (
    Decision,
    DutyPolicy,
    DutyPosition,
    DutyQualification,
    PrototypeCase,
    Signal,
    SportlinkDutyRegistration,
)

FUNCTION_EXEMPT_ROLES = {
    "trainer",
    "teamleider",
    "commissielid",
    "bestuurslid",
    "ledenadministrateur",
    "beheerder CKC Kleding Beheer Tool",
}
DEFAULT_DUTY_POLICY = DutyPolicy(required_hours=10)


def _age(birth_date: date | None, today: date) -> int | None:
    if birth_date is None:
        return None
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _role_is_active(role, today: date) -> bool:
    return role.active and (role.start_date is None or role.start_date <= today) and (role.end_date is None or role.end_date >= today)


def _older_minor_family_subject(case: PrototypeCase, today: date) -> str | None:
    age = _age(case.person.birth_date, today)
    if age is None or age >= 18:
        return None

    parents = {
        rel.from_person_id
        for rel in case.relationships
        if rel.to_person_id == case.person.person_id
        and rel.relationship_type == "parent_guardian"
        and rel.active
    }
    if not parents:
        return None

    older = []
    for rel in case.relationships:
        if (
            rel.relationship_type != "parent_guardian"
            or not rel.active
            or rel.from_person_id not in parents
            or rel.to_person_id == case.person.person_id
        ):
            continue
        person = next((p for p in case.all_persons if p.person_id == rel.to_person_id), None)
        membership = next(
            (m for m in case.all_memberships if m.person_id == rel.to_person_id and m.status == "active"),
            None,
        )
        sibling_age = _age(person.birth_date, today) if person else None
        if (
            person
            and membership
            and sibling_age is not None
            and sibling_age < 18
            and person.birth_date
            and case.person.birth_date
            and person.birth_date < case.person.birth_date
        ):
            older.append(person)

    if not older:
        return None
    return sorted(older, key=lambda p: p.birth_date)[0].person_id


def derive_duty_qualification(case: PrototypeCase, today: date) -> DutyQualification:
    """Derive task duty from source facts only; no hours norm is applied here."""
    person_id = case.person.person_id
    membership = case.membership

    if membership.status != "active":
        return DutyQualification(person_id, False, "inactive_membership", person_id)
    if not membership.plays_football:
        return DutyQualification(person_id, False, "not_playing", person_id)
    if membership.honorary:
        return DutyQualification(person_id, False, "honorary", person_id)
    if membership.recreational:
        return DutyQualification(person_id, False, "recreational", person_id)

    exempt_roles = sorted(
        {
            role.role
            for role in case.roles
            if role.person_id == person_id and _role_is_active(role, today)
        }
        & FUNCTION_EXEMPT_ROLES
    )
    if exempt_roles:
        return DutyQualification(person_id, False, f"function:{exempt_roles[0]}", person_id)

    family_subject = _older_minor_family_subject(case, today)
    if family_subject:
        return DutyQualification(person_id, False, f"family_duty:{family_subject}", person_id)

    return DutyQualification(person_id, True, "playing_member", person_id)


def expected_required_hours(
    qualification: DutyQualification,
    policy: DutyPolicy = DEFAULT_DUTY_POLICY,
) -> int:
    """Apply CKC policy to the derived qualification."""
    return policy.required_hours if qualification.duty_required else 0


def duty_position_from_registration(registration: SportlinkDutyRegistration) -> DutyPosition:
    """Translate registered A/B/C/D to DutyPosition without inventing a missing A."""
    if registration.required_hours is None:
        raise ValueError("Sportlink required hours (A) are missing")
    return DutyPosition(
        A=registration.required_hours,
        B=registration.correction_hours,
        C=registration.completed_hours,
        D=registration.scheduled_hours,
    )


def evaluate_duty_foundation(
    case: PrototypeCase,
    today: date,
    policy: DutyPolicy = DEFAULT_DUTY_POLICY,
) -> Decision:
    """Compare derived duty + policy consequence with optional Sportlink administration."""
    qualification = derive_duty_qualification(case, today)
    expected = expected_required_hours(qualification, policy)
    registration = case.sportlink_duty
    registered = registration.required_hours if registration is not None else None
    comparison_performed = registration is not None

    facts = {
        "duty_required": qualification.duty_required,
        "qualification_reason": qualification.reason,
        "administrative_subject": qualification.administrative_subject_id,
        "policy_required_hours": policy.required_hours,
        "expected_required_hours": expected,
        "sportlink_required_hours": registered,
        "sportlink_comparison_performed": comparison_performed,
    }

    signals = ()
    status = "ok"
    message = "Taakplicht en urenverplichting reproduceerbaar afgeleid."
    if comparison_performed and registered != expected:
        signal = Signal(
            "sportlink_required_hours_mismatch",
            "Sportlink-registratie van verplichte taakuren wijkt af van de DVK-afleiding.",
            "attention",
            case.person.person_id,
            {"expected_required_hours": expected, "sportlink_required_hours": registered},
        )
        signals = (signal,)
        status = "attention"
        message = signal.message

    if registration is not None and registration.required_hours is not None:
        position = duty_position_from_registration(registration)
        facts["duty_position"] = {"A": position.A, "B": position.B, "C": position.C, "D": position.D, "E": position.E}

    return Decision("duty_foundation", status, message, facts, signals)
