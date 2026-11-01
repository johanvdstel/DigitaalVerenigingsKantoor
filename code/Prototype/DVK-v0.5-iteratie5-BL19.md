# Iteratie 5 — BL-19: technische oplevering

Status: implementatie ter technische beoordeling en lokale functionele acceptatie.
Geen functionele acceptatie, merge of administratieve afsluiting.

## Context en herleiding

GitHub-baseline: `prototype-v0.5`,
`4f0d8ff064c26a3ddb19a3fd0b20a4a913af4f78` (geverifieerd vóór uitvoering).
Werkbranch: `codex/iteratie-5-bl19-no-showmanagement`, geïsoleerde worktree.
De bestaande gewijzigde checkout is ongemoeid gelaten.
`main` blijft de v0.4-releasebaseline; v0.5 is nog niet integraal geaccepteerd.
BL-11 en Iteratie 4/BL-14 zijn volgens de actuele backlog geaccepteerd.

Geaccepteerde eis voor deze uitvoering: de door CKC goedgekeurde BL-19-opdracht
van 1 november 2026. Sportlink blijft bronhouder van inroosteringen en uren;
Leden.csv bepaalt bekende personen; CKC beheert de dienstencatalogus; DVK
bewaart no-showfeiten, intrekkingen en sanctiebeoordelingen.

Tijdens uitvoering heeft Johan het expliciete beslispunt voor Andere dienst
beantwoord: de planner mag de oorspronkelijke taakcode invoeren, maar deze blijft
**onbevestigd** en geeft uitsluitend mogelijke-duplicaatsignalering. Een lege
code is eveneens toegestaan; de dienstomschrijving en verklaring zijn verplicht.

Vastgestelde verschillen met oudere documentatie:

- FR-09 en §6 van het planningssessieontwerp vereisen een actuele boeking in de
  actieve planning. BL-19 vervangt dit door zelfstandige bronraadpleging en de
  expliciet toegestane handmatige registratie van een verwijderde boeking.
- De omschrijving ‘laatste 14 kalenderdagen inclusief vandaag’ in de oudere
  planning/backlog is vervangen door het expliciete venster **vandaag − 14 t/m
  vandaag**, dus 15 kalenderdatums.
- De herregistratiebeperking uit de oorspronkelijke FR-10-tekst was al vervangen
  door geaccepteerde BL-11-herregistratie na intrekking; die werking blijft.
- FR-12 is geen aanvullende correctiewerkvoorraadopdracht: BL-11 is volgens de
  backlog afgesloten en de actuele opdracht vraagt behoud van bestaande werking.

Deze verschillen worden hier gerapporteerd. Root README, backlog,
prototypeplanning, productieroadmap en bestaande functionele contracten zijn
niet gewijzigd. Geen migratie, historische reconstructie of productievoorziening.

## Implementatie en proportionaliteit

| Bestand onder `code/Prototype` | Concrete wijziging / acceptatiegrond |
| --- | --- |
| `dvk/no_show.py` | Handmatige dienstsnapshot en bevestigde verklaring; gezamenlijk duplicaatbegrip; lokaal 15-datumsvenster en werkelijk aanvangsmoment. BL-19 §§4.3–4.8. Bestaande sanctieregels blijven intact. |
| `dvk/application_services.py` | Beide nieuwe registratieroutes delen tijdcontrole, duplicaatcontrole en opslag. Exact actief duplicaat blokkeert; mogelijke duplicaten vereisen bevestiging van de daadwerkelijk getoonde event-ID's. Historie/filtering en bestaande intrekking via publieke services. |
| `dvk/no_show_source.py` | Zelfstandige read-only client/adapterraadpleging zonder planningsrepository. Bij echte bevestiging één heropvraag van de geselecteerde taak; vergelijking van identiteit, context en oorspronkelijke broninhoud. Geen API-verkeer bij gewone UI-reruns. |
| `dvk/vrijwilligers_adapter.py` | Expliciet strikt tijdpad voor zelfstandige no-showraadpleging: ontbrekende, dubbelzinnige en niet-bestaande lokale tijden worden geweigerd. Expliciete UTC-offsets blijven werkelijke instants. Bestaande adapterpaden blijven behouden. |
| `dvk/persistence/no_show_records.py` | Bestaande schema-13-JSON-payload leest de optionele handmatige snapshot; geen nieuwe tabel, migratie of herschrijving. |
| `streamlit_app.py` | Zelfstandige portaalfunctie, Sportlink/Handmatig, catalogus/Andere dienst, persoonskeuze, duplicaatwaarschuwing, seizoenshistorie en intrekking. Oude bediening uit Planning verwijderd. Bestaande bevoegdheden, resultaatmeldingen en databasefoutafhandeling hergebruikt. |
| `tests/test_bl19_no_show_management_v05.py` | Nieuwe synthetische contract-, grens-, concurrency-, bron-, persistentie- en operationele UI-tests. |
| Bestaande tests en testhelpers | Gerichte aanpassing van navigatie en presentatie die BL-19 expliciet vervangt; expliciete historische testklok voor bestaande BL-11-cases. Zie hieronder. |

De bestaande `BEGIN IMMEDIATE`-schrijfgrens serialiseert controle en toevoeging;
zonder die grens zouden twee sessies dezelfde actieve gebeurtenis kunnen
vastleggen. Die bestaande transactie is voldoende: geen extra index/tabel nodig.
Intrekking gebruikt dezelfde schrijfgrens en heeft geen registratievenster.

De ongewijzigde sanctiedomeinlogica bepaalt historische beoordeling en actuele
seizoensteller. Geen rechtstreekse uren-, Sportlink-, planning- of sessiemutaties.
Handmatige context wordt nooit opgeslagen als VolunteerBooking of planningdienst.
Persoonsnummer, historische naam, concrete tijden, omschrijving, locatie,
toelichting, taakidentiteitsstatus, verklaring, actor en registratiemoment blijven
zelfstandig leesbaar. Ontbrekende `manual`-velden in oude payloads behouden de
bestaande Sportlink-interpretatie. De oorspronkelijke seizoensinterpretatie van
oude UTC-payloads wordt niet achteraf veranderd; nieuwe events gebruiken de lokale
begindatum en een in Amsterdam uitgedrukt occurrence-tijdstip.

## Gericht aangepaste regressies

Historische C/W/I/R-cases en fixturebestanden zijn niet gewijzigd.
De vaste BL-11-registratiedatums liggen bij latere CI-runs buiten het nieuwe
venster. `historical_registration_context` maakt hun oorspronkelijke
registratiemoment daarom expliciet als testklok. Historisch verschillende taken
op dezelfde dag worden in die fixture expliciet bevestigd als mogelijke
duplicaten. De nieuwe BL-19-tests gebruiken deze fixture niet en bewijzen juist
de afwijzing zonder bevestiging en de hercontrole bij datumwisseling.

Bestaande UI-tests openen voortaan No-showmanagement. Hun oorspronkelijke
synthetische boekingen worden als onafhankelijke testbron aangeboden; de echte
nieuwe client/adapterketen wordt afzonderlijk door BL-19-tests getest. De eerdere
UI-verwachting dat alleen een gewijzigde *planningsrevisie* registratie blokkeert
is gericht vervangen: een ongewijzigde externe boeking blijft zelfstandig geldig.
Gewijzigde/verdwenen externe boekingen worden afzonderlijk afgewezen.

De overige verwachtingwijzigingen zijn de negende portaalfunctie, afwezigheid van
no-showbediening in de vijf planningsecties, twee extra begrensde overzichtstabellen
en bron-/diensttijdcontrole in de applicatieservice. Bestaande registratie,
intrekking, herregistratie, historie en sanctie-uitkomsten blijven getoetst.

### Exact gewijzigde testbestanden

- `tests/conftest.py`: expliciete historische registratieklok en bevestiging van
  de bestaande verschillende taken; geen toepassing op de nieuwe BL-19-tests.
- `tests/sportlink_fixtures.py`: onafhankelijke synthetische bron voor de
  bestaande verplaatste UI-proeven; geen wijzigingen aan oorspronkelijke boekingen.
- `tests/test_bl14_catalog_v05.py`, `tests/test_gate9_application_v05.py`,
  `tests/test_gate9_hardening_v05.py`, `tests/test_no_show_choices_v05.py`,
  `tests/test_no_show_sportlink_v05.py`, `tests/test_planning_runtime_v05.py`,
  `tests/test_schema_validation_v05.py`,
  `tests/test_volunteer_planning_integration_v05.py`: uitsluitend gebruik van de
  expliciete historische registratiecontext; oorspronkelijke assertions behouden.
- `tests/test_gate10c_application_v05.py`: dezelfde klokfixture; registratietijd
  van de historische eventbuilder expliciet timezone-aware, zoals de bronstart.
- `tests/test_gate10ade_ui_v05.py`, `tests/test_no_show_reregistration_v05.py`,
  `tests/test_no_show_result_message_v05.py`, `tests/test_planning_ui_names_v05.py`,
  `tests/test_volunteer_identity_v05.py`: bestaande registratie-/intrekkings- en
  resultaatproeven naar de zelfstandige UI verplaatst; oorspronkelijke
  historie-/sanctie-/naam-/bevoegdheidsassertions behouden.
- `tests/test_planning_session_source_v05.py`: historische klok en gerichte
  vervanging van de eerder beschreven planningsrevisie-UI-verwachting.
- `tests/test_dashboard_database_isolation_v05.py`: no-showdatabasefout op het
  zelfstandige scherm toetsen; taakplichtcontrole blijft bereikbaar.
- `tests/test_duty_population_dashboard_v05.py`, `tests/test_navigation_v05.py`,
  `tests/test_planning_sections_bl18.py`, `tests/test_gate10d_no_show_ui_v05.py`:
  expliciet gewijzigde scherm-/presentatiecontracten en de service-tijdroute.

## Verificatie

- BL-19-contracttests: **48 geslaagd**.
- BL-19 plus bestaande presentatie-/intrekkingsselectie: **59 geslaagd**.
- Volledige definitieve regressie vanuit `code/Prototype`: **1355 geslaagd**,
  0 fouten, 0 overgeslagen, 88,93 seconden (Python 3.11.16 / Streamlit 1.66.1).
- Alle elf bestaande synthetische acceptatiescripts: geslaagd (exitcode 0).
- Python-syntax/compilecontrole en `git diff --check`: geslaagd.
- GitHub-PR/CI en exacte oplevercommit: zie commit-specifieke terugrapportage.

De eerste volledige ontwikkelrun had 59 fouten en 18 fixturefouten (1272 tests
geslaagd): vaste historische datums, oude planningsnavigatie en de nieuwe
testverwachtingen waren nog niet aangepast. Een latere gerichte selectie had
136 geslaagde tests en één AppTest-keuzeroundtripfout bij identieke labels; de
fixture opent dat historische intrekkingsscherm nu zonder extra bronrerun.
Daarna slaagden 1353 regressietests. Twee aanvullende seizoens-/datumwisseltests
zijn vervolgens toegevoegd; definitieve aantallen staan in de oplevering.
Een aanvullende, verkeerd vanuit de repositoryroot gestarte run verzamelde ook
`code/Prototype/test_prototype_cases.py`, buiten `testpaths = ["tests"]`.
Die oude tests verwachten een dictionary van de engine waar de huidige engine
een tuple levert: 11 fouten naast 1355 geslaagde tests. Een geïsoleerde exportrun
van exact dezelfde 11 tests tegen de ongewijzigde baselinecommit geeft eveneens
11 fouten. Dit bestaande verschil valt buiten BL-19; het bestand, de engine,
pytestconfiguratie en geaccepteerde C-cases zijn niet aangepast. De voorgeschreven
regressiesuite en alle elf acceptatierunners zijn wel groen.

Geen mislukte live bronproef: alle bronnen en personen in tests zijn synthetisch.

## Lokale functionele acceptatie

1. Gebruik de volledige codecommit uit de oplevering in deze afzonderlijke
   worktree. Controleer `git rev-parse HEAD`. Start de bestaande Streamlit-app
   vanuit `code/Prototype` met de lokale Pythonomgeving. Deel geen echte exports,
   database of API-antwoorden. Gebruik een afzonderlijke proefdatabase/checkout
   voor fictieve registraties; maak geen fictieve no-shows in de operationele DB.
2. Open **No-showmanagement** zonder planning te starten/hervatten. Controleer
   het seizoensoverzicht. Personen komen alleen uit lokale Leden.csv; voormalige
   leden en naamgenoten blijven selecteerbaar, ongeacht taakplicht.
3. Kies Handmatig. Selecteer een catalogusdienst en afwijkende werkelijke tijden;
   bevestig de verklaring. Controleer de historische omschrijving, tijden,
   registratievorm, actor en het registratiemoment. Er ontstaat geen planningboeking.
4. Kies Andere dienst met omschrijving en eventueel oorspronkelijke taakcode.
   Controleer de onbevestigde taakidentiteit. Bij mogelijke dubbelen toont DVK de
   bestaande gebeurtenissen en is expliciet doorgaan vereist.
5. Raadpleeg Sportlink afzonderlijk. Controleer een betrouwbaar gekoppelde dienst
   die al begonnen is. Bevestiging herleest de gekozen taak; een gewijzigde of
   verdwenen boeking wordt geweigerd. Gebruik synthetische tests wanneer zulke
   situaties niet zonder echte bronmutaties kunnen worden aangetoond.
6. Controleer vandaag−14 en vandaag; vandaag−15, morgen en later vandaag worden
   geweigerd. Controleer een nachtdienst en de datum-/tijdgrenzen met synthetische
   voorbeelden. Lokale ambigue/niet-bestaande DST-tijden worden niet ingevuld.
7. Controleer exact duplicaat, mogelijk duplicaat, intrekking met reden buiten
   het venster, herregistratie binnen het venster en historie na herstart.
8. Laat een bestaande planning met tijdelijke indeling open; raadpleeg en gebruik
   no-showbeheer en keer terug. Periode, bron, tijdelijke indelingen en A/B/C/D/E
   moeten gelijk blijven. API-uitval laat handmatige registratie beschikbaar.
9. Leg bevindingen en exacte SHA voor aan ChatGPT-regie. Functioneel akkoord en
   afzonderlijke merge-toestemming blijven vereist. Codex merge't niet.

## Resterende grenzen

Geen live Sportlink-proef of functionele CKC-acceptatie uitgevoerd. De bestaande
lokale prototype-identiteit blijft gelden; productie-authenticatie valt buiten
scope. Onbevestigde historische taakcodes leveren bewust geen exactheidsbewijs.
Een consultatiesnapshot leeft alleen in de UI-sessie; duurzame historie staat in
SQLite. Bronwijzigingen leiden conservatief tot opnieuw raadplegen; oude feiten
worden nooit met teruggekeerde bronboekingen samengevoegd of gereconstrueerd.
