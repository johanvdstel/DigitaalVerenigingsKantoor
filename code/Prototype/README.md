# DVK Prototype v0.4 — functioneel geaccepteerde baseline

**Status: functioneel geaccepteerd op 13 september 2026.**

Dit is het uitvoerbare prototype van het Digitaal Verenigingskantoor (DVK) voor de werkstroom Ledendiensten & Vrijwilligersbeleid. Prototype v0.4 bouwt voort op de volledig behouden v0.3-baseline en voegt read-only real-data-integratie toe.

De formele actuele baseline staat in [`BASELINE-v0.4.md`](BASELINE-v0.4.md). [`BASELINE-v0.3.md`](BASELINE-v0.3.md) blijft de historische en regressieve grondslag voor C01–C22, W01–W13 en I01/I02.

## v0.4 in één oogopslag

Prototype v0.4 voegt aan de bestaande v0.3-engine toe:

- real-data-import van leden-, functie-, commissie-, team- en urenfeiten;
- read-only Sportlink Programma-integratie voor wedstrijden;
- CKC ShiftCatalog als expliciete configuratiebron voor diensten en bezetting;
- read-only Sportlink Vrijwilligers-integratie voor concrete vrijwilligersregistraties;
- behoud en segmentering van afwijkende concrete dienstperioden;
- afleiding van staffing/open need;
- expliciete signalering van onbekende of ambigue taakcodes;
- provenance met onderscheid `SOURCE_FACT`, `CONFIGURATION` en `DERIVED`;
- integrale koppeling van echte-bronachtige data aan de bestaande kandidaat-, voorstel-, menselijke-beslissing- en assignmentketen.

De afsluitende GitHub Actions-run **#130** is volledig groen: **118 tests passed**, inclusief **3/3 R16–R18 geïntegreerde eindacceptatietests**.

## Architectuur

```text
Bronnen
  ├── Sportlink/exportdata
  ├── Sportlink Programma API
  ├── Sportlink Vrijwilligers API
  └── CKC ShiftCatalog
          │
          ▼
      adapters
          │
          ▼
   normalisatie
          │
          ▼
canonieke DVK-objecten
          │
          ▼
 bestaande v0.3-engine
          │
          ├── taakplicht / urenpositie
          ├── kandidaatselectie
          ├── prioritering
          └── adviesplanning
          │
          ▼
 AssignmentProposal
          │
          ▼
 menselijke beslissing
     ├── afwijzen → geen mutatie
     └── goedkeuren
             │
             ▼
       DutyAssignment
             │
             ▼
        D omhoog, E omlaag
```

Kernprincipe blijft:

> **DVK-voorstel ≠ CKC-besluit.**

## v0.4 integratielagen

### Real-data import

`dvk/real_data_import.py` normaliseert echte CKC-exportfeiten naar canonieke DVK-objecten en legt provenance en datakwaliteitssignalen vast. Ontbrekende of ambigue informatie wordt niet stilzwijgend ingevuld.

### Sportlink Programma

`dvk/programma_client.py` verzorgt de read-only HTTP-toegang. `dvk/programma_adapter.py` vertaalt bronregels naar canonieke `Match`-objecten, inclusief `HOME/AWAY`, statusverwerking en provenance. Niet-operationele wedstrijden worden niet als normale kandidaatcontext gebruikt.

### ShiftCatalog

`dvk/shift_catalog.py` behandelt de CKC ShiftCatalog als `CONFIGURATION`. Taakcode is de natuurlijke sleutel. Minimumbezetting bepaalt de noodzakelijke staffing; maximumbezetting blijft afzonderlijke registratie-/planningscapaciteit.

### Sportlink Vrijwilligers

`dvk/vrijwilligers_client.py` en `dvk/vrijwilligers_adapter.py` verwerken concrete registraties read-only. Koppeling aan diensten gebeurt via taakcode en datum/tijd, niet via de naam van de vrijwilliger als sleutel.

Afwijkende concrete Sportlink-dienstperioden blijven volledig bronfeit. DVK mag daaruit planbare segmenten afleiden langs catalogusgrenzen en werkelijke randtijden, maar mag geen periode stilzwijgend weggooien of verzinnen.

### Staffing en taakcoderesolutie

`dvk/staffing.py` leidt bezetting en open behoefte af. Deze uitkomsten hebben provenance `DERIVED`.

`dvk/task_code_resolution.py` koppelt uitsluitend exacte, unieke taakcodes. Onbekende, afwijkende en ambigue codes worden expliciet gesignaleerd; DVK gokt of corrigeert niet stilzwijgend.

## Provenancecontract

v0.4 maakt het onderscheid expliciet:

- `SOURCE_FACT` — feiten uit Sportlink of andere brondata;
- `CONFIGURATION` — CKC-inrichting, zoals ShiftCatalog;
- `DERIVED` — door DVK berekende uitkomsten, zoals staffing/open need.

Dit voorkomt dat een DVK-afleiding later ten onrechte als bronfeit wordt behandeld.

## Acceptatiebasis

De actuele regressiebasis bestaat uit:

- **C01–C22** — geaccepteerde v0.2-masterset;
- **W01–W13** — geaccepteerde v0.3-werkstroomcases;
- **I01/I02** — import- en UI/enginecontract uit v0.3;
- **R01–R18** — v0.4 real-data- en integratieacceptatie.

De v0.4-stappen zijn functioneel geaccepteerd als:

1. R01–R09 — real-data-import;
2. R10–R11 — Sportlink Programma;
3. R12 — ShiftCatalog;
4. R13/R13b — Sportlink Vrijwilligers en afwijkende concrete tijden;
5. R14 — staffing/open need;
6. R15 — onbekende/ambigue taakcodes;
7. R16 — provenance;
8. R17 — integrale weekendketen;
9. R18 — volledige regressie/eindacceptatie.

Zie [`BASELINE-v0.4.md`](BASELINE-v0.4.md) voor het formele acceptatiecontract.

## Belangrijkste structuur

```text
code/Prototype/
├── 22 cases.md
├── ontwerp-dvk-prototype-v0.2.md
├── ontwerp-dvk-prototype-v0.3.md
├── BASELINE-v0.3.md
├── BASELINE-v0.4.md
├── README.md
├── pyproject.toml
├── run_*.py
├── dvk/
│   ├── model.py
│   ├── workstream_model.py
│   ├── duty.py
│   ├── engine.py
│   ├── candidate_selection.py
│   ├── prioritization.py
│   ├── recommendation_planner.py
│   ├── proposals.py
│   ├── assignments.py
│   ├── real_data_import.py
│   ├── programma_adapter.py
│   ├── programma_client.py
│   ├── shift_catalog.py
│   ├── vrijwilligers_adapter.py
│   ├── vrijwilligers_client.py
│   ├── staffing.py
│   └── task_code_resolution.py
└── tests/
    ├── test_integrated_v03.py
    ├── test_integrated_v04.py
    └── ...
```

## Uitvoeren

Vanaf `code/Prototype/`:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest -q
```

GitHub Actions voert de volledige regressiesuite en afzonderlijke acceptatiestappen uit. Live Programma- en Vrijwilligersvalidatie wordt alleen in de daarvoor ingerichte handmatige workflowcontext uitgevoerd; gevoelige credentials worden niet in code, baseline of logs opgenomen.

## Scopegrens van v0.4

v0.4 valideert de read-only real-data-integratie en de volledige functionele keten. Buiten deze baseline vallen onder meer:

- automatisch schrijven naar Sportlink;
- productie-e-mail/notificaties;
- productie-authenticatie en -autorisatie;
- persistente workflow-/auditopslag;
- het vervangen van menselijke CKC-besluitvorming door automatische indeling.

## Baselineregel

Vanaf 13 september 2026 geldt:

> **Prototype v0.4 is functioneel geaccepteerd en vormt de actuele regressiebaseline voor de real-data-integratie van Ledendiensten. Nieuwe ontwikkeling moet R01–R18 én de onderliggende v0.3-baseline behouden, tenzij CKC expliciet een functionele wijziging besluit.**
