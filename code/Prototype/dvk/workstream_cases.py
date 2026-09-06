from __future__ import annotations

from datetime import date

from .model import Membership, Person, PersonRelationship, PrototypeCase, SportlinkDutyRegistration

TODAY = date(2026, 9, 4)

W_CASES = (
    PrototypeCase(
        "W01", "Taakplicht automatisch afgeleid",
        Person("W01P", "Senior Taakplicht", date(1990, 5, 1)),
        Membership("W01P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W02", "Afwijkende Sportlink-administratie",
        Person("W02P", "Senior Afwijking", date(1991, 6, 1)),
        Membership("W02P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration("W02P", required_hours=None),
    ),
    PrototypeCase(
        "W03", "Senior taakplichtig lid met thuiswedstrijd op dienstdag",
        Person("W03P", "Senior Thuiswedstrijd", date(1992, 3, 1)),
        Membership("W03P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W04", "Minderjarig jeugdlid: ouder/verzorger is uitvoerdercategorie",
        Person("W04P", "Jeugdlid Thuis", date(2012, 4, 10)),
        Membership("W04P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W05", "Vijftienjarig jeugdlid",
        Person("W05P", "Jeugdlid Vijftien", date(2011, 2, 1)),
        Membership("W05P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W06", "Zeventienjarig jeugdlid en overgang naar meerderjarigheid",
        Person("W06P", "Jeugdlid Zeventien", date(2008, 10, 1)),
        Membership("W06P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W07", "Urenpositie A=10 B=0 C=4 D=3",
        Person("W07P", "Senior Urenpositie", date(1989, 7, 1)),
        Membership("W07P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration("W07P", required_hours=10, correction_hours=0, completed_hours=4, scheduled_hours=3),
    ),
    PrototypeCase(
        "W08", "Grotere actuele E krijgt hogere prioriteit",
        Person("W08P", "Senior Grote E", date(1987, 4, 1)),
        Membership("W08P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration("W08P", required_hours=10, correction_hours=0, completed_hours=1, scheduled_hours=1),
    ),
    PrototypeCase(
        "W09", "Relevante achterstand vorig seizoen wordt vóór 1 december meegewogen",
        Person("W09P", "Senior Oude Achterstand", date(1986, 9, 1)),
        Membership("W09P", "active", "bondslid", plays_football=True),
        sportlink_duty=SportlinkDutyRegistration("W09P", required_hours=10, correction_hours=0, completed_hours=4, scheduled_hours=3),
    ),
    PrototypeCase(
        "W10", "Senior taakplichtig lid met uitwedstrijd op dienstdag",
        Person("W10P", "Senior Uitwedstrijd", date(1993, 8, 1)),
        Membership("W10P", "active", "bondslid", plays_football=True),
    ),
    PrototypeCase(
        "W13", "Familieverplichting: jonger minderjarig kind veroorzaakt geen tweede verplichting",
        Person("W13Y", "Jonger Kind", date(2013, 6, 1)),
        Membership("W13Y", "active", "bondslid", plays_football=True),
        persons=(Person("W13O", "Ouder", date(1980, 1, 1)), Person("W13E", "Ouder Kind", date(2010, 5, 1))),
        memberships=(Membership("W13E", "active", "bondslid", plays_football=True),),
        relationships=(
            PersonRelationship("W13O", "W13E", "parent_guardian"),
            PersonRelationship("W13O", "W13Y", "parent_guardian"),
        ),
    ),
)

W_CASE_BY_ID = {case.case_id: case for case in W_CASES}
