# DVK Prototype v0.3 — architectuur en werkstroomprototype

Dit is het zelfstandig uitvoerbare prototype van het Digitaal Verenigingskantoor (DVK).

De oorspronkelijke basis is de masterset C01–C22 uit `22 cases.md` en het ontwerp uit `ontwerp-dvk-prototype-v0.2.md`. In v0.3 is daarop een tweede, meer operationele keten toegevoegd voor ledendiensten: bronimport, taakplicht, urenpositie, kandidaatselectie, prioritering en dashboardweergave.

De ontwerpgrondslag sluit aan op `docs/informatiemodel/Canoniek_Informatiemodel.md`.

## Hoofdgedachte

De prototypeketen is:

`bronfeit → adapter → canoniek DVK-object → afleiding/beleid → werkstroomlogica → Decision/Signal/Action of dashboardweergave → test`

De kernprincipes zijn:

- brondata en beleidslogica blijven van elkaar gescheiden;
- het canonieke DVK-model vormt de gemeenschappelijke taal tussen bronnen en werkstromen;
- afleidingen en beslissingen zijn deterministisch en uitlegbaar;
- kandidaatselectie en prioritering zijn expliciet gescheiden;
- tests en testdata bewaken de lagen afzonderlijk én in samenhang;
- externe acties worden in het prototype nog niet daadwerkelijk uitgevoerd.

## Architectuuroverzicht

```text
                           DVK PROTOTYPE
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
   BRON / TESTDATA                              TESTSCENARIO'S
          │                                           │
 testdata/v03_import/                            dvk/cases.py
 ├─ members.csv                                 C01 … C22
 ├─ duty_hours.csv                                   │
 ├─ teams.csv                                        │
 ├─ matches.csv                                      │
 └─ services.csv                                     │
          │                                           │
          ▼                                           │
  import_adapter.py                                   │
          │                                           │
          │ vertaalt brondata                         │
          ▼                                           ▼
 ┌──────────────────────────────────────────────────────────┐
 │                  CANONIEK DVK-MODEL                      │
 │                                                          │
 │  dvk/model.py                    dvk/workstream_model.py  │
 │                                                          │
 │  Person                          DutyService              │
 │  Membership                      TeamMembership           │
 │  PersonRelationship              Match                    │
 │  RoleAssignment                  CandidateAssessment      │
 │  AuthorityGrant                  CandidatePriority        │
 │  SportlinkDutyRegistration       Dashboard...             │
 │  DutyQualification                                       │
 │  Decision / Signal / Action                              │
 │  PrototypeCase                                           │
 └───────────────────────────┬──────────────────────────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │  AFLEIDING / REGELS  │
                 └──────────┬───────────┘
                            │
             ┌──────────────┼────────────────┐
             │              │                │
             ▼              ▼                ▼
        dvk/rules.py     dvk/duty.py    overige regels
             │              │
             │              ├─ taakplicht bepalen
             │              ├─ vrijstellingen
             │              ├─ uitvoerder lid/ouder
             │              ├─ normuren toepassen
             │              └─ A-B-C-D → E
             │
             ▼
        dvk/engine.py
          RuleEngine
             │
             ▼
      Decision / Signal / Action
```

## De v0.3-ledendienstketen

Naast de oorspronkelijke rule-engine-keten bevat v0.3 een operationele werkstroom voor ledendiensten.

```text
 PrototypeCase + SportlinkDutyRegistration
                │
                ▼
             duty.py
      "is deze persoon taakplichtig?"
      "hoeveel uur resteert? (E)"
                │
                ├──────────────────────┐
                ▼                      │
      candidate_selection.py           │
                ▲                      │
                │                      │
      DutyService + Team + Match       │
                │                      │
                ▼                      │
       "is kandidaat geschikt?"       │
       "wedstrijd thuis/uit?"         │
       "lid of ouder/verzorger?"      │
                │                      │
                ▼                      │
        CandidateAssessment            │
                │                      │
                ▼                      │
        prioritization.py ◄────────────┘
                │
       actuele E-uren
       achterstand vorig seizoen
       wedstrijdvoorkeur
                │
                ▼
         CandidatePriority
                │
                ▼
           dashboard.py
                │
                ▼
       DashboardViewModel
       ├─ taakplichtigen
       ├─ open diensten
       ├─ voorgestelde kandidaten
       └─ niet-voorgestelde kandidaten
```

`candidate_selection.py` bepaalt geschiktheid en praktische wedstrijdcontext, maar rangschikt nog niet. `prioritization.py` rangschikt vervolgens de geschikte kandidaten transparant op resterende uren (`E`), eventuele achterstand uit het vorige seizoen en wedstrijdvoorkeur. Er wordt bewust geen verborgen gewogen score gebruikt.

## Verantwoordelijkheid per laag

```text
                        model.py
                   "Wat weet DVK?"
                          │
                          ▼
               rules.py / duty.py
              "Wat betekent dat?"
                          │
                          ▼
           candidate_selection.py
              "Wie kan dit doen?"
                          │
                          ▼
             prioritization.py
              "Wie eerst?"
                          │
                          ▼
                dashboard.py
           "Wat ziet de gebruiker?"
```

### 1. Canoniek model

`dvk/model.py` is het hart van het algemene DVK-prototype. Hierin staan onder meer:

- `Person`
- `Membership`
- `PersonRelationship`
- `RoleAssignment`
- `Resource`
- `AuthorityGrant`
- `RequiredAuthorization`
- `AccessGrant`
- `DutyRegistration`
- `SportlinkDutyRegistration`
- `DutyPolicy`
- `DutyQualification`
- `DutyPosition`
- `ClothingIssue`
- `ComplianceFact`
- `Signal`
- `Action`
- `Decision`
- `PrototypeCase`

`dvk/workstream_model.py` bevat aanvullende objecten die specifiek nodig zijn voor de operationele ledendienstwerkstroom, zoals `DutyService`, `TeamMembership`, `Match`, `CandidateAssessment`, `CandidatePriority` en de dashboard-viewmodels.

### 2. Regels en afleidingen

`dvk/rules.py` bevat de deterministische regels voor de oorspronkelijke C01–C22-functionele clusters.

`dvk/duty.py` bevat de expliciete grondslag voor de ledendienstlogica. Daar worden onder meer afgeleid:

- of iemand taakplichtig is;
- welke vrijstelling van toepassing is;
- of de uitvoerder het lid zelf of een ouder/verzorger is;
- hoeveel normuren uit CKC-beleid volgen;
- of de Sportlink-registratie daarvan afwijkt;
- de actuele urenpositie `A-B-C-D=E`.

De CKC-norm is beleidsinformatie en wordt dus niet als bronfeit behandeld.

### 3. Rule engine

`dvk/engine.py` vormt voor het oorspronkelijke C01–C22-model de orkestratielaag. Eén `PrototypeCase` wordt achtereenvolgens beoordeeld op onder meer lidmaatschap, relaties, ledendienst, kleding, autorisatie, compliance en datakwaliteit.

De uitkomst bestaat uit `Decision`, eventueel met `Signal` en `Action`.

### 4. Kandidaatselectie

`dvk/candidate_selection.py` beoordeelt per open dienst of iemand als kandidaat in aanmerking komt. Daarbij worden onder andere gebruikt:

- taakplicht;
- categorie lid of ouder/verzorger;
- teamlidmaatschap;
- thuis- of uitwedstrijd;
- overlap tussen wedstrijd en dienst;
- praktische voorkeur of uitsluiting.

Het resultaat is een `CandidateAssessment`.

### 5. Prioritering

`dvk/prioritization.py` rangschikt geschikte kandidaten. De volgorde is expliciet en uitlegbaar:

1. resterende uren `E`;
2. relevante achterstand uit het vorige seizoen;
3. wedstrijdvoorkeur;
4. stabiele tie-break op `person_id`.

Vanaf 1 december wordt de achterstand uit het vorige seizoen niet meer meegewogen.

### 6. Dashboard

`dvk/dashboard.py` vertaalt beslissingen, diensten, kandidaatbeoordelingen en prioriteiten naar een `DashboardViewModel` met:

- taakplichtigen met openstaande uren;
- nog te bezetten diensten;
- voorgestelde kandidaten;
- niet-voorgestelde kandidaten met reden.

Dit is de presentatielaag; de onderliggende beleidslogica blijft in de eerdere lagen.

## Bronimport en testdata

De map `testdata/v03_import/` bevat Sportlink-achtige CSV-bronnen:

```text
testdata/v03_import/
├── members.csv
├── duty_hours.csv
├── teams.csv
├── matches.csv
└── services.csv
```

`dvk/import_adapter.py` vertaalt deze bronrepresentaties naar canonieke DVK-objecten.

```text
Sportlink-achtige CSV
        │
        ▼
 import_adapter.py        ← kent bronvelden en formaten
        │
        ▼
 Canonieke DVK-objecten   ← brononafhankelijk
        │
        ▼
 duty / rules / selectie  ← kent CKC-beleid en werkstroomlogica
```

De adapter bevat bewust geen CKC-beleid. Daardoor kan later bijvoorbeeld een echte Sportlink API-adapter worden toegevoegd zonder de kernlogica voor taakplicht, selectie of prioritering fundamenteel te veranderen.

## Twee soorten testdata

Het prototype gebruikt bewust twee vormen van testdata:

1. `dvk/cases.py` — Python-fixtures voor de gezaghebbende C01–C22-scenario's;
2. `testdata/v03_import/` — externe, meer realistische bronbestanden voor de v0.3-import- en werkstroomketen.

De eerste vorm test vooral beslislogica. De tweede vorm test ook de overgang van bronrepresentatie naar canonieke objecten.

## Tests

De tests vormen een vangnet rond de verschillende lagen.

```text
                    PRODUCTIECODE
                         │
     ┌───────────────────┼──────────────────────┐
     │                   │                      │
 test_cases.py     test_workstream_v03.py  test_import_v03.py
     │                   │                      │
 C01–C22              duty/selectie/         CSV → DVK
 regelengine          prioritering             model
                                                │
                                                │
                                      test_dashboard_v03.py
                                                │
                                      model → dashboardbeeld
```

De huidige testmodules zijn:

```text
tests/
├── test_cases.py
├── test_import_v03.py
├── test_workstream_v03.py
└── test_dashboard_v03.py
```

## Huidige structuur

```text
code/Prototype/
├── 22 cases.md
├── ontwerp-dvk-prototype-v0.2.md
├── ontwerp-dvk-prototype-v0.3.md
├── README.md
├── pyproject.toml
├── run_cases.py
├── run_candidate_cases.py
├── dvk/
│   ├── __init__.py
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
│   └── dashboard.py
├── testdata/
│   └── v03_import/
│       ├── members.csv
│       ├── duty_hours.csv
│       ├── teams.csv
│       ├── matches.csv
│       └── services.csv
└── tests/
    ├── test_cases.py
    ├── test_import_v03.py
    ├── test_workstream_v03.py
    └── test_dashboard_v03.py
```

De oudere losse Python-bestanden in de root van `code/Prototype/`, zoals `model.py`, `rules.py`, `engine.py` en `cases.py`, zijn legacy uit v0.1. De `dvk/` package is vanaf v0.2 de uitvoerbare bron.

## Functionele clusters C01–C22

1. bestaande kern en ledendienst: C01–C09;
2. personen/gezinsrelaties: C03, C04, C20, C22;
3. kleding en beëindiging: C10;
4. governance/autorisatie: C11–C17 en C19;
5. compliance: C18;
6. datakwaliteit: C20–C22.

## Uitvoeren

Vanaf `code/Prototype/`:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest
```

Alle C01–C22-cases handmatig tonen:

```bash
python run_cases.py
```

De kandidaat-/werkstroomcases handmatig uitvoeren:

```bash
python run_candidate_cases.py
```

## Scope v0.3

Het prototype is nog steeds deterministisch en voert geen externe productieacties uit. `Action` beschrijft wat moet gebeuren, bijvoorbeeld e-mail sturen, toegang laten toekennen/intrekken of een blokkade handhaven.

De v0.3-importadapter leest uitsluitend lokale Sportlink-achtige CSV-testdata. Een echte productieverbinding met Sportlink, e-mail, kassasysteem of andere externe systemen valt nog buiten deze prototypefase.

De architectuur is daar wel bewust op voorbereid: externe bronnen worden via adapters vertaald naar canonieke DVK-objecten, waarna dezelfde afleidings- en werkstroomlogica kan blijven functioneren.
