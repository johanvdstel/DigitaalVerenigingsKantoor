# Iteratie 4 — BL-14: implementatie en lokale acceptatie

Status: technisch geïmplementeerd ter lokale CKC-acceptatie; **niet functioneel
geaccepteerd, niet gemerged**. Opdracht: CKC-goedgekeurde implementatieopdracht
Iteratie 4, BL-14 inclusief voormalig BL-15.

## Baseline en scope

Integratiebaseline `prototype-v0.5` op
`9394785a1751e52c53743aa3a118baa5b90dde51`, read-only op GitHub geverifieerd.
Werkbranch `codex/iteratie-4-bl14`, aparte worktree; de twee vooraf bestaande
wijzigingen op `codex/vrijwilligers-planning-integratie` zijn ongemoeid gelaten.
Iteraties 1–3 zijn functioneel geaccepteerd. Integrale v0.5-acceptatie blijft open.
CKC beheert configuratie; Sportlink blijft bronhouder van inroosteringen; DVK
leidt diensten/bezetting af en bewaart tijdelijke planning en duurzame no-shows
onderscheiden. Geen writeback, gegevensmigratie of productiearchitectuur.

## Wijzigingen en herleiding

| Bestand(en) onder `code/Prototype`, tenzij anders aangegeven | Reden / acceptatiecriteria |
| --- | --- |
| `dvk/shift_catalog.py` | Lokale CSV zonder terugval; validatie, datumbereik, nachtgrenzen, deterministische identiteit, gebruikte codes. AC-01–07, AC-10/12. |
| `dvk/configuration/shift_week_pattern.csv` | Alleen twee datumkolommen toevoegen aan het bestaande uitgangsvoorbeeld; alle 29 diensten behouden. AC-03. |
| `dvk/vrijwilligers_adapter.py` | Expliciet planningpad voor bekende werkelijke tijdvakken; bestaande exacte/overlaproutes behouden. AC-08–14, AC-21. |
| `dvk/volunteer_planning.py` | Unie van catalogus- en bronmomenten, namen en bezetting via publieke service; gekoppelde persoon eenmaal per dienst. Sessiecontrole tegen verouderde service-instantie. AC-08–16/20. |
| `dvk/application_services.py` | Planningcontract doorgeven; catalogus bij eerste bronpublicatie met bestaande transactie bewaren. Geen verandering booking-identiteit of bronvalidatiegrens. AC-20/21. |
| `dvk/planning_session.py`, `dvk/persistence/planning_session.py` | Bevestigde reload via bestaande BL-16-herstart. Catalogusinhoud bij actieve sessie bewaren, ook bij herstart; geen vingerafdruk, inhoudsvergelijking of versieadministratie. AC-17–21. |
| `dvk/workstream_model.py` | Concrete duur als werkelijk verstreken tijd voor timezone-aware tijdstippen; bestaande naive gevallen blijven gelijk. AC-06/12, zomer-/wintertijd. |
| `streamlit_app.py` | Reload-bediening, foutmeldingen, sessiecatalogus en publieke namenservice; bestaande kandidaten-/voorstellen-/undo-keten gebruiken voor alle diensten. AC-02/08–21. |
| `tests/test_bl14_catalog_v05.py` | Nieuwe synthetische contract-, keten-, grens- en UI-tests. |
| `tests/conftest.py`, `tests/serve_synthetic_planning.py` | Bestaande synthetische proefomgeving expliciet voorzien van catalogusvoorbeelden; nooit echte lokale bestanden lezen. |
| `tests/test_volunteer_planning_integration_v05.py`, `tests/test_volunteer_identity_v05.py` | Alleen expliciet door BL-14 vervangen verwachtingen aanpassen; oorspronkelijke projectiecontroles behouden. Zie hieronder. |
| Root `README.md`, `BACKLOG.md`, `DVK-PROTOTYPE-PLANNING.md`, `DVK-BRONCONTRACTEN-v0.5.md`, prototype `README.md`, dit verslag | CSV-contract, bediening, broninterpretatie en acceptatiebasis vastleggen; geen functionele acceptatie claimen. |

Dienstidentiteit bestaat uit exacte taakcode plus UTC-begin/einde. Locatie blijft
broncontext; anders zouden gelijke momenten uit catalogus en API door
locatieverschillen dubbel verschijnen. Verschillende barcodes blijven aparte
dienstcontexten, terwijl de bestaande bargroepering voor bezettingsprojectie
geldt. Namen kunnen oorspronkelijke bronregistraties blijven tonen; gekoppelde
personen tellen voor bezetting eenmaal. Afgeschermde/niet-gekoppelde bookings
blijven op hun bestaande booking-identiteit onderscheiden.

De actieve sessie bewaart één catalogusinhoud in het bestaande JSON-sessierecord.
Dit is nodig om gewone reruns en procesherstart niet tot impliciete reload te
maken. Er is geen schemawijziging, migratie, historisch catalogusarchief,
wijzigingsdetectie of catalogusversiebeheer. Een bestaande gevalideerde sessie
zonder catalogusinhoud vraagt in de UI voor actuele planningsbezetting om expliciete
reload. Bestaande no-showbediening blijft op de bewaarde broncontext beschikbaar. Zij wordt
niet automatisch gewist of historisch gereconstrueerd.

## Expliciet vervangen verwachtingen

De oude planningintegratietests eisten dat een geldig interval zonder overlap
publicatie blokkeerde, en dat lange broninroosteringen uitsluitend bestaande
catalogusslots opleverden. De opdracht §§6.1–6.3 en AC-08/09 vervangen dit voor
Ledendienst Planning: feitelijke afwijkende intervallen verschijnen aanvullend.
De bestaande catalogusprojectie wordt nog steeds afzonderlijk met dezelfde
verwachte bezetting gecontroleerd; aanvullende momenten krijgen eigen assertions.
De oorspronkelijke exacte/overlapadaptertests blijven ongewijzigd.

De 16 broncode/cataloguscodecombinaties gebruiken nu voor elke bedoelde uitvraag
expliciet een roosterregel (waar nodig een buiten de periode liggende incidentele
regel). Dit volgt uit AC-07: alleen een definitie is geen actieve uitvraagcode.
Een andere taakgroep bezet het oorspronkelijke catalogusslot niet, maar mag wel
een eigen aanvullend dienstmoment opleveren. De ongewijzigde 29-diensten-,
C/W/I/R-, minimum/maximum-, booking- en no-showcontracten blijven regressiebasis.

## Technische verificatie

Gerichte definitieve ketenselectie: **152 geslaagd**, geen fouten. Deze selectie
omvat `test_bl14_catalog_v05.py`, `test_volunteer_planning_integration_v05.py`,
`test_volunteer_identity_v05.py`, `test_planning_session_source_v05.py` en de
ongewijzigde `test_gate10ade_ui_v05.py`. De browserharnessselectie met BL-14 was
ook groen (38 tests vóór de laatste periodegrensgevallen).

De 11 bestaande synthetische acceptatiescripts zijn allemaal geslaagd:
`run_cases.py`, `run_workstream_cases.py`, `run_import_cases.py`,
`run_candidate_cases.py`, `run_priority_cases.py`, `run_dashboard.py`,
`run_proposal_cases.py`, `run_assignment_cases.py`, `run_dashboard_actions.py`,
`run_integrated_acceptance.py`, `run_v04_demo.py`. Geen live scripts uitgevoerd.
`git diff --check` is geslaagd.

| Acceptatiegroep | Technisch bewijs |
| --- | --- |
| AC-01–07 | Lokale bestanden, geen fallback, 29-dienstenbasis, gedateerde/onbezette regels, daadwerkelijke duur, nacht/DST, periode-onafhankelijke gebruikte codes. |
| AC-08–14 | Buitenrooster-/overlap-/exacte intervallen, unieke diensten, eigen normen, groepsprojectie en persoonsdeduplicatie; bestaande exacte/overlapadaptertests behouden. |
| AC-15–16 | Publieke kandidaat-/prioriteits-/voorstelketen, bevestiging en undo voor incidentele en aanvullende diensten; ook operationele Streamlit-UI-test. |
| AC-17–21 | Reload-waarschuwing, annuleren, identieke herlaadactie, ongeldige bestanden, rollback, stale sessie, proceshervatting, nieuwe bronvalidatie en no-showreferenties/intrekkingen. |
| AC-22 | 1304 volledige regressietests, 11 acceptatiescripts, syntaxcontrole en diffcontrole geslaagd; PR-CI op exacte oplevercommit in terugrapportage. |

Definitieve volledige regressie op de oplevercode: **1304 geslaagd**, 0 fouten,
0 overgeslagen (82,20 seconden; Python 3.11.16 / Streamlit 1.64.0).
De 11 acceptatiescripts en syntaxcontrole zijn ook op deze code opnieuw geslaagd.
De eerste losse syntaxcheck via de systeem-Python liep tegen sandbox-cacherechten
aan; de definitieve controle met de projectomgeving slaagde.
CI-status en exacte oplever-SHA/PR worden in de terugrapportage vermeld.
Eerste volledige run: 1290 geslaagd. Na herstel van de no-showmelding: 1302
geslaagd. Aanvullende UTC-daggrens- en expliciete wintertijd-instantcases zijn daarna toegevoegd; concrete
planningdiensten worden expliciet in Europe/Amsterdam getoond, zodat datumselectie
en vrijdag-/zaterdagbezettingsnormen dezelfde lokale begindatum gebruiken.
Expliciete broninstants worden op hun werkelijke UTC-volgorde gevalideerd; er
wordt geen lokale fold geraden en de historische adapterpaden blijven intact. Daarna aanvullende tests toegevoegd voor
reload/UI, voorstel-bevestiging-undo, sessieherstart en no-showreferenties.
Een tussenrun van 161 gerichte tests had 25 fouten: dit waren de hierboven
benoemde oude verwachtingen voor aanvullende tijdvakken en ongebruikte
uitvraagcodes. Een eerste sandboxrun is afgebroken na 24 van dezelfde contractfouten
en 38 geslaagde tests. Een latere volledige run vond zes no-show-UI-regressies
door een te brede legacy-sessiemelding (1294 geslaagd); die blokkade is in de
implementatie hersteld, zonder de historische no-showtests te wijzigen. Deze verschillen zijn functioneel herleid, geen versoepeling van
bronintegriteit of geaccepteerde historische fixtures.

## Lokale acceptatie op de exacte oplevercommit

1. Gebruik een afzonderlijke lokale checkout van de volledige oplever-SHA uit de
   terugrapportage; controleer `git rev-parse HEAD`. Start vanuit `code/Prototype`
   met de bestaande Python/Streamlit-omgeving. Gebruik een eigen lokale database.
2. Plaats beide CSV-bestanden volgens het [formaatcontract](README.md#bl-14--lokale-dienstencatalogus)
   in `~/Documents/DVK-Sportlink-exports/`. Onderhoud echte bestanden uitsluitend
   lokaal. De meegeleverde configuratie kan buiten Git als uitgangspunt dienen;
   DVK maakt geen bestanden aan en gebruikt geen stille terugval.
3. Controleer de oorspronkelijke week: 29 catalogusdiensten, bestaande tijden,
   vrijdagbezetting en onafhankelijke bar-/commissiekamerdiensten.
4. Voeg in wegwerp/synthetische configuratie een eenmalige onbezet gebleven dienst
   en een vrijdag 23:00–02:00 toe. Kies Reload catalog, controleer waarschuwing,
   annuleer en controleer behoud. Bevestig daarna: nieuwe sessie, oude tijdelijke
   planning weg, Sportlink-bezetting onbekend. Controleer datumgrenzen en vrijdagnorm.
5. Haal Sportlink handmatig opnieuw op. Vergelijk lokaal een afwijkend tijdvak,
   een overlappend tijdvak en een exacte overeenkomst. Verwacht respectievelijk
   een extra dienst, een extra dienst en één dienst. Meerdere vrijwilligers
   veroorzaken geen extra dienstkopieën. Wijzig geen echte Sportlink-registraties
   voor een proef; gebruik synthetische tests als bronvoorbeelden ontbreken.
6. Selecteer een aanvullende dienst, genereer kandidaten/voorstellen, bevestig
   tijdelijk en controleer bezetting en undo. De planner beslist; geen writeback.
7. Bewerk configuratie zonder reload en herstart Streamlit: de bestaande sessie
   houdt haar geladen catalogus. Bevestig Reload catalog met ongewijzigde bestanden:
   ook dan ontstaat een nieuwe sessie. Controleer onbekende bron tot nieuwe fetch.
8. Controleer met wegwerp/synthetische invoer ontbrekende bestanden, eenzijdige
   datums, ongeldige perioden, duplicaten en ambigue/niet-bestaande lokale tijden.
   Bestaande sessie en werk blijven bij ongeldige reload behouden. Een mislukte
   API-verversing publiceert niets gedeeltelijk.
9. Controleer behoud van bestaande no-shows, intrekkingen en historie na reload en
   herstart. Geen fictieve no-shows op echte CKC-inroosteringen aanmaken.

Rapporteer geslaagd/mislukt, exacte SHA en geanonimiseerde aantallen. Geen namen,
exports, lokale database, credentials of ruwe API-responsen naar GitHub/Codex.

## Grenzen en resterende risico's

Geen lokale CKC-functionele acceptatie of live API-proef door Codex uitgevoerd.
De API heeft geen unieke dienstidentifier: langere broninroosteringen kunnen
extra dienstmomenten veroorzaken; dit is bewust door CKC geaccepteerd.
Begindatum blijft bepalend voor selectie en overlapprojectie. Alleen concrete
lokale tijdgrenzen voor de gekozen periode worden op DST-eenduidigheid getoetst.
Rooster Generator wordt niet gewijzigd of uniform gemaakt met Ledendienst
Planning. BL-19 en overige backlogfunctionaliteit blijven buiten scope.

## UI-correctie periodekeuze — vervolg op lokale acceptatie

Uitgangscommit `6dd02a79de37f94f481c08c6b00416586a0d39da`, dezelfde werkbranch
`codex/iteratie-4-bl14` en draft-PR #58. CKC heeft de precisering bevestigd:
Dag/Week/Aangepast blijven bestaan. Alleen bij Week heet het datumveld nu
**Week waarin datum valt**. Dag en Aangepast behouden **Vanaf**; Aangepast
behoudt **Tot en met**. Direct bij de keuze staat **Roosterperiode: dd-mm-jjjj
t/m dd-mm-jjjj**, rechtstreeks uit het reeds berekende `PlanningPeriod`.
Er is geen veld Aantal weken toegevoegd en geen periode-, bron-, kandidaat-,
sessie- of reloadlogica gewijzigd.

Gewijzigd: `streamlit_app.py` (uitsluitend label en weergave),
`tests/test_planning_period_labels_v05.py` (drie synthetische UI-cases, inclusief
controle dat de getoonde periode overeenkomt met de opgeslagen sessie vóór een
Sportlink-uitvraag) en dit verslag. De nieuwe test dekt Dag 31-10-2026, Week
26-10-2026 t/m 01-11-2026 en een aangepaste periode 31-10-2026 t/m 15-11-2026.

**Lokale CKC-acceptatiebevinding, door CKC gerapporteerd:** de lokaal onderhouden
weekcatalogus is van 29 naar **23 diensten per week** aangepast. DVK toont na
bevestigde Reload catalog correct 23 diensten. Het lokale configuratiebestand
is niet door Codex gelezen of overgenomen. Meegeleverde configuratie en
synthetische 29-diensten-regressies blijven ongewijzigd. Deze bevinding markeert
BL-14 niet als definitief functioneel geaccepteerd.

Korte heracceptatie op de nieuwe volledige oplever-SHA uit de terugrapportage:
kies Week met datum 31-10-2026; verwacht het nieuwe label en direct
**Roosterperiode: 26-10-2026 t/m 01-11-2026**. Kies Dag: label Vanaf en beide
periodegrenzen 31-10-2026. Kies Aangepast met einde 15-11-2026: bestaande labels
en exact 31-10-2026 t/m 15-11-2026. Controleer dit vóór bronophaling; bestaande
sessiegrenzen en bevestigingsvragen blijven van kracht. Niet mergen zonder
afzonderlijke toestemming; definitieve functionele acceptatie blijft open.

Technische verificatie van deze UI-correctie: **55 gerichte tests geslaagd**
(nieuwe periode-UI-tests, bestaande sessie/runtime-tests en BL-14-ketentests);
**1307 tests in de volledige regressiesuite geslaagd**, 0 fouten, 0 overgeslagen
(82,08 seconden). `git diff --check` geslaagd. De eerste gerichte aanroep vanuit
de repositoryroot vond de relatieve testpaden niet; vanuit `code/Prototype`
slaagde de selectie zonder aanpassing van verwachtingen. De nieuwe commit en
CI-status staan in de terugrapportage en dezelfde draft-PR #58.
