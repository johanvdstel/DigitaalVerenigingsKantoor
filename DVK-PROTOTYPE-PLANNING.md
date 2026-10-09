# DVK — Prototypeplanning v0.5

**Status:** voorgestelde en op hoofdlijnen afgestemde ontwikkelvolgorde, 9 oktober 2026.  
**Doel:** van geaccepteerde taakplichtcontrole naar bruikbare CKC-ledendienstplanning met echte brongegevens.  
**Gerelateerd:** [Backlog](BACKLOG.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md).

## Mijlpalen en stappen

| Volgorde | Stap | Gewenst resultaat / acceptatie | Status |
| --- | --- | --- | --- |
| Afgerond | Stap 2 ronde 4 — taakplichtcontrole | Read-only afleiding, vergelijking met Sportlink A, bron- en controlediagnose; lokaal functioneel geaccepteerd en [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged. | **Afgerond** |
| 1 | BL-04 — DVK-portaal | Welkomstpagina en moduleoverzicht, correcte beschikbaarheidsstatus; Ledendienst Planning toegankelijk, bestaande functies blijven werken. | **Volgende stap** |
| 2 | Integratie Vrijwilligers API | Actuele diensten, Sportlink-inroosteringen en bezetting betrouwbaar ophalen/vertalen; bronstatus, fouten, peildatum en herhaalbaarheid controleren. | **Apart onderzoeken, implementeren en accepteren** |
| 3 | Integratie Programma API | Wedstrijden en relevante team-/wedstrijdcontext betrouwbaar ophalen/vertalen voor kandidaatbeoordeling; bronstatus en foutafhandeling testen. | **Apart onderzoeken, implementeren en accepteren** |
| 4 | BL-03 — Achterstallige uren | Lokaal planner-Excel koppelen op lidnummer; seizoens- en matchcontroles; prioriteit t/m 31 december, geen wijziging Sportlink A. | **Hoge prioriteit; Excel bevestigd, nog te ontvangen** |
| 5 | Stap 3 — Ledendienst Planning | Taakplicht + Vrijwilligers + Programma + achterstanden combineren voor zinvolle kandidaten, prioriteit, bezetting en tijdelijke planning. | **Na bronacceptaties** |
| Vervolg | BL-05/06/07/08/09/10/11 | Openstaande besluiten, broncorrecties en integrale processen realiseren of verifiëren volgens backlog; exacte onderlinge volgorde nader bepalen. | **Open / afhankelijkheden** |
| Mijlpaal | Integrale functionele acceptatie v0.5 | Echte CKC-bronnen lokaal, samenhang tussen taakplicht, bronnen, planning, sync, no-shows, portaal; afwijkingen expliciet beoordeeld. | **Nog open** |

De volgorde is **geen onwrikbaar watervalplan**: het Excel-bestand kan eerder beschikbaar komen en in parallel worden voorbereid. Stap 3 mag niet afhankelijk zijn van onbevestigde aannames over de twee API's. De API-integraties zijn **twee afzonderlijke ontwikkel- en acceptatiestappen**.

## Acceptatie per stap

- **Vooraf:** controleer actuele code, bestaande adapters, tests en GitHub Issues. Beschrijf alleen bewezen hiaten.
- **Functioneel:** leg concrete invoer, verwachte uitvoer, bronherkomst, foutscenario's en grenzen vast; toets met opdrachtgever.
- **Technisch:** synthetische tests, volledige regressie, privacycontrole en CI groen; geen writeback naar Sportlink in v0.5.
- **Integratie:** echte CKC-brondata alleen lokaal op de computer van opdrachtgever; geen persoonsgegevens in commits, logs of PR's.
- **Governance:** aparte branch/PR; niet mergen zonder expliciete goedkeuring.

## Bijzonderheden en afhankelijkheden

### Taakplicht (Stap 2)
De read-only controle is functioneel geaccepteerd: 650 leden, 563 overeenkomsten, 87 afwijkingen, 0 onbetrouwbaar beoordeelbaar. De 87 afwijkingen liggen bij de planner; terugkoppeling voedt BL-05, niet het reeds geaccepteerde dashboard.

### Vrijwilligers API
Er bestaan reeds Sportlink Vrijwilligers-client-/adapterbouwstenen in het prototype. Bepaal vóór nieuwe code welke verbinding, broncontracten en actuele bezetting werkelijk werken. Bevestig authenticatie, leesrechten, peildatum, bronidentiteit, synchronisatiegrens en veilige foutafhandeling. Geen aannames dat live toegang al operationeel is.

### Programma API
Onderzoek bestaande client-/adapterbouwstenen en beschikbaarheid van wedstrijdgegevens. Leg teamkoppeling, tijdstippen, thuis/uit, actualiteit en eventuele onvolledigheid expliciet vast voordat kandidaatselectie met deze bron wordt geaccepteerd.

### Achterstallige uren (BL-03)
De planner bevestigt een Excel-overzicht; levering/kolommen moeten nog worden geverifieerd. Koppel betrouwbaar op lidnummer en seizoen; behandel ontbrekende/dubbele regels expliciet. **Beleidswijziging B-13:** vóór implementatie formeel aanpassen van 1 december naar **31 december inclusief** en regressies toevoegen voor de jaargrens. Geen vermenging met verplichte uren A.

### Stap 3 — Planning
Controleer de volledige keten: beschikbare diensten, feitelijke Sportlink-bezetting, actuele taakplicht, kandidaatgeschiktheid op basis van wedstrijdcontext, prioriteit en achterstand, tijdelijke DVK-planning, undo, handmatige Sportlink-verwerking en correcte synchronisatie. Houd no-shows gekoppeld aan feitelijke Sportlink-inroosteringen.

## Eindmijlpaal v0.5 (voormalig BL-12)

Acceptatie is een **besluit**, geen backlogfeature. Toets gezamenlijk:
1. brongegevens, provenance, actualiteit en foutafhandeling;
2. taakplicht, vrijstellingen, afwijkingen en plannerbeslissingen;
3. kandidaatselectie, achterstanden, tijdelijke planning en sync;
4. no-shows, intrekkingen en correctieopvolging;
5. DVK-portaal en begrijpelijke modulenavigatie.

Vastgelegde restpunten en bewuste beperkingen mogen expliciet worden geaccepteerd; geen stilzwijgende productierijpverklaring. **Prototypeacceptatie is geen productieacceptatie.**

## Na het prototype

De aparte [productieroadmap](PRODUCTIE-ROADMAP.md) behandelt hosting, echte database, veilige imports, identity & access management, security, privacy, operations en migratie. Productiearchitectuur wordt later gekozen; v0.5 houdt businesslogica en UI/gegevensinfrastructuur gescheiden.
