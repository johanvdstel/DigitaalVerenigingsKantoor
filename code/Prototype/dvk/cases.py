from __future__ import annotations

from datetime import date

from .model import AccessGrant, AuthorityGrant, ClothingIssue, ComplianceFact, DutyRegistration, Membership, Person, PersonRelationship, PrototypeCase, Resource, RoleAssignment

TODAY = date(2026, 9, 4)
KLEDING = Resource("CKC Kleding Beheer Tool", "CKC Kleding Beheer Tool")
LEDEN = Resource("ledenadministratie", "CKC ledenadministratie", "gegevensverzameling")
KASSA = Resource("kassasysteem", "Digitaal kassasysteem")
BESTUUR = Resource("bestuursresource", "Bestuurlijke resource")


def p(i, name, born, mobile=None, address=None): return Person(i, name, born, mobile, address)
def m(i, status="active", kind="bondslid", **kw): return Membership(i, status, kind, **kw)
def role(i, name, **kw): return RoleAssignment(i, name, **kw)
def auth(aid, resource, actions, role_name=None, person_id=None, **kw): return AuthorityGrant(aid, resource, frozenset(actions), "DB", role_name, person_id, **kw)
def access(i, resource, actions): return AccessGrant(i, resource, frozenset(actions))
def rel(parent, child): return PersonRelationship(parent, child, "parent_guardian")

P03O = p("P03O", "Ouder Charlie", date(1980, 1, 1))
P04O = p("P04O", "Ouder Dani", date(1980, 2, 2))
P04A = p("P04A", "Ouder kind", date(2011, 2, 2))
P22O = p("P22O", "Ouder Tweehuizen", date(1980, 3, 3), address="Adres O")
P22A = p("P22A", "Kind Een", date(2011, 3, 3), address="Adres A")
P22B = p("P22B", "Kind Twee", date(2013, 3, 3), address="Adres B")

CASES = (
    PrototypeCase("C01", "Actief volwassen spelend lid met 4/10 uur", p("P01","Alex Actief",date(1995,5,1)), m("P01", plays_football=True), duty=DutyRegistration("P01", completed_hours=4)),
    PrototypeCase("C02", "Actief volwassen spelend lid heeft 10 uur voltooid", p("P02","Bo Voldoende",date(1990,6,12)), m("P02", plays_football=True), duty=DutyRegistration("P02", completed_hours=10)),
    PrototypeCase("C03", "Minderjarig eerste kind; ouder voert ledendienst uit", p("P03","Charlie Jeugd",date(2012,3,4)), m("P03", plays_football=True), persons=(P03O,), relationships=(rel("P03O","P03"),), duty=DutyRegistration("P03", completed_hours=0)),
    PrototypeCase("C04", "Jonger minderjarig kind heeft geen tweede gezinsverplichting", p("P04","Dani Jonger",date(2014,8,20)), m("P04", plays_football=True), persons=(P04O,P04A), memberships=(m("P04A", plays_football=True),), relationships=(rel("P04O","P04A"),rel("P04O","P04"))),
    PrototypeCase("C05", "Spelend trainer", p("P05","Evan Trainer",date(1986,2,17)), m("P05", plays_football=True), roles=(role("P05","trainer"),), compliance=(ComplianceFact("P05","VOG",True),)),
    PrototypeCase("C06", "Commissielid", p("P06","Fleur Commissie",date(1979,11,9)), m("P06",kind="verenigingslid"), roles=(role("P06","commissielid"),)),
    PrototypeCase("C07", "Eenmalige barvrijwilliger/ouder is geen lid", p("P07","Gio Ouder",date(1982,1,15)), m("P07","none","none"), roles=(role("P07","eenmalige barvrijwilliger"),)),
    PrototypeCase("C08", "Erelid", p("P08","Hanna Erelid",date(1958,7,30)), m("P08",kind="verenigingslid",honorary=True)),
    PrototypeCase("C09", "Recreant is vrijgesteld", p("P09","Ivo Recreant",date(1975,10,10)), m("P09",kind="verenigingslid",recreational=True), duty=DutyRegistration("P09", completed_hours=2)),
    PrototypeCase("C10", "Opgezegd lid met openstaande kleding", p("P10","Jules Uitgeschreven",date(2000,4,5)), m("P10","ended",end_date=date(2026,6,30),plays_football=True), clothing=(ClothingIssue("P10","wedstrijdshirt","M"),ClothingIssue("P10","trainingsbroek","M",returned=True))),
    PrototypeCase("C11", "Beheerder kledingtool correcte toegang", p("P11","Kim Kledingbeheer",date(1988,12,1)), m("P11",kind="verenigingslid"), roles=(role("P11","beheerder CKC Kleding Beheer Tool"),), authorities=(auth("A11",KLEDING.resource_id,{"read","update","manage_access"},"beheerder CKC Kleding Beheer Tool"),), resources=(KLEDING,), access=(access("P11",KLEDING.resource_id,{"read","update","manage_access"}),)),
    PrototypeCase("C12", "Niet-beheerder heeft manage_access", p("P12","Lars Teveel",date(1985,1,1)), m("P12",kind="verenigingslid"), authorities=(auth("A12",KLEDING.resource_id,{"read"},person_id="P12"),), resources=(KLEDING,), access=(access("P12",KLEDING.resource_id,{"read","manage_access"}),)),
    PrototypeCase("C13", "Ledenadministrateur correcte toegang", p("P13","Mila Ledenadmin",date(1984,2,1)), m("P13",kind="verenigingslid"), roles=(role("P13","ledenadministrateur"),), authorities=(auth("A13",LEDEN.resource_id,{"read","update"},"ledenadministrateur"),), resources=(LEDEN,), access=(access("P13",LEDEN.resource_id,{"read","update"}),)),
    PrototypeCase("C14", "Oud-bestuurslid heeft nog toegang", p("P14","Nora Oudbestuur",date(1970,2,1)), m("P14",kind="verenigingslid"), roles=(role("P14","bestuurslid",end_date=date(2026,8,1),active=False),), authorities=(auth("A14",BESTUUR.resource_id,{"read","update"},"bestuurslid"),), resources=(BESTUUR,), access=(access("P14",BESTUUR.resource_id,{"read","update"}),)),
    PrototypeCase("C15", "Nieuwe functionaris mist toegang", p("P15","Omar Nieuw",date(1981,2,1)), m("P15",kind="verenigingslid"), roles=(role("P15","ledenadministrateur",start_date=date(2026,9,1)),), authorities=(auth("A15",LEDEN.resource_id,{"read","update"},"ledenadministrateur"),), resources=(LEDEN,)),
    PrototypeCase("C16", "Toegang zonder bevoegdheidsgrond", p("P16","Puck Onverklaard",date(1982,2,1)), m("P16",kind="verenigingslid"), resources=(LEDEN,), access=(access("P16",LEDEN.resource_id,{"read"}),)),
    PrototypeCase("C17", "Persoon vervult twee functies", p("P17","Quinn Dubbelrol",date(1983,2,1)), m("P17",kind="verenigingslid"), roles=(role("P17","ledenadministrateur"),role("P17","bestuurslid")), authorities=(auth("A17a",LEDEN.resource_id,{"read","update"},"ledenadministrateur"),auth("A17b",BESTUUR.resource_id,{"read"},"bestuurslid")), resources=(LEDEN,BESTUUR), access=(access("P17",LEDEN.resource_id,{"read","update"}),access("P17",BESTUUR.resource_id,{"read"}))),
    PrototypeCase("C18", "Trainer zonder VOG", p("P18","Ravi Trainer",date(1987,2,1)), m("P18",kind="verenigingslid"), roles=(role("P18","trainer"),)),
    PrototypeCase("C19", "Barteamlid met ongerechtvaardigde update-toegang", p("P19","Sara Bar",date(1988,2,1)), m("P19",kind="verenigingslid"), roles=(role("P19","barteamlid"),), authorities=(auth("A19",KASSA.resource_id,{"read","use"},"barteamlid"),), resources=(KASSA,), access=(access("P19",KASSA.resource_id,{"read","use","update"}),)),
    PrototypeCase("C20", "Jeugdlid zonder ouder/verzorger", p("P20","Timo Jeugd",date(2012,2,1)), m("P20",plays_football=True)),
    PrototypeCase("C21", "Lid met mobiel nummer van 9 cijfers", p("P21","Uma Mobiel",date(1990,2,1),mobile="612345678"), m("P21",kind="verenigingslid")),
    PrototypeCase("C22", "Ouder met twee kinderen op verschillende adressen", P22A, m("P22A",plays_football=True), persons=(P22O,P22B), memberships=(m("P22B",plays_football=True),), relationships=(rel("P22O","P22A"),rel("P22O","P22B"))),
)

CASE_BY_ID = {case.case_id: case for case in CASES}
