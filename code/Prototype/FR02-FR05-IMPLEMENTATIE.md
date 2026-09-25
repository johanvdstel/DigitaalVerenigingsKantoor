# FR-02 t/m FR-05 — tijdelijke planningswerkvoorraad

Status: technisch geïmplementeerd voor Issue #12; functionele acceptatie blijft bij Johan/CKC.

## Baseline en scope

- Repository: `johanvdstel/DigitaalVerenigingsKantoor`.
- Startbranch: `prototype-v0.5`.
- Startcommit: `125bfbc8790ee8d77d4a47994a33743982b51033`.
- Bestaande werkbranch: `codex/fr02-fr05-planning-workqueue`, vóór wijzigingen exact op die commit gecontroleerd.
- PR-doel: `prototype-v0.5`; niet mergen.
- Gelezen: root `AGENTS.md`, `docs/ontwikkelworkflow-codex.md`, `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md`, `TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md` en `BASELINE-v0.4.md`.

Alleen FR-02–05 zijn geïmplementeerd. Het actuele functionele contract en Issue #12 vervangen expliciet de historische interpretatie dat een lokale assignment Sportlink D/E wijzigt.

## Technische representatie en grenzen

`TemporaryPlanning` combineert de bevestigde `DutyAssignment` (status `temporary`, inclusief beslisser/tijd/provenance) met de concrete `DutyService`. Migratie 011 voegt uitsluitend `temporary_planning` toe. De tabel bevat de actieve werkpositie; undo verwijdert precies één rij. Er ontstaat geen AssignmentRevocation of nieuwe duurzame functionele audithistorie.

De bestaande voorstel-/beslissingopslag wordt hergebruikt. Zij levert geen bezetting: alleen actieve werkvoorraad telt. Hun bestaande opslag wordt in deze iteratie niet opgeschoond; de sync-lifecycle FR-06–08 blijft apart werk.

Nieuwe lokale planning wordt niet in de historische `duty_assignments`-tabel geschreven. Die tabel blijft beschikbaar voor bestaande Gate-9/10 no-showreferenties. Historische assignments worden niet automatisch tot actieve werkvoorraad gepromoveerd: hun concrete dienstcontext ontbreekt en wordt niet gegokt. No-showservices, no-show-UI en migratie 010 blijven functioneel ongewijzigd. FR-09–12 zijn niet geïmplementeerd.

De concrete lokale dienst wordt vergeleken op dienst-ID plus begin/einde. Dit is geen Sportlink scheduling-key. Het voorkomt dat de herhaalde demo-ID van een volgende week ten onrechte als dezelfde concrete dienst wordt geteld. De opgeslagen dienstcontext blijft ook buiten de zichtbare periode beschikbaar voor conflicten en menselijke undo-labels.

`StaffingNeed.confirmed_occupancy` blijft bronbezetting; `temporary_occupancy` is afzonderlijk en `planning_occupancy` is de som. Open minimum en vrije maximumcapaciteit worden telkens opnieuw afgeleid. Een reeds afgeleid of verouderd UI-resultaat veroorzaakt daardoor geen dubbeltelling.

De kandidaatbeoordeling behoudt bestaande kandidaat-/wedstrijdregels en voegt de actieve planning toe. Dezelfde dienst en echte overlap sluiten uit; boundary-touch is geen overlap. Dezelfde dag zonder overlap geeft `avoid` en een expliciet noodvoorstel (`suitability=emergency`). De bestaande rangorderegels worden niet herontworpen. Een inmiddels verouderd normaal voorstel voor dezelfde dag moet opnieuw als noodvoorstel beoordeeld worden voordat bevestiging mogelijk is.

`approve()` en `approve_many()` gebruiken dezelfde applicatiecontrole en vereisen persistence en staffingcontext. SQLite `BEGIN IMMEDIATE` serialiseert het lezen/controleren/schrijven van de werkvoorraad. Dubbele personen, overlap en overschrijding van maximum worden centraal geweigerd; een fout rolt de hele batch terug, ook wanneer de aanroeper de fout binnen de unit of work opvangt. SQL/repositories voeren alleen opslag en transacties uit, geen beleidsberekeningen.

`apply_assignment_to_case()` behoudt de persoon-/registratievalidatie en retourneert de ongewijzigde broncase. Het modelleert geen fictieve Sportlink-mutatie. Volledige dienstduur en negatieve bronuren blijven toegestaan; FR-02–05 voegen geen nieuwe afleiding of vermindering van persoonsuren toe.

## Gewijzigde bestanden en reden

Alle onderstaande paden zijn relatief aan `code/Prototype/`.

| Bestanden | Reden |
| --- | --- |
| `dvk/planning_workqueue.py` | Actieve positie, concrete dienstvergelijking, conflict- en staffingregels. |
| `dvk/application_services.py` | Actuele werkvoorraad bij lezen en bevestigen, centrale invarianten, atomische batch en undo. |
| `dvk/assignments.py`, `dvk/dashboard_actions.py`, `dvk/workstream_model.py` | Tijdelijke assignmentsemantiek, ongewijzigde Sportlink-case en planningscontext op kandidaatbeoordeling. |
| `dvk/candidate_selection.py`, `dvk/proposals.py` | Uitsluiting/dagconflict en expliciet noodvoorstel. |
| `dvk/staffing.py`, `dvk/planning.py` | Bronbezetting en tijdelijke bezetting apart, actuele minimum-/maximumpositie. |
| `dvk/persistence/migrations.py`, `dvk/persistence/planning_records.py`, `dvk/persistence/sqlite.py` | Additieve migratie 011, actieve opslag/verwijdering en transactievergrendeling. |
| `streamlit_app.py` | Publieke applicatieservices, afzonderlijke bezettingskolommen, herberekening na bevestigen en menselijke undo-selector. |
| `tests/test_planning_workqueue_v05.py` | 15 nieuwe regressies, inclusief parametrisatie, concurrency en echte Streamlit-runs. |
| `tests/test_assignments_v03.py`, `tests/test_dashboard_actions_v03.py`, `tests/test_integrated_v03.py`, `tests/test_integrated_v04.py`, `tests/test_gate8_v05.py` | Traceerbare vervanging van uitsluitend de vervallen lokale Sportlink-D/E-mutatie. |
| `tests/test_gate8b_persistence_v05.py` | Reconstructie van dezelfde provenance-/beslisketen via actieve werkvoorraad na heropenen. |
| `tests/test_gate10b_persistence_v05.py` | Schema 011 en expliciet lege nieuwe tabel; alle bestaande data blijven exact gecontroleerd. |
| `run_assignment_cases.py`, `run_dashboard_actions.py`, `run_integrated_acceptance.py`, `run_v04_demo.py` | CI-demonstraties maken ongewijzigde bronuren expliciet; R17-demoverificatie volgt het nieuwe contract. |
| `FR02-FR05-IMPLEMENTATIE.md` | Technische keuzes, regressietrace en resterende grenzen. |

## Bewust aangepaste historische regressies

- **W11** (`test_assignments_v03`): lokale planning van drie uur verandert bron-D/E niet meer van 1/7 naar 4/4. Assignmentduur en menselijke bevestiging blijven getest.
- **Step 9 dashboard** (`test_dashboard_actions_v03`) en **integrale v0.3-goedkeuring** (`test_integrated_v03`): dezelfde vervangen D/E-verwachting; afwijzing en eerdere keten blijven beschermd.
- **R17** (`test_integrated_v04`): lokale assignment van één uur verhoogt bron-D niet en verlaagt bron-E niet. De volledige adapter-/voorstel-/beslisketen en provenance blijven behouden.
- **Gate 8 V07 duurtests** (`test_gate8_v05`): volledige vier en vierenhalf uur blijven toegestaan, maar worden niet als nieuwe bronuren gepresenteerd. Bestaande negatieve-bronurenregressies zijn niet gewijzigd.
- **Gate 8b V07 persistence**: leest de nieuwe actieve positie in plaats van de legacy no-showassignmenttabel. Beslisser, tijdstip, engine-run, snapshots en versies blijven exact gecontroleerd.
- **Gate 10b migratietest**: technische schema-uitbreiding, geen functionele wijziging. Alle vooraf bestaande tabellen worden nog exact vergeleken; de nieuwe tabel moet leeg zijn.

Historische fixtures en geaccepteerde baselinebestanden zijn niet gewijzigd. De nieuwe v0.5-regressies bewijzen het vervangende lokale bezettings-/beschikbaarheidseffect, undo en bronimmutabiliteit.

## Verificatie

Python 3.12, tijdelijke virtualenv buiten de repository met de dependencies uit `pyproject.toml`.

- Baseline planning/candidate/assignment/staffing/Gate 8: **39 passed**.
- Volledige baseline: **258 passed**. De eerste koude run had 257 passed en één Streamlit-starttimeout (15 seconden). Ongewijzigde herhaling van die groep: 10 passed; volledige herhaling: 258 passed.
- Nieuwe FR-02–05-regressies: **15 passed** (onderdeel van de gerichte suite).
- Gerichte suite inclusief planning, staffing, assignments, Gate 8, integratieketens en migratie: **71 passed**.
- Volledige suite na implementatie: **273 passed**.
- `python -m compileall -q dvk streamlit_app.py`: geslaagd.
- `git diff --check`: geslaagd.
- Alle elf niet-live CI-demonstraties: exit 0 (`run_cases`, `run_workstream_cases`, `run_import_cases`, `run_candidate_cases`, `run_priority_cases`, `run_dashboard`, `run_proposal_cases`, `run_assignment_cases`, `run_dashboard_actions`, `run_integrated_acceptance`, `run_v04_demo`).
- Tijdens ontwikkeling: één volledige run met 271 passed / één mislukte schema-vergelijking doordat tabel 011 bijkwam; bovenstaande expliciete migratietest corrigeert die technische verwachting. Geen testtimeout verhoogd of test overgeslagen.
- GitHub CI wordt na push/PR afzonderlijk gerapporteerd; lokaal groen is geen functionele acceptatie.

## Resterende risico's en beslispunten

- Geen automatische opruiming bij import/sync: de precieze succesvolle sync-grens behoort tot FR-06–08 en is niet ingevuld. Gebruik deze werkvoorraad binnen de actieve cyclus.
- Legacy no-showfunctionaliteit gebruikt nog historische lokale assignments. De migratie naar feitelijke Sportlink-inroosteringen en hun stabiele identiteit blijft FR-09–12.
- Maximum en bronbezetting komen uit de bestaande canonieke staffinginput/configuratie. Deze iteratie herontwerpt geen bronimport of configuratiebeheer.
- De UI blijft de bestaande demo gebruiken. Geen Sportlink-writeback, portaal, taakplichtcontrole, nieuw beleidsbesluit of generiek framework.
- Bestaande Streamlit-deprecationwaarschuwingen over `use_container_width` zijn buiten scope.
