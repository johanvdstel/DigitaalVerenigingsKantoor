# CKC Gegevenswoordenboek & Bronnenmapping

**Versie:** 0.1  
**Status:** Werkversie / ontwerpbaseline  
**Datum:** 29 augustus 2026  
**Onderdeel van:** Digitaal Verenigingskantoor – Ledenadministratie

## 1. Doel

Dit document legt de gemeenschappelijke betekenis van kerngegevens vast en koppelt die aan de systemen waarin de gegevens momenteel of in de toekomst worden geregistreerd.

Het document vormt de brug tussen het [CKC Personenmodel](personenmodel.md), het [Logisch Informatiemodel](logisch-informatiemodel.md) en de feitelijke CKC-bronnen.

De mapping is in versie 0.1 nadrukkelijk nog niet volledig op veldniveau. Waar bronhouderschap nog moet worden vastgesteld, staat dat expliciet aangegeven.

## 2. Bronsystemen

### 2.1 Sportlink Club

Belangrijk operationeel bronsysteem voor leden- en voetbalgerelateerde registratie.

Bekende relevante informatie omvat onder andere:

- persoonsgegevens;
- adresgegevens;
- contactgegevens;
- lidsoort;
- functies;
- teamkoppelingen;
- lidmaatschapsinformatie;
- KNVB-gerelateerde gegevens.

Sportlink kent onder meer de categorieën **Bondslid**, **Verenigingslid** en **Relatie**. Deze categorieën worden niet één-op-één overgenomen als CKC-begrippenmodel.

### 2.2 CKC Access-database

Historische/lokale CKC-administratie die aanvullende gegevens kan bevatten die niet of onvoldoende in Sportlink worden bewaard.

Een belangrijk voorbeeld is detailhistorie van meerdere start- en eindperioden van lidmaatschappen.

### 2.3 Sponsit

CRM voor sponsorgerelateerde zaken.

Bekende informatie omvat:

- NAW-gegevens;
- contactpersonen;
- sponsorrelaties;
- contracten;
- facturen;
- taken;
- afspraken.

### 2.4 CKC-inschrijfformulier / KNVB `club_aanmelden`

Huidige voorkeursroute voor het aanmelden van nieuwe leden via de CKC-website.

Bekende verplichte gegevens omvatten onder andere:

- postcode;
- huisnummer;
- straatnaam;
- woonplaats;
- e-mail + herhaling;
- IBAN;
- tenaamstelling.

CKC wil daarnaast bij inschrijving onder andere **voornaam**, **tussenvoegsel** en **mobiel telefoonnummer** afdwingen, ook waar die niet vanuit KNVB verplicht zijn.

### 2.5 Toekomstige CKC-kernregistratie

De beoogde eigen informatievoorziening van het Digitaal Verenigingskantoor.

Deze registratie hoeft niet alle bronsystemen te vervangen. Zij moet wel een coherent CKC-beeld kunnen vormen, inclusief bronverwijzing, historie, afleidingen en beleidsregels.

## 3. Begrippenwoordenboek

| Begrip | Definitie | Type | Mogelijke bron(nen) | Opmerking |
|---|---|---|---|---|
| Partij | Natuurlijk persoon of organisatie die voor CKC relevant is | Kernbegrip | Meerdere | Overkoepelend begrip |
| Persoon | Natuurlijk persoon | Bronobject | Sportlink, Access, Sponsit, inschrijving | Identiteit staat los van CKC-relaties |
| Organisatie | Bedrijf, instelling, instantie of andere organisatorische partij | Bronobject | Sponsit, toekomstige CKC-registratie | O.a. leverancier, sponsor, overheid |
| Lidmaatschap | Formele relatie waarbij een Persoon lid van CKC is gedurende een periode | Bronfeit | Sportlink, Access, CKC-besluit | Historie kan over bronnen verdeeld zijn |
| Voetbaldeelname | Feit dat een Persoon gedurende een periode aan een voetbalvorm deelneemt | Bronfeit | Sportlink, CKC-registratie | Los van lidmaatschap modelleren |
| Functionele rol | Functie die een Persoon gedurende een periode voor CKC vervult | Bronfeit | Sportlink, CKC-registratie | O.a. trainer, commissielid |
| Organisatorische eenheid | Team, commissie, bestuur of andere CKC-groep | Bronobject | Sportlink, CKC-registratie | Lokale teamnamen kunnen hier thuishoren |
| Persoonlijke relatie | Functioneel relevante relatie tussen Personen | Bronfeit | Inschrijving, CKC-registratie | O.a. ouder/verzorger |
| Bijzondere kwalificatie | Expliciet door CKC toegekende bijzondere status | Bronfeit | CKC-besluit, Sportlink/Access indien geregistreerd | O.a. erelid, lid van verdienste |
| Zakelijke/externe relatie | Niet-primaire ledenrelatie tussen CKC en een Partij | Bronfeit | Sponsit, CKC-registratie | O.a. leverancier, overheid |
| Sponsorrelatie | Zakelijke relatie waarin een Partij sponsor van CKC is | Bronfeit | Sponsit | Contracten e.d. blijven gekoppeld |
| Afgeleide kwalificatie | Reproduceerbare classificatie uit één of meer bronfeiten | Afleiding | CKC-regellaag | O.a. oud-lid, spelend trainer |
| Beleidsregel | Vastgestelde CKC-regel die feiten omzet in gevolgen | Beleid | CKC-regelrepository | Bij voorkeur versieerbaar |
| Beleidsgevolg | Uitkomst van een beleidsregel voor een Partij | Afgeleid beleid | Digitaal Verenigingskantoor | O.a. contributiepositie |
| Bronverwijzing | Herkomst van een geregistreerd feit | Metadata | Alle bronnen | Nodig voor audittrail |

## 4. Persoonsgegevens: voorlopige mapping

| CKC-gegeven | Betekenis | Huidige/waarschijnlijke bron | Opmerking |
|---|---|---|---|
| Voornaam | Gebruikelijke/formeel geregistreerde voornaam | Inschrijving, Sportlink | CKC wil dit bij inschrijving verplicht |
| Tussenvoegsel | Tussenvoegsel bij achternaam | Inschrijving, Sportlink | CKC wil dit waar van toepassing vastleggen |
| Achternaam | Achternaam van Persoon | Inschrijving, Sportlink | Kernidentificatie |
| Geboortedatum | Geboortedatum | Inschrijving, Sportlink | Relevant voor leden/voetbal |
| Postcode | Postcode woonadres | Inschrijving, Sportlink | Verplicht in huidige aanmeldroute |
| Huisnummer | Huisnummer woonadres | Inschrijving, Sportlink | Verplicht |
| Straatnaam | Straat woonadres | Inschrijving, Sportlink | Verplicht |
| Woonplaats | Woonplaats | Inschrijving, Sportlink | Verplicht |
| E-mailadres | Primair e-mailadres | Inschrijving, Sportlink | Huidig formulier vraagt bevestiging |
| Mobiel telefoonnummer | Mobiel contactnummer | Inschrijving, Sportlink | CKC wil dit verplicht stellen |
| IBAN | Rekeningnummer voor betaling/incasso | Inschrijving, Sportlink/financiële registratie | Toegang beperken vanwege gevoeligheid |
| Tenaamstelling | Naam rekeninghouder | Inschrijving, financiële registratie | Hoort bij betaalrelatie |

## 5. Lidmaatschap en deelname: voorlopige mapping

| CKC-gegeven | Betekenis | Bron(nen) | Mapping-/kwaliteitsvraag |
|---|---|---|---|
| Actueel lidmaatschap | Persoon is op peildatum statutair lid | Sportlink + CKC-regels | Sportlink-lidsoort niet zonder meer gelijkstellen aan statutair lid |
| Lidmaatschapsperiode | Begin- en einddatum van een lidmaatschap | Sportlink, Access | Access kan rijkere historie bevatten |
| Sportlink-lidsoort | Technische/functionele Sportlink-classificatie | Sportlink | Bondslid / Verenigingslid / Relatie als bronwaarde bewaren |
| Status lidmaatschap | Lokaal vrij invoerveld in huidige inrichting | Sportlink | Bevat heterogene waarden; niet als zuiver kernbegrip gebruiken |
| Voetbaldeelname | Feitelijke deelname aan voetbal | Sportlink teams/functies + CKC-regels | Expliciet CKC-bronfeit van maken |
| Recreatieve deelname | Deelname aan recreatieve voetbalvorm | Sportlink/lokaal team | Oldstars e.d. als team/groep, niet als statutair type |
| Competitieve deelname | Deelname aan competitievoetbal | Sportlink | Precieze bronlogica nog vaststellen |

## 6. Rollen: voorlopige mapping

| CKC-gegeven | Betekenis | Bron(nen) | Opmerking |
|---|---|---|---|
| Trainer | Persoon vervult trainersfunctie | Sportlink / CKC | Kan zonder lidmaatschap bestaan |
| Teamleider | Persoon vervult teamleidersfunctie | Sportlink / CKC | Koppeling aan team |
| Scheidsrechter | Persoon vervult scheidsrechtersfunctie | Sportlink / CKC | Bond/clubonderscheid later detailleren |
| Commissielid | Persoon is lid van CKC-commissie | Sportlink / CKC | Bij CKC relevant voor statutair lidmaatschap |
| Bestuurslid | Persoon vervult bestuursfunctie | Sportlink / CKC | Formele functie |
| Vrijwilliger | Persoon verricht vrijwilligerswerk | Sportlink / CKC | Niet iedere incidentele bardienst maakt iemand commissielid of statutair lid |

## 7. Bijzondere kwalificaties

| CKC-gegeven | Betekenis | Bron | Opmerking |
|---|---|---|---|
| Erelid | Door CKC toegekende kwalificatie erelid | CKC-besluit; huidige registratie nader bepalen | Niet reduceren tot vrije statuswaarde |
| Lid van verdienste | Door CKC toegekende kwalificatie lid van verdienste | CKC-besluit; huidige registratie nader bepalen | Afzonderlijk van lidmaatschap |
| Oud-lid | Persoon met historisch maar geen actueel lidmaatschap | Afgeleid uit historie | Geen zelfstandig bronfeit |
| Spelend trainer | Persoon met voetbaldeelname én trainersrol | Afgeleid | Geen zelfstandig persoonstype |

## 8. Zakelijke en externe relaties

| CKC-gegeven | Betekenis | Bron | Opmerking |
|---|---|---|---|
| Leverancier | Organisatie/Persoon levert goederen of diensten aan CKC | CKC-registratie, financiële bron nader bepalen | Contactpersonen afzonderlijk modelleren |
| Sponsor | Partij heeft sponsorrelatie met CKC | Sponsit | Sponsit is primaire operationele bron voor sponsorzaken |
| Sponsorcontract | Contract behorend bij sponsorrelatie | Sponsit | Contract is geen eigenschap van Persoon |
| Sponsorafspraak | Afspraak met sponsor/contactpersoon | Sponsit | CRM-informatie |
| Sponsortaak | Taak in sponsorproces | Sponsit | Procesinformatie |
| Sponsorfactuur | Factuur in sponsorcontext | Sponsit | Relatie met financiële administratie nader bepalen |
| Externe instantie | Organisatie met institutionele relatie tot CKC | CKC-registratie | O.a. Sportbedrijf, gemeente, tuchtcommissie |
| Extern contactpersoon | Persoon die namens externe Organisatie optreedt | CKC-registratie/Sponsit | Persoon koppelen aan Organisatie en relatie |

## 9. Bronnenmatrix

| Informatiedomein | Sportlink | Access | Sponsit | Inschrijving | Toekomstige CKC-kern |
|---|---|---|---|---|---|
| Persoonsidentiteit leden | Sterk | Aanvullend/historisch | Alleen sponsorcontext | Initiële bron | Geïntegreerd beeld |
| Contactgegevens leden | Sterk | Mogelijk | Sponsorcontext | Initiële bron | Geïntegreerd beeld |
| Lidmaatschap actueel | Sterk | Aanvullend | Nee | Aanvraagfase | Geïntegreerd/afgeleid |
| Lidmaatschap historie | Beperkt | Sterk/aanvullend | Nee | Nee | Te consolideren |
| Voetbaldeelname | Sterk maar deels impliciet | Mogelijk | Nee | Beoogde deelname | Expliciet logisch feit |
| Functies | Sterk voor Sportlink-functies | Mogelijk | Sponsorcontacten/taken | Beperkt | Geïntegreerd |
| Commissies | Aanwezig maar kwaliteit wisselend | Mogelijk | Nee | Nee | Explicieter modelleren |
| Erelid / lid van verdienste | Huidige registratie nader bepalen | Mogelijk | Nee | Nee | Zuiver kernbegrip |
| Sponsors | Beperkt/niet leidend | Nee | Sterk | Nee | Verwijzing/geïntegreerd beeld |
| Leveranciers | Niet primair | Mogelijk | Mogelijk indien CRM-gebruikt | Nee | Nog te bepalen |
| Externe organisaties | Niet primair | Mogelijk | Mogelijk | Nee | Kernregistratie gewenst |
| Beleidsregels | Nee | Nee | Nee | Nee | CKC-regellaag |
| Afgeleide kwalificaties | Deels impliciet | Deels impliciet | Deels | Nee | Expliciet en reproduceerbaar |

**Legenda:** “Sterk” betekent dat het systeem voor dit domein een belangrijke operationele bron is; dit is nog niet automatisch hetzelfde als formeel **autoritatief bronhouderschap**.

## 10. Bronhouderschap

Voor ieder kerngegeven moet in een volgende versie worden vastgesteld:

1. welke bron het gegeven kan aanleveren;
2. welke bron autoritatief is;
3. of CKC het gegeven lokaal mag/zal verrijken;
4. welke bron prevaleert bij conflicten;
5. hoe wijzigingen worden gesynchroniseerd;
6. welke historie behouden moet blijven;
7. welke auditinformatie nodig is.

Daarmee wordt onderscheid gemaakt tussen:

- **bron** – systeem waarin een waarde voorkomt;
- **autoritatieve bron** – systeem waarvan CKC de waarde als leidend beschouwt;
- **afgeleide waarde** – door CKC berekende waarde;
- **presentatiewaarde** – waarde die voor gebruiksgemak wordt getoond maar niet zelfstandig leidend is.

## 11. Bekende datakwaliteitsrisico’s

- Het vrije veld “Status lidmaatschap” bevat verschillende soorten betekenissen door elkaar.
- Sportlink-lidsoorten hebben een Sportlink/KNVB-betekenis en mogen niet automatisch als CKC-statutaire categorie worden geïnterpreteerd.
- Sommige relaties zijn alleen impliciet zichtbaar via functies of teamkoppelingen.
- Historie is verdeeld over Sportlink en de Access-database.
- Dezelfde Partij kan in meerdere systemen voorkomen zonder gemeenschappelijke identifier.
- Lokale labels kunnen ten onrechte als structurele categorie worden geïnterpreteerd.
- Beleidsuitkomsten kunnen in bestaande registraties als “feit” zijn opgeslagen zonder zichtbare onderliggende regel.

## 12. Relatie met andere documenten

- [CKC Personenmodel](personenmodel.md) – definieert de conceptuele werkelijkheid.
- [CKC Logisch Informatiemodel](logisch-informatiemodel.md) – structureert de informatieobjecten.
- `../procesontwerp/ledenadministratie.md` – beschrijft het ledenadministratieproces waarin veel van deze gegevens ontstaan of worden gebruikt.

## 13. Vervolg

Voor versie 0.2 ligt de nadruk op:

- veldniveau-mapping van Sportlink;
- inventarisatie van relevante Access-velden;
- verdere Sponsit-mapping;
- vaststelling autoritatieve bron per gegeven;
- identificatie- en matchingsregels tussen systemen;
- historie- en synchronisatieregels;
- validatieregels voor nieuwe inschrijvingen.
