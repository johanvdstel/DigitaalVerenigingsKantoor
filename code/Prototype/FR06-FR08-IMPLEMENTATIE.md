# FR-06–FR-08 — Sportlink-synchronisatiegrens

## Baseline en scope

- Integratiebaseline: `prototype-v0.5`, `4f25cdb6d08c7bd65ef90dcc1ffa00aa66c748d8`.
- Werkbranch: `codex/fr06-fr08-sportlink-sync-boundary`.
- Documentatie-HEAD vóór implementatie: `1cd43bde5df0174dd739ac311c73a20c24a2d954`.
- Functioneel contract en issue #14 blijven leidend; geen FR-09–12, E, F of Sportlink-mutaties.
- Kalendersemantiek is expliciet door Johan bevestigd op 27 september 2026, op basis van de CKC Roostergenerator en feitelijke API-output.

## Kalender en actieve periode

`weekoffset=-1` begint op maandag van de huidige kalenderweek; `0` op maandag van de volgende kalenderweek. `aantaldagen=N` telt N kalenderdagen inclusief de begindag. Op zondag 27 september 2026 betekent `0,7`: 28 september tot en met 4 oktober.

De bestaande `PlanningPeriod` bewaart vaste inclusieve datums. De planner kiest een periode die op maandag begint; een anders beginnende periode wordt in de applicatieservice geweigerd. `sportlink_parameters()` berekent bij iedere opvraag de bijbehorende relatieve offset opnieuw, zodat een opgeslagen periode niet met de kalenderweek meeschuift. Een weekwissel tijdens een opvraag breekt de poging af.

Migratie **012** voegt alleen een singleton `planning_state` toe: actieve periode, revisie en de laatst gezamenlijk bevestigde synchronisatie/bronverwijzingen. `temporary_planning` krijgt geen extra kolommen. Nieuwe bevestigingen moeten binnen de actieve periode liggen. Periodewijziging met werkvoorraad wordt geweigerd. Bestaande werkvoorraad zonder periode wordt niet gemigreerd naar een geraden periode: de planner kan expliciet een periode koppelen die alle bestaande diensten omvat, of expliciet weggooien.

## Dubbele synchronisatie

`PlanningSyncApplicationService.synchronize()` accepteert CSV-bytes plus een expliciete bevestiging dat de aangeboden export actueel is, en gebruikt de bestaande read-only Vrijwilligers-client. Er is geen invoer voor eerdere snapshot-ID's of opgeslagen importresultaten.

1. Lees de actieve periode/revisie en valideer dienstbindings en relevante leden.
2. Vraag iedere betrokken Sportlink-taakcode op met exact dezelfde actieve periode.
3. Normaliseer roosterregels met de bestaande adapter en bevestig een afzonderlijke `vrijwilligers_rooster`-snapshot.
4. Parse de aangeboden CSV via `SportlinkRealDataAdapter.parse_csv()` en de gedeelde `import_duty_rows()`-validatie voor `vrijwilligers_periode`.
5. Bevestig die CSV als afzonderlijke snapshot, zonder `source_period`. Ontbrekende/dubbele relevante urenposities en blokkerende imports worden geweigerd.
6. Sluit uitsluitend deze combinatie gezamenlijk af.

Beide bronfeiten behouden eigen raw/canonical payloads, provenance, importbatch en snapshot. Individuele `confirm_import()` blijft ongewijzigd en wist nooit planning. Een gedeeltelijk bevestigde bron blijft beschikbaar, maar wordt niet als gezamenlijk geaccepteerde planningspositie gebruikt.

Elke poging krijgt nieuwe import-identiteiten. De Streamlit-upload en de bevestiging krijgen na iedere poging nieuwe widgetkeys, ook bij fouten. Identieke bytes van een expliciet opnieuw aangeboden actuele export zijn toegestaan: een hash kan de actualiteit van een Sportlink-export niet bewijzen. De download en verklaring van actualiteit blijven menselijke handelingen.

## Atomaire afsluiting en weggooien

De afsluiting gebruikt `BEGIN IMMEDIATE`, controleert de ongewijzigde actieve staat/revisie en beide bevestigde bronresultaten van dezelfde poging, legt de nieuwe bronverwijzingen vast, voert `temporary_planning.clear()` uit en commit. Iedere fout rolt beide wijzigingen terug. Bevestigen en undo verhogen de revisie; daardoor kan een gelijktijdige planningswijziging niet ongemerkt worden gewist.

Expliciet weggooien gebruikt dezelfde volledige clear in een eigen transactie en geeft de periode vrij. Er ontstaat geen AssignmentRevocation of nieuwe functionele historie. Laatst bevestigde bronfeiten blijven bewaard. Een rooster wordt alleen voor zijn eigen periode toegepast; de actuele urenpositie blijft beschikbaar na een periodewissel.

## Doorwerking na synchronisatie

Planning leest de gezamenlijk geaccepteerde snapshots: roosterbezetting vervangt de eerdere bronbezetting, urenposities vervangen A/B/C/D en E wordt via bestaande logica afgeleid. Tijdelijke effecten verdwijnen volledig; er vindt geen individuele reconciliatie plaats. Zichtbare namen worden uitsluitend exact vergeleken, zonder fuzzy matching. `Afgeschermd` telt als bezetting en wordt nooit aan een persoon gekoppeld. Verouderde voorstellen kunnen gewijzigde uren of een overlappende Sportlink-inroostering niet alsnog bevestigen.

## Bestanden en redenen

- `dvk/planning_sync.py`: kalenderconversie, lifecycle, dubbele bronverwerking, transactionele afsluiting en gebruik van de nieuwe bronpositie.
- `dvk/real_data_import.py`: bestaande CSV-parser en urenvalidatie gedeeld met synchronisatie; v0.4-exportsemantiek behouden.
- `dvk/application_services.py`: periodebewaking bij bevestiging, revisies bij bevestigen/undo, staffing/beschikbaarheid/uren uit de geaccepteerde bronpositie.
- `dvk/persistence/migrations.py`, `planning_records.py`, `sqlite.py`: migratie 012, singleton-repository, clear en UoW-aansluiting.
- `streamlit_app.py`: vaste periode, expliciet koppelen/weggooien, CSV-aanbod en bewuste synchronisatie; beleidsvalidatie blijft in applicatielaag.
- `tests/test_planning_sync_v05.py`: 29 gerichte tests inclusief kalender, werkvoorraad, imports, privacy, rollback, concurrentie, oude snapshots en UI-acties.
- `tests/test_planning_workqueue_v05.py`: expliciete periode in fixture; reload controleert nu geblokkeerde periodekeuze; kandidaatcheckboxes onderscheiden van de nieuwe CSV-bevestiging. Staffing/conflict/undo-verwachtingen behouden.
- `tests/test_gate8b_persistence_v05.py`, `test_gate8c_atomic_v05.py`: expliciete periode als nieuwe preconditie, oorspronkelijke assertions behouden.
- `tests/test_gate10b_persistence_v05.py`: schema 12 en exact lege nieuwe staat verwacht; alle historische no-showfeiten en overige rijen blijven exact gecontroleerd.

## Verificatie

- Gerichte FR-06–08 plus FR-02–05, Gate 8 persistence/atomiciteit en import/snapshot/Vrijwilligers/staffing: **84 passed**.
- Volledige suite: **302 passed**.
- Syntaxcontrole Streamlit en synchronisatiemodule: geslaagd.
- `git diff --check`: geslaagd.

Er zijn geen historische functionele verwachtingswaarden versoepeld. De UI-periodewissel met actieve werkvoorraad is expliciet vervangen door FR-06; de schemaverwachting volgt de nieuwe forward migration.

## Grenzen voor acceptatie

De bestaande Streamlit-pagina blijft een prototype met demoleden en demodiensten. De nieuwe synchronisatie valideert tegen die zichtbare context; taakcodes worden expliciet opgegeven. De service zelf accepteert bestaande echte leden en dienstbindings. Deze iteratie bouwt geen nieuwe live leden-/dienstcatalogus-UI en gebruikt geen verborgen demoresultaten als geslaagde Sportlink-opvraag.

API-verkeer is in tests via een gecontroleerde read-only clientrespons getest; er is geen live CKC-synchronisatie uitgevoerd. De actualiteit van een handmatig gedownloade CSV berust op de expliciete gebruikershandeling, niet op een niet-bestaande Sportlink-transactiegarantie. Groene tests/CI vervangen geen functionele acceptatie.
