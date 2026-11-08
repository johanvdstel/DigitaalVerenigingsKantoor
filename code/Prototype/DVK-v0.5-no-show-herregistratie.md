# PR #38 — herregistratie na ingetrokken No-Show

## Grondslag en scope

Uitgangscommit `46b0eb39cc86186014b525ce11828bc11fe96de4`, bestaande werkbranch `codex/vrijwilligers-planning-integratie`, doel `prototype-v0.5`. De ontwerpbaseline blijft BL-16 / PR #39; v0.4 op main blijft de geaccepteerde releasebaseline. De expliciete vervolgopdracht van CKC bepaalt nu: alleen een niet-ingetrokken No-Show blokkeert herregistratie op dezelfde Sportlink-inroostering. Ingetrokken feiten en hun intrekkingen blijven duurzaam in de historie, zonder effect op de actuele teller/sanctie.

Vastgestelde blokkades: `register()` keek naar één historische registratie; `sportlink_no_show_events.assignment_id` had bovendien een UNIQUE-tabelbeperking. Alleen de applicatiecontrole wijzigen zou dus alsnog een databasefout veroorzaken. De hieronder beschreven schemawijziging is noodzakelijk voor de opgedragen regel, niet voor een andere architectuur of nieuw beleid.

## Wijzigingen

- `dvk/application_services.py`: controleert de gehele historie voor dezelfde inroostering en weigert zodra één registratie geen intrekking heeft. De bestaande `BEGIN IMMEDIATE` serialiseert controle en registratie, zodat ook gelijktijdige registraties maximaal één actief feit opleveren. Persoonskoppeling, actor, bronherkomst, actieve sessie, bronrevisie, periode, sanctieafleiding en commit blijven behouden.
- `dvk/persistence/no_show_records.py`: voegt een volledige historiequery per inroostering toe. Het oude enkelvoudige toegangspunt blijft compatibel en retourneert het eerste historische feit; de registratiecontrole gebruikt voortaan de volledige historie.
- `dvk/persistence/migrations.py`: voegt uitsluitend stap 13 toe. Migraties 1–12 blijven inhoudelijk ongewijzigd.
- `tests/test_no_show_reregistration_v05.py`: tien nieuwe synthetische gevallen: één/drie/zes cycli, andere actieve No-Show, twee gelijktijdige pogingen, behoud bij versie-12-upgrade, drie rollbackfouten en de UI-cyclus.
- `tests/test_no_show_sportlink_v05.py`: de verwachting na intrekking volgt het nieuwe expliciete besluit; de oorspronkelijke registratie en intrekking worden extra gecontroleerd.
- `tests/test_schema_validation_v05.py`, `test_gate10b_persistence_v05.py` en `test_dashboard_database_isolation_v05.py`: actuele versieverwachtingen worden 13; historische versie-12-controles blijven herkenbaar behouden. De upgrade-reeks test nu ook versie 12. Een toekomstige, niet-ondersteunde versie is voortaan 14.

## Expliciete schemawijziging: 12 → 13

In `sportlink_no_show_events` vervalt uitsluitend `UNIQUE(assignment_id)`. De primaire sleutel `no_show_id` blijft behouden. Een gewone index `idx_sportlink_no_show_assignment` ondersteunt het opvragen van alle historische registraties voor dezelfde inroostering. De regel maximaal één actieve registratie wordt in de applicatielaag onder de schrijflock afgedwongen; een ingetrokken registratie wordt niet verwijderd of overschreven.

SQLite kan deze inline UNIQUE-beperking niet afzonderlijk verwijderen. Stap 13 bewaart daarom de drie gekoppelde tabellen tijdelijk binnen dezelfde migratietransactie: events, revocations en sanction assessments. De tabellen worden met dezelfde gegevens opnieuw opgebouwd, met uitsluitend de genoemde beperking gewijzigd. De intrekkings- en sanctietabellen behouden hun definities, foreign keys, sleutels en intrekkingsuniciteit. Bestaande expliciete indexen en immutable triggers worden teruggeplaatst. Foreign-key-handhaving blijft ingeschakeld; integriteit wordt vóór en na de operatie gecontroleerd. Er is geen succesvolle tussenstaat waarin slechts een gedeelte van de historie is gepubliceerd.

De bestaande buitenste migratiesavepoint omvat alle DDL, kopieeracties, schemavalidatie en versieadministratie. Bij fouten wordt alles teruggedraaid. In synthetische proeven met fouten tijdens kopiëren, na de migratiestap en bij een ontbrekende vereiste index bleef het oorspronkelijke versie-12-bestand byte-identiek. Daarna slaagden de upgrade en herregistratie alsnog. Succesvolle upgrades behouden alle rijen en oorspronkelijke JSON-payloads van bestaande tabellen, met uitsluitend een nieuwe versieadministratieregel. Gewone heropening van versie 13 blijft read-only voor de historie.

De oudere, verlaten `no_show_events`-tabellen en de eerder geaccepteerde historische migratiesemantiek veranderen niet. Deze correctie voegt geen reconstructie van oude prototypegegevens toe. Geen reset vereist.

## Testresultaten

Uitsluitend synthetische gegevens in tijdelijke databases en AppTest-kopieën. Gerichte selectie: **187 geslaagd**, 0 mislukt/overgeslagen:

```text
python -m pytest -q tests/test_no_show_reregistration_v05.py tests/test_schema_validation_v05.py tests/test_no_show_sportlink_v05.py tests/test_gate9_hardening_v05.py tests/test_gate10c_application_v05.py tests/test_planning_session_source_v05.py tests/test_gate10b_persistence_v05.py tests/test_dashboard_database_isolation_v05.py
```

Volledige regressiesuite vanuit `code/Prototype`: `python -m pytest -q` — **917 geslaagd**, 0 mislukt/overgeslagen. Commit en CI-status worden in PR #38 en de oplevering vermeld.

Alle acht gevraagde registratie-/intrekkingsvoorwaarden zijn getest. Daarnaast: historie en teller na databaseheropening, immutable triggers en foreign keys na upgrade, één actieve registratie bij concurrentie, ongewijzigde BL-16-broncontroles en het echte Streamlit-pad met eenmalige resultaatmelding. C/W/I/R- en overige functionele regressies blijven behouden. Tussentijds faalden uitsluitend drie verouderde actuele-versieasserties; die zijn expliciet bijgewerkt voor schema 13, zonder de inhoudelijke behouds-/rollbackcontroles te versoepelen.

## Lokale functionele acceptatie en gegevensgrens

Codex heeft de bestaande lokale CKC-database niet geopend, gemigreerd, gewijzigd of gereset. Ook geen echte exports of live API-responsen gebruikt. De twee vooraf aanwezige lokale wijzigingen blijven buiten de commit. Er is geen nieuwe PR of merge.

De nieuwe code bevat wel een echte schema-upgrade: bij een latere, door Johan uitgevoerde normale initialisatie van een geldige versie-12-database wordt versie 13 transactioneel aangebracht. Plan die eerste lokale start bewust, met de applicatie gestopt en desgewenst vooraf een uitsluitend lokale back-up van de database. Geen reset uitvoeren; behoud van bestaande gegevens is juist het doel van deze upgrade.

Acceptatie na die eigen lokale start:

1. Hervat een planning met geldige bron en een betrouwbaar gekoppelde inroostering; registreer een bedoeld acceptatiegeval.
2. Controleer eerste waarschuwing, actuele teller 1 en weigering bij een dubbele registratie.
3. Trek het feit expliciet in met toelichting; controleer teller 0 en blijvende historie.
4. Registreer opnieuw op exact dezelfde inroostering: geen databasefout, teller 1 en eerste waarschuwing als er geen andere actieve No-Shows zijn.
5. Controleer dat de nieuwe dubbele registratie opnieuw wordt geweigerd, terwijl de oude registratie en intrekking behouden zijn.
6. Herhaal een cyclus, navigeer/heropen de applicatie en controleer historie en actuele teller. Gebruik alleen bedoelde CKC-acceptatiegevallen en deel uitsluitend niet-herleidbare uitkomsten.

Nog niet aangetoond: upgrade en werking met de werkelijke lokale CKC-database; die functionele acceptatie volgt afzonderlijk. Groene tests en CI zijn geen functioneel acceptatie- of mergebesluit. PR #38 blijft open en ongemerged.
