# DVK Prototype v0.1 — Rule Engine

Deze repository bevat uitsluitend de kernlogica van het eerste DVK-prototype:
geen Streamlit, geen database en geen externe koppelingen.

## Doel

Bewijzen dat we CKC-feiten kunnen omzetten in reproduceerbare besluiten,
met geautomatiseerde tests als vangrail.

De prototypeketen is:

`bronfeit -> canoniek prototype-object -> rule engine -> besluit -> test`

## Model

De minimale kern bestaat uit:

- `Person`
- `Membership`
- `RoleAssignment`
- `DutyRegistration`
- `ClothingIssue`
- `AccessGrant`
- `PrototypeCase`
- `Decision`

## Elf cases

1. Actief volwassen spelend lid, 4/10 uur ledendienst.
2. Actief volwassen spelend lid, 10/10 uur voltooid.
3. Minderjarig eerste kind; ouder/verzorger voert de verplichting uit.
4. Jonger minderjarig kind; vrijstelling via broederdienst.
5. Spelend trainer; actief lid plus functievrijstelling.
6. Commissielid; statutair lid plus functievrijstelling.
7. Eenmalige barvrijwilliger/ouder; geen lid.
8. Erelid; actief lid en vrijgesteld.
9. Recreant; statutair lid ondanks niet-competitieve deelname.
10. Opgezegd lid met nog niet ingeleverde CKC-kleding.
11. Beheerder CKC Kleding Beheer Tool met raadpleeg-, update- en toegangsbeheerrecht.

Daarnaast staat er één negatieve guardrail-test in:
een niet-beheerder mag geen `manage_access`-recht uitoefenen voor de
CKC Kleding Beheer Tool.

## Uitvoeren

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

## Ontwerpkeuze

De rules zijn bewust pure Python-functies. Daarmee kunnen we eerst de
inhoud en testbaarheid stabiliseren. YAML-regels of een beheerinterface
kunnen later worden toegevoegd zonder het canonieke gegevensmodel of de
tests opnieuw te hoeven ontwerpen.

## Belangrijke prototype-aanname

Voor v0.1 staat `broederdienst_exempt` nog als expliciet contextfeit in
de testcase. In een volgende iteratie moet dit een afgeleide kwalificatie
worden uit ouder-kind- en broer/zusrelaties plus leeftijd en
lidmaatschapsstatus.

Ook de lijst `FUNCTION_EXEMPT_ROLES` is in v0.1 expliciet en lokaal.
Die hoort later uit CKC-beleid/configuratie te komen.
