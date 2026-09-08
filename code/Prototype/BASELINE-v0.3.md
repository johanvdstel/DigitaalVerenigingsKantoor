# DVK Prototype v0.3 — functioneel geaccepteerde baseline

**Status:** functioneel geaccepteerd  
**Acceptatiedatum:** 8 september 2026  
**Werkstroom:** Ledendiensten & Vrijwilligersbeleid — Fase 1  
**Branch:** `main`

## Baselinebesluit

DVK Prototype v0.3 is op 8 september 2026 functioneel geaccepteerd. Deze versie vormt vanaf dit moment de regressiebaseline voor verdere ontwikkeling van het Digitaal Verenigingskantoor.

Nieuwe functionaliteit mag de hieronder beschreven geaccepteerde werking niet ongemerkt wijzigen. Een bedoelde functionele wijziging vereist een expliciete ontwerp- en acceptatiebeslissing en bijbehorende aanpassing van de regressietests.

## Geaccepteerde functionele basis

De baseline omvat twee samenhangende delen:

1. de reeds geaccepteerde masterset **C01–C22** uit `22 cases.md` en Prototype v0.2;
2. de v0.3-werkstroom **Ledendiensten & Vrijwilligersbeleid — Fase 1** volgens `ontwerp-dvk-prototype-v0.3.md`.

De v0.3-keten is:

`bronfeiten → import/normalisatie → taakplicht → urenpositie → kandidaatselectie → prioritering → adviesplanning → DVK-voorstel → menselijke beslissing → DutyAssignment → dashboard`

## Geaccepteerde v0.3-functionaliteit

- taakplicht wordt afgeleid uit bronfeiten en CKC-beleid;
- de 10-uursnorm is beleidsinformatie en geen bronfeit;
- de urenpositie wordt bepaald als `E = A - B - C - D`;
- voor minderjarigen is de uitvoerdercategorie ouder/verzorger, terwijl het lid administratief subject blijft;
- de bestaande gezins-/broederdienstlogica blijft behouden;
- Sportlink-achtige CSV-bronnen worden via een aparte importlaag naar canonieke DVK-objecten vertaald;
- kandidaatgeschiktheid houdt rekening met taakplicht, team- en wedstrijdcontext;
- geschikte kandidaten worden uitlegbaar geprioriteerd op actuele E-uren, relevante achterstand vorig seizoen en wedstrijdvoorkeur;
- DVK spreidt adviezen waar mogelijk over verschillende personen op dezelfde dag;
- het dashboard presenteert vooraf berekende engine-uitkomsten en bevat geen eigen selectie- of prioriteringsbeleid;
- een `AssignmentProposal` is nadrukkelijk nog geen CKC-besluit;
- goedkeuring door een mens kan leiden tot een `DutyAssignment`;
- bij planning stijgt D en daalt E; C verandert pas na daadwerkelijke uitvoering;
- afwijzing vereist een reden, maakt geen `DutyAssignment` en verandert de urenpositie niet;
- goedkeuren en afwijzen kunnen vanuit de dashboardlaag worden georkestreerd via dezelfde domeinfuncties.

## Acceptatiecontract

De permanente regressiebasis bestaat uit:

- **C01–C22** — bestaande functionele mastercases;
- **W01–W13** — v0.3 werkstroomcases zoals gedefinieerd in het ontwerp en de tests;
- **I01** — Sportlink-achtige bronimport levert canonieke DVK-objecten waarop dezelfde regels reproduceerbaar werken;
- **I02** — het dashboard gebruikt engine-uitkomsten en bevat geen eigen selectie-/prioriteringsbeleid;
- geïntegreerde end-to-endacceptatie van taakplicht tot en met menselijke beslissing en indeling.

W08 is in de definitieve baseline conform het ontwerp vastgelegd als **E=7 versus E=3**.

## Technische acceptatie

De afsluitende GitHub Actions-run voor commit `5b8866e47e9d069b6dd0fcdebf7e0faf604f258f` is volledig geslaagd:

- **59 tests passed**;
- C01–C22 acceptatie-uitvoer: geslaagd;
- W-case acceptatie-uitvoer: geslaagd;
- I01 importacceptatie: geslaagd;
- kandidaatselectie: geslaagd;
- prioritering: geslaagd;
- dashboard: geslaagd;
- AssignmentProposal en menselijke beoordeling: geslaagd;
- DutyAssignment W11/W12: geslaagd;
- dashboardbeslissingen: geslaagd;
- geïntegreerde v0.3 eindacceptatie: geslaagd.

De geïntegreerde einduitvoer eindigt met:

> EINDRESULTAAT: functionele keten v0.3 reproduceerbaar.

## Belangrijkste implementatiemodules

```text
dvk/
├── model.py
├── workstream_model.py
├── cases.py
├── workstream_cases.py
├── rules.py
├── duty.py
├── engine.py
├── import_adapter.py
├── candidate_selection.py
├── prioritization.py
├── recommendation_planner.py
├── dashboard.py
├── proposals.py
├── assignments.py
└── dashboard_actions.py
```

De acceptatie wordt ondersteund door de tests onder `tests/` en de leesbare acceptatierunners `run_*.py`.

## Baselineregel voor vervolgontwikkeling

Vanaf deze acceptatie geldt:

> **Prototype v0.3 is de functioneel geaccepteerde referentie. C01–C22 en het v0.3-acceptatiecontract worden niet opnieuw ter discussie gesteld tenzij CKC bewust een functionele beleids- of ontwerpwijziging besluit.**

Vervolgontwikkeling wordt bovenop deze baseline uitgevoerd en moet de volledige regressiesuite groen houden.
