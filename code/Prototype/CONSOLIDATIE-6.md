# Consolidatie 6 — Vereenvoudigingsbesluit

**Datum:** 23 september 2026 · **Type:** analyse/documentatie · **Status:** ter review, geen functionele acceptatie.

Gecontroleerde start: `prototype-v0.5`, commit `820c13cff547fca9f4f1fd94c8152b16922157be`, schone working tree. Werkbranch: `codex/c6-simplification`; PR-doel: `prototype-v0.5`. Alleen dit document wordt toegevoegd. Alle codeverwijzingen beschrijven deze startcommit; voorstellen worden hier niet uitgevoerd.

## 1. Samenvatting en grondslag

Prototype v0.5 is technisch nog beheersbaar: selectie, rangschikking, voorstellen, menselijke besluiten en opslag hebben herkenbare afzonderlijke verantwoordelijkheden. `application_services.py` bevat zes aparte serviceklassen, geen enkele klasse die alle processen combineert. Opsplitsen op bestandsomvang is daarom niet gerechtvaardigd. De grootste onderhoudsgrens ligt bij Streamlit: die orkestreert kandidaatvorming, leest repositories en bepaalt welke no-shows een vervangingspad krijgen. Daarnaast beschrijft het publieke UnitOfWork-protocol niet alle werkelijk gebruikte repositories en beschermt CI de UI-syntax niet expliciet.

Uitkomst: **16 onderdelen: 5 Behouden, 6 Documenteren, 5 Vereenvoudigen**. De vereenvoudigingen zijn kleine vervolgvoorstellen binnen bestaande grenzen. Geen samenvoeging van domeinconcepten, nieuw fixture-framework of productiecode-refactor is nodig om deze analyse op te leveren. De lokale volledige regressiesuite slaagt met **224 tests**; dit bewijst geen integrale functionele acceptatie van v0.5.

Grondslag: [AGENTS.md](../../AGENTS.md), [ontwikkelworkflow](../../docs/ontwikkelworkflow-codex.md), [v0.4-baseline](BASELINE-v0.4.md), [v0.3-baseline](BASELINE-v0.3.md), [C-masterset](22%20cases.md), [v0.2-ontwerp](ontwerp-dvk-prototype-v0.2.md), [v0.3-ontwerp](ontwerp-dvk-prototype-v0.3.md), het [canonieke informatiemodel](../../docs/informatiemodel/Canoniek_Informatiemodel.md), implementatie, tests en testdata in deze checkout. v0.4 blijft de geaccepteerde baseline; Gate-tests zijn v0.5-ontwikkelregressies. De oorspronkelijke kaarten uit Consolidatie 1–5 zijn niet als afzonderlijke documenten in deze checkout aangetroffen; onderstaande kruiskaart is uit de aanwezige bronnen gereconstrueerd.

## 2. Functionele ketenkaart

### Bron tot assignment

```text
v0.3 CSV-bestanden → import_adapter.SportlinkCsvImportAdapter
v0.4 exports      → real_data_import.SportlinkRealDataAdapter
Programma/Vrijwilligers → read-only clients → adapters
ShiftCatalog (configuratie) → DutyService; registraties → staffing/open need
                         ↓
canonieke personen, lidmaatschappen, uren, teams, wedstrijden en diensten
                         ↓
duty: taakplicht / uitvoerdercategorie / E = A − B − C − D
                         ↓
candidate_selection.assess_candidate → CandidateAssessment
                         ↓
prioritization.prioritize_candidates → CandidatePriority
                         ↓
proposals.create_assignment_proposal → AssignmentProposal
                         ↓
mens selecteert en bevestigt of wijst gemotiveerd af
                         ↓
ProposalDecisionApplicationService → dashboard_actions
  → proposals.assess_proposal → HumanDecision
  → assignments.create_duty_assignment → DutyAssignment bij goedkeuring
  → assignments.apply_assignment_to_case → nieuwe urenpositie (D↑, E↓)
                         ↓
UnitOfWork: voorstel + besluit + eventuele assignment; commit/rollback
```

Dit is een kaart van componenten, geen claim dat de huidige demo al deze bronnen integraal aansluit. `EngineRunApplicationService.record` registreert een run; hij voert de engine niet uit. `RuleEngine.evaluate` bedient de historische C-regels via `rules.py`; de W-keten gebruikt onder meer `duty.py` en de selectie-/planningsfuncties. R17 bouwt zijn keten expliciet op in `tests/test_integrated_v04.py`.

Drie verschillende betekenissen van planning moeten zichtbaar blijven:

| Component | Feitelijke verantwoordelijkheid en aansluiting |
| --- | --- |
| `recommendation_planner.plan_recommendations` | Historische v0.3-adviesplanning over meerdere diensten; spreiding op dezelfde dag en gelijke eerste keuzes. `dashboard.build_dashboard` ontvangt het berekende plan. |
| `proposal_planning.plan_proposals` | v0.5-selectie van gerangschikte voorstellen tot resterende maximumcapaciteit; onderscheid minimumdekking/optionele aanvulling. Geen assignment. |
| `planning.build_planning_overview` | Alleen leesoverzicht van periode, diensten, reeds afgeleide staffing, wedstrijden, bronstatus en datakwaliteit. `PlanningApplicationService` autoriseert dit. |

Streamlit gebruikt `_demo_proposals` → selectie → prioritering → voorstel → `plan_proposals`. Deze route roept **niet** `plan_recommendations` aan. Beide paden mogen niet stilzwijgend worden samengevoegd of als identieke dekking worden gepresenteerd. De keten is met deze kaart te volgen; alleen de huidige bestandsnamen maken dit onderscheid onvoldoende duidelijk.

`dashboard_actions.py` is UI-onafhankelijke orkestratie ondanks zijn naam. De applicatieservice voegt autorisatie en optionele persistence toe. `approve_many` controleert onder meer capaciteit en schrijft de batch met één commit; de contextmanager verzorgt rollback bij een fout. Goedkeuring alleen verandert geen Sportlink-bronfeit: de teruggegeven bijgewerkte case en opgeslagen assignment zijn geen write-back. C blijft gelijk bij inplanning; negatieve E blijft toegestaan.

### Assignment tot vervangende uitvoering

```text
bestaande DutyAssignment + menselijke no-showregistratie
  → NoShowApplicationService.register: autorisatie / identiteit / referentie
  → no_show.assess_sanction: SanctionAssessment
  → no-showfeit en beoordeling opslaan

no-showhistorie + replacementhistorie
  → replacement_duty.active_sanction_state: actuele sanctiestatus
  → mens regelt bestaande vervangende assignment
  → ReplacementDutyApplicationService.register_replacement: koppeling
  → bevoegde mens bevestigt uitvoering via complete_replacement
  → uitvoering opslaan → actieve sanctiestatus opnieuw afleiden
```

`no_show.py` beschrijft gebeurtenissen, seizoensgrens en sanctieladder. `replacement_duty.py` beschrijft de afzonderlijke koppeling/uitvoering en afgeleide actieve toestand. Historische beoordeling en actuele toestand zijn verschillende resultaten. De service bewaakt bevoegdheden en referenties; repositories bewaren feiten en resultaten. Samenvoegen van beide domeinen verhelpt geen chronologieprobleem.

**Bekende ontwikkelgrenzen:** `NoShowApplicationService.register` gebruikt `assess_sanction` met no-showhistorie zonder replacements; `_state` gebruikt wel beide. `active_sanction_state` herkent een voltooide vervanging via het no-show-ID, zonder de uitvoeringstijd in de gebeurtenisvolgorde te verwerken. `complete_replacement` controleert nog niet of op de vervangende assignment een no-show staat. Streamlit gebruikt bij een normale no-show diensttijd, maar bij een replacement-no-show `now`, en meldt na voltooiing onvoorwaardelijk teller 0. Dit zijn concrete aandachtspunten voor de afzonderlijke Gate-10-opdrachten, geen in C6 vastgestelde nieuwe beleidsregels of opgeloste punten A–F.

### Import en persistence

`import_adapter.py` verwerkt de historische vijfdelige CSV-fixture. `real_data_import.py` verwerkt andere bronkolommen, cardinaliteiten, duplicaten, provenance en expliciete datakwaliteit. Dat zijn verschillende broncontracten: bijvoorbeeld de oude adapter behandelt lege B/C/D als nul, terwijl de real-data-adapter ontbrekende verplichte uren signaleert. Een gedeelde parser zou die verschillen kunnen uitwissen.

`import_management.py` levert batch-/snapshotmodellen en opslagonafhankelijke vergelijking. `import_workflow.py` vergelijkt met het vorige snapshot en bevestigt een gevalideerde batch transactioneel. `ImportApplicationService` voegt autorisatie en de bevestigersidentiteit toe. Hij ontvangt reeds opgebouwde `SnapshotRecord`-objecten; de service vormt geen automatische export-naar-snapshotpipeline. Documenteer deze overdracht en de commit-eigenaar; voeg geen extra abstractielaag toe.

`persistence/migrations.py` beheert schema/integriteit, `sqlite.py` verbindingen en transacties, de `*_records.py`-modules serialisatie en gerichte opslag. In de onderzochte opslagcode wordt geen sanctieladder, kandidaatprioriteit of gezinsvrijstelling berekend. De SQL-filter `n.status='valid'` in `SQLiteSanctionAssessmentRepository.get` is wel functioneel zichtbaar: een ingetrokken no-show levert geen effectieve opgeslagen sanctie op. Leg dit leescontract vast naast historische versus actieve status; verplaats geen verdere sanctieafleiding naar SQL. Foreign keys, uniciteit en versiecontroles blijven integriteitsbewaking.

## 3. Regressie- en testdatakruiskaart

Paden hieronder zijn relatief aan `code/Prototype/`. Een technische test is niet automatisch een nieuwe functionele cataloguscase.

| Functionele bescherming | Implementatie / tests | Testdata en karakter |
| --- | --- | --- |
| C01–C22: lidmaatschap, plicht, relaties, kleding, bevoegdheden, VOG, datakwaliteit | `engine.py`, `rules.py`, `tests/test_cases.py` | **Basisfixtures:** `dvk/cases.py`; normatieve beschrijving in `22 cases.md`. Ook de niet-planningscases blijven beschermd. |
| W01–W10, W13: plicht, uitvoerder, gezin, E, context, rangorde | `duty.py`, `candidate_selection.py`, `prioritization.py`; `tests/test_workstream_v03.py` | **Basisfixtures:** `dvk/workstream_cases.py`; lokale teams/wedstrijden/backlog in tests. W08 vergelijkt E=7 met E=3. |
| W11/W12: menselijke goedkeuring/afwijzing, D/E, C onveranderd | `proposals.py`, `assignments.py`, `dashboard_actions.py`; `tests/test_assignments_v03.py`, `test_proposals_v03.py`, `test_dashboard_actions_v03.py` | **Lokale scenariodata:** `_fixture()` in assignment-tests op basis van W08, met eigen dienst/team/wedstrijd. W11/W12 zijn volwaardige W-cases, ook zonder eigen object in `W_CASES`. |
| I01: bronimport; I02: dashboard gebruikt berekende uitkomsten; integrale v0.3-keten | `tests/test_import_v03.py`, `test_dashboard_v03.py`, `test_integrated_v03.py` | **Brondataset:** `testdata/v03_import/{members,duty_hours,teams,matches,services}.csv`; daarnaast lokale W-gebaseerde dashboard-/ketenscenario's. |
| R01–R09: identiteit, cardinaliteit, normalisatie, urenreconciliatie, negatieve E | `real_data_import.py`; `tests/test_real_data_import_v04.py` | **Lokale scenariodata als tijdelijke brondatasets:** exportbestanden opgebouwd door de tests. Niet verwarren met v0.3-CSV. |
| R10–R15, inclusief R13b: read-only clients, wedstrijden, catalogus, registraties/segmenten, staffing, exacte taakcodes | `tests/test_programma*_v04.py`, `test_shift_catalog_v04.py`, `test_vrijwilligers*_v04.py`, `test_staffing_v04.py`, `test_task_code_resolution_v04.py` | **Lokale scenariodata:** bronregels, responsen, tijdvakken en catalogusdefinities. Geen live bron nodig voor pytest. |
| R16–R18: provenance, menselijke weekendketen en behoud volledige baseline | `tests/test_integrated_v04.py` en volledige regressiesuite | **Lokale ketenfixture:** `_integrated_fixture()`, onder meer W08. R18 betekent volledige regressiebehoud; geen eis voor een aparte test met naam R18. |
| Gate 1–3: persistence, snapshots, runcontext | `test_persistence_v05.py`, `test_import_snapshots_v05.py`, `test_run_context_v05.py`, `test_versioning_v05.py` | **Lokale scenariodata:** `tmp_path`-databases, batches, records, versieobjecten en fetches; heropenen/rollback/provenance. |
| Gate 4–6: expliciet beleid, applicatieservices en autorisatie | `test_policy_v05.py`, `test_application_services_v05.py`, `test_security_v05.py`; aanvullend `test_season_closing_v05.py` | **Lokale scenariodata:** verschillende policyversies, adressen, identiteiten, importbatches en bevroren seizoenposities. Historische standaardpolicy blijft herkenbaar. |
| Gate 7–8: overzicht, selectie, capaciteit, besluiten, audit, atomiciteit | `test_planning_v05.py`, `test_gate8_v05.py`, `test_gate8_match_decision_tree_v05.py`, `test_gate8b_persistence_v05.py`, `test_gate8c_atomic_v05.py` | **Lokale scenariodata**, deels op W07/W08 en jeugd-W-cases; tijdsgrenzen, runcontext, dubbele IDs en rollback. |
| Gate 9: no-shows, sancties, correctie, autorisatie en UI | `tests/test_gate9*.py` | **Lokale scenariodata:** assignments, gebeurtenissen, seizoenen en databases; UI-tests lezen broncode als tekst. |
| Gate 10: actieve toestand, replacements, persistence, services en demo/UI | `tests/test_gate10*.py` | **Lokale scenariodata:** `ns`, `replacement`, `_seed`, `_replacement`; **integrale demodata:** `dvk/demo_data_v05.py`. |

De vier datacategorieën blijven gescheiden. `demo_data_v05.py` maakt afgeleide kopieën van W08/W07/W04; alleen de demo vult W04 aan met A/B/C/D=10/0/3/1. De oorspronkelijke W04-fixture wordt niet gewijzigd. De demotests toetsen kandidaatcontext en planninginputs; de UI-teksttests bewijzen geen volledige gebruikersinteractie. `test_gate10d_demo_v05.py` heeft ook een lokale `_context`; die kleine overlap rechtvaardigt geen centraal fixture-framework.

## 4. Classificatietabel

Risico betreft de kleinste vervolgactie; S1–S5 worden in §5 gespecificeerd.

| Onderdeel | Classificatie | Concreet probleem / reden | Beschermde regressies | Kleinste vervolgactie | Risico |
| --- | --- | --- | --- | --- | --- |
| Application services als bestand | **Documenteren** | Zes serviceklassen met eigen taken; bestandsdeling is niet het aangetoonde probleem | Gate 5/6/8/9/10 | Benoem per klasse ingang, autorisatie, delegatie en commitgrens | Laag |
| Kandidaatselectie en prioritering | **Behouden** | Geschiktheid en rangorde hebben verschillende inputs/uitkomsten | W03–W10/W13, Gate 4/8 | Geen refactor | Geen wijzigingsrisico |
| Drie planningsmodules | **Documenteren** | Dagspreiding, capaciteitsafkapping en leesoverzicht zijn verschillende paden | I02, W08/W09, R14, Gate 7/8 | Gebruik de aansluitingen uit §2 | Laag |
| Voorstel, besluit, dashboardactie, assignment | **Behouden** | Menselijk beslismoment en urenmutatie blijven expliciet; batch is atomair | W11/W12, R17, Gate 8b/8c | Geen samenvoeging | Geen wijzigingsrisico |
| Historische en real-data-adapters | **Behouden** | Verschillende broncontracten en foutsemantiek | I01, R01–R16 | Behoud adapters en bron/configuratie/afleiding | Geen wijzigingsrisico |
| Importmodellen, workflow en service | **Documenteren** | Snapshotbeheer is geen bronparser; overdracht en commit-eigenaarschap zijn verspreid | Gate 2/3/5/6, I01/R16 | Benoem inputcontract en bevestigingspad | Laag |
| Persistence-bestandsgrenzen | **Behouden** | Schema, transacties en objectserialisatie zijn afzonderlijke taken | Gate 1–3/8b/8c/9/10b | Geen samenvoeging; leescontract hierboven behouden | Geen wijzigingsrisico |
| UnitOfWork-/repositorycontract | **Vereenvoudigen** | Protocol loopt achter op concrete repositories en gebruikte methoden | Gate 1/5/8/9/10 | S4: bestaand contract aanvullen | Laag |
| No-show en replacement als domeinen | **Behouden** | Gebeurtenis/sanctie en herstel/actieve toestand zijn verschillende begrippen | Gate 9/10a–c | Chronologie afzonderlijk behandelen | Geen wijzigingsrisico |
| Historische versus actieve sanctiestatus | **Documenteren** | Registratie, opgeslagen beoordeling en actieve afleiding volgen verschillende routes | Gate 9/10 | Benoem routes en bekende grenzen uit §2 | Laag; functionele reparatie apart |
| UI: private state, repositorytoegang en statusselectie | **Vereenvoudigen** | UI kent `_state`, repositoryqueries en voorwaarden voor eerste no-show | Gate 6/9/10, I02-grens | S1: kleine publieke leesoperaties | Middel |
| UI: technische identifiers en labels | **Vereenvoudigen** | Replacementkeuzes tonen dienst-/assignment-ID en herhalen naamlookup | Gate 9/10 UI, geen wijziging W-fixtures | S2: één presentatiefunctie voor bestaande context | Laag/middel |
| UI: kandidaatorkestratie | **Vereenvoudigen** | `_demo_proposals` kent de hele domeinketen; vervanging van Streamlit vereist overdracht | W03–W10, I02, R17, Gate 7/8/10-demo | S3: bestaande orkestratie achter publieke service | Middel |
| Test- en fixturevindbaarheid | **Documenteren** | Functionele cases en technische fixtures hebben verschillende vindplaatsen | C/W/I/R en Gate 1–10 | Gebruik §3; geen dataverplaatsing | Laag |
| CI: zichtbaarheid Gate 9/10 | **Documenteren** | Geen aparte benoemde stap; tests draaien wel in volledige pytest | Gate 9/10 | Leg dekking vast; aparte rapportagestappen kunnen wachten | Laag |
| CI: UI-syntaxbescherming | **Vereenvoudigen** | Broncode-teksttests parsen/importeren Streamlit-app niet | Gate 9/10 UI | S5: één expliciete syntaxcheck in vervolgiteratie | Laag |

## 5. Kleinste vereenvoudigingsvoorstellen

### S1 — Publieke leesgrens voor no-show/replacement

- **Probleem en bewijs:** `streamlit_app.py:194–213` leest `uow.no_shows`/`uow.replacements`, roept `_state` aan en herhaalt de actieve-eerste-no-showvoorwaarde uit `application_services.py:95–97`. Ook regels 167/245 lezen assignments rechtstreeks; regel 220 selecteert vervangingskandidaten. De UI heeft zo kennis van opslag én domeintoestand. Database-initialisatie als samenstelling van de app is op zichzelf niet het probleem.
- **Betrokken modules:** `streamlit_app.py`, `application_services.py`; bestaande repositories en `replacement_duty.py` als ongewijzigde afhankelijkheden.
- **Functionele bescherming:** autorisatie, menselijke registratie/bevestiging, ingetrokken feiten en history/active-onderscheid; `test_gate9_application_v05.py`, `test_gate9_hardening_v05.py`, `test_gate10a_v05.py`, `test_gate10c_application_v05.py` en UI-regressies. I02 levert de architectuurgrens, maar zijn historische tests dekken deze UI niet integraal.
- **Testdata:** bestaande lokale Gate-9/10-seeds en `tmp_path`-databases, inclusief gekoppelde/onvoltooide/voltooide replacement en ingetrokken no-show.
- **Minimale wijziging:** voeg geautoriseerde publieke leesoperaties aan de bestaande services toe voor benodigde assignment- en replacementcontext; laat de UI die resultaten tonen. Verplaats alleen de bestaande selectie, met ongewijzigde volgorde en huidige limiet van 50 assignments. Geef `_state` niet uitsluitend een publieke naam: de repositorylussen moeten uit de UI verdwijnen. Gerichte service-/grensregressies moeten dezelfde uitkomsten bewijzen.
- **Risico en non-goals:** verplaatsing kan selectie of permissies veranderen. Geen wijziging van sanctiehoogte, chronologie, tijdzone, herstelvoorwaarden, limiet, schema of Gate-10-punten A–F. Bestaand foutgedrag wordt niet stilzwijgend beleidscontract; functionele correcties krijgen een afzonderlijke opdracht.

### S2 — Eén menselijke identificatie voor assignmentkeuzes

- **Probleem en bewijs:** `streamlit_app.py:216–234` herhaalt `W_CASE_BY_ID`-naamlookup; replacementlabels gebruiken `service_id` of `assignment_id` terwijl de normale no-showselector bij beschikbare context datum/tijd/dienst toont. Dit maakt hetzelfde object verschillend herkenbaar en koppelt presentatie aan historische fixtures.
- **Betrokken modules:** `streamlit_app.py`, de publieke context uit S1; bestaande demo-/planningdata leveren namen en dienstgegevens.
- **Functionele bescherming:** stabiele interne selectie-ID, geen verandering van toewijzing, geen gegokte identiteit/tijd; `test_gate9_ui_regression_v05.py`, `test_gate10d_no_show_ui_v05.py`, `test_gate10d_ui_v05.py`.
- **Testdata:** bestaande demodata plus lokale assignment met beschikbare en ontbrekende context. Historische W-fixtures blijven intact.
- **Minimale wijziging:** één gedeelde formattering voor datum/tijd, dienst en naam uit aangeleverde context; ID blijft interne sleutel. Ontbrekende informatie expliciet tonen, niet reconstrueren uit namen of een technisch ID. Een nieuwe persistente namen-/dienstenbron valt buiten dit voorstel.
- **Risico en non-goals:** gelijke labels mogen verschillende assignments niet samenvoegen. Geen nieuwe zoek-/selectieregel, policy, schema, eventtijd of vervangingsvoorwaarde. De presentatie van ontbrekende context moet bij de vervolgopdracht expliciet worden vastgesteld.

### S3 — Bestaande kandidaatorkestratie uit Streamlit

- **Probleem en bewijs:** `streamlit_app.py:55–63` combineert demo-input, geschiktheid, filtering, rangorde, proposal-ID en capaciteitsplanning. Domeinregels worden aangeroepen in plaats van opnieuw berekend, maar de keten is niet via een publieke applicatieservice bruikbaar zonder UI-kennis.
- **Betrokken modules:** `streamlit_app.py`, `application_services.py`; ongewijzigde functies uit `candidate_selection.py`, `prioritization.py`, `proposals.py`, `proposal_planning.py`.
- **Functionele bescherming:** W03–W10, voorstel ≠ besluit, Gate-8-capaciteit en wedstrijdboom, stabiele proposal-run-ID over reruns; `test_gate8_v05.py`, `test_gate8_match_decision_tree_v05.py`, `test_gate9_ui_regression_v05.py`, `test_gate10d_demo_v05.py`; W11/W12/R17 bewaken het vervolg.
- **Testdata:** `demo_data_v05.py` en bestaande lokale Gate-8-scenario's; demo-aanvulling W04 blijft lokaal aan de demo.
- **Minimale wijziging:** een publieke methode op de bestaande planningservice orkestreert dezelfde functies met expliciete cases, teams, datum, backlog en run-ID als input. UI levert demo-input en presenteert output. Eerst het onderscheid met `plan_recommendations` uit §2 vastleggen; daarna gelijkblijvende resultaten en autorisatie gericht toetsen.
- **Risico en non-goals:** verandering van ID-generatie, datum of volgorde kan reruns/besluiten beïnvloeden. Geen andere rangorde, dagspreiding toevoegen, demo vervangen door live import, extra persistence, automatische assignment of nieuwe beleidsregel.

### S4 — Het bestaande UnitOfWork-contract compleet maken

- **Probleem en bewijs:** `persistence/unit_of_work.py:11` mist `proposals`, `decisions`, `assignments`, `no_shows`, `sanctions` en `replacements`, die `SQLiteUnitOfWork.__enter__` wel levert en services gebruiken. `DutyAssignmentRepository` mist `recent`; protocollen voor no-show/sanctie/replacement ontbreken. Een vervangende implementatie kan dus aan het beschreven contract voldoen en toch services niet ondersteunen.
- **Betrokken modules:** `persistence/unit_of_work.py`, `persistence/repositories.py`, typeverwijzingen in `application_services.py`; concrete opslag blijft gelijk.
- **Functionele bescherming:** Gate 1/5/8b/8c/9/10b/10c: heropenen, auditrelaties, autorisatie, batchrollback.
- **Testdata:** bestaande `tmp_path`-databases en lokale service-/repository-seeds; geen nieuwe centrale fixture.
- **Minimale wijziging:** uitsluitend reeds gebruikte repositories/methodesignatures beschrijven en de betrokken serviceparameters typeren. Controleer conformiteit met de huidige SQLite-implementatie; introduceer geen tweede database of generieke repositorylaag.
- **Risico en non-goals:** laag, maar imports mogen geen cyclus veroorzaken. Geen SQL-/schema-/serialisatiewijziging, andere commitgrens, herberekening of verplaatsing van businesslogica naar persistence.

### S5 — Expliciete syntaxcheck voor Streamlit

- **Probleem en bewijs:** `test_gate9_ui_regression_v05.py`, `test_gate10d_ui_v05.py` en `test_gate10d_no_show_ui_v05.py` zoeken tekst. De [workflow](../../.github/workflows/dvk-prototype-tests.yml) voert pytest/runners uit maar compileert `streamlit_app.py` niet expliciet. Een syntaxfout kan daardoor buiten deze bescherming vallen.
- **Betrokken bestanden:** uitsluitend een toekomstige workflowstap voor `streamlit_app.py`.
- **Functionele bescherming:** uitvoerbaarheid van Gate-7–10-presentatie boven op de bestaande suite; geen bewijs van functionele interactie of acceptatie.
- **Testdata:** geen scenariodata nodig voor compilatie; bestaande pytest-datasets blijven ongewijzigd meelopen.
- **Minimale wijziging:** één CI-commando `python -m py_compile streamlit_app.py` onder de al gebruikte Python-versie/werkdirectory. Deze iteratie wijzigt de workflow niet.
- **Risico en non-goals:** laag; dit importeert/start de UI niet. Geen browsertestframework, live Sportlink, nieuwe testcases of herschrijven van teksttests om een refactor te laten slagen.

**Afhankelijkheden, geen voorkeursranglijst:** S1 vereist de expliciete scheiding history/active uit §2; S2 gebruikt die publieke context. S3 vereist de planningskaart. S4 kan onafhankelijk, of vóór S1 als contractbasis. S5 kan onafhankelijk. Geen voorstel vereist samenvoeging van de domeinmodules.

## 6. Advies vóór hervatting Gate 10

**Eerst regelen voordat verantwoord verder wordt uitgebreid:** leg voor de volgende Gate-10-opdracht vast welk afzonderlijk probleem A–F wordt behandeld, met concrete gebeurtenistijden, verwachte actieve toestand en regressie. De volledige A–F-specificatie staat niet in deze checkout/opdracht; C6 vult die niet in. Scheid correctie van chronologie/replacement-no-show expliciet van S1. Voer S1 uit vóór verdere uitbreiding van de betreffende UI-selectielogica, zodat nieuwe regels niet opnieuw in Streamlit ontstaan. S5 is een kleine aanbevolen voorafgaande beschermingsstap bij komende UI-wijzigingen. Dit zijn vervolgacties ter besluitvorming, geen voorwaarde om het huidige analysedocument te accepteren of een gerichte Gate-10-bugfix te onderzoeken.

**Alleen documenteren:** verantwoordelijkheden/commitgrenzen van de zes services, de drie planningspaden, adapter-versus-snapshotoverdracht, historische versus actieve sanctiestatus en de vier testdatacategorieën. Dit document biedt het compacte overzicht; geen nieuwe documentatiehiërarchie nodig. Gate 9/10 zitten al in de volledige pytest-stap; afzonderlijke CI-stapnamen leveren zichtbaarheid, geen ontbrekende testdekking.

**Kan wachten tot na v0.5:** S4 zolang SQLite de enige implementatie is; S3 zolang de huidige demo-orkestratie niet wordt uitgebreid; afzonderlijke CI-rapportagestappen. S2 kan met de eerstvolgende betrokken UI-aanpassing worden meegenomen en hoeft geen algemene refactor te blokkeren. Bestanden samenvoegen, application services opsplitsen en fixtures centraliseren hebben op basis van deze analyse geen aangetoonde noodzaak.

**Tegenstrijdigheden en grenzen:** geen onoplosbaar conflict tussen geaccepteerde C/W/I/R-afspraken en tests vastgesteld dat deze classificatie blokkeert. De vroegere startnotitie over minder dan vijf uur vorig seizoen wordt expliciet verfijnd door het v0.3-ontwerp (§4 stap 7), dus is geen nieuw te kiezen beleid. De afwijkende Gate-9/10-statusroutes en UI-aannames uit §2 blijven ontwikkelproblemen; groen pytest neemt ze niet weg. Een vervolgwijziging die een ontbrekende CKC-regel of conflicterende verwachting blootlegt, moet stoppen voor besluitvorming. Dit document geeft geen functionele goedkeuring voor zo'n wijziging.

## 7. Verificatie en oplevergrens

- Startbranch, HEAD én lokale referentie `prototype-v0.5` zijn op de opgegeven SHA gecontroleerd; working tree was schoon vóór branchaanmaak.
- Implementatie, relevante baseline-/ontwerpdocumenten, C/W/I/R-tests, Gate-1–10-tests en fixturebronnen zijn onderzocht; geen tests of verwachte uitkomsten aangepast.
- `pytest -q` was aanvankelijk niet beschikbaar op PATH; de bestaande `.venv` bevatte Python 3.11.16 maar geen pytest. Een aparte tijdelijke omgeving `/private/tmp/dvk-c6-tests` kreeg pytest 9.1.1. Vanuit `code/Prototype` uitgevoerd: `PATH=/private/tmp/dvk-c6-tests/bin:$PATH PYTHONPATH=. pytest -q` → **224 passed in 0.62s**. Geen repositorydependencybestand gewijzigd.
- De opleverdiff mag uitsluitend dit nieuwe document bevatten. Productiecode, Streamlit, tests, fixtures, CSV, Actions, bestaande baselines, `AGENTS.md` en ontwikkelworkflow blijven ongewijzigd.
- Commit/PR en actuele CI-uitkomst worden in het opleverrapport vastgelegd. Dit document valt onder `code/Prototype/**`, het bestaande PR-padfilter voor CI; er wordt geen workflow gewijzigd of live validatie aangevraagd.
- Niet mergen. Na oplevering volgen ChatGPT-review en functionele acceptatie door Johan/CKC; PR #5 naar `main` blijft buiten deze iteratie.
