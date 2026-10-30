# Iteratie 3 — BL-23 en BL-24

Status: BL-23 en BL-24 functioneel geaccepteerd op 30 oktober 2026 op oplevercommit `0aa8445d9f70d2f099f2599e117035f00d05e0a1`. De opdrachtgever gaf daarna afzonderlijk akkoord voor merge van PR #56, mits de acceptatie eerst is gedocumenteerd. Geen integrale v0.5-acceptatie.

Baselinebranch: `prototype-v0.5`, geverifieerde GitHub-HEAD `240aeaec5958a84d6bd9a02a699065513e98115d`. Deze bevat Iteratie 2-codebaseline `d8b405a3f2888652efcb42c1a7e832ccc6292ef8` plus de aanvullende live-verificatie. De lokale integratiebranch liep alleen deze documentatiecommit achter.
Werkbranch: `codex/iteratie-3-bronstatus-rubrieken`. Werkmap: `/private/tmp/dvk-iteratie-3`. De oplevercommit en PR worden in de terugrapportage vastgelegd; dit verslag behoort tot diezelfde commit.

## Context, bewijs en herleiding

Geaccepteerde releasebaseline blijft v0.4 op main. v0.5 is prototypeontwikkeling; Iteraties 1 en 2 zijn afzonderlijk geaccepteerd. Sportlink blijft bronhouder van exports en API-gegevens; CKC/Johan bepaalt beleid en functionele acceptatie. De historische export is optioneel en de planner borgt het juiste vorige seizoen. Gelezen: AGENTS.md, README, backlog, prototypeplanning, productieroadmap, Iteratie-2-verslag, broncontracten en herijkte Ledendiensten-baseline, relevante code en tests. Het overige broncontract is een reconstructieconcept, geen nieuwe geaccepteerde eis.

Vastgesteld in code: `_render_planning` had vijf hoofdcontainers, met een extra uitgeklapte wedstrijdrubriek. `VolunteerPlanningApplicationService.planning_data` leverde uitsluitend Vrijwilligers-status aan `overview.source_statuses`. De kandidaatcontext bevatte Programma-resultaat/statistieken en bronbestandsnamen, maar gooide het beschikbare gezamenlijke CSV-inleesmoment weg. De afzonderlijke historische bron had geen inleesmoment.

Expliciete eisen: uitsluitend BL-23 en BL-24 uit de goedgekeurde Iteratie-3-opdracht. De BL-18-startstand vervalt alleen waar deze opdracht dat bepaalt. Geen selectie-, beleids-, opslag- of importvalidatieregels veranderd. Geen migratie of aanvullende infrastructuur nodig: de ontbrekende presentatie en twee in-memory metadatawaarden volstaan. Geaccepteerde regressiefixtures blijven ongewijzigd; alle tests en browserproeven gebruiken synthetische gegevens.

## Gewijzigde bestanden en reden

| Bestand | Reden |
| --- | --- |
| `streamlit_app.py` | Vijf native expanders, aanvankelijk dicht; bestaande widgets behouden. Wedstrijdtabel direct in hoofdrubriek. Compleet bronoverzicht via presenter. |
| `dvk/planning_source_presenter.py` | Acht vaste bronregels, onderscheid laadstatus/bruikbaarheid en toelichting, API-succes versus gegevens, eerlijk onbekende tijdstippen. Geen ophalen of beleidslogica. |
| `dvk/candidate_context.py` | Bestaande `LoadedLocalExports.loaded_at` behouden als `csv_loaded_at`; expliciet aangeleverde bytes hebben zonder metadata een onbekend moment. |
| `dvk/historical_backlog.py` | Optioneel in-memory `loaded_at`, standaard onbekend. |
| `dvk/local_csv_sources.py` | Tijdstip na werkelijk lezen van historische bron; ontbrekende/onleesbare bron houdt onbekend tijdstip. |
| `tests/test_planning_source_status_v05.py` | Synthetische bronstatus-, tijdstip-, fout-, waarschuwing- en UI-regressies. |
| `tests/test_planning_sections_bl18.py`, `tests/test_navigation_v05.py` | Bestaande structuurproeven aanpassen aan expliciet gewijzigde BL-23-startstand; inhoud, widgets en selectiecontroles behouden. |
| `README.md`, `BACKLOG.md`, `DVK-PROTOTYPE-PLANNING.md`, dit verslag | Technische status en acceptatieprotocol; geen functionele acceptatieclaim. |

## Bronpresentatie en beperkingen

- De vijf reguliere bronnen houden hun gezamenlijke, werkelijk geregistreerde inleesmoment. Dit is geen exportdatum of bewijs van inhoudelijke actualiteit. Functies en Commissies krijgen geen ouderdomswaarschuwing.
- Bij afgebroken reguliere CSV-import is er geen individuele laadadministratie: alle vijf blijven zichtbaar als niet geladen, bruikbaarheid onbekend, met de bestaande foutmelding (inclusief ontbrekend bestand waar bekend). Andere bestanden worden niet als bewezen ontbrekend of bruikbaar voorgesteld. Er worden geen extra bestanden gelezen voor deze tabel.
- Historie toont eigen beschikbaarheid, eventuele gedeeltelijke bruikbaarheid en bestaand plannerbericht. Ontbreken blokkeert de planning niet.
- Vrijwilligers gebruikt bestaande laatste succesvolle bronmetadata en laatste mislukte poging. Een mislukte verversing behoudt het tijdstip en de bruikbaarheid van de vorige bron; tabel vermeldt de mislukking en bronperiode. Geen verzonnen ophaalmoment bij een fout.
- Programma gebruikt bestaande kandidaatcontextmetadata. Een geldige lege lijst is technisch geslaagd, met nul operationele wedstrijden. Een geslaagde aanvraag met onbruikbare teamkoppeling blijft technisch geslaagd maar inhoudelijk onbruikbaar. Bij een mislukte aanvraag is er geen succesvol ophaalmoment.
- Demonstratie toont expliciet synthetische planning en onbekende echte bronmomenten. Geen automatische verversing of broninhoudvergelijking toegevoegd.
- Native expanderstanden leven in de browser. Gewone heruitvoering behoudt deze; geen nieuwe duurzame UI-opslag. De bestaande Streamlit-runtime 1.64.0 is gebruikt. AppTest kan native open-/dichtklikken niet simuleren; die werking is aanvullend in de echte browser gecontroleerd.

## Verificatie

Definitieve volledige regressiesuite: **1263 geslaagd**, 0 mislukt of overgeslagen, in 75,66 seconden. Syntaxcontrole van de gewijzigde Python-modules en `git diff --check` geslaagd. CI op de exacte oplevercommit wordt na push in de definitieve terugrapportage vastgelegd.

Gericht: 31 tests geslaagd in 19,26 seconden, inclusief bronstatus, BL-23-structuur, navigatie, kandidaatcontext, historische bron en bevestigen/undo.
Alle elf synthetische scripts uit CI: exit 0 (run_cases, run_workstream_cases, run_import_cases, run_candidate_cases, run_priority_cases, run_dashboard, run_proposal_cases, run_assignment_cases, run_dashboard_actions, run_integrated_acceptance, run_v04_demo).

Eerste gerichte run: vier oude BL-18-structuurverwachtingen faalden; die zijn op grond van BL-23 aangepast. Geen functionele selectie- of fixtureverwachting versoepeld. De eerste lokale serverstart werd door sandbox-netwerktoegang geblokkeerd; de goedgekeurde start buiten de sandbox werkte.

Browserproef uitsluitend synthetisch op poort 8533: vijf rubrieken aanvankelijk dicht; alle vijf tegelijkertijd geopend; bronverversing veroorzaakte heruitvoering van run 2 naar run 4 met behoud van de standen; Instellingen sluiten liet de overige rubrieken open. Bronstatusoverzicht bevatte alle acht bronregels. Geen echte CKC-exports, databases of credentials gelezen. De lokale wijzigingen in de oorspronkelijke werkmap zijn niet aangeraakt.

## Praktisch lokaal acceptatieprotocol

Controleer eerst `git rev-parse HEAD` in `/private/tmp/dvk-iteratie-3` tegen de volledige oplever-SHA. Start uitsluitend de geïsoleerde synthetische launcher:

```bash
cd /private/tmp/dvk-iteratie-3/code/Prototype
/private/tmp/dvk-bl18-venv/bin/python -B tests/serve_synthetic_planning.py --members 3 --historical --port 8533
```

1. Open `http://127.0.0.1:8533` in een nieuwe tab. Alle vijf rubrieken zijn dicht. Open/sluit elk afzonderlijk; open ze vervolgens alle vijf. Geen andere rubriek mag hierdoor sluiten.
2. Kies een dienst en kandidaten. Controleer periode, seizoen en geselecteerde dienst. Klik Brongegevens vernieuwen: de open rubrieken blijven open. Kandidaatselecties mogen volgens bestaand verversingsgedrag worden gewist; bronverversing heeft daarin geen nieuw contract.
3. Bevestig een synthetische kandidaat en controleer de tijdelijke indeling en undo. Controleer dat bestaande waarschuwingen en No-showonderdelen bereikbaar blijven.
4. Open Databronnen → Bronstatus en actualiteit. Controleer alle zes CSV's en twee API's. Reguliere CSV-inleesmomenten zijn gelijk; historie heeft een eigen inleesmoment. Programma toont technisch geslaagd en nul operationele wedstrijden. Gebruik tabel-fullscreen of horizontaal scrollen voor alle kolommen.
5. Stop de launcher met Ctrl+C. Start zonder `--historical`: historie niet beschikbaar, tijdstip onbekend, zichtbare waarschuwing; gewone planning blijft bruikbaar.
6. Voor ontbrekende reguliere CSV, API-fouten, onbruikbare koppelingen, onbekende tijden en oude Functies/Commissies: voer de synthetische gerichte tests uit. Geen echte bestanden verwijderen of live API's gebruiken:

```bash
/private/tmp/dvk-bl18-venv/bin/python -m pytest -q tests/test_planning_source_status_v05.py tests/test_planning_sections_bl18.py tests/test_candidate_context_ui_v05.py tests/test_historical_backlog_ui_v05.py
```

De tijdelijke launcher heeft bewust geen Git-versiecaption; de gecontroleerde root en vooraf gecontroleerde Git-SHA bepalen de codeversie. Functionele acceptatie van deze exacte commit is op 30 oktober 2026 door de opdrachtgever bevestigd: BL-23 vijf lokale controles geslaagd; BL-24 vier aangepaste lokale controles geslaagd, overige uitzonderingssituaties gedekt door synthetische regressietests. Afzonderlijke merge-toestemming voor PR #56 is daarna verleend, onder voorwaarde van voorafgaande documentatie. Geen integrale v0.5-acceptatie.
