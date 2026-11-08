# Digitaal Verenigingskantoor

Deze repository bevat de functionele modellen, ontwerpen, documentatie en uitvoerbare prototypes voor het **Digitaal Verenigingskantoor (DVK)** van CKC.

DVK ontwikkelt zich van een prototype dat afzonderlijke CKC-cases kan interpreteren naar een verenigingskantoor met een eigen canonieke informatielaag: bestaande bronsystemen blijven bronhouder, terwijl DVK bronfeiten combineert, kwalificaties en beleidsgevolgen afleidt en menselijke besluitvorming ondersteunt.

## Prototype-ontwikkeling

| Versie | Hoofddoel | Kern |
| --- | --- | --- |
| **v0.1** | Concept bewijzen | Minimaal logisch prototype rond concrete CKC-cases: personen, lidmaatschap, rollen/functies, externe systemen en regels. Bewees dat DVK bronfeiten kan combineren en daar betekenisvolle vervolgacties uit kan afleiden. |
| **v0.2** | Functionele correctheid en robuustheid bewijzen | Consolidatie naar de gezaghebbende C01–C22. Uitzonderingen en randgevallen werden expliciet en vormden een functionele regressiebasis. |
| **v0.3** | Een echte werkstroom modelleren | Werkstroom **Ledendiensten & Vrijwilligersbeleid**: taakplicht, vrijstellingen, ouders/minderjarigen, gezinslogica, functies, recreanten en verplichte uren. Het onderscheid **bronfeit → afgeleide kwalificatie → beleidsgevolg** werd leidend. v0.3 is functioneel geaccepteerd. |
| **v0.4** | Werkelijke CKC-bronnen aansluiten | Bron- en integratiecontract voor onder meer Sportlink, Vrijwilligers, Teams, Programma/Wedstrijden, exports en de CKC-dienstencatalogus. Echte bronnen worden aangesloten zonder de DVK-domeinlogica daarvan afhankelijk te maken. v0.4 is de huidige functioneel geaccepteerde releasebaseline op `main`. |
| **v0.5** | De werkstroom operationeel bruikbaar maken | Concrete Ledendienst Planning met diensten, bezetting, kandidaten, wedstrijdconflicten, prioritering, tijdelijke planning, no-shows en gecontroleerde synchronisatie met Sportlink. De mens blijft beslisser; DVK ondersteunt en stelt voor. v0.5 is in ontwikkeling en nog niet integraal functioneel geaccepteerd. |

Kort samengevat:

> **v0.1:** concept bewijzen → **v0.2:** functionele correctheid bewijzen → **v0.3:** werkstroom en beleidslogica bewijzen → **v0.4:** echte bronnen aansluiten → **v0.5:** operationeel bruikbaar maken.

## Huidige ontwikkelstatus

- `main` bevat de functioneel geaccepteerde **v0.4-releasebaseline**.
- `prototype-v0.5` is de integratiebranch voor de ontwikkeling van **v0.5**.
- De pull request van `prototype-v0.5` naar `main` blijft draft totdat v0.5 integraal functioneel is geaccepteerd.
- Een groene CI-run is noodzakelijk, maar is op zichzelf geen functionele acceptatie.
- **Stand 24 oktober 2026:** read-only taakplichtcontrole (PR #28) en DVK-portaal (PR #32) zijn functioneel geaccepteerd. Aanvullend zijn bronresponsvalidatie voor de Vrijwilligers API (PR #34) en levensduur/periodewisseling van tijdelijke planning (PR #35) gemerged; PR #35 is lokaal functioneel geaccepteerd. De live-integratie van de Vrijwilligers API en BL-16 (duurzame planningssessies en No-Show-broncontroles) zijn via PR #38 lokaal functioneel geaccepteerd en gemerged. De teamnaamkoppeling en datumverwerking van de Programma API zijn via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) lokaal geaccepteerd (141/141 operationele wedstrijden); de Programma-integratie is inmiddels via BL-18/PR #46 functioneel afgerond. [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseert de lokale CSV-importlocatie en vijf bestandsnamen; lokaal is het standaardpad voor Teams.csv geaccepteerd. Integrale planning en v0.5-eindacceptatie blijven open; BL-03 is op 29 oktober 2026 afzonderlijk functioneel geaccepteerd. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [backlog](BACKLOG.md).

- **29 oktober 2026 — Iteratie 1 geaccepteerd:** BL-17/20/21 via [PR #53](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/53): Sportlink leidend voor kandidaten, uitzonderingsinvoer verwijderd, teamspeeldagfilter met minimumgebonden noodkandidaten, directe begrijpelijke kandidaatdetails en actieve codeversie. 1209 regressietests en CI #381 groen voor de geaccepteerde codeversie. Eén weekendrichting en noodkandidaten uitsluitend synthetisch getoetst; zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md). Volgende stap: BL-03; integrale v0.5-acceptatie blijft open.

- **BL-03 — Iteratie 2 functioneel geaccepteerd (29 oktober 2026):** optionele historische Sportlink-CSV `Overzicht per periode vorig seizoen.csv`, gekoppeld op relatiecode. Positieve bronachterstand beïnvloedt uitsluitend prioriteit voor diensten in juli–december; actuele uren blijven gelijk. Planner borgt het vorige seizoen. Onbeschikbare/onbetrouwbare historie sluit geen kandidaat uit. [Verslag en acceptatieprotocol](code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md). Lokale synthetische acceptatie (prioriteit 8/4/0 bij E=10, waarschuwing bij ontbrekende historie, bevestiging/undo) geslaagd op `e3b17fc`; 1251 regressietests en CI #385 groen. [PR #55](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/55) is op 29 oktober 2026 gemerged naar `prototype-v0.5`.

**Iteratie 3 — BL-23/BL-24:** vijf onafhankelijk inklapbare rubrieken en bronstatus van alle acht bronnen functioneel geaccepteerd op 30 oktober 2026 op commit `0aa8445d9f70d2f099f2599e117035f00d05e0a1`; [PR #56](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/56) op 30 oktober 2026 gemerged naar `prototype-v0.5` (mergecommit `d9942c328e75a7235803319807504fbd36c522d4`); aanvullende lokale visuele controle op de gemergede versie geslaagd. Zie [Iteratie 3-verslag](code/Prototype/DVK-v0.5-iteratie3-bronstatus-rubrieken.md).

De ontwikkeling is baseline-gedreven. Code, functioneel contract, bron-/integratiecontracten, relevante configuratie en geaccepteerde regressies vormen samen de releasebaseline. Nieuwe requirements of correcties van eerdere ontwerpen wijzigen die baseline niet impliciet.

Zie [`docs/ontwikkelworkflow-codex.md`](docs/ontwikkelworkflow-codex.md) en [`AGENTS.md`](AGENTS.md) voor de afgesproken ontwikkel-, change-control- en Codex-werkwijze.

## Repositorystructuur

- `code/Prototype/` — uitvoerbare DVK-prototypes, ontwerpen, testcases, migraties en regressietests;
- `docs/informatiemodel/` — canoniek en logisch informatiemodel, gegevenswoordenboek en bronnenmapping;
- `docs/DVK – Werkstroom Ledendiensten & Vrijwilligersbeleid/` — functionele werkelijkheid en werkstroomdocumentatie;
- `docs/functioneel-ontwerp/` — functionele ontwerpen per domein;
- `docs/procesontwerp/` — procesontwerpen;
- `docs/ontwikkelworkflow-codex.md` — baseline-gedreven ontwikkelworkflow en change-control;
- `AGENTS.md` — bindende uitvoeringsregels voor gecontroleerde technische iteraties.

## Ontwerpprincipes

De architectuurrichting is:

    sources
    → adapters
    → normalization / canonical DVK objects
    → domain / engine
    → proposal
    → human decision
    → scheduling

Belangrijke principes zijn dat bronfeiten, configuratie en DVK-afleidingen onderscheiden blijven, provenance behouden blijft, beleidslogica niet in de UI of SQL terechtkomt, ontbrekende brondata niet wordt gegokt en een DVK-voorstel nooit automatisch een CKC-besluit wordt.

## Baselineprincipe

GitHub is de gezaghebbende projectadministratie. Een geaccepteerde releasebaseline is het contract voor volgende ontwikkeling. Een chat, overdracht of technische implementatie kan daarnaar verwijzen, maar vervangt de baseline niet.

Zie voor technische details en uitvoerinstructies ook de [README van het prototype](code/Prototype/README.md).

**Iteratie 4 — BL-14 (functioneel geaccepteerd op 31 oktober 2026; PR #58 gemerged):** Ledendienst Planning
gebruikt twee lokale CSV-bestanden (`shift_definitions.csv` en
`shift_week_pattern.csv`) in `~/Documents/DVK-Sportlink-exports/`, in plaats van
rechtstreeks `Shift Catalog.xlsx`. Reguliere en incidentele catalogusdiensten
worden aangevuld met feitelijke Sportlink-diensttijdvakken. `Reload catalog`
vereist bevestiging en begint altijd een nieuwe planningssessie. Geen
Sportlink-writeback. Zie het [formaat en de bediening](code/Prototype/README.md#bl-14--lokale-dienstencatalogus)
en het [implementatie- en acceptatieverslag](code/Prototype/DVK-v0.5-iteratie4-BL14.md).
CKC heeft BL-14 inclusief voormalig BL-15 lokaal functioneel geaccepteerd op codecommit `be1cd1d52ae1dad7a10d35d7e89c3874e285e7ad`; [PR #58](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/58) is gemerged naar `prototype-v0.5` (mergecommit `267c94779a04`). De lokaal onderhouden CKC-weekcatalogus toont na reload **23 reguliere diensten**; aanvullende Sportlink-dienstmomenten, validatie, kandidaten en undo zijn gecontroleerd. De drie periodekeuzes Dag, Week en Aangepast tonen de correcte roosterperiode. 55 gerichte en 1307 regressietests geslaagd; CI #397 groen. Lokale CKC-configuratie is niet opgenomen in GitHub. **Volgende iteratie: BL-19 — zelfstandig No-showmanagement.** Integrale v0.5-acceptatie blijft open.


### Iteratie 5 — BL-19 functioneel geaccepteerd (2 november 2026)

**2 november 2026 — Iteratie 5 / BL-19 functioneel geaccepteerd door CKC**, op codecommit `069e5a1388e1b66372062d411b5f44a6a6a5429d` van [PR #61](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/61), **nog niet gemerged**. Zelfstandig No-showmanagement (Sportlink-raadpleging en handmatige registratie), 15 kalenderdatums vandaag−14 t/m vandaag, actieve en ingetrokken historie, sanctietelling en intrekking geaccepteerd. Correcties BL-19-01 (datumkiezer), BL-19-02 (alfabetische persoonskeuzes), BL-19-03 (periode-uitleg) en BL-19-05 (historie met tien regels per pagina, registratiemoment nieuwste eerst en één detailpaneel) geaccepteerd. BL-19-04 en BL-19-06 bleken na nadere controle geen defect. 106 gerichte en 1371 regressietests geslaagd, CI #402 groen; paginering met meer dan tien regels, uitzonderingspaden en planningisolatie met synthetische tests gecontroleerd, niet volledig lokaal met echte CKC-scenario's. Geen Sportlink-writeback, schema- of sanctieregelwijziging. Integrale v0.5-acceptatie blijft open; volgende iteratie is **Iteratie 6 — BL-22**. [Acceptatieverslag](code/Prototype/DVK-v0.5-iteratie5-BL19.md). De eerdere historische statusregels blijven als tijdgebonden momentopnamen staan.

### Iteratie 6 — BL-22 functioneel geaccepteerd (2 november 2026)

CKC heeft de onderhoudbaarheid van de bestaande Ledendiensten-beleidsregels functioneel geaccepteerd op codecommit `d0be7dccb31eaeace038bfb867a7c25b2995dd70` van [draft-PR #62](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/62), **nog niet gemerged**. Vijf herkenbare taakplichtstappen, één gedeelde B-02-kwalificatie per teamregistratie, behoud van CSV-functieclassificatie en een [regelindex met elf synthetische demonstraties](docs/DVK-v0.5-CKC-beleidsregelindex-Ledendiensten.md). De index is compleet genoeg geacht voor acceptatie, maar voor niet-ingewijden lastig leesbaar; een latere read-only DVK-functie 'Beleidsregels bekijken' blijft een optie bij aantoonbare behoefte. Volgens technisch verslag: 768 equivalente vóór/na-situaties, 1501 regressietests geslaagd, 11/11 synthetische runners geslaagd en CI #407 groen. Geen beleidswijziging of UI-wijziging. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie6-BL22-acceptatie.md). **Volgende correctieronde: Iteratie 7add** (melding roosterbezetting en kolombreedtes dienstentabel); daarna blijft de integrale v0.5-acceptatie een afzonderlijke mijlpaal. Oudere statusregels hierboven zijn historische momentopnamen.

### Iteratie 7add — UI-correcties functioneel geaccepteerd (3 november 2026)

CKC heeft beide kleine UI-correcties in Ledendienst Planning lokaal functioneel geaccepteerd op codecommit `e4d6a9df5c599a47751ea79fa3366dd18ac7b3f5` van [draft-PR #63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63). De waarschuwing over ontbrekende actuele Sportlink-bezetting staat in sectie 3 Diensten bij de synchronisatieknop. Na twee breedterondes zijn Dienst (110 px), Sportlink (140 px) en Vrije capaciteit (65 px) geaccepteerd: de waarden in de laatste kolom zijn zonder horizontaal scrollen zichtbaar, ook al is de kop afgekapt; dienstnamen blijven leesbaar en volledige Sportlink-namen zijn via dubbelklik toegankelijk. 131 gerichte tests, 1502 regressietests, 11 synthetische runners en [CI #414](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41540805895) geslaagd. [Acceptatieverslag](code/Prototype/DVK-v0.5-iteratie7add-acceptatie.md). PR #63 blijft tot expliciete merge-toestemming ongemerged. Volgende mijlpaal: integrale functionele acceptatie v0.5; BL-13/RPA volgt afzonderlijk. De vertraagde lokale Streamlit-start wordt afzonderlijk onderzocht.


### Actuele vervolgplanning na Planner-overleg (3 november 2026)

De eerdere aanduiding van integrale v0.5-acceptatie als *directe* vervolgstap na Iteratie 7add is achterhaald. **Iteratie 8** (Databronnen en schermindeling) is gemerged en **Iteratie 9** (kandidaatselectie en prioritering) is functioneel geaccepteerd op `67dd98e` in PR #66 (nog niet gemerged). De vier UI-/bronvoorstellen van Iteratie 8 vragen eerst nadere functionele uitwerking; voor Iteratie 9 zijn uitgangspunten overeengekomen, maar de samenhang met code, contracten en regressies moet nog worden getoetst. **Iteratie 10** is de integrale functionele acceptatiemijlpaal van v0.5. Daarna blijft **BL-13 RPA** een afzonderlijk vervolgtraject. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [backlog](BACKLOG.md) voor de exacte afspraken, open vragen en acceptatiegrenzen. Historische statusregels hierboven zijn momentopnamen. Geen Sportlink-writeback of productieacceptatie.


### Iteratie 8 — Databronnen en schermindeling (3 november 2026)

**Lokaal functioneel geaccepteerd** door CKC op codecommit `69255327dcf5fc35a578bc12ace985afa0ffe900` in [draft-PR #65](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/65), nog niet gemerged. De Planner toont vijf standaard ingeklapte rubrieken in de volgorde Instellingen, Databronnen, Wedstrijden, Diensten, Kandidaten. De catalogusknop **Dienstencatalogus (roosterindeling) opnieuw laden** staat onder Diensten; bevestiging en annuleren zijn lokaal geslaagd. Bronstatus bevat acht bronnen met één kolom **Laatst ingelezen door DVK**, zonder te suggereren dat API-tijden Sportlink-actualisatietijden zijn. De demonstratiekeuze is uit de normale UI verwijderd, met behoud van synthetische testvoorzieningen. Na 1506 regressietests, 11 synthetische acceptatiescripts en groene CI #422 is de lokale acceptatie afgerond. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie8-acceptatie.md). **Iteratie 9** is gepland, niet geïmplementeerd; **Iteratie 10** is de integrale v0.5-acceptatiemijlpaal. BL-13/RPA volgt afzonderlijk. Historische voortgangsnotities hierboven blijven momentopnamen.


### Iteratie 9 — functioneel geaccepteerd (4 november 2026)

CKC heeft Iteratie 9 lokaal functioneel geaccepteerd op codecommit `67dd98efe2fb5a2c696d6bb864b4f818a1e24755` in [PR #66](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/66) (nog niet gemerged bij deze vastlegging). [CI #429](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41878191393) is groen; Codex rapporteert 1.584 geslaagde regressietests, waaronder 78 nieuwe synthetische tests. Handmatig geslaagd: zaterdag-ochtend- en middaggroepen, uitsluiting bij wedstrijdconflict, jeugd-thuis zonder overlap met juiste thuiswedstrijdverklaring, actuele uren en historische achterstand als prioriteit, expliciete bevestiging en undo. De BL-20-noodgroep van de andere weekenddag bij minimumtekort is uitsluitend synthetisch getest; een aanvullende handmatige proef werd door een **bestaande** fout bij synchronisatie van feitelijke Sportlink-inroosteringen geblokkeerd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie9-acceptatie.md).

**Actueel beleid na Iteratie 9:** jeugdteams zijn JO/O/MO met leeftijdscategorie t/m 20, andere teams senioren; groepsprioriteit vóór actuele E, daarna positieve historische achterstand vorig seizoen en stabiele persoonssleutel. Historie telt het gehele lopende seizoen mee (januari–december), zonder wijziging van actuele A/B/C/D/E. De eerdere juli–december-beperking van BL-03 is hiermee vervangen. Jeugd-thuis zonder wedstrijdoverlap valt in de noodgroep 'zonder wedstrijd' maar behoudt de feitelijke thuiswedstrijdcontext. BL-20 blijft de laatste minimumgebonden noodgroep. Iteratie 10 blijft de integrale functionele acceptatie van v0.5, zonder nieuwe functionaliteit.

**Afzonderlijk vervolg buiten Iteratie 9:** bij de Sportlink-week 9–15 november 2026 werden twee verschillende personen als 'Afgeschermd' voor dezelfde dienst aangeleverd. De bestaande boekingssleutel kan dan botsen; concrete API-records zijn nog niet onderzocht. CKC heeft besloten dat iedere aangeleverde 'Afgeschermd'-regel afzonderlijk als bezette plaats zichtbaar moet blijven, zonder automatische persoonskoppeling, persoonsgebonden uren of no-show, en zonder blokkade van de overige synchronisatie. De technische uitwerking en regressietests volgen in een afzonderlijke opdracht; de overige duplicaatcontrole blijft behouden. De extra avonddienst 22:30–23:55 is waargenomen maar niet als oorzaak vastgesteld.


### Correctie afgeschermde boekingen — PR #67 (7 november 2026)

De correctie voor meerdere identieke `Afgeschermd`-regels uit Sportlink is op commit `90d3dde` functioneel geaccepteerd. Twee afgeschermde boekingen worden naast twee reguliere boekingen afzonderlijk getoond; de bezetting telt alle vier en de vrije capaciteit is 0. De technische regressies beschermen de anonimiteit, uitsluiting van persoonsgebonden uren/no-show en idempotente synchronisatie (1.597 tests; CI #433 groen). Zie [acceptatieverslag](code/Prototype/DVK-v0.5-PR67-afgeschermde-inroosteringen-acceptatie.md). Integrale acceptatie v0.5 (Iteratie 10) blijft open.

De ontwikkelomgeving is opnieuw lokaal opgebouwd buiten de iCloud-beheerde Documenten-map. Sportlink-exports en de Client-ID-configuratie staan afzonderlijk buiten de Git-repository. Het exportpad in de applicatie moet nog configureerbaar en persistent worden gemaakt via een **afzonderlijke technische correctie**; de bestaande hardcoded verwijzingen in oudere documentatie beschrijven de vorige lokale inrichting. Oude Documenten-mappen worden pas na succesvolle broncontrole opgeruimd.


## Iteratie 9A.1 — Databronnen (functioneel geaccepteerd op 7 november 2026)

De zelfstandige functie **Ledendiensten → Databronnen** en de configureerbare lokale Sportlink-exportmap zijn functioneel geaccepteerd in [draft-PR #68](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/68) (oplevercommit `06d1fe50bd30235fe2c9658e51395509082bf699`; CI #437 groen). De gekozen map wordt lokaal bewaard in `~/.config/dvk/settings.json`, buiten de repository. De beoogde locatie is `~/Development/DVK-Data/Sportlink-Exports/`. De vijf verplichte en één optionele CSV en de twee API-bronnen hebben afzonderlijke statusweergave. De lokale acceptatie bevestigde het behoud van tijdelijke indelingen en Sportlink-bezetting bij navigatie. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a1-acceptatie.md).

**Nog niet gerealiseerd:** automatisch laden van CSV, Programma API en Vrijwilligers API bij nieuwe planning; dat is Iteratie 9A.2. De huidige afzonderlijke handmatige laadacties zijn als onoverzichtelijk beoordeeld. De databaseverplaatsing en lokale omgevingscontrole volgen later in 9A. De PR is nog open; merge alleen na afzonderlijke toestemming. Integrale functionele acceptatie van prototype v0.5 volgt pas in Iteratie 10.


## Iteratie 9A.2 — Automatisch laden bij nieuwe planning (functioneel geaccepteerd op 7 november 2026)

**Status:** functioneel geaccepteerd door CKC op codecommit `045afbdc467185a870da5220d9a910ccc05f9333` in [draft-PR #69](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/69), gericht op `prototype-v0.5`; **niet gemerged bij deze vastlegging**. [CI #441](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/42420999174) geslaagd; Codex rapporteert 117 gerichte tests, 1.609 regressietests en 11 synthetische acceptatiescripts geslaagd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a2-acceptatie.md).

Bij een nieuwe planning is de huidige kalenderweek de standaard en kan de planner vooraf een andere periode kiezen. Pas na **Start nieuwe planning** worden de vijf verplichte en één optionele lokale CSV, Sportlink Programma en Sportlink Vrijwilligers automatisch geladen, met voortgang en onderscheiden bronstatus voor lege resultaten en fouten. Hervatten gebruikt de duurzaam in SQLite opgeslagen kandidaat- en wedstrijdcontext en bestaande gevalideerde bezetting, zonder nieuwe bronaanroepen; tijdelijke indelingen blijven behouden. Handmatige verversing blijft onder **Ledendiensten → Databronnen**, met expliciete bevestiging voor vervanging van bezetting. Bij ontbrekende verplichte bronnen zijn kandidaatvoorstellen niet veilig beschikbaar; bij mislukte Vrijwilligers-uitvraag is bezetting onbekend. Geen Sportlink-writeback.

**Lokale acceptatie:** (1) automatisch laden en periodekeuze geslaagd; (2) na Streamlit-herstart dezelfde periode, wedstrijden, bezetting en tijdelijke indeling zonder opnieuw laden; (3) vervanging zonder expliciete bevestiging geblokkeerd, tijdelijke indeling behouden; (4) tijdelijk hernoemde `Functies.csv` leidt tot een duidelijke foutmelding met exacte verwachte locatie en hersteladvies. De gebruiker is verzocht `Functies.csv.test` weer terug te noemen; herstel is niet afzonderlijk bevestigd. Geen productie- of integrale v0.5-acceptatie.

**Vervolg:** 9A.3 sessie- en regressiebescherming; 9A.4 lokale omgeving/databasepad verifiëren zonder ongevraagde migratie of opruiming; 9A.5 afronding en voorbereiding; Iteratie 10 integrale functionele acceptatie. Merge PR #69 uitsluitend na afzonderlijke toestemming.

### Iteratie 9A.3 — Sessie- en regressiebescherming (8 november 2026)

CKC heeft Iteratie 9A.3 functioneel geaccepteerd op codecommit `3a64213d47eb35b2a2baef9723c42f5957175170` in [draft-PR #70](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/70) (nog niet gemerged bij deze vastlegging). Bij hervatten na Streamlit-herstart bleven periode, broncontext en tijdelijke indeling behouden zonder ongevraagd laden. Een mislukte CSV-bronverversing werd in twee browsers gemeld; een oud kandidaatvoorstel verdween en de tijdelijke indeling bleef behouden. Twee synthetische tests voor onderbroken initiële bronlading slaagden; Codex rapporteerde 1.621 regressietests en groene CI #445. Zie het [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a3-acceptatie.md). Hierna volgen 9A.4 (lokale omgeving/databasepad), 9A.5 (afronding) en Iteratie 10 (integrale v0.5-acceptatie). Geen productieacceptatie of Sportlink-writeback.

### Iteratie 9A.4 — Lokale ontwikkelomgeving gecontroleerd (8 november 2026)

CKC heeft de beperkte lokale omgevingscontrole functioneel geaccepteerd. De SQLite-database staat onder `~/Development/DigitaalVerenigingsKantoor/code/Prototype/`; de verwachte Sportlink-CSV's en beide actieve dienstencatalogus-CSV's zijn aanwezig onder `~/Development/DVK-Data/Sportlink-Exports/`. Een zoekactie in Python-bronbestanden vond geen vaste verwijzingen naar de oude Documenten-map. Geen databaseverplaatsing, migratie of codewijziging nodig op basis van deze controle. Oude mappen worden alleen na afzonderlijke toestemming opgeruimd. Hierna volgt Iteratie 9A.5, daarna Iteratie 10 (integrale functionele acceptatie v0.5).
