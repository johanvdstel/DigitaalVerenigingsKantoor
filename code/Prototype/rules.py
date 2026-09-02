from __future__ import annotations

from datetime import date

from .model import Decision, PrototypeCase


CLOTHING_SYSTEM = "CKC Kleding Beheer Tool"
LEDENDIENST_HOURS = 10

# In het prototype behandelen we deze rollen als een door CKC erkende
# structurele vrijwilligersfunctie die vrijstelling van de urenplicht kan geven.
FUNCTION_EXEMPT_ROLES = {
    "trainer",
    "teamleider",
    "commissielid",
    "bestuurslid",
    "ledenadministrateur",
    "beheerder CKC Kleding Beheer Tool",
}


def _age_on(birth_date: date | None, on_date: date) -> int | None:
    if birth_date is None:
        return None
    return (
        on_date.year
        - birth_date.year
        - ((on_date.month, on_date.day) < (birth_date.month, birth_date.day))
    )


def evaluate_membership(case: PrototypeCase, today: date) -> Decision:
    membership = case.membership

    if membership.status == "none":
        return Decision(
            code="membership",
            status="not_applicable",
            message="Persoon heeft geen CKC-lidmaatschap.",
        )

    if membership.status == "ended":
        return Decision(
            code="membership",
            status="attention",
            message="Lidmaatschap is beëindigd.",
            facts={"end_date": membership.end_date.isoformat() if membership.end_date else None},
        )

    return Decision(
        code="membership",
        status="ok",
        message="Actief CKC-lidmaatschap.",
        facts={
            "kind": membership.kind,
            "plays_football": membership.plays_football,
            "recreational": membership.recreational,
            "honorary": membership.honorary,
        },
    )


def evaluate_ledendienst(case: PrototypeCase, today: date) -> Decision:
    membership = case.membership
    active_roles = {r.role for r in case.roles if r.active}

    if membership.status != "active":
        return Decision(
            code="ledendienst",
            status="not_applicable",
            message="Geen urenplicht bij niet-actief lidmaatschap.",
        )

    if membership.honorary:
        return Decision(
            code="ledendienst",
            status="ok",
            message="Vrijgesteld als erelid.",
            facts={"exempt_reason": "erelid"},
        )

    exempt_roles = sorted(active_roles & FUNCTION_EXEMPT_ROLES)
    if exempt_roles:
        return Decision(
            code="ledendienst",
            status="ok",
            message="Vrijgesteld op basis van erkende vrijwilligersfunctie.",
            facts={"exempt_roles": exempt_roles},
        )

    if bool(case.context.get("broederdienst_exempt")):
        return Decision(
            code="ledendienst",
            status="ok",
            message="Vrijgesteld door broederdienst-regel.",
            facts={"exempt_reason": "broederdienst"},
        )

    age = _age_on(case.person.birth_date, today)
    actor = "lid"
    if age is not None and age < 18:
        actor = "ouder/verzorger namens minderjarig lid"

    completed = case.duty.completed_hours if case.duty else 0
    remaining = max(0, LEDENDIENST_HOURS - completed)
    status = "ok" if remaining == 0 else "attention"

    return Decision(
        code="ledendienst",
        status=status,
        message=(
            "Ledendienstplicht voldaan."
            if remaining == 0
            else f"Nog {remaining} uur ledendienst te vervullen."
        ),
        facts={
            "required_hours": LEDENDIENST_HOURS,
            "completed_hours": completed,
            "remaining_hours": remaining,
            "actor": actor,
        },
    )


def evaluate_clothing(case: PrototypeCase, today: date) -> Decision:
    outstanding = [
        {"article": item.article, "size": item.size}
        for item in case.clothing
        if not item.returned
    ]

    if not outstanding:
        return Decision(
            code="clothing",
            status="ok",
            message="Geen openstaande CKC-kleding.",
        )

    if case.membership.status == "ended":
        return Decision(
            code="clothing",
            status="attention",
            message="Uitgeschreven lid heeft CKC-kleding nog niet ingeleverd.",
            facts={"outstanding": outstanding},
        )

    return Decision(
        code="clothing",
        status="ok",
        message="CKC-kleding is geregistreerd als uitgegeven.",
        facts={"outstanding": outstanding},
    )


def evaluate_clothing_access(case: PrototypeCase, today: date) -> Decision:
    grants = [g for g in case.access if g.system == CLOTHING_SYSTEM]
    if not grants:
        return Decision(
            code="clothing_access",
            status="not_applicable",
            message="Geen toegang tot CKC Kleding Beheer Tool.",
        )

    levels = set().union(*(set(g.levels) for g in grants))

    is_manager = any(
        r.active and r.role == "beheerder CKC Kleding Beheer Tool"
        for r in case.roles
    )

    if "manage_access" in levels and not is_manager:
        return Decision(
            code="clothing_access",
            status="blocked",
            message="Alleen de beheerder CKC Kleding Beheer Tool mag toegangsrechten beheren.",
            facts={"levels": sorted(levels)},
        )

    if is_manager and {"read", "update", "manage_access"}.issubset(levels):
        return Decision(
            code="clothing_access",
            status="ok",
            message="Beheerder heeft raadpleeg-, update- en toegangsbeheerrechten.",
            facts={"levels": sorted(levels)},
        )

    return Decision(
        code="clothing_access",
        status="ok",
        message="Gedelegeerde toegang is geldig binnen de toegekende rechten.",
        facts={"levels": sorted(levels)},
    )
