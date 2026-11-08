# Stabilisatie read-only taakplichtcontrole

## Context en scope

Startcommit, expliciet bevestigd door Johan: `9a0c0633ee93c1bd1f44bae8a575ffbc9fce279a` op bestaande werkbranch `codex/v05-stap2-ronde4-taakplichtdashboard`. Integratiebaseline: `prototype-v0.5`, GitHub-commit `35396c354d6efed2ac6db86ee61c5604834a4334`, voorouder van het startpunt. Beide remote commits read-only gecontroleerd met `git ls-remote`. De lokale branch `prototype-v0.5` is verouderd en is niet als startpunt gebruikt.

Ontwikkelfase: v0.5-integratie; geen integrale functionele acceptatie. Geaccepteerde referenties: BASELINE-v0.4, herijkte B-01–B-14-baseline, ontwikkelworkflow en ronde-4-dashboardrapport. Sportlink houdt de bronfeiten, CKC bepaalt beleid en Johan bepaalt functionele acceptatie. C/W/I/R-regressiecases blijven ongewijzigd. Deze opdracht accepteert uitsluitend technische bereikbaarheid en databaseveiligheid; taakplichtregels, B-02 op dezelfde Teams-record, relatiecode, drie uitkomsten en filters blijven gelijk.

Proportionaliteit: een aangetoonde opstartafhankelijkheid verhindert de nieuwe controle bij de gemelde SQLite-fout. Eén foutgrens om de bestaande planningweergave is daarvoor voldoende. Geen nieuwe pagina, navigatie, schemawijziging, opslaglaag of algemene databasevalidatie. Alleen synthetische ontwikkeltestdata; geen echte database of CKC-exports geopend, gewijzigd of opgenomen. Er is geen vastgestelde opdracht om historische gegevens te reconstrueren.

## Feiten, hypothese en onzekerheid

**Vastgesteld in code:** `streamlit_app.py` initialiseert de database en bouwt eerst het planningsoverzicht. Dit gebruikt `sportlink_bookings`; daarna volgen tijdelijke planning, kandidaten, no-showcontexten en intrekkingen. Pas daarna staat de CSV-taakplichtcontrole. Een eerdere exception beëindigde de hele uitvoering. Ook ontbrekende no-showtabellen, een onleesbare database of een initialisatiefout kunnen daardoor de controle blokkeren.

**Vastgesteld in code:** `dvk/persistence/migrations.py:migrate` gebruikt uitsluitend `MAX(version)` en voert alleen hogere migraties uit. Zowel `SQLiteDatabase.initialize` als het openen van een unit of work gebruiken deze procedure. Versie 12 zonder de huidige tabel wordt dus niet hersteld en geeft bij het uitlezen een SQLite-fout.

**Vastgesteld in Git-historie:** commit `7da00d618f28747edc19c44e57a4c1fb5736c3e9` definieert migratie 12 als aanmaak van `planning_state`. Commit `cba876a440ffc2600007e0a08eab5f8a5e0505c6` introduceert vanaf een reeks met elf migraties een andere migratie 12: `sportlink_bookings`, drie bijbehorende no-show/sanctietabellen en vier immutable triggers. Hetzelfde versienummer heeft dus in verschillende historische code twee betekenissen. Dit bewijst geen in-place wijziging binnen één gebruikte lokale ontwikkelketen.

**Hypothese:** een database die eerder onder de eerste definitie versie 12 kreeg, wordt onder de huidige code overgeslagen en mist de huidige tabellen. Een synthetische database met de oude versiesignatuur reproduceert dit. Ook verwijderen van een tabel of elders gemaakte versieadministratie kan dezelfde toestand geven.

**Niet bewezen:** welke code de lokale gebruikersdatabase heeft aangemaakt, of `planning_state` daarin aanwezig is en of gegevens uit ontbrekende tabellen ooit bestonden. De door de opdrachtgever gemelde lokale toestand is niet zelfstandig onderzocht. Daarom geen automatische herstelactie of stellige historische oorzaakaanduiding.

## Correctie en gewijzigde bestanden

- `streamlit_app.py`: bestaande planningweergave ingesprongen in `_render_planning`, zonder wijzigingen aan planning-/no-showhandelingen. Alleen bekende SQLite-schemafouten (ontbrekende tabel/kolom) en opslagfoutcodes worden met een menselijke melding afgehandeld; daarna loopt de oorspronkelijke CSV-controle door. SQL-syntaxfouten, andere onbekende databasefouten en programmeerexceptions worden opnieuw doorgegeven. De controlecode blijft ongewijzigd. De omvang van de diff komt hoofdzakelijk door inspringing; `git diff -w` toont de beperkte inhoudelijke wijziging.
- `tests/test_dashboard_database_isolation_v05.py`: acht synthetische tests voor ontbrekende tabel bij versie 12, oudere versiesignatuur, geldige database, alle vijf uploads zonder SQLite/Sportlink-toegang, twee programmeerfouten, latere no-showfout en database-openfout.
- Dit rapport: analyse, bewijsgrenzen, tests en afzonderlijke herstelprocedure.

De foutmelding toont geen SQL, gegevens of traceback. Een ontbrekende tabel/kolom kan ook door een verkeerde SQL-verwijzing worden veroorzaakt; de UI kan die oorzaak niet onderscheiden. Daarvoor blijft code-/schemaonderzoek nodig. De foutgrens maakt geen gegevenscorrectie en claimt geen herstel.

## Daadwerkelijk uitgevoerde verificatie

Alle geslaagde testaanroepen zijn vanuit `code/Prototype` met de bestaande `.venv/bin/python` uitgevoerd; pytest 9.1.1. Er zijn geen afhankelijkheden geïnstalleerd.

- Uitgangssituatie: dashboard, planning, planningwerkvoorraad, Sportlink-no-shows en bestaande no-show-UI-tests: **84 passed in 2.32s**.
- Eerste nieuwe gerichte controle plus dashboard: **43 passed in 1.63s** (zes nieuwe tests).
- Definitieve gerichte suite, inclusief twee extra foutgrensgevallen en bestaande planning/no-showtests: **92 passed in 2.66s**.
- Volledige regressiesuite: **551 passed in 4.46s**.
- `git diff --check`: schoon.

AppTest bewijst daadwerkelijke dashboardweergave bij de databasefouten en daadwerkelijke tabelweergave na vijf synthetische CSV-uploads. In de uploadtest zijn SQLite-connecties en de Sportlink-fetch expliciet verboden. Bij een bestaande versie-12-database en een geldige database blijft de inhoud byte-identiek. De volledige suite bevat ook de bestaande planning-, no-show-, intrekkings- en geaccepteerde regressies.

Niet geslaagde voorbereidende aanroepen: systeem-Python had geen pytest; een aanroep gebruikte ten onrechte `.venv` vanaf de repositoryroot; een volgende aanroep vanaf die root strandde bij testcollectie op `ModuleNotFoundError: dvk`. Na gebruik van de juiste projectdirectory zijn bovenstaande suites werkelijk uitgevoerd. Geen testverwachtingen versoepeld.

Geen nieuwe CI-run: niet gepusht, geen PR geopend, geen merge uitgevoerd. Lokale tests zijn geen CI-bewijs of functionele acceptatie.

## Afzonderlijk herstelvoorstel — niet uitgevoerd

De bereikbaarheidscorrectie vereist geen herstel. Onderstaande procedure is een aanbeveling voor een afzonderlijke opdracht en vereist expliciete goedkeuring vóór wijzigingen aan de gebruikersdatabase.

1. Stop de app en andere schrijvers. Maak een consistente SQLite-back-up met de SQLite-backup-API en bewaar het origineel, inclusief eventuele journal/WAL-bestanden. Kopieer geen actieve database met alleen een gewone bestandskopie. Houd alle kopieën lokaal, buiten Git en rapportages.
2. Inspecteer een werkkopie zonder app-initialisatie: alleen versies, tabel-/index-/triggerdefinities, integriteitscontrole en foreign-keycontrole. Vergelijk met een afzonderlijke verse synthetische database uit de huidige reguliere migraties. Aanwezigheid van `planning_state` ondersteunt de hypothese, maar bewijst niet welke historische handelingen plaatsvonden. Log geen records of persoonsgegevens.
3. Stel eerst vast welke huidige migratie-12-objecten ontbreken en welke bestaande duurzame no-showfeiten/intrekkingen behouden moeten blijven. Bij gedeeltelijke schema's of aanwijzingen voor verdwenen feiten: stop voor een gericht besluit; het aanmaken van een lege tabel reconstrueert geen gegevens.
4. Maak pas na akkoord een afzonderlijk, expliciet herstel binnen de reguliere migratiestructuur met een nieuw versienummer en vooraf gecontroleerde schema-uitgangssituatie. Verander geen oude versieregistraties. Bij geheel ontbrekende huidige objecten kan de bestaande migratie-12-definitie als basis dienen; bij gedeeltelijke aanwezigheid moet een afzonderlijk gecontroleerd plan uitsluitend ontbrekende objecten toevoegen. Geen generiek `CREATE IF NOT EXISTS` dat afwijkende bestaande objecten maskeert. Behoud alle bestaande tabellen en gegevens; herhaal geen oude destructieve migraties.
5. Test die afzonderlijke herstelwijziging transactioneel op de werkkopie, verifieer schema, integriteit, foreign keys en behoud van bestaande gegevens, en voer de regressiesuite uit. Leg resultaat en resterende onzekerheden voor aan Johan. Pas na expliciete goedkeuring toepassen op de lokale gebruikersdatabase, met gecontroleerde back-up/terugvalmogelijkheid.

Dit is geen uitvoerbaar herstelprogramma en geen toestemming voor herstel. Herstelimplementatie en behoudsbesluiten vallen buiten deze correctie.

## Overdracht

Geen taakplicht-, bronmapping- of architectuurbesluit nodig voor de bereikbaarheidscorrectie. Open: werkelijke historische databaseoorzaak, eventueel afzonderlijk herstelbesluit en lokale functionele beoordeling met de vijf echte exports door Johan. Planning blijft bij een defecte database beperkt beschikbaar totdat de oorzaak afzonderlijk is opgelost. De read-only controle blijft daarvan onafhankelijk.

Oplevercommit wordt afzonderlijk in de eindrapportage vermeld. Deze correctie is gereed voor beoordeling, niet functioneel geaccepteerd.
