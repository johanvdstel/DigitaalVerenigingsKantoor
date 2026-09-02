from __future__ import annotations

from datetime import date

from .model import (
    AccessGrant,
    ClothingIssue,
    DutyRegistration,
    Membership,
    Person,
    PrototypeCase,
    RoleAssignment,
)

TODAY = date(2026, 9, 2)


CASES: tuple[PrototypeCase, ...] = (
    PrototypeCase(
        case_id="C01",
        description="Actief volwassen spelend lid met nog openstaande ledendiensturen",
        person=Person("P01", "Alex Actief", date(1995, 5, 1)),
        membership=Membership("P01", "active", "bondslid", plays_football=True),
        duty=DutyRegistration("P01", required_hours=10, completed_hours=4),
    ),
    PrototypeCase(
        case_id="C02",
        description="Actief volwassen spelend lid heeft 10 uur voltooid",
        person=Person("P02", "Bo Voldoende", date(1990, 6, 12)),
        membership=Membership("P02", "active", "bondslid", plays_football=True),
        duty=DutyRegistration("P02", required_hours=10, completed_hours=10),
    ),
    PrototypeCase(
        case_id="C03",
        description="Minderjarig eerste kind: ouder/verzorger vervult ledendienst",
        person=Person("P03", "Charlie Jeugd", date(2012, 3, 4)),
        membership=Membership("P03", "active", "bondslid", plays_football=True),
        duty=DutyRegistration("P03", required_hours=10, completed_hours=0),
    ),
    PrototypeCase(
        case_id="C04",
        description="Jonger minderjarig kind vrijgesteld via broederdienst",
        person=Person("P04", "Dani Jonger", date(2014, 8, 20)),
        membership=Membership("P04", "active", "bondslid", plays_football=True),
        context={"broederdienst_exempt": True},
    ),
    PrototypeCase(
        case_id="C05",
        description="Spelend trainer: lid en vrijgesteld door erkende functie",
        person=Person("P05", "Evan Trainer", date(1986, 2, 17)),
        membership=Membership("P05", "active", "bondslid", plays_football=True),
        roles=(RoleAssignment("P05", "trainer"),),
    ),
    PrototypeCase(
        case_id="C06",
        description="Commissielid is statutair lid en vrijwilligersfunctie geeft vrijstelling",
        person=Person("P06", "Fleur Commissie", date(1979, 11, 9)),
        membership=Membership("P06", "active", "verenigingslid"),
        roles=(RoleAssignment("P06", "commissielid"),),
    ),
    PrototypeCase(
        case_id="C07",
        description="Eenmalige barvrijwilliger/ouder is geen lid",
        person=Person("P07", "Gio Ouder", date(1982, 1, 15)),
        membership=Membership("P07", "none", "none"),
        roles=(RoleAssignment("P07", "eenmalige barvrijwilliger"),),
    ),
    PrototypeCase(
        case_id="C08",
        description="Erelid is actief lid en vrijgesteld van ledendienst",
        person=Person("P08", "Hanna Erelid", date(1958, 7, 30)),
        membership=Membership("P08", "active", "verenigingslid", honorary=True),
    ),
    PrototypeCase(
        case_id="C09",
        description="Recreant is statutair lid, ook zonder competitieve voetbaldeelname",
        person=Person("P09", "Ivo Recreant", date(1975, 10, 10)),
        membership=Membership(
            "P09", "active", "verenigingslid",
            plays_football=False, recreational=True
        ),
        duty=DutyRegistration("P09", required_hours=10, completed_hours=2),
    ),
    PrototypeCase(
        case_id="C10",
        description="Opgezegd lid heeft uitgegeven CKC-kleding nog niet ingeleverd",
        person=Person("P10", "Jules Uitgeschreven", date(2000, 4, 5)),
        membership=Membership(
            "P10", "ended", "bondslid",
            end_date=date(2026, 6, 30),
            plays_football=True,
        ),
        clothing=(
            ClothingIssue("P10", "wedstrijdshirt", "M", returned=False),
            ClothingIssue("P10", "trainingsbroek", "M", returned=True),
        ),
    ),
    PrototypeCase(
        case_id="C11",
        description="Beheerder CKC Kleding Beheer Tool mag rechten beheren en delegeren",
        person=Person("P11", "Kim Kledingbeheer", date(1988, 12, 1)),
        membership=Membership("P11", "active", "verenigingslid"),
        roles=(RoleAssignment("P11", "beheerder CKC Kleding Beheer Tool"),),
        access=(
            AccessGrant(
                "P11",
                "CKC Kleding Beheer Tool",
                frozenset({"read", "update", "manage_access"}),
                delegated_by="DB",
            ),
        ),
    ),
)


CASE_BY_ID = {case.case_id: case for case in CASES}
