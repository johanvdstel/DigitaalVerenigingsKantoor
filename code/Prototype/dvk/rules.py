from __future__ import annotations

import re
from datetime import date

from .model import Action, Decision, PrototypeCase, Signal

LEDENDIENST_HOURS = 10
FUNCTION_EXEMPT_ROLES = {"trainer", "teamleider", "commissielid", "bestuurslid", "ledenadministrateur", "beheerder CKC Kleding Beheer Tool"}


def _age(birth_date: date | None, today: date) -> int | None:
    if birth_date is None:
        return None
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def _active_role(case: PrototypeCase, role: str, today: date) -> bool:
    return any(r.person_id == case.person.person_id and r.role == role and r.active and (r.start_date is None or r.start_date <= today) and (r.end_date is None or r.end_date >= today) for r in case.roles)


def evaluate_membership(case: PrototypeCase, today: date) -> Decision:
    m = case.membership
    if m.status == "none":
        return Decision("membership", "not_applicable", "Persoon heeft geen CKC-lidmaatschap.")
    if m.status == "ended":
        return Decision("membership", "attention", "Lidmaatschap is beëindigd.", {"end_date": m.end_date.isoformat() if m.end_date else None})
    return Decision("membership", "ok", "Actief CKC-lidmaatschap.", {"kind": m.kind, "plays_football": m.plays_football, "recreational": m.recreational, "honorary": m.honorary})


def evaluate_relationships(case: PrototypeCase, today: date) -> Decision:
    if _age(case.person.birth_date, today) is None or _age(case.person.birth_date, today) >= 18:
        return Decision("relationships", "not_applicable", "Geen minderjarigheidscontrole nodig.")
    links = [
        {"parent_guardian": r.from_person_id, "child": r.to_person_id}
        for r in case.relationships
        if r.relationship_type == "parent_guardian" and r.active
    ]
    parents = [link["parent_guardian"] for link in links if link["child"] == case.person.person_id]
    if not parents:
        sig = Signal("missing_parent_guardian", "Minderjarig lid heeft geen geregistreerde ouder/verzorger.", "error", case.person.person_id)
        action = Action(
            "investigate_parent_guardian",
            case.person.person_id,
            "ledenadministrateur",
            "Onderzoek en registreer de ontbrekende ouder/verzorgerrelatie; verzin geen relatie zonder bronfeit.",
        )
        return Decision("relationships", "error", sig.message, {"parent_guardians": [], "parent_guardian_links": links}, (sig,), (action,))
    return Decision("relationships", "ok", "Ouder/verzorgerrelatie geregistreerd.", {"parent_guardians": parents, "parent_guardian_links": links})


def evaluate_ledendienst(case: PrototypeCase, today: date) -> Decision:
    m = case.membership
    if m.status != "active":
        return Decision("ledendienst", "not_applicable", "Geen urenplicht bij niet-actief lidmaatschap.")
    if m.honorary:
        return Decision("ledendienst", "ok", "Vrijgesteld als erelid.", {"exempt_reason": "erelid"})
    if m.recreational:
        return Decision("ledendienst", "ok", "Recreatieve speler is vrijgesteld van ledendienst.", {"exempt_reason": "recreatief"})
    roles = sorted({r.role for r in case.roles if r.person_id == case.person.person_id and r.active} & FUNCTION_EXEMPT_ROLES)
    if roles:
        return Decision("ledendienst", "ok", "Vrijgesteld op basis van erkende vrijwilligersfunctie.", {"exempt_roles": roles})

    age = _age(case.person.birth_date, today)
    actor = case.person.person_id
    if age is not None and age < 18:
        parents = [r.from_person_id for r in case.relationships if r.to_person_id == case.person.person_id and r.relationship_type == "parent_guardian" and r.active]
        actor = parents[0] if parents else None
        # Een ouder/verzorger heeft per beleidsperiode slechts één verplichting namens minderjarige kinderen.
        if parents:
            siblings = []
            for rel in case.relationships:
                if rel.relationship_type == "parent_guardian" and rel.active and rel.from_person_id in parents and rel.to_person_id != case.person.person_id:
                    p = next((x for x in case.all_persons if x.person_id == rel.to_person_id), None)
                    mm = next((x for x in case.all_memberships if x.person_id == rel.to_person_id and x.status == "active"), None)
                    sibling_age = _age(p.birth_date, today) if p else None
                    if p and mm and sibling_age is not None and sibling_age < 18:
                        siblings.append(p)
            older = [p for p in siblings if p.birth_date and case.person.birth_date and p.birth_date < case.person.birth_date]
            if older:
                family_subject = sorted(older, key=lambda p: p.birth_date)[0]
                return Decision(
                    "ledendienst",
                    "ok",
                    f"Geen tweede gezinsverplichting; verplichting rust op ouder/verzorger namens ouder minderjarig kind {family_subject.person_id}.",
                    {"exempt_reason": "gezinsverplichting", "actor": actor, "family_duty_subject": family_subject.person_id},
                )

    completed = case.duty.completed_hours if case.duty else 0
    remaining = max(0, LEDENDIENST_HOURS - completed)
    status = "ok" if remaining == 0 else "attention"
    actions = ()
    # De verantwoordelijkheid blijft bij het volwassen lid; DVK kan de Vrijwilligerscommissie wel een planningsvoorstel doen.
    if remaining > 0 and age is not None and age >= 18 and actor == case.person.person_id and case.duty is not None:
        actions = (
            Action(
                "propose_duty_scheduling",
                case.person.person_id,
                "vrijwilligerscommissie",
                f"Stel voor het lid in te roosteren voor de resterende {remaining} uur ledendienst; de verantwoordelijkheid voor vervulling blijft bij het lid.",
                facts={"remaining_hours": remaining},
            ),
        )
    return Decision("ledendienst", status, "Ledendienstplicht voldaan." if remaining == 0 else f"Nog {remaining} uur ledendienst te vervullen.", {"required_hours": LEDENDIENST_HOURS, "completed_hours": completed, "remaining_hours": remaining, "actor": actor}, actions=actions)


def evaluate_clothing(case: PrototypeCase, today: date) -> Decision:
    outstanding = [{"article": x.article, "size": x.size} for x in case.clothing if not x.resolved]
    if not outstanding:
        return Decision("clothing", "ok", "Geen openstaande CKC-kleding.")
    if case.membership.status == "ended":
        sig = Signal("outstanding_clothing", "Uitgeschreven lid heeft CKC-kleding nog niet ingeleverd of financieel afgehandeld.", "error", case.person.person_id, {"outstanding": outstanding})
        actions = (
            Action(
                "send_email",
                case.person.person_id,
                "ledenadministrateur",
                "Verzoek kleding in te leveren of restwaarde te betalen en melden dat geen vrijgave voor overschrijving plaatsvindt zolang de kledingkwestie niet is afgehandeld.",
            ),
            Action("block_transfer_release", case.person.person_id, "ledenadministrateur", "Kledingkwestie is nog niet afgehandeld.", "active"),
        )
        return Decision("clothing", "blocked", sig.message, {"outstanding": outstanding, "transfer_release_blocked": True}, (sig,), actions)
    return Decision("clothing", "ok", "CKC-kleding is geregistreerd als uitgegeven.", {"outstanding": outstanding})


def evaluate_authorization(case: PrototypeCase, today: date) -> Decision:
    actual: dict[str, set[str]] = {}
    for grant in case.access:
        actual.setdefault(grant.resource_id, set()).update(grant.levels)

    required: dict[str, set[str]] = {}
    authority_ids: dict[str, list[str]] = {}
    active_roles = {r.role for r in case.roles if r.person_id == case.person.person_id and r.active and (r.start_date is None or r.start_date <= today) and (r.end_date is None or r.end_date >= today)}
    for auth in case.authorities:
        valid = auth.active and (auth.start_date is None or auth.start_date <= today) and (auth.end_date is None or auth.end_date >= today)
        applies = (auth.person_id == case.person.person_id) or (auth.role is not None and auth.role in active_roles)
        if valid and applies:
            required.setdefault(auth.resource_id, set()).update(auth.actions)
            authority_ids.setdefault(auth.resource_id, []).append(auth.authority_id)

    missing = {res: sorted(req - actual.get(res, set())) for res, req in required.items() if req - actual.get(res, set())}
    unexplained: dict[str, list[str]] = {}
    excess: dict[str, list[str]] = {}
    for res, act in actual.items():
        extra = act - required.get(res, set())
        if not extra:
            continue
        has_known_context = bool(case.authorities or case.roles)
        if res not in required and not has_known_context:
            unexplained[res] = sorted(extra)
        else:
            excess[res] = sorted(extra)

    facts = {
        "required": {k: sorted(v) for k, v in required.items()},
        "actual": {k: sorted(v) for k, v in actual.items()},
        "missing": missing,
        "excess": excess,
        "unexplained": unexplained,
        "authority_ids": authority_ids,
    }
    signals = []
    actions = []

    if missing:
        signals.append(Signal("missing_authorization", "Benodigde feitelijke toegang ontbreekt.", "error", case.person.person_id, missing))
        actions.append(Action("grant_access", case.person.person_id, "toegangsbeheerder", "Feitelijke toegang in overeenstemming brengen met geldige bevoegdheid.", facts=missing))
    if excess:
        signals.append(Signal("excess_authorization", "Feitelijke toegang is ruimer dan de bekende geldige bevoegdheid.", "error", case.person.person_id, excess))
        actions.append(Action("revoke_access", case.person.person_id, "toegangsbeheerder", "Onbevoegde of achtergebleven toegang intrekken.", facts=excess))
    if unexplained:
        signals.append(Signal("unexplained_authorization", "Feitelijke toegang heeft geen bekende actuele bevoegdheidsgrond en moet worden onderzocht.", "attention", case.person.person_id, unexplained))
        actions.append(Action("investigate_authorization", case.person.person_id, "toegangsbeheerder", "Onderzoek de bevoegdheidsgrond; trek toegang alleen in als geen geldige grond blijkt te bestaan.", facts=unexplained))

    if missing or excess:
        return Decision("authorization", "blocked", "Feitelijke en gewenste autorisatie wijken af.", facts, tuple(signals), tuple(actions))
    if unexplained:
        return Decision("authorization", "attention", "Feitelijke toegang is onverklaard en vereist onderzoek.", facts, tuple(signals), tuple(actions))
    if not actual and not required:
        return Decision("authorization", "not_applicable", "Geen autorisatiecontrole van toepassing.", facts)
    return Decision("authorization", "ok", "Feitelijke toegang komt overeen met geldige bevoegdheid.", facts)


def evaluate_compliance(case: PrototypeCase, today: date) -> Decision:
    if not _active_role(case, "trainer", today):
        return Decision("compliance", "not_applicable", "Geen VOG-controle voor deze functie.")
    vog = [c for c in case.compliance if c.person_id == case.person.person_id and c.compliance_type == "VOG" and c.valid and (c.valid_until is None or c.valid_until >= today)]
    if vog:
        return Decision("compliance", "ok", "Geldige VOG geregistreerd.", {"vog_valid": True})
    sig = Signal("missing_vog", "Trainer heeft geen geldige geregistreerde VOG.", "error", case.person.person_id)
    action = Action("start_vog_followup", case.person.person_id, "VOG-beheerder", "Trainerfunctie vereist geldige VOG.")
    return Decision("compliance", "error", sig.message, {"vog_valid": False}, (sig,), (action,))


def evaluate_data_quality(case: PrototypeCase, today: date) -> Decision:
    signals = []
    actions = []
    mobile = case.person.mobile_number
    if mobile is not None:
        digits = re.sub(r"\D", "", mobile)
        if len(digits) == 9:
            signals.append(Signal("invalid_mobile", "Mobiel telefoonnummer bevat slechts 9 cijfers.", "error", case.person.person_id, {"mobile_number": mobile}))
            actions.append(Action("request_data_correction", case.person.person_id, "ledenadministrateur", "Mobiel telefoonnummer corrigeren."))
    # Verschillende adressen binnen een expliciete ouder-kindrelatie zijn mogelijk en dus geen fout.
    address_anomaly = False
    for rel in case.relationships:
        if rel.relationship_type == "parent_guardian" and rel.active:
            parent = next((p for p in case.all_persons if p.person_id == rel.from_person_id), None)
            child = next((p for p in case.all_persons if p.person_id == rel.to_person_id), None)
            if parent and child and parent.address and child.address and parent.address != child.address:
                address_anomaly = True
    if signals:
        return Decision("data_quality", "error", "Datakwaliteitsprobleem gevonden.", {"address_difference_possible": address_anomaly}, tuple(signals), tuple(actions))
    return Decision("data_quality", "ok", "Geen blokkerend datakwaliteitsprobleem gevonden.", {"address_difference_possible": address_anomaly})
