# CKC Informatiemodel

Deze map bevat de functionele informatie-architectuur voor het **Digitaal Verenigingskantoor** van CKC.

De documenten beschrijven vanuit verschillende perspectieven dezelfde werkelijkheid. Samen vormen zij de ontwerpbaseline tussen het procesontwerp en de latere technische implementatie.

## Documenten

| Document | Centrale vraag | Huidige versie |
|---|---|---:|
| [Personenmodel](personenmodel.md) | Welke personen, organisaties en relaties bestaan er voor CKC? | 0.2.1 |
| [Logisch Informatiemodel](logisch-informatiemodel.md) | Welke informatieobjecten moet CKC logisch kunnen vastleggen en hoe hangen die samen? | 0.2 |
| [Gegevenswoordenboek & Bronnenmapping](gegevenswoordenboek-bronnenmapping.md) | Wat betekenen de gegevens precies en in welke systemen komen ze voor? | 0.1 |

## Samenhang

De documenten bouwen op elkaar voort:

```text
CKC-werkelijkheid
      │
      ▼
Personenmodel
begrippen en relaties
      │
      ▼
Logisch Informatiemodel
informatieobjecten en samenhang
      │
      ▼
Gegevenswoordenboek & Bronnenmapping
definities, brongegevens en bronhouderschap
      │
      ▼
Technisch gegevensmodel / integratielaag
(toekomstige stap)
```

Het [Personenmodel](personenmodel.md) is dus het meest conceptuele niveau. Het [Logisch Informatiemodel](logisch-informatiemodel.md) structureert die begrippen tot informatieobjecten. Het [Gegevenswoordenboek & Bronnenmapping](gegevenswoordenboek-bronnenmapping.md) verbindt die objecten vervolgens met de feitelijke CKC-administratie en bronsystemen.

## Relatie met het procesontwerp

Het informatiemodel staat niet op zichzelf.

Het bestaande procesontwerp:

`../procesontwerp/ledenadministratie.md`

beschrijft **wat er in de ledenadministratie gebeurt**.

De documenten in deze map beschrijven **welke informatie daarvoor nodig is en wat die informatie betekent**.

Proces en informatie moeten elkaar uiteindelijk wederzijds valideren:

- iedere processtap moet kunnen beschikken over de benodigde informatie;
- ieder belangrijk informatieobject moet een duidelijke reden hebben om in een proces of beleidsregel te worden gebruikt;
- invoer, wijziging en afleiding moeten herleidbaar zijn;
- uitzonderingen mogen het kernmodel niet onnodig vervuilen.

## Kernprincipes

### Eén identiteit, meerdere relaties

Een Persoon of Organisatie wordt één keer als identiteit beschouwd en kan meerdere gelijktijdige of historische relaties met CKC hebben.

### Bronfeiten zijn iets anders dan afleidingen

Bijvoorbeeld:

- “trainer” kan een geregistreerde functionele rol zijn;
- “voetballer” volgt uit voetbaldeelname;
- “spelend trainer” kan vervolgens uit beide feiten worden afgeleid.

### Beleid is geen bronfeit

Een contributiecategorie of vrijstelling is een beleidsgevolg. De feiten waarop dat gevolg is gebaseerd moeten afzonderlijk beschikbaar blijven.

### Bronsysteem is geen begrippenmodel

Sportlink, Access en Sponsit hebben ieder hun eigen gegevensstructuur en doel. Het CKC-informatiemodel wordt niet rechtstreeks afgeleid uit de tabellen, velden of categorieën van één van die systemen.

### Historie hoort bij het model

Waar een relatie in de tijd kan veranderen, moet het model die historie kunnen bewaren. Dat geldt in het bijzonder voor lidmaatschap, voetbaldeelname en functionele rollen.

## Belangrijkste bronsystemen

De huidige analyse omvat ten minste:

- **Sportlink Club** – leden, KNVB-relaties, functies en voetbalgerelateerde registratie;
- **CKC Access-database** – lokale en historische aanvullende ledeninformatie;
- **Sponsit** – CRM voor sponsorgerelateerde gegevens, contracten, facturen, taken en afspraken;
- **KNVB/CKC-inschrijfformulier (`club_aanmelden`)** – initiële gegevens bij nieuwe aanmeldingen;
- **toekomstige CKC-kernregistratie** – de nog te ontwerpen geïntegreerde informatievoorziening van het Digitaal Verenigingskantoor.

## Status en versiebeheer

De bestanden in deze map bevatten bovenaan hun eigen:

- versienummer;
- status;
- datum.

De bestandsnamen bevatten bewust **geen versienummer**. Git bewaart de documenthistorie. Daardoor blijft bijvoorbeeld `personenmodel.md` de vaste verwijzing naar de actuele versie, terwijl oudere versies via de Git-history terug te vinden zijn.

Bij een betekenisvolle nieuwe ontwerpversie wordt:

1. het versienummer in het document verhoogd;
2. de wijziging via Git vastgelegd;
3. waar nodig deze README bijgewerkt;
4. bij belangrijke baselines eventueel later een Git-tag/release gebruikt.

## Huidige ontwerpbaseline

Per 29 augustus 2026 bestaat de baseline uit:

- Personenmodel v0.2.1;
- Logisch Informatiemodel v0.2;
- Gegevenswoordenboek & Bronnenmapping v0.1;
- het afzonderlijk opgeslagen Procesontwerp Ledenadministratie.

Deze baseline is nog geen definitief technisch ontwerp. Zij is bedoeld als stabiel vertrekpunt voor verdere detaillering, bronanalyse en technische architectuur.

## Logische vervolgstappen

Vanuit deze baseline zijn de belangrijkste vervolgstappen:

1. bronhouderschap per gegeven vaststellen;
2. de mapping naar Sportlink, Access en Sponsit op veldniveau verdiepen;
3. historie- en synchronisatieregels vastleggen;
4. beleidsregels expliciet modelleren;
5. het logisch model vertalen naar een technisch gegevensmodel;
6. het geheel opnieuw toetsen aan concrete CKC-processen en persona’s.

Zo ontstaat uiteindelijk een traceerbare keten van:

**proces → begrip → informatieobject → gegeven → bron → regel → technische implementatie**.
