# Technische impactanalyse v0.5 — functioneel contract A/B + E + F

**Analysebaseline:** `362c6a817ea00a13685a07c13ade71ed14c1eda4`  
**Functioneel contract:** `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md`  
**Type:** analyse; geen herontwerp van het functionele contract en geen productiecodewijziging.

## Samenvatting

De baseline ondersteunt belangrijke bouwstenen al: read-only Sportlink-adapters, minimum/maximum staffing, kandidaatbeoordeling, proposals/human decisions/assignments, snapshot/provenance-infrastructuur, Gate-10 no-showintrekking en v0.4-taakplichtafleiding. De grootste mismatch is semantisch: `DutyAssignment` is nu een duurzaam feit en bron voor no-shows, terwijl het nieuwe contract DVK-inroostering als tijdelijke werkvoorraad behandelt en no-shows uitsluitend aan feitelijke Sportlink-inroosteringen koppelt.

## A — Planning en synchronisatie

### Reeds ondersteund
- `staffing.py` onderscheidt minimumbezetting, maximumcapaciteit, open need en remaining capacity.
- `PlanningApplicationService`/`planning.py` leveren een read-only planningsoverzicht.
- kandidaatselectie en prioritering bestaan als domeinlogica; wedstrijd-overlap en bestaande Gate-8-regels blijven bruikbaar.
- `ProposalDecisionApplicationService` bewaakt bevestiging via een applicatieservice; Streamlit hoeft geen beleidsbesluit te nemen.
- read-only Sportlink is reeds architectuurregel.
- import/snapshot-infrastructuur kent bevestigde snapshots en supersedes-relaties.

### Concrete gaps
1. **Lokale assignments tellen niet mee in staffing.** `calculate_staffing_need()` telt alleen Sportlink/`VolunteerBooking`-bookings. Na bevestiging in Streamlit wordt het planningsoverzicht niet opgebouwd uit bronbezetting + actieve lokale werkvoorraad. FR-03 ontbreekt.
2. **Geen planning-conflictmodel voor lokale inroosteringen.** `approve_many()` bewaakt alleen capaciteit van de geselecteerde dienst en dubbele proposal-id's binnen één call. Er is geen centrale invariant voor dezelfde dienst, overlap op dezelfde dag of noodstatus bij twee niet-overlappende diensten op dezelfde dag (FR-04).
3. **Geen undo van tijdelijke inroostering.** Repository ondersteunt add/get/recent, geen verwijderen/terugdraaien als werkvoorraad (FR-05).
4. **`DutyAssignment` heeft verkeerde duurzame semantiek.** Model, persistence en v0.4-tests presenteren assignment als feitelijke scheduling en muteren D via `apply_assignment_to_case`. Voor het nieuwe contract moet worden bepaald welke bestaande typen/namen behouden kunnen blijven als tijdelijke werkvoorraad zonder historische geaccepteerde regressies stilzwijgend te herschrijven.
5. **Succesvolle sync ruimt lokale werkvoorraad niet op.** `confirm_import()` creëert/supersede een SourceSnapshot maar heeft geen expliciete koppeling naar actieve tijdelijke planning. Er is ook geen atomaire regel “alleen na succesvolle bevestiging lokale werkpositie vervangen”; mislukte import moet haar juist behouden (FR-07).
6. **Proposals/decisions/assignments worden nu duurzaam opgeslagen.** Het contract vereist geen permanente functionele historie van selecteren/inroosteren/undo na succesvolle sync. De impact op bestaande audit-/Gate-8-tests moet gecontroleerd worden; niet automatisch tabellen verwijderen.

### Te behouden
- minimum versus maximum;
- bestaande kandidaat- en wedstrijdregels;
- expliciete menselijke bevestiging;
- read-only Sportlink;
- snapshot/provenance-principe.

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
3. **Leeftijdsvoorwaarde meerderjarig controleren.** `_household_function_exemption()` controleert gelijk adres maar niet expliciet dat het te beoordelen gezinslid meerderjarig is. Volgens E-04 moet deze regel specifiek voor meerderjarige gezinsleden gelden.
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
2. **Sync boundary** — koppel tijdelijke werkvoorraad gecontroleerd aan een eenduidig succesvolle Sportlink-sync; mislukte sync behoudt state.
3. **Sportlink scheduling identity + no-show ontkoppeling** — modelleer feitelijke Sportlink-inroostering als bron voor no-show, voeg duurzame snapshot/provenance toe en migreer Gate-10 schema vooruit.
4. **No-show Sportlink-correctiewerkvoorraad** — openstaand/afgehandeld.
5. **Taakplichtcontrole** — policyconfiguratiegrens, meerderjarige household-regel en dashboard; concrete live functielijst blijft uitgesteld tot live data.
6. **Lichte portaalnavigatie** — F zichtbaar maken zonder frameworkbouw.

Iedere stap hoort een afzonderlijke werkbranch/PR en gerichte regressies te krijgen.

## Beslispunten vóór specifieke implementatiestappen

Dit zijn technische/functionele gegevens die de analyse niet invult:
- welke Sportlink scheduling-key/provenance betrouwbaar en stabiel genoeg is voor FR-09/10;
- welke combinatie van bevestigde Sportlink-datasets precies de succesvolle synchronisatiegrens van FR-07 vormt;
- of het markeren van een Sportlink-correctie als afgehandeld in v0.5 weer teruggezet moet kunnen worden (het contract eist dat niet);
- de definitieve CKC-lijst van functies met self-/household-vrijstelling blijft bewust uitgesteld tot live data.

Geen van deze punten verandert het vastgestelde functionele contract; ze begrenzen latere implementatie.
