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
- **Stand 24 oktober 2026:** read-only taakplichtcontrole (PR #28) en DVK-portaal (PR #32) zijn functioneel geaccepteerd. Aanvullend zijn bronresponsvalidatie voor de Vrijwilligers API (PR #34) en levensduur/periodewisseling van tijdelijke planning (PR #35) gemerged; PR #35 is lokaal functioneel geaccepteerd. De live-integratie van de Vrijwilligers API en BL-16 (duurzame planningssessies en No-Show-broncontroles) zijn via PR #38 lokaal functioneel geaccepteerd en gemerged. De teamnaamkoppeling en datumverwerking van de Programma API zijn via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) lokaal geaccepteerd (141/141 operationele wedstrijden); de Programma-integratie is inmiddels via BL-18/PR #46 functioneel afgerond. [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseert de lokale CSV-importlocatie en vijf bestandsnamen; lokaal is het standaardpad voor Teams.csv geaccepteerd. Functionele acceptatie van achterstallige uren (BL-03), integrale planning en v0.5-eindacceptatie blijven open. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [backlog](BACKLOG.md).

- **29 oktober 2026 — Iteratie 1 geaccepteerd:** BL-17/20/21 via [PR #53](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/53): Sportlink leidend voor kandidaten, uitzonderingsinvoer verwijderd, teamspeeldagfilter met minimumgebonden noodkandidaten, directe begrijpelijke kandidaatdetails en actieve codeversie. 1209 regressietests en CI #381 groen voor de geaccepteerde codeversie. Eén weekendrichting en noodkandidaten uitsluitend synthetisch getoetst; zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md). Volgende stap: BL-03; integrale v0.5-acceptatie blijft open.

- **BL-03 — technische uitvoering Iteratie 2:** optionele historische Sportlink-CSV `Overzicht per periode vorig seizoen.csv`, gekoppeld op relatiecode. Positieve bronachterstand beïnvloedt uitsluitend prioriteit voor diensten in juli–december; actuele uren blijven gelijk. Planner borgt het vorige seizoen. Onbeschikbare/onbetrouwbare historie sluit geen kandidaat uit. [Verslag en acceptatieprotocol](code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md). Functionele acceptatie en merge staan open.

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
