# DVK — Prototypeplanning v0.5

**Status:** ontwikkelvolgorde bijgewerkt op 21 oktober 2026; BL-04 en voorbereidende verbeteringen PR #34/#35 afgerond.  
**Doel:** van geaccepteerde taakplichtcontrole naar bruikbare CKC-ledendienstplanning met echte brongegevens.  
**Gerelateerd:** [Backlog](BACKLOG.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md).

## Mijlpalen en stappen

| Volgorde | Stap | Gewenst resultaat / acceptatie | Status |
| --- | --- | --- | --- |
| Afgerond | Stap 2 ronde 4 — taakplichtcontrole | Read-only afleiding, vergelijking met Sportlink A, bron- en controlediagnose; lokaal functioneel geaccepteerd en [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged. | **Afgerond** |
| Afgerond | BL-04 — DVK-portaal | Startscherm en modulenavigatie; lokaal geaccepteerd en [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged. | **Afgerond (19 oktober 2026)** |
| Voorbereiding afgerond | Vrijwilligers API-responsvalidatie (PR #34) en tijdelijke planning (PR #35) | Ongeldige bronresponsen worden vóór publicatie geweigerd; tijdelijke planning bleef volgens de toen geaccepteerde afspraak behouden bij navigatie en verviel bij procesherstart; deze laatste afspraak is vervangen door het op 22 oktober 2026 geaccepteerde [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). | **Afgerond en lokaal geaccepteerd waar van toepassing; geen volledige live API-integratie** |
| 2 | Integratie Vrijwilligers API | Actuele diensten, Sportlink-inroosteringen en bezetting betrouwbaar ophalen/vertalen; bronstatus, fouten, peildatum en herhaalbaarheid controleren. | **Apart onderzoeken, implementeren en accepteren** |
| 3 | Integratie Programma API | Wedstrijden en relevante team-/wedstrijdcontext betrouwbaar ophalen/vertalen voor kandidaatbeoordeling; bronstatus en foutafhandeling testen. | **Apart onderzoeken, implementeren en accepteren** |
| 4 | BL-03 — Achterstallige uren | Lokaal planner-Excel koppelen op lidnummer; seizoens- en matchcontroles; prioriteit t/m 31 december, geen wijziging Sportlink A. | **Hoge prioriteit; Excel bevestigd, nog te ontvangen** |
| 5 | Stap 3 — Ledendienst Planning | Taakplicht + Vrijwilligers + Programma + achterstanden combineren voor zinvolle kandidaten, prioriteit, bezetting en tijdelijke planning. | **Na bronacceptaties** |
| Vervolg | BL-05/06/07/08/09/10/11 | Openstaande besluiten, broncorrecties en integrale processen realiseren of verifiëren volgens backlog; exacte onderlinge volgorde nader bepalen. | **Open / afhankelijkheden** |
| Mijlpaal | Integrale functionele acceptatie v0.5 | Echte CKC-bronnen lokaal, samenhang tussen taakplicht, bronnen, planning, sync, no-shows, portaal; afwijkingen expliciet beoordeeld. | **Nog open** |

De volgorde is **geen onwrikbaar watervalplan**: het Excel-bestand kan eerder beschikbaar komen en in parallel worden voorbereid. Stap 3 mag niet afhankelijk zijn van onbevestigde aannames over de twee API's. De API-integraties zijn **twee afzonderlijke ontwikkel- en acceptatiestappen**.

### Aanvullende afgeronde voorbereidingen (21 oktober 2026)

- **PR #34 — VRIJ-01:** ongeldige of lege Vrijwilligers API-responsen worden vóór publicatie geweigerd; bestaande bronfeiten en tijdelijke planning blijven behouden bij een mislukte verversing. Gemerged naar `prototype-v0.5` (merge-commit `8ccdb473`). Dit is bronveiligheid, **geen** bewijs dat de volledige live API-integratie is geaccepteerd.
- **PR #35 — tijdelijke planning:** werkvoorraad blijft behouden tijdens schermwisselingen en browser-refresh binnen hetzelfde applicatieproces; een periodewisseling met tijdelijke indelingen vereist waarschuwing en expliciete bevestiging; volgens de destijds geaccepteerde implementatie werd de werkvoorraad na een echte applicatieherstart gewist; **dit is inmiddels een achterhaalde functionele regel**, vervangen door het [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). Lokaal vijf acceptatiescenario's geslaagd; 693 regressietests en CI groen. Gemerged naar `prototype-v0.5` (merge-commit `e7d173e7`). Duurzame no-showgegevens blijven buiten deze wisacties.
- **Resterend:** feitelijke Vrijwilligers API-integratie, Programma API, achterstallige uren en de integrale planning/acceptatie blijven open volgens onderstaande volgorde.

### Afronding BL-04

BL-04 is lokaal visueel geaccepteerd en via [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged naar `prototype-v0.5` (`68ae25fa`). BL-04-01: functiespecifieke instellingen direct onder de betreffende schermtitels; BL-04-03: overbodige toelichting verwijderd, Rooster Generator als uitgeschakelde knop; BL-04-04: acht functies uniform één per regel op het startscherm. BL-04-02 is vervallen en niet geïmplementeerd; Planning blijft bewust met demonstratiegegevens werken. 62 gerichte tests, 636 regressietests en CI groen. Bekende beperking: CSV-uploads van Taakplichtcontrole na schermwisseling opnieuw selecteren. Volgende stap: afzonderlijke verificatie en acceptatie Vrijwilligers API.

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

## Releasevervolg — RPA (BL-13), toegevoegd 12 oktober 2026

**Voorstel op verzoek van opdrachtgever:** RPA krijgt de eerste afgebakende vervolgproef na integrale functionele acceptatie van v0.5. De bestaande v0.5-stappen en read-only scope blijven gelden. Er zijn nog geen vaste kalenderdata of geaccepteerde versienummers voor dit vervolg.

| Volgorde / releasevenster | Onderdeel | Besluit / acceptatie |
| --- | --- | --- |
| Huidige v0.5 | Portaal (BL-04 afgerond), afzonderlijke API-acceptaties, achterstanden, Stap 3 Planning en integrale verificatie | Resterende planning afronden; Sportlink-verwerking blijft handmatig |
| Eerstvolgende vervolgiteratie na acceptatie v0.5 | BL-13a — RPA-haalbaarheidsproef | Eén goedgekeurde indeling, teruglezen, dubbele invoer voorkomen en onderbreking veilig hervatten; go/no-go voor pilot |
| Volgende pilotrelease na positieve proef | BL-13b — Kleine batch onder toezicht | Resultaat per indeling en veilige herstart; actuele bezetting opnieuw controleren; fouten naar planner |
| Productierelease na pilotacceptatie en productievoorwaarden | BL-13c — Beheerde RPA-invoering | Voorwaarden P1–P3 uit productieroadmap, operationeel beheer en expliciete productie-go/no-go |

**Motivering:** eerst bewijzen dat DVK met actuele bronnen de juiste voorstellen en synchronisatie levert; daarna pas de externe invoer automatiseren. Zo wordt RPA een vervangbare uitvoercomponent en blijft de bestaande functionele baseline toetsbaar.

**Afhankelijkheden:** Stap 3 Planning, BL-10, unieke bronidentificatie, goedgekeurde indelingen en actuele bezetting. De proef kan lokaal onder toezicht plaatsvinden; een gehoste productierobot is daarvoor geen vereiste. P1 kan de uitvoeromgeving alvast onderzoeken, maar P2-productiebouw volgt pas na positief proefresultaat.

**Aannames / open punten:** Sportlink-browserschermen en rechten zijn nog niet beproefd; ontbreken van een schrijf-API is een uitgangspunt van opdrachtgever. Playwright + Python is een technische kandidaat, geen definitief architectuurbesluit. Exacte datum, releasenummer, beschikbare capaciteit en onderhoudseigenaar worden bij start bepaald. Geen vervroeging van writeback naar v0.5 en geen wijziging van CKC-beleid.

De gedetailleerde scope en acceptatiecriteria staan bij [BL-13](BACKLOG.md#bl-13--rpa-voor-invoer-van-goedgekeurde-ledendiensten-in-sportlink).

## Geaccepteerd ontwerp planningssessies (22 oktober 2026)

Het [functioneel ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md) is door CKC geaccepteerd als nieuwe functionele baseline, **nog niet geïmplementeerd**. Een sessie blijft voortaan bij browser-/procesherstart bestaan, kan worden hervat en wordt alleen na expliciete bevestiging afgesloten of vervangen. Periodewisseling en succesvolle vervangende Sportlink-synchronisatie zijn eveneens gecontroleerde sessiegrenzen. No-Show-registratie gebruikt uitsluitend de actieve gevalideerde bron; historische No-Shows blijven duurzaam bewaard. Dit vervangt uitsluitend de tegenstrijdige eerdere herstartafspraak; PR #35 blijft historisch als afgeronde implementatiestap geregistreerd. Technische uitvoering en lokale acceptatie zijn open, zonder wijzigingen aan code of database in deze documentatiestap.
