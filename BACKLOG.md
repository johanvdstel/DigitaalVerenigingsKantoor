# DVK — Functionele backlog

**Status:** bijgewerkt op 24 oktober 2026 na merges PR #41 en #42; BL-10/BL-11 kennen nog resterende integrale verificatie  
**Scope:** prototype v0.5 en later; geen implementatieplanning of productiearchitectuur.  
**Verwijzingen:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md)

De backlog bevat openstaande functionaliteit, beleidsbesluiten en bronafhankelijkheden. De volgorde, afzonderlijke ontwikkelstappen en integrale acceptatiemijlpaal staan in de prototypeplanning. Statussen beschrijven wat is afgesproken; ze bewijzen niet dat code al bestaat.

## Afgerond

| ID | Onderwerp | Status / bewijs |
| --- | --- | --- |
| BL-01 | Adresgebaseerde huishoud- en minderjarigenregels B-05/B-06/B-07 | **Afgerond en functioneel geaccepteerd** in Stap 2 ronde 4; uitsluitend volledig geregistreerd adres als automatische huishoudsleutel; relevante leden op peildatum; geen ouder-/achternaamheuristiek. |
| BL-02 | Read-only taakplichtcontroledashboard | **Afgerond en functioneel geaccepteerd.** Lokale CKC-acceptatie: 650 relevante leden, 563 overeenkomsten, 87 afwijkingen, 0 niet betrouwbaar beoordeelbaar. Bron- en controlediagnose behouden. [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged naar `prototype-v0.5`. |
| BL-04 | DVK-frontend, hoofdmenu, licht portaal | **Afgerond en functioneel geaccepteerd op 19 oktober 2026.** Startscherm met acht functies in drie groepen, één per regel; zijbalk uitsluitend navigatie; instellingen op eigen scherm. Rooster Generator als uitgeschakelde knop. Correcties BL-04-01/03/04 verwerkt; BL-04-02 vervallen. 62 gerichte tests, 636 regressietests en CI groen. [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged naar `prototype-v0.5` (`68ae25fa`). CSV-uploads moeten na schermwisseling opnieuw worden geselecteerd. |

## Open / geprioriteerd

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |
| BL-03 | Achterstallige uren vorig seizoen | **Hoge prioriteit, v0.5.** Planner bevestigt beschikbaar Excel-overzicht; bestand/kolommen nog te ontvangen en lokaal te verifiëren. Koppeling bij voorkeur op Sportlink-lidnummer, met seizoen, openstaande uren en controle op duplicaten/ontbrekende matches. Achterstand beïnvloedt kandidaatprioritering **tot en met 31 december**; vanaf 1 januari niet meer. Niet optellen bij Sportlink A van het nieuwe seizoen. **Wijziging B-13** t.o.v. eerdere grens 1 december: functionele baseline, configuratie en regressietests expliciet bijwerken vóór implementatie. | Excel van planner; bronsemantiek en seizoensidentificatie |
| BL-05 | Duurzame plannerbeslissingen bij taakplichtafwijkingen | **v0.5, na terugkoppeling planner.** Leg besluit, reden, actor, tijdstip, geldigheid en herbeoordeling na bronvernieuwing vast; onderscheid DVK-afleiding van menselijke administratieve beslissing. Ontwerp mede op basis van beoordeling van de 87 afwijkingen. | Terugkoppeling CKC-planner; B-09/B-14 |
| BL-06 | Urenoverdracht bij 18 jaar | **v0.5.** Signaleer overdrachtsmogelijkheid; uitsluitend menselijke goedkeuring en twee tegengestelde handmatige Sportlink-B-correcties; na nieuwe import beide verifiëren. Geen automatische Sportlink-mutatie. | B-08; verificatie Sportlink B |
| BL-07 | Sportlink-urenbron en seizoensgegevens | **Gedeeltelijk gevalideerd.** Sportlink A is voor read-only taakplichtcontrole met echte CKC-exports getoetst. Nog open: werkelijke B/C/D/E-betekenis, beschikbare velden, seizoensafbakening en controle van correcties na import. | Brononderzoek Sportlink |
| BL-08 | Functieclassificatie `Verzorger` | **Wacht op CKC-broncorrectie.** Onderscheid betaalde en onbetaalde functie in Sportlink nog niet betrouwbaar; huidige tijdelijke classificatie niet persoonsgebonden hardcoden. Na correctie lokaal opnieuw controleren. Blokkeert ander v0.5-werk niet. | CKC/Sportlink |
| BL-09 | Bronactualiteit functies en commissies | **Bewaken binnen v0.5.** Bestaande bron- en controlediagnose behouden; verouderde of onvolledige bronfeiten signaleren, geen ontbrekende functiedatums verzinnen. Geen aparte ontwikkelronde tenzij controle een concrete tekortkoming aantoont. | Nieuwe bronexports |
| BL-10 | Tijdelijke planning en Sportlink-synchronisatie | **v0.5, duurzame sessies en Vrijwilligers-bronverversing lokaal geaccepteerd via PR #38; integrale planningsverificatie open.** PR #34 borgt afwijzing van ongeldige Vrijwilligers-responsen vóór publicatie en behoud van bestaande gegevens bij mislukte verversing. PR #35 borgde behoud tijdens navigatie/refresh, bevestigde periodewisseling en destijds wissen bij procesherstart; vijf lokale acceptatiescenario's geslaagd. **De herstartregel is inmiddels functioneel achterhaald** door het op 22 oktober 2026 geaccepteerde [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). Nog te toetsen in de volledige API-/planningsketen: actuele bezetting en beschikbaarheid, undo, handmatige Sportlink-verwerking en succesvolle bronverversing als wisgrens. Alleen aantoonbare gaps herstellen. | API Vrijwilligers; FR-02–FR-08 |
| BL-11 | No-shows en handmatige Sportlink-correctiewerkvoorraad | **v0.5, registratie, intrekking en sanctieafleiding lokaal geaccepteerd via PR #38; handmatige correctiewerkvoorraad en integrale verificatie blijven open.** Controleer koppeling aan feitelijke Sportlink-inroostering, duurzame no-show, intrekking, sanctieafleiding en status openstaand/afgehandeld van handmatige correctie. Hergebruik geaccepteerde functionaliteit. | API Vrijwilligers; FR-09–FR-12 |

## BL-16 — Levenscyclus planningssessies (geïmplementeerd en functioneel geaccepteerd)

**Status:** ontwerp geaccepteerd op 22 oktober 2026; implementatie via [PR #38](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/38) op 23 oktober 2026 lokaal functioneel geaccepteerd en gemerged naar `prototype-v0.5`. SQLite-schema 13; 917 regressietests en CI #332 groen. Zie [DVK v0.5 — Functioneel ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md).

**Scope:** maximaal één duurzaam hervatbare planningssessie; expliciete start, hervatten, afsluiten en vervangen; drie navigatiesituaties bij Ledendienst Planning; periodekeuze vóór handmatige Vrijwilligers API-ophaalactie; bevestigde sessiegrenzen bij nieuwe planning, periodewisseling en vervangende synchronisatie; behoud bij browser- en procesherstart; geen gegevensverlies bij mislukte synchronisatie; No-Show-selectie en registratie uitsluitend vanuit de actieve gevalideerde bron. Historische No-Shows en intrekkingen blijven behouden.

**Opgelost in PR #38:** No-Show-selectie uitsluitend uit de actieve gevalideerde bron en periode, hercontrole bij registratie, volledige chronologisch gesorteerde keuzelijst, eenmalige resultaatmelding en herregistratie na intrekking met behoud van historie.

**Acceptatiegrens:** navigatie, browser- en Streamlit-herstart, bronvervanging met bevestiging, No-Show-registratie/intrekking/herregistratie en schema-upgrade zijn lokaal gecontroleerd. Mislukte synchronisatie, race tussen selectie en registratie, tijdelijke indelingen na computerherstart en periodewisseling mét tijdelijke indelingen zijn niet afzonderlijk lokaal beproefd; regressietests dekken deze scenario's. Integrale v0.5-acceptatie blijft open.

## Nieuwe beheerwensen (21 oktober 2026)

Deze wensen zijn afzonderlijke backlogrequirements en blokkeren de lopende Vrijwilligers API-integratie niet. Prioriteit voorlopig **normaal**; nadere uitwerking en acceptatie volgen afzonderlijk.

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |
| BL-14 | Beheer op te vragen Sportlink-taakcodes | **Nieuwe wens; na eerste Vrijwilligers API-integratie.** Onderhoudscherm voor bevoegde DVK-gebruiker om de vaste set uit te vragen Sportlink-taakcodes toe te voegen, te wijzigen en te deactiveren, zonder codewijziging. Synchronisatie vraagt altijd de volledige actieve set op; het dashboard toont per uitgevraagde taakcode de resultaten voor de gekozen periode, inclusief nul inroosteringen. Nieuwe Sportlink-taakcodes worden niet automatisch ontdekt; beheer vereist expliciete opname. | Werkende en geaccepteerde Vrijwilligers API-integratie; vast taakcodecontract |
| BL-15 | Beheer DVK-dienstencatalogus | **Nieuwe wens; na eerste bronintegratie.** Onderhoudscherm voor bevoegde DVK-gebruiker als vervanging van het huidige Excel-onderhoud van de eigen dienstencatalogus. Onderhoud van bestaande catalogusgegevens (zoals diensttype, gekoppelde taakcode, weekpatroon en bezettingsnormen) conform te verifiëren broncontract. Catalogus bepaalt alle concrete diensten per week, ook volledig onbezet; Vrijwilligers API levert uitsluitend feitelijke inroosteringen. Migratie en beheeropslag pas bij uitwerking bepalen; geen nieuwe catalogusarchitectuur veronderstellen. | Bestaande Excel-catalogus en cataloguscontract verifiëren; integratie met concrete dienstmomenten |

## BL-13 — RPA voor invoer van goedgekeurde Ledendiensten in Sportlink

**Status:** toegevoegd op verzoek van Johan, 12 oktober 2026; vervolg na integrale acceptatie v0.5. Nog geen implementatie of functionele acceptatie.

**Doel:** een bevoegde planner laat een menselijk goedgekeurde DVK-indeling via de Sportlink-browserversie invoeren en krijgt per indeling een gecontroleerd resultaat terug. RPA verzorgt de uitvoering; kandidaatselectie en CKC-beleid blijven in DVK.

- **Bevestigd door opdrachtgever:** browseromgeving gebruiken; RPA opnemen in backlog en releaseplanning.
- **Uitgangspunt opdrachtgever, niet onafhankelijk geverifieerd:** geen beschikbare schrijf-API voor Ledendienstindelingen. Bij de proef opnieuw controleren.
- **Technisch voorstel:** Playwright met Python als kandidaat voor een afzonderlijke uitvoercomponent; definitieve keuze pas na de haalbaarheidsproef.
- **Nog onbewezen:** de benodigde Sportlink-schermen, rechten en terugleesmogelijkheden lenen zich voor betrouwbare automatisering.

### Afbakening en afhankelijkheden

Geen Sportlink-writeback in v0.5. Eerst Stap 3 Planning en BL-10 accepteren: betrouwbare personen-/dienstidentificatie, actuele bezetting, menselijke goedkeuring en synchronisatiegrens. Een tijdelijke DVK-planning of interne assignment bewijst geen Sportlink-registratie. De concrete betekenis van goedkeuring en uitvoering wordt voor de proef vastgelegd.

De eerste proef gebruikt een zichtbaar browservenster waarin de bevoegde planner zelf inlogt. Alleen vooraf goedgekeurde indelingen worden verwerkt. Geen automatische beleidsbeslissingen, uren-/sanctiecorrecties, communicatie of automatisering van de Voetbal.nl-app in deze scope.

### Fasering en acceptatie

| Onderdeel | Resultaat en acceptatie | Voorwaarde |
| --- | --- | --- |
| BL-13a — Haalbaarheidsproef | Eén expliciet goedgekeurde indeling invoeren; persoon, taak/dienst, datum en tijden vooraf uniek controleren; daarna feitelijke opslag teruglezen. Bestaande indeling overslaan; onderbreking veilig hervatten zonder dubbele invoer. Onduidelijk resultaat apart melden en niet als geslaagd afvinken. | Na integrale acceptatie v0.5; rechten, testwerkwijze en eventuele notificaties van Sportlink vooraf vaststellen |
| BL-13b — Pilot onder toezicht | Kleine goedgekeurde batch; resultaat per indeling, fouten en gedeeltelijke uitvoering zichtbaar; opnieuw controleren op gewijzigde bezetting en bij hervatten eerst teruglezen. Correctie-/stopprocedure en handmatige verwerking beschikbaar. | Positief proefresultaat en expliciete acceptatie van pilotscope |
| BL-13c — Beheerde productie-invoering | Bevoegdheden, veilige sessies, uitvoerregistratie, herstel, monitoring en onderhoud van schermkoppelingen geborgd; pilotacceptatie en productie-go/no-go. | Productieroadmap P1–P3 en voldoende praktijkbewijs |

**Prioriteit / plek:** eerste afgebakende vervolgproef na v0.5; pilot pas na positief haalbaarheidsbesluit. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [productieroadmap](PRODUCTIE-ROADMAP.md). Exact releasenummer, datum, capaciteit en onderhoudseigenaar zijn nog te besluiten.

## Gegevensintegraties als afzonderlijke ontwikkelstappen

De **Vrijwilligers API** en **Programma API** zijn noodzakelijke bouwstenen voor Stap 3 Planning. Ze staan als aparte acceptatiestappen in [DVK-PROTOTYPE-PLANNING.md](DVK-PROTOTYPE-PLANNING.md), niet als verondersteld geheel nieuwe backlogfunctionaliteit. De Vrijwilligers API is via PR #38 lokaal geaccepteerd. Voor Programma zijn teamnaamkoppeling en datum-/tijdverwerking via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) lokaal geaccepteerd (141/141 gekoppelde operationele wedstrijden); de operationele schermintegratie en volledige kandidaatcontext blijven open. [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseert de vijf lokale CSV-exportpaden; de standaardlocatie voor Teams.csv is lokaal functioneel gecontroleerd. Eerst de actuele adapters, broncontracten en werkelijke integratiestatus verifiëren; geen duplicatie.

## Niet in de backlog

Voormalig **BL-12 — Integrale acceptatie prototype v0.5** is een **implementatie-/acceptatiemijlpaal**, geen functionele backlogwens. Deze staat daarom in de [prototypeplanning](DVK-PROTOTYPE-PLANNING.md).

## Werkafspraken

1. Besluiten uit deze bespreking vormen geen stilzwijgende codewijziging. Functionele baseline, technische implementatie en tests worden traceerbaar bijgewerkt.
2. Echte CKC-bestanden (Sportlink CSV's, planner-Excel), persoonsgegevens en lokale databases blijven op de eigen computer; niet uploaden naar GitHub, Codex of ChatGPT. Alleen synthetische voorbeelden en niet-herleidbare aggregaten in repository.
3. Elke ontwikkelstap krijgt een afgebakende branch/PR, regressie en expliciete functionele acceptatie; geen merge zonder akkoord.
4. Productievereisten worden apart beheerd in [PRODUCTIE-ROADMAP.md](PRODUCTIE-ROADMAP.md).
5. De historische backlog is een gereconstrueerde werklijst; controleer bij uitvoering de actuele code en GitHub Issues voordat iets als ontbrekend wordt aangemerkt.

## Functionele bronnen

- [Herijkte functionele baseline Ledendiensten](code/Prototype/DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md)
- [Functioneel contract v0.5 vervolg](code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md)
- [Technische impactanalyse v0.5 vervolg](code/Prototype/TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md)
- [GitHub Issue #12](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/12) en [#14](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/14)
