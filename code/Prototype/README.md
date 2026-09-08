# DVK Prototype v0.3 — functioneel geaccepteerde baseline

**Status: functioneel geaccepteerd op 8 september 2026.**

Dit is het zelfstandig uitvoerbare prototype van het Digitaal Verenigingskantoor (DVK). Prototype v0.3 vormt vanaf deze acceptatie de functionele regressiebaseline voor verdere ontwikkeling.

De formele baseline is vastgelegd in [`BASELINE-v0.3.md`](BASELINE-v0.3.md). De ontwerpgrondslag staat in `ontwerp-dvk-prototype-v0.3.md`; de bestaande C01–C22-masterset blijft gezaghebbend via `22 cases.md` en het geaccepteerde v0.2-ontwerp.

## Baseline in één oogopslag

Prototype v0.3 combineert:

- de reeds geaccepteerde **C01–C22** uit Prototype v0.2;
- de werkstroom **Ledendiensten & Vrijwilligersbeleid — Fase 1**;
- Sportlink-achtige bronimport;
- automatische afleiding van taakplicht;
- urenpositie `A-B-C-D=E`;
- minderjarigen- en gezinslogica;
- wedstrijdcontext en kandidaatselectie;
- uitlegbare prioritering;
- spreiding van voorstellen over kandidaten op dezelfde dag;
- dashboardweergave;
- `AssignmentProposal` en menselijke goedkeuring/afwijzing;
- `DutyAssignment` na goedkeuring;
- dashboardacties voor goedkeuren en afwijzen;
- geïntegreerde end-to-endacceptatie.

De afsluitende acceptatierun op GitHub Actions was volledig groen: **59 tests passed** en alle leesbare acceptatiestappen zijn geslaagd.

## Functionele keten

```text
bronfeiten
    │
    ▼
import / normalisatie
    │
    ▼
canonieke DVK-objecten
    │
    ▼
taakplicht afleiden
    │
    ▼
urenpositie A-B-C-D=E
    │
    ▼
kandidaatselectie
    │
    ▼
prioritering
    │
    ▼
adviesplanning
    │
    ├──────────────► dashboard
    │
    ▼
AssignmentProposal
    │
    ▼
menselijke beoordeling
    ├── afwijzen ──► geen indeling; uren ongewijzigd
    │
    └── goedkeuren
            │
            ▼
      DutyAssignment
            │
            ▼
       D omhoog, E omlaag
       C blijft gelijk tot uitvoering
```

Een kernprincipe is:

> **DVK-voorstel ≠ CKC-besluit.**

Het systeem adviseert en verklaart. De feitelijke indeling ontstaat pas na menselijke goedkeuring.

## Architectuurlagen

### 1. Canoniek model

`dvk/model.py` bevat het algemene DVK-domeinmodel, waaronder `Person`, `Membership`, relaties, rollen, autorisaties, `SportlinkDutyRegistration`, `DutyQualification`, `DutyPosition`, `Decision`, `Signal`, `Action` en `PrototypeCase`.

`dvk/workstream_model.py` bevat de operationele ledendienstobjecten, waaronder:

- `DutyService`
- `TeamMembership`
- `Match`
- `CandidateAssessment`
- `CandidatePriority`
- `AssignmentProposal`
- `HumanDecision`
- `DutyAssignment`
- dashboard-viewmodels.

### 2. Regels en taakplicht

`dvk/rules.py` bevat de geaccepteerde C01–C22-regels.

`dvk/duty.py` leidt voor de ledendienstwerkstroom onder meer af:

- taakplicht;
- vrijstelling;
- administratief subject;
- uitvoerdercategorie lid of ouder/verzorger;
- beleidsnormuren;
- afwijking van Sportlink-administratie;
- urenpositie `E = A - B - C - D`.

De CKC-norm van 10 uur is beleidsinformatie en wordt niet als bronfeit behandeld.

### 3. Importlaag

`dvk/import_adapter.py` vertaalt Sportlink-achtige CSV-bronnen naar canonieke DVK-objecten. De adapter kent bronvelden en bronformaten, maar bevat geen CKC-beleidsregels.

De representatieve testbronnen staan onder:

```text
testdata/v03_import/
├── members.csv
├── duty_hours.csv
├── teams.csv
├── matches.csv
└── services.csv
```

### 4. Kandidaatselectie

`dvk/candidate_selection.py` bepaalt of iemand voor een concrete Ledendienst geschikt is. Daarbij spelen onder meer taakplicht, teamlidmaatschap, thuis-/uitwedstrijd, tijdscontext en uitvoerdercategorie een rol.

Deze laag bepaalt **geschiktheid**, niet de rangorde.

### 5. Prioritering

`dvk/prioritization.py` rangschikt geschikte kandidaten transparant:

1. actuele resterende uren `E`;
2. relevante achterstand uit het vorige seizoen vóór 1 december;
3. wedstrijdvoorkeur;
4. stabiele tie-break.

W08 is conform het geaccepteerde ontwerp vastgelegd als **E=7 versus E=3**.

### 6. Adviesplanning

`dvk/recommendation_planner.py` zet de per-dienst-rangorde om in concrete eerste adviezen. Daarbij wordt, wanneer er alternatieven zijn, voorkomen dat dezelfde persoon meerdere keren op dezelfde dag als eerste kandidaat wordt voorgesteld.

Deze logica staat bewust **niet** in het dashboard.

### 7. Dashboard

`dvk/dashboard.py` is een presentatielaag. Het toont:

- leden met openstaande Ledendiensturen;
- open diensten;
- voorgestelde kandidaten;
- alternatieven en niet-voorgestelde kandidaten met reden.

Het dashboard gebruikt vooraf berekende engine-uitkomsten. Daarmee blijft acceptatiecriterium I02 behouden: geen verborgen selectie- of prioriteringsbeleid in de UI-laag.

### 8. Voorstel en menselijke beslissing

`dvk/proposals.py` maakt een uitlegbaar `AssignmentProposal` met de relevante uren-, team-, wedstrijd- en prioriteitscontext.

Een mens kan het voorstel vervolgens goedkeuren of gemotiveerd afwijzen. Afwijzing verwijdert de taakplicht niet en verandert de urenpositie niet.

### 9. Feitelijke indeling

`dvk/assignments.py` maakt alleen na goedkeuring een `DutyAssignment`.

Bij planning:

- A blijft gelijk;
- B blijft gelijk;
- C blijft gelijk;
- D stijgt met de ingeplande diensturen;
- E daalt overeenkomstig.

C verandert pas wanneer de dienst daadwerkelijk is uitgevoerd.

`dvk/dashboard_actions.py` orkestreert goedkeuren en afwijzen vanuit de dashboardcontext met dezelfde domeinfuncties; het voegt geen nieuw beleid toe.

## Geaccepteerde acceptatiebasis

De baseline wordt bewaakt door:

- **C01–C22** — bestaande functionele masterset;
- **W01–W13** — v0.3 werkstroomacceptatie;
- **I01** — bronimport naar canonieke DVK-objecten;
- **I02** — dashboard uitsluitend op basis van vooraf berekende uitkomsten;
- geïntegreerde end-to-endtests van taakplicht tot en met menselijke beslissing en `DutyAssignment`.

De afsluitende CI-run van de functionele acceptatie rapporteerde:

```text
59 passed
EINDRESULTAAT: functionele keten v0.3 reproduceerbaar.
```

## Belangrijkste structuur

```text
code/Prototype/
├── 22 cases.md
├── ontwerp-dvk-prototype-v0.2.md
├── ontwerp-dvk-prototype-v0.3.md
├── BASELINE-v0.3.md
├── README.md
├── pyproject.toml
├── run_cases.py
├── run_workstream_cases.py
├── run_import_cases.py
├── run_candidate_cases.py
├── run_priority_cases.py
├── run_dashboard.py
├── run_proposal_cases.py
├── run_assignment_cases.py
├── run_dashboard_actions.py
├── run_integrated_acceptance.py
├── dvk/
│   ├── model.py
│   ├── workstream_model.py
│   ├── cases.py
│   ├── workstream_cases.py
│   ├── rules.py
│   ├── duty.py
│   ├── engine.py
│   ├── import_adapter.py
│   ├── candidate_selection.py
│   ├── prioritization.py
│   ├── recommendation_planner.py
│   ├── dashboard.py
│   ├── proposals.py
│   ├── assignments.py
│   └── dashboard_actions.py
├── testdata/
│   └── v03_import/
└── tests/
```

De `dvk/` package is de uitvoerbare bron. Oudere losse Python-bestanden in de root van `code/Prototype/` zijn legacy uit eerdere prototypeversies.

## Uitvoeren

Vanaf `code/Prototype/`:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest -q
```

Leesbare acceptatie-uitvoer kan afzonderlijk worden uitgevoerd, bijvoorbeeld:

```bash
python run_cases.py
python run_workstream_cases.py
python run_dashboard.py
python run_dashboard_actions.py
python run_integrated_acceptance.py
```

GitHub Actions voert bij wijzigingen onder `code/Prototype/` automatisch de volledige regressiesuite en de acceptatierunners uit.

## Scopegrens van v0.3

Prototype v0.3 is een deterministisch functioneel prototype. Het voert nog geen productieacties uit in externe systemen.

Buiten deze baseline vallen onder meer:

- een echte Sportlink API-koppeling of productie-import;
- daadwerkelijk schrijven naar Sportlink;
- productie-e-mail of notificaties;
- authenticatie en productie-autorisatie van dashboardgebruikers;
- persistente workflow-/auditopslag;
- overige productie-integraties.

De architectuur is hier wel op voorbereid doordat bronadapters, domeinlogica, adviesplanning, menselijke besluitvorming en presentatie van elkaar gescheiden zijn.

## Baselineregel

Vanaf 8 september 2026 geldt:

> **Prototype v0.3 is functioneel geaccepteerd en vormt de regressiebaseline. Nieuwe ontwikkeling moet deze werking behouden, tenzij CKC expliciet een functionele wijziging besluit.**

Zie [`BASELINE-v0.3.md`](BASELINE-v0.3.md) voor de formele vastlegging.
