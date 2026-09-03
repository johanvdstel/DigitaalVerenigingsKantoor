# DVK Prototype v0.2 — Rule Engine

Dit is het zelfstandig uitvoerbare prototype van het Digitaal Verenigingskantoor voor de masterset C01–C22 uit `22 cases.md`.

De ontwerpgrondslag staat in `ontwerp-dvk-prototype-v0.2.md` en sluit aan op `docs/informatiemodel/Canoniek_Informatiemodel.md`.

## Prototypeketen

`bronfeit → canoniek object → afleiding → beleidsgevolg → Decision/Signal → Action → test`

## Structuur

```text
code/Prototype/
├── 22 cases.md                         # gezaghebbende masterset
├── ontwerp-dvk-prototype-v0.2.md      # goedgekeurd ontwerp
├── pyproject.toml                     # installeerbaar Python-project
├── run_cases.py                       # handmatige runner
├── dvk/
│   ├── __init__.py
│   ├── model.py                       # canoniek prototype-model
│   ├── cases.py                       # C01-C22 testdata
│   ├── rules.py                       # deterministische regels
│   └── engine.py                      # rule orchestration
└── tests/
    └── test_cases.py                  # geautomatiseerde C01-C22 regressietests
```

De oudere losse Python-bestanden in de root van `code/Prototype/` zijn legacy uit v0.1. De `dvk/` package is vanaf v0.2 de uitvoerbare bron.

## Functionele clusters

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

Alle cases handmatig tonen:

```bash
python run_cases.py
```

## Scope v0.2

Het prototype is deterministisch en voert nog geen externe acties uit. `Action` beschrijft wat moet gebeuren, bijvoorbeeld e-mail sturen, toegang laten toekennen/intrekken of een overschrijvingsblokkade handhaven. Koppelingen met Sportlink, e-mail, kassasysteem of andere productiebronnen vallen buiten v0.2.
