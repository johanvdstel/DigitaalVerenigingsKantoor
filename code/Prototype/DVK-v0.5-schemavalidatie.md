# PR #38 — Veilige schemavalidatie en migraties

## Context en grondslag

Opdracht Stap 2 van Johan/CKC, 22 oktober 2026. Werkbranch `codex/vrijwilligers-planning-integratie`, uitgangscommit `a9dbab8854165f7245cf3cf83617d0ca04def31e`. GitHub PR #38 bevestigt doel `prototype-v0.5` met PR-baseline `1399493e70bd35b356a0108e87a0ff8ec614b5af`. De Vrijwilligersintegratie en laatste UI zijn volgens deze opdracht lokaal functioneel geaccepteerd en worden niet gewijzigd. De geaccepteerde releasebaseline blijft v0.4 op main; deze opdracht is geen integrale v0.5-releaseacceptatie.

De repositorydocumentatie (`BACKLOG.md`, prototypeplanning, productieroadmap, broncontracten, persistence-interfaces en no-show-/databasestabilisatierapporten) is gecontroleerd. Sportlink blijft bronhouder, CKC bepaalt de functionele werkelijkheid, SQLite is de bestaande prototypeopslag. Er komt geen productiearchitectuur, nieuwe functie of herstelvoorziening bij.

Vastgestelde afwijkingen: `migrate()` vertrouwde alleen op MAX(version), waardoor versie 12 met ontbrekende objecten werd geaccepteerd. DDL en versieadministratie hadden geen gezamenlijke buitenste transactie. De Connection-contextmanager commit/rollbackt maar sluit niet zelf; daarnaast wordt `__exit__` niet aangeroepen wanneer `__enter__` faalt. De opdracht vereist daarom uitsluitend schemacontrole, transactionele migratie en deterministische verbindingssluiting.

## Versiegebonden referentieschema

`schema_validation.py` gebruikt een gelijkwaardige methode voor een afzonderlijk uitgeschreven schemaspecificatie: de ongewijzigde historische migratiereeks bouwt iedere ondersteunde versie op in een aparte, lege SQLite-geheugendatabase. SQLite zelf interpreteert daarbij de DDL. De resulterende metadata wordt per versie gecachet. De bestaande database krijgt nooit referentie-DDL als herstelactie aangeboden.

De referentie is afkomstig van een afzonderlijk vastgelegde tuple met de historische migratiefuncties. Een in tests opzettelijk beschadigde uitvoermigratie wijzigt daardoor niet haar eigen verwachte schema. Bij toekomstige ontwikkeling worden nieuwe stappen aan de migratiereeks toegevoegd; oude geaccepteerde stappen worden niet hergebruikt voor een andere betekenis. De twaalf huidige migratiefuncties zijn met AST-vergelijking aantoonbaar ongewijzigd.

De controle vergelijkt:

- alle vereiste tabellen en hun definities;
- kolomnamen, volgorde, type, NOT NULL, standaardwaarde, PK-positie en verborgen/gegenereerde kolomstatus via table_xinfo;
- foreign-key-definities, inclusief verwijzingen en acties;
- vereiste expliciete indexen en impliciete PK/UNIQUE-indexen, uniciteit, oorsprong, partial-status, sleutelvolgorde, collatie en sorteerrichting;
- SQL-definities van vereiste indexen en triggers, inclusief de immutable no-showbescherming;
- de administratie met exact de opeenvolgende gehele stappen 1 t/m de geregistreerde versie.

DDL-formattering, keyword-hoofdletters en gebruikelijke identifierquoting worden genormaliseerd; letterlijke SQL-waarden en de inhoud van constraints/triggerbodies blijven betekenisvol. Handmatig anders herschreven, semantisch mogelijk equivalente DDL kan conservatief worden afgewezen. Dat is geen opdracht om die database automatisch te corrigeren. Aanvullende losse tabellen/indexen/triggers worden niet verwijderd; de validatie eist het DVK-contract en is geen algemeen beheer van extra gebruikersobjecten. De bestaande foutinjectietrigger uit de historische migratietest blijft daardoor bruikbaar.

## Afwijzing en nieuwe databases

Zonder versieadministratie geldt alleen een structuur zonder applicatieobjecten en zonder eerdere SQLite-schemawijziging als nieuw. SQLite's interne schema_version-counter helpt een volledig leeggehaald oud schema herkennen; die counter is niet de DVK-versieadministratie. Een lege correcte schema_version-tabel zonder overige objecten is ook een geldige bootstraptoestand.

Een ontbrekende/afwijkende versieadministratie, gaten, nul/negatieve of toekomstige stappen en afwijkingen in een vereist object stoppen de initialisatie vóór enige migratie. Er is geen reset, inferentie van een versienummer, heraanmaak van ontbrekende feitentabellen of herstel van records. Schemaversie 12 blijft 12; deze wijziging voegt geen schema-stap of tabel toe aan de applicatiedatabase.

`SchemaValidationError`, een SQLite OperationalError, bevat uitsluitend de relevante vaste objectnaam/categorie en een begrijpelijke melding dat initialisatie is gestopt. Definities, recordinhoud, persoonsgegevens en credentials worden niet opgenomen. Echte ontbrekende tabellen/kolommen behouden de bestaande foutcategorie waarmee de UI al omgaat. De UI zelf en haar foutgrens blijven ongewijzigd.

## Transacties en verbindingen

Validatie, noodzakelijke migratiestappen, versie-inserts en controle van het resultaat vallen onder één savepoint. Ook na iedere stap worden structuur en volledige versieadministratie gecontroleerd. Mislukt een latere stap, dan worden eerdere stappen uit dezelfde upgrade eveneens teruggedraaid.

Bezit `migrate()` zelf de transactie, dan volgt bij fouten een volledige rollback. Alleen rollback-to/release van het buitenste savepoint kan nog een no-op-schrijftransactie committen en de SQLite-header wijzigen; de volledige rollback voorkomt dit. Binnen een reeds geopende transactie van de aanroeper gebruikt de migratie uitsluitend haar eigen savepoint en commit of verwijdert zij geen eerdere handelingen van die aanroeper.

`SQLiteDatabase.initialize()` sluit met closing de verbinding expliciet op succes en fouten en schakelt foreign keys in. `SQLiteUnitOfWork.__enter__()` rolt bij een fout terug, sluit en zet de verbinding op None, ook wanneer repository-initialisatie mislukt. Er is geen wijziging van transacties of functionele handelingen binnen de applicatieservices.

De historische semantiek blijft gelden: migratie 8 weigert dubbele oude no-shows; migratie 10 verwijdert uitsluitend de eerder expliciet vrijgegeven obsolete prototypefeiten/repairgegevens. Deze opdracht introduceert geen nieuwe destructieve SQL. De ongewijzigde historische regressies bewijzen zowel die geautoriseerde uitzondering als behoud van alle overige gegevens.

## Bestanden en verificatie

| Bestand onder code/Prototype | Reden |
| --- | --- |
| dvk/persistence/schema_validation.py | Versiegebonden schema- en administratiecontrole zonder herstel |
| dvk/persistence/migrations.py | Validatie vóór gebruik en na iedere stap; atomaire upgrade/rollback |
| dvk/persistence/sqlite.py | Expliciete verbindingssluiting en foutafhandeling in beide toegangspaden |
| tests/test_schema_validation_v05.py | 54 nieuwe synthetische regressies voor contract, behoud, rollback en resources |
| Dit rapport | Gekozen methode, beperkingen, historische semantiek en controlebewijs |

Gerichte persistentie-/migratie-/isolatieselectie: **78 geslaagd**. Volledige regressiesuite: **859 geslaagd**, 0 mislukt, 0 overgeslagen. `git diff --check` groen. De nieuwe tests omvatten migratie vanaf elke versie 1–11; behoud van werkvoorraad, bron-/importgegevens en alle huidige feitentabellen; fouten in kolommen, types/defaults/PK/FK/indexen/triggers; corrupte versieadministratie; foutinjectie na DDL en geautoriseerde historische verwijdering; resultaatvalidatie; geneste transactie-eigendom; gesloten verbindingen en vrijgegeven locks. Gezonde heropening, afgewezen inconsistenties en mislukte upgrades van bestaande databases blijven in de gerichte proeven byte-identiek. Nieuwe mislukte initialisatie laat geen gedeeltelijke applicatiestructuur achter.

Tussentijds faalden drie nieuwe bytevergelijkingen na savepoint-rollback/release. Schema en gegevens waren toen al hersteld, maar de bestandsheader wijzigde. De implementatie is aangepast naar volledige rollback bij eigen transactie; de oorspronkelijke strengere tests blijven behouden en slagen nu. Bestaande migratie-, UI- en domeintests zijn niet versoepeld of aangepast.

De lokale wijzigingen die vóór deze opdracht aanwezig waren in streamlit_app.py en DVK-v0.5-vrijwilligers-integratie.md blijven ongemoeid en buiten de commit. Geen echte CKC-export, live Sportlink-respons of bestaande lokale database geopend of gewijzigd. Alle tests gebruiken synthetische gegevens in tijdelijke databases.

Beperkingen: dit valideert het schema en de migratieketen, niet de inhoudelijke juistheid of historische volledigheid van willekeurige JSON-records. Extra gebruikersobjecten vallen buiten het DVK-contract. De bytevergelijkingen betreffen de geteste rollback-journal-situaties, geen algemene claim over journal-/WAL-bestanden of fysieke herstelbaarheid. Een daadwerkelijk inconsistent bestand vereist afzonderlijk onderzoek en toestemming voor herstel; deze wijziging reconstrueert geen verdwenen gegevens. PR #38 blijft open en ongemerged; deze technische stap wacht op afzonderlijke beoordeling.

Technische referenties: [Python sqlite3-contextmanager](https://docs.python.org/3.11/library/sqlite3.html#how-to-use-the-connection-context-manager), [SQLite-savepoints](https://www.sqlite.org/lang_savepoint.html), [SQLite-PRAGMA metadata](https://www.sqlite.org/pragma.html).
