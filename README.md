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
