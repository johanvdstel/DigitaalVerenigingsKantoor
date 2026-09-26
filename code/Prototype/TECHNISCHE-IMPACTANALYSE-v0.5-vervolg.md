# Technische impactanalyse v0.5 — functioneel contract A/B + E + F

**Analysebaseline FR-06–FR-08:** `4f25cdb6d08c7bd65ef90dcc1ffa00aa66c748d8`  
**Functioneel contract:** `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md`  
**Type:** analyse; geen herontwerp van het functionele contract en geen productiecodewijziging.

## Samenvatting

De baseline ondersteunt belangrijke bouwstenen al: read-only Sportlink-adapters, minimum/maximum staffing, kandidaatbeoordeling, proposals/human decisions/assignments, snapshot/provenance-infrastructuur, Gate-10 no-showintrekking en v0.4-taakplichtafleiding. De grootste mismatch is semantisch: `DutyAssignment` is nu een duurzaam feit en bron voor no-shows, terwijl het nieuwe contract DVK-inroostering als tijdelijke werkvoorraad behandelt en no-shows uitsluitend aan feitelijke Sportlink-inroosteringen koppelt.

## A — Planning en synchronisatie

### Stand op baseline `4f25cdb...`
FR-02 t/m FR-05 zijn op deze baseline geïmplementeerd en functioneel geaccepteerd. `TemporaryPlanning` is een afzonderlijke actieve werkvoorraad; `PlanningApplicationService` telt deze mee in staffing en kandidaatbeschikbaarheid; `ProposalDecisionApplicationService.undo()` kan één tijdelijke inroostering verwijderen. De tijdelijke planning muteert de Sportlink-bronpositie niet.

De resterende implementatieopgave in A is daarom FR-06 t/m FR-08: de bewuste dubbele Sportlink-synchronisatie en het gecontroleerd afsluiten of bewust weggooien van de tijdelijke planningscyclus.

### Twee bronresultaten binnen één synchronisatiehandeling
Ledendienst Planning heeft voor een succesvolle synchronisatie twee verse Sportlink-bronresultaten nodig:

1. **Roosterdata:** `SportlinkVrijwilligersAdapter` leest de Sportlink Vrijwilligers-API. De door de planner gekozen planningsperiode moet exact overeenkomen met de periode van deze API-opvraag, gestuurd met `weekoffset` en `aantaldagen`. De `VolunteerBooking`-records bepalen de feitelijke bezetting.
2. **Sportlink Vrijwilligers-snapshot:** de actuele snapshot met de A/B/C/D/E-urenpositie van de relevante leden. Dit is een actuele toestandsopname; hiervoor is functioneel geen afzonderlijk datuminterval, seizoenlabel of extra peilmoment nodig.

Beide worden binnen dezelfde bewuste synchronisatiehandeling direct na elkaar opgehaald. DVK beschouwt ze samen als één voldoende actuele en gezaghebbende Sportlink-bronpositie. Er wordt geen sterkere transactionele garantie ontworpen die Sportlink zelf niet aanbiedt.

### Gap 1 — Vrijwilligers-API is nog geen bevestigde snapshotbron
`SportlinkVrijwilligersAdapter` levert `VolunteerBooking`, provenance en signalen, maar de huidige flow maakt daarvan nog geen `ImportBatch`/`SnapshotRecord`/`SourceSnapshot`. De adapter moet bronadapter blijven; persistence hoort in de import/applicatielaag. De roosteropvraag moet wel aantoonbaar bij de actieve planningsperiode horen.

De bestaande generieke `confirm_import()` bevestigt steeds één dataset en commit die afzonderlijk. Dat gedrag mag niet zelfstandig `temporary_planning` leegmaken.

### Gap 2 — er ontbreekt een Ledendienst Planning-synchronisatie-eenheid
Er is een kleine applicatie-orchestratie nodig boven de afzonderlijke bronimports. Die kent de actieve planningsperiode en kan alleen succesvol afronden als beide vereiste verse bronresultaten uit dezelfde bewuste synchronisatiehandeling zonder blokkerende fouten zijn verwerkt.

Dit hoeft geen generiek synchronisatieframework te worden. Een Ledendienst Planning-specifieke synchronization service/unit volstaat.

Een afzonderlijk bronresultaat mag al duurzaam bevestigd zijn als het andere later faalt. Functioneel kritisch is dat zo'n gedeeltelijke successituatie de tijdelijke planning nooit beëindigt.

### Gap 3 — gezamenlijke afronding moet atomair zijn
De afsluitende operatie moet in één transactie:
- vaststellen dat beide vereiste bronresultaten voor deze synchronisatie succesvol zijn;
- de synchronisatie als succesvol afronden;
- de volledige actieve `temporary_planning` leegmaken;
- committen.

Bij een fout in deze afronding volgt rollback: de synchronisatie geldt niet als afgerond en de tijdelijke werkvoorraad blijft intact.

De twee bronimports zelf hoeven daarom niet kunstmatig in één grote databasetransactie te worden gedwongen.

### Gap 4 — tijdelijke werkvoorraad kent nog geen volledige afsluitoperatie
`SQLiteTemporaryPlanningRepository` ondersteunt nu `add()`, `all()` en `remove(assignment_id)`. Voor FR-07/08 is daarnaast een transactionele `clear()`-achtige operatie nodig.

Periodegebaseerde verwijderlogica, JSON-datumselectie en extra `service_starts_at`/`service_ends_at`-kolommen zijn niet nodig. De functionele invariant is eenvoudiger: er is maximaal één actieve planningsperiode en alle tijdelijke DVK-inroosteringen behoren daartoe. De plannerperiode is exact de periode van de Vrijwilligers-API-opvraag. Na succesvolle dubbele synchronisatie kan de volledige werkvoorraad worden geleegd.

### Gap 5 — actieve planningsperiode moet centraal worden bewaakt
De UI en applicatielaag moeten waarborgen dat er maximaal één actieve planningsperiode is en dat tijdelijke inroosteringen alleen binnen die periode worden toegevoegd. Zolang tijdelijke planning bestaat, mag de UI niet stilzwijgend naar een andere periode overschakelen.

De planner krijgt wel expliciet de keuze de huidige planning weg te gooien en opnieuw te beginnen, bijvoorbeeld met een andere periode. Ook dat gebruikt de volledige clear-operatie; het is geen duurzame AssignmentRevocation of auditgebeurtenis.

### Privacy-afscherming is geen synchronisatieblokker
De Vrijwilligers-API levert geen lidmaatschapsnummer maar een Sportlink-weergavenaam. Voor zichtbare namen is het gedefinieerde Sportlink-naamformaat de deterministische koppeling met de andere Sportlink-bron. Bij privacy-afscherming kan `Afgeschermd` voorkomen.

Voor FR-06–FR-08 is persoonsidentiteit niet nodig om een roosterregel als bezetting te tellen. `Afgeschermd` blijft dus een geldig bronfeit en blokkeert de synchronisatie niet. Geen fuzzy matching, aliasbestand of handmatige persoonskoppeling in deze iteratie. Het identiteitsvraagstuk hoort bij FR-09–FR-12/no-show.

### Geen onnodige metadata op de Vrijwilligers-snapshot
De actuele Sportlink Vrijwilligers-snapshot krijgt functioneel geen kunstmatige `[start,end)`-scope, extra seizoen/periodebetekenis of apart peilmoment. Technische timestamps mogen voor provenance/logging bestaan, maar sturen de functionele synchronisatielogica niet.

De roosterbron heeft wél de expliciete plannerperiode, omdat alleen daarmee vaststaat welke concrete diensten via de Vrijwilligers-API zijn opgehaald.

### Te behouden
- minimum versus maximum;
- FR-02–FR-05 planning-conflict-, staffing- en undo-semantiek;
- expliciete menselijke verwerking in Sportlink;
- read-only Sportlink;
- bronfeit/afleiding/provenance-scheiding;
- bestaande individuele snapshotbevestiging, mits die niet zelfstandig de planningcyclus afsluit.

### Gerichte regressies FR-06–FR-08
Minimaal bewijzen:
1. alleen succesvolle roosteropvraag/bevestiging leegt de werkvoorraad niet;
2. alleen succesvolle actuele Sportlink Vrijwilligers-snapshot leegt de werkvoorraad niet;
3. fout/blokkerende validatie in één bron behoudt de volledige tijdelijke planning;
4. beide verse geldige bronresultaten binnen één bewuste synchronisatiehandeling kunnen de synchronisatie succesvol afronden;
5. succesvolle afronding leegt de volledige actieve tijdelijke werkvoorraad;
6. geen individuele reconciliatie van tijdelijke personen/inroosteringen met Sportlink;
7. `Afgeschermd` telt als feitelijke bezetting en blokkeert synchronisatie niet;
8. fout tijdens de afsluitende transactie laat synchronisatiestatus en tijdelijke werkvoorraad intact;
9. een planner kan de volledige tijdelijke planning expliciet weggooien en daarna een andere periode kiezen;
10. stilzwijgend wisselen van planningsperiode met actieve tijdelijke planning wordt verhinderd;
11. de plannerperiode en de Vrijwilligers-API-periode (`weekoffset` + `aantaldagen`) zijn exact dezelfde scope;
12. bestaande FR-02–FR-05-tests en volledige regressie blijven groen.

## B — No-show

### Reeds ondersteund
- immutable `NoShowEvent` en afzonderlijke `NoShowRevocation`;
- autorisatie, verplichte intrekkingsreden, maximaal één intrekking;
- actuele sanctiestatus wordt opnieuw afgeleid en ingetrokken no-shows tellen niet mee;
- seizoen 1 juli–30 juni en Gate-9-sanctieladder;
- SQLite append-only bescherming voor no-show/revocation uit Gate 10;
- UI gebruikt menselijke assignmentlabels.

### Concrete gaps
1. **Verkeerde bronafhankelijkheid.** `NoShowEvent` bevat `assignment_id`; `NoShowApplicationService.register()` vereist een bestaande lokale `DutyAssignment`; UI haalt no-showkeuzes uit `uow.assignments.recent()`. Dit schendt FR-09.
2. **Geen canoniek model voor feitelijke Sportlink-inroostering als no-showbron.** De Vrijwilligersadapter levert `VolunteerBooking`, maar de exacte stabiele bronidentiteit/provenance die een no-show duurzaam moet refereren moet technisch worden vastgesteld. Niet gokken.
3. **No-show bewaart onvoldoende zelfstandige broncontext.** Na latere Sportlink-sync is de huidige `assignment_id`-koppeling afhankelijk van lokale assignmentpersistence. FR-10 vereist een duurzaam begrijpelijke snapshot van persoon/dienst/source scheduling/provenance.
4. **Duplicate-check zit op lokale assignment-id.** Deze moet uiteindelijk op de identiteit van de concrete Sportlink-inroostering rusten.
5. **Geen Sportlink-correctiewerkvoorraad.** Openstaand/afgehandeld uit FR-12 ontbreekt in model, persistence, applicatieservice en UI.
6. **Migratie nodig.** Gate 10 schema 010 is geaccepteerd. Ontkoppeling van `assignment_id` moet daarom als nieuwe follow-upmigratie gebeuren; schema 010 niet herschrijven.

### Te behouden
Gate-10 event/revocation-semantiek, sanctieafleiding, autorisatie, seizoenslogica en immutable auditfeiten.

## E — Taakplichtcontrole

### Reeds ondersteund
- `model.py` bevat `DutyPolicy` en `FunctionExemptionPolicy`; configuratie is dus al modelleerbaar.
- `duty.py` bevat `derive_duty_qualification()`, `expected_required_hours()` en `evaluate_duty_foundation()`.
- eigen functie, erelid, recreatief, niet-spelend/inactief en minderjarigen-/gezinslogica zijn aanwezig.
- `_household_function_exemption()` werkt expliciet op gelijk adres en kan household-exempt functies toepassen; ontbrekende adressen kunnen tot onzekerheidssignaal leiden.
- v0.4 real-data import kan verwacht A vergelijken met Sportlink A en `REQUIRED_HOURS_MISMATCH` signaleren.
- bronfeit versus afleiding is reeds expliciet in v0.4.

### Concrete gaps / verificatiepunten
1. **Configuratie bestaat technisch, maar defaultbeleid is nog legacy hardcoded.** `LEGACY_FUNCTION_EXEMPTIONS` is een tuple in `duty.py`; de live CKC-lijst moet later externe/expliciete configuratie worden (E-03).
2. **Belangrijk detail:** de huidige legacy function policies worden aangemaakt met `household_exempt=False`. De code kan de meerderjarige gezinsvrijstelling technisch uitvoeren, maar de defaultconfiguratie activeert haar voor geen enkele functie. E-04 is dus nog niet operationeel afgedekt door de default policy.
3. **Huishoudregel is leeftijdsonafhankelijk.** `_household_function_exemption()` controleert gelijk adres en legt terecht geen meerderjarigheidsvoorwaarde op. Volgens E-04 geldt de huishoudvrijstelling voor alle leden van hetzelfde huishouden/adres wanneer een ander huishoudlid een CKC-erkende vrijstellende functie vervult. De implementatie moet deze regel dus niet alsnog tot meerderjarigen beperken.
4. **Dashboard ontbreekt.** Er is nog geen taakplichtcontroleweergave met lid, afleiding, reden, Sportlink A en controlestatus/filter op afwijkingen/onzekerheid.
5. **Verklaarbaarheid deels aanwezig.** Qualification reasons en signals bestaan, maar moeten naar stabiele menselijke UI-teksten worden vertaald zonder beleidslogica in Streamlit.
6. **10 uur staat zowel in legacybeleid als oudere rules-code.** Voor nieuwe v0.5-flow moet één expliciete policy/configuration-boundary worden gebruikt; historische regressiecompatibiliteit niet opportunistisch verwijderen.

## F — DVK-portaal

### Reeds ondersteund
- Streamlit is expliciet vervangbare UI-laag.
- technische IDs zijn volgens `AGENTS.md` al ongewenst wanneer menselijke identificatie bestaat.

### Concrete gaps
1. `streamlit_app.py` presenteert rechtstreeks “DVK v0.5 — Planning, kandidaten en menselijke beslissing”; er is geen portaalniveau/modulekeuze.
2. Status van Rooster Generator en toekomstige modules is niet zichtbaar.
3. Ledendienstfuncties zijn nog één doorlopende pagina; een lichte modulaire navigatie ontbreekt.
4. Geen generiek portalframework nodig. De minimale implementatie moet F-08 volgen en businesslogica buiten Streamlit houden.

## Cross-cutting gevolgen

### Persistence
De huidige SQLite-laag bewaart proposals, decisions en assignments duurzaam. Voor de tijdelijke werkvoorraad is minimaal actieve-state lifecycle nodig: toevoegen, queryen voor planning/conflicten, undo en opruimen/vervangen na succesvolle sync. Of bestaande tabellen daarvoor worden hergebruikt of een expliciete tijdelijke-planningrepresentatie wordt toegevoegd is een technische keuze voor een afgebakende implementatie-iteratie, zolang geen concurrerende waarheid na sync overblijft.

### Synchronisatiegrens
`confirm_import()` is de bestaande gecontroleerde snapshotbevestiging. De implementatie moet exact bepalen welke Sportlink-dataset(s) samen de “succesvolle synchronisatie” voor planning vormen. Dit kan niet uit het contract worden gegokt. Opruimen van werkvoorraad mag pas worden gekoppeld wanneer die grens technisch eenduidig is.

### Kandidaten
Bestaande `candidate_selection.py` behandelt wedstrijdcontext, niet conflicten met lokale DVK-planning. Een afzonderlijke planning-conflictbeoordeling is nodig zodat dezelfde dag zonder overlap als nood/avoid kan worden aangeboden en overlap wordt uitgesloten. Dit hoort in domein/applicatielogica.

### Historische regressies
R17 noemt `DutyAssignment` nog “factual scheduled duty” en verwacht D-update na assignment. Het nieuwe contract vervangt die semantiek voor v0.5 expliciet: een DVK-inroostering is tijdelijke planningswerkvoorraad en Sportlink blijft bronhouder van de feitelijke inroostering. Historische regressietests worden beschermd voor zover de onderliggende functionele afspraak nog geldig is. Een test die aantoonbaar een door dit contract vervangen afspraak vastlegt, mag daarom niet de nieuwe v0.5-semantiek blokkeren; zo'n test wordt bewust en traceerbaar aangepast of vervangen. Nieuwe v0.5-tests moeten de gewijzigde lifecycle expliciet bewijzen.

## Aanbevolen implementatievolgorde

1. **Planning work queue + conflict/undo + staffing-effect** — maak FR-02 t/m FR-05 waar zonder no-show mee te trekken.
2. **Sync boundary (FR-06–FR-08, huidige iteratie)** — twee verse Sportlink-bronresultaten binnen één bewuste synchronisatiehandeling; succesvolle gezamenlijke afronding leegt de actieve werkvoorraad, mislukking behoudt haar.
3. **Sportlink scheduling identity + no-show ontkoppeling** — modelleer feitelijke Sportlink-inroostering als bron voor no-show, voeg duurzame snapshot/provenance toe en migreer Gate-10 schema vooruit.
4. **No-show Sportlink-correctiewerkvoorraad** — openstaand/afgehandeld.
5. **Taakplichtcontrole** — policyconfiguratiegrens, meerderjarige household-regel en dashboard; concrete live functielijst blijft uitgesteld tot live data.
6. **Lichte portaalnavigatie** — F zichtbaar maken zonder frameworkbouw.

Iedere stap hoort een afzonderlijke werkbranch/PR en gerichte regressies te krijgen.

## Beslispunten vóór specifieke implementatiestappen

Dit zijn technische/functionele gegevens die de analyse niet invult:
- welke Sportlink scheduling-key/provenance betrouwbaar en stabiel genoeg is voor FR-09/10;
- of het markeren van een Sportlink-correctie als afgehandeld in v0.5 weer teruggezet moet kunnen worden (het contract eist dat niet);
- de definitieve CKC-lijst van functies met self-/household-vrijstelling blijft bewust uitgesteld tot live data.

Geen van deze punten verandert het vastgestelde functionele contract; ze begrenzen latere implementatie.
