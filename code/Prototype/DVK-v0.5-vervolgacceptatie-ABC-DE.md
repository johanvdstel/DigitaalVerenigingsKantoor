# PR #44 — vervolgacceptatie A/B/C en onderzoek D/E

Status: technisch uitgevoerd vanaf `6b63caa`, bestaande branch
`codex/actuele-kandidaatcontext`, basis `prototype-v0.5` / `5958b982`.
Geen functionele eindacceptatie of merge. De geaccepteerde v0.4-mastercases,
taakplichtcriteria, prioriteringsregels en No-Show-regels blijven behouden.

## A — Herleidbare bronmeldingen (geïmplementeerd)

De oude import behield voor conflicterende leden alleen signalen: `continue`
stond vóór het vastleggen van bruikbare herkomstvelden. De bestaande parser
bewaart nu ook een minimale projectie van de reeds ingelezen regels, vóór
uitsluiting. Er is geen tweede importmechanisme. Bronbestand, bronregelnummer
(recordindex zonder kolomkop), relatiecode, naam en relevante waarden blijven
beschikbaar, ook wanneer de canonieke persoon niet kan worden gemaakt.

`source_diagnostics` levert gestructureerde Nederlandse meldingen aan de
applicatie/UI. Dubbele registraties staan per afwijking afzonderlijk in de tabel.
Geboortedatum wordt alleen getoond voor een identiteits-/geboortedatumconflict;
email, telefoon, bankgegevens en adressen worden niet in deze diagnostische
projectie opgeslagen. Beschikbare Programma-team-/competitiecontext staat bij
Programma-meldingen. Bij ontbrekende bronwaarden blijven velden leeg; niets wordt
gereconstrueerd. De gegevens blijven uitsluitend lokaal in het procesgeheugen.
Geen correctieknoppen, automatische bronreparatie of nieuwe opslag.

## B — Volledig kandidatenaanbod (geïmplementeerd)

Oorzaak van de afkapping: `plan_proposals` gebruikte
`ranked[:staffing_need.candidate_slots]`. De operationele applicatieservice levert
nu alle geschikte voorstellen, in dezelfde prioriteitsvolgorde. Ook de demo-UI
gebruikt het volledige aanbod. De historische standaardaanroep van
`plan_proposals` blijft beschikbaar voor de bestaande baselinecases.

De bestaande tabel met kolommen en selectievakjes blijft in een verticaal
scrollbare container van 330 pixels. Naam, rang, actuele uren, wedstrijdcontext
en toelichting blijven zichtbaar; lager gerangschikte kandidaten vallen niet
weg. Een voorstel is nog geen indeling. De planner kan minder of precies de
vrije capaciteit selecteren. Bij overschrijding meldt de publieke
`PlanningApplicationService.selection_problem` de bestaande domeincontrole en
is bevestigen niet beschikbaar. De checkboxkeuze kan dus tijdelijk ongeldig
zijn, maar kan nooit als indeling worden bevestigd. `approve_many` hercontroleert
atomair tegen de actuele werkvoorraad; dubbele, conflicterende en te grote
selecties blijven geweigerd. Capaciteit blijft de bestaande Max minus bezetting,
inclusief tijdelijke DVK-planning; geen nieuwe beleidsregel.

## C — Uniforme lokale CSV-broninvoer (geïmplementeerd)

`LocalCsvSourceApplicationService` leest de bestaande vijf standaardbestanden uit
`~/Documents/DVK-Sportlink-exports/` via de bestaande tekstlezer en parser.
Kandidaatselectie en Taakplichtcontrole laden automatisch bij gebruik en na
relevante invoerwijziging. Bij terugkeer via de navigatie worden bronnen opnieuw
geladen. Filter-/selectieacties controleren de map niet opnieuw. De geladen
toestand en laadtijd staan in de lokale Streamlit-sessie; dit regelt de expliciet
gevraagde bronlevensduur, niet een optimalisatiecache van kandidaatberekeningen.

**Brongegevens vernieuwen** leest opnieuw. Bij een mislukte verversing verdwijnt
de oude weergave; een fout wordt niet bij elke checkboxklik automatisch opnieuw
geprobeerd. Bestandsnamen en laatste laadtijd zijn zichtbaar. Na handmatige
vervanging van exports moet de planner vernieuwen of het scherm opnieuw openen.
Er is geen achtergrondcontrole en laadtijd bewijst geen exportactualiteit.

De aparte vijf uploads in Taakplichtcontrole zijn verwijderd. Synchronisatie
leest eveneens Leden.csv uit dezelfde map, opnieuw bij de bestaande expliciete
synchronisatieactie. Consequentie: voor een ander ledenbestand vervangt de planner
Leden.csv in de map; een aparte ad-hocupload in dit scherm is niet meer nodig.
De bestaande openbare Python-import met expliciete paden/streams blijft werken.
CSV-validatie, persoonskoppeling en gevolgen van synchronisatie zijn ongewijzigd.
De taakplichtcontrole blijft read-only, zonder SQLite/API-toegang, en behoudt
haar strikte beoordelings-/invoercontract; de kandidaatroute behoudt haar
persoonsisolatie. Bronbestanden worden nooit herschreven.

## D — Vaste selectiekolom (alleen onderzocht)

Huidige dienstenweergave: `st.data_editor`, Kies als CheckboxColumn van 60 px,
1275 px totale breedte, 32 px rijhoogte, overige velden read-only. Kies is een
gewone gegevenskolom en is nu niet vastgezet.

Lokaal gecontroleerd met `inspect.signature` en de geïnstalleerde publieke
API-documentatie: **Streamlit 1.64.0** ondersteunt
`st.column_config.CheckboxColumn(..., pinned=True)`. Volgens de documentatie
blijft die kolom links zichtbaar tijdens horizontaal scrollen. Dit past met één
kolomoptie binnen de bestaande architectuur en behoudt selectie in de tabel.
Er is geen externe component, JavaScript of aparte selectiebediening nodig.

Niet geïmplementeerd. Het project declareert `streamlit>=1.40,<2`, geen vaste
1.64-versie. Ondersteuning in iedere toegestane oudere versie is niet bewezen;
bij een vervolgopdracht moet de daadwerkelijke runtime worden gecontroleerd en
zo nodig de ondersteunde minimumversie expliciet worden vastgelegd. Het huidige
scrollgedrag blijft tot dat besluit behouden. Een visuele browserproef moet de
vastgezette checkboxkolom daarna functioneel bevestigen.

## E — Vertraging bij acties (alleen onderzocht)

Reproduceerbaar meetinstrument: `tests/measure_planning_actions.py`.
Uitvoeren vanuit `code/Prototype` met de bestaande omgeving:

```bash
python -B tests/measure_planning_actions.py --members 50
python -B tests/measure_planning_actions.py --members 250
```

Alle personen/exports zijn synthetisch (volwassenen, afzonderlijke adressen, geen functies/bronafwijkingen); Programma-respons en Vrijwilligers-sync
zijn gesimuleerd; SQLite en profielbestanden staan in een tijdelijke map. Het
profiel draait op de Streamlit-scriptthread. Per actie drie herhalingen;
onderstaande medianen komen uit na elkaar uitgevoerde meetreeksen, Python 3.11,
Streamlit 1.64.0 op deze Mac. Profiler/AppTest veroorzaken overhead; het is geen
meting van de browser of van de werkelijke CKC-populatie.

| Populatie / actie | Totale server/AppTest-tijd | Kandidaatketen | Daarvan taakplicht/uren | Prioritering | SQLite execute-tijd |
| --- | ---: | ---: | ---: | ---: | ---: |
| 50 / dienstkeuze | 492 ms | 10 ms | 8 ms | <1 ms | 5 ms |
| 50 / kandidaatkeuze | 446 ms | 10 ms | 8 ms | <1 ms | 5 ms |
| 250 / dienstkeuze | 5812 ms | 186 ms | 178 ms | 1 ms | 7 ms |
| 250 / kandidaatkeuze | 4372 ms | 187 ms | 179 ms | <1 ms | 7 ms |

Elke actie doet een volledige Streamlit-rerun en bouwt de kandidatenrijen met
meerdere kolommen, widgets en detailformulieren opnieuw op. De bestaande
kandidaatketen/taakplichtafleiding wordt ook bij een checkboxklik opnieuw
uitgevoerd. Bij 250 kandidaten ligt het grootste gemeten deel in schermopbouw,
niet in prioritering of bronverkeer. De bestaande urencontrole scant per persoon urenregistraties en herkomstgegevens; dit werk groeit met de populatie. Grotere populaties, functies/huishoudens en vele bronmeldingen zijn niet met echte CKC-data gemeten.

De oorspronkelijke weergave vóór B was
beperkt tot capaciteit; deze meting na A/B/C bewijst dus niet de precieze oorzaak
van de eerder met echte exports gemelde vertraging.

Tijdens beide acties: **0 Sportlink-CSV-herlezingen, 0 Programma-aanroepen**.
De kleine versiebeheerde functieclassificatie-CSV wordt wel opnieuw door de
bestaande taakplichtafleiding gelezen. Database-initialisatie/schema-validatie
gebeurt éénmaal per rerun (circa 3 ms). Het profiel telt circa 1119 SQLite
execute-aanroepen, inclusief referentieschema-/metadatavalidatie; hun totale
execute-tijd is circa 5–7 ms. Dit zijn geen 1119 operationele wijzigingen.
Keuzeacties schrijven geen tijdelijke indeling; alleen expliciete bevestiging
gebruikt de bestaande schrijftransactie.

Mogelijke vervolgstappen, **niet uitgevoerd**:

- Eerst een compacte native tabelweergave onderzoeken om het aantal individuele
  widgets/detailformulieren te verlagen. In deze meting heeft dat het grootste
  potentiële effect; toegankelijkheid, meervoudige selectie en herleidbare
  toelichting moeten behouden blijven. Werkelijk effect vraagt een vervolgproef.
- Een gerichte fragment-/schermgrens kan ongewijzigde schermdelen buiten de rerun
  houden. Dit vereist expliciet toetsen van actualiteit en bron-/planningsgrenzen.
- Hergebruik van berekeningen kan domeinwerk uitsparen, maar vereist betrouwbare
  invalidatie op bron, dienst, peildatum en tijdelijke planning. Geen nieuwe
  cachingstrategie invoeren zonder afzonderlijke opdracht; bij deze omvang is
  de gemeten domeintijd bovendien kleiner dan de UI-opbouwtijd.
- Databaseoptimalisatie heeft op basis van deze meetreeks geen prioriteit.

## Verificatie en lokale heracceptatie

13 nieuwe A/B/C-regressiegevallen plus de aangepaste UI-/broninvoertests.
Gerichte A/B/C- en UI-suite: **70 geslaagd**. Volledige suite: **1117 geslaagd**. Bestaande import-, conflict-, database-isolatie-
en No-Show-controles blijven getest. Alleen verwachtingen die door de expliciete
B/C-opdracht zijn vervangen (uploads, handmatige eerste laadactie, beperkt aanbod)
zijn aangepast; C-/W-/I-/R-mastercases blijven intact. Tests isoleren HOME en
simuleren alleen het standaard Programma-transport; echte exports/live API's zijn
uitgesloten. Syntax en diffcontrole worden vóór commit uitgevoerd; CI volgt op PR #44.

1. Start de juiste PR-checkout met de bestaande Python-omgeving; kies de planning.
2. Controleer automatisch geladen bestandsnamen en laadtijd. Open bronmeldingen en
   controleer de betrokken regels van de bekende duplicaten/statusafwijking.
3. Synchroniseer via de bestaande expliciete bediening; selecteer een dienst met
   vrije capaciteit. Controleer dat meer kandidaten dan plaatsen worden aangeboden.
4. Selecteer één/meerdere kandidaten. Boven capaciteit moet bevestigen onmogelijk
   zijn; onder/op capaciteit blijft de bestaande menselijke bevestiging gelden.
5. Open Taakplichtcontrole: geen uploads; dezelfde map, afzonderlijke beoordeling.
   Vernieuw expliciet na vervangen van exports. Een fout mag geen oude tabel als
   actuele uitslag laten staan. Gebruik alleen lokale testkopieën voor foutproeven.
6. Controleer undo en No-Shows zoals eerder. Functionele acceptatie en merge blijven
   een afzonderlijk besluit. D en E hebben geen vastzet- of optimalisatiecode gekregen.

## Gewijzigde onderdelen

- `real_data_import.py`, `source_diagnostics.py`, `candidate_context.py`: minimale
  bronprojectie, gestructureerde meldingen en volledig kandidatenaanbod.
- `proposal_planning.py`, `application_services.py`: aanbod los van capaciteit;
  presentatie van de bestaande selectiecontrole, atomische goedkeuring behouden.
- `local_csv_sources.py`, `sportlink_exports.py`, `streamlit_app.py`: uniforme
  invoer, transparantie, verversingsgrenzen en bestaande tabel/selectiebediening.
- De A/B/C-regressietests, bijgewerkte UI-testfixtures, `tests/conftest.py` en het
  meetinstrument: uitsluitend synthetische bron- en onderzoeksverificatie.
- Prototype-README, herijkte baseline, actuele-kandidaatcontext en dit verslag:
  huidige werking/afbakening naast de historische besluiten beschreven.


## Vervolg: dienstentabel en prestaties — 25 oktober 2026

Vertrekpunt `a8e5a1f`, dezelfde werkbranch en PR #44, integratiebasis
`prototype-v0.5` / `5958b982`. De opdrachtgever heeft A/B/C hierboven lokaal
functioneel geaccepteerd. Deze vervolgstap behoudt die werking en vereist zelf
nog lokale heracceptatie. `main` blijft de geaccepteerde v0.4-releasebaseline.
De historische onderzoeksresultaten D/E hierboven zijn het vertrekpunt, niet
meer de actuele implementatiestatus.

### Dienstentabel A1–A5

- **A1:** een native checkboxcallback verwerkt een nieuwe keuze vóór de volgende
  schermopbouw. De volgende tabel toont alleen die dienst geselecteerd; ook
  deselecteren blijft mogelijk. Een nieuwe widgetidentiteit wist eerdere edits.
  De kandidaatketen ontvangt meteen de nieuwe dienst. Selecteren schrijft geen
  tijdelijke planning.
- **A2:** `Kies` krijgt `pinned=True` wanneer de publieke kolomconstructor dit
  ondersteunt. Geïnstalleerd en getest: Streamlit **1.64.0**. De projectgrens
  blijft `>=1.40,<2`; opties worden met de publieke functiesignatuur gecontroleerd.
  Oudere runtimes zonder pinned/alignment behouden gewone native kolommen;
  voor die opties worden geen onbewezen argumenten meegegeven en er wordt geen
  dependencygrens verhoogd. Aanvullend is het officiële PyPI-wheel van 1.40.0
  uitsluitend in een tijdelijke map geïnspecteerd: Column/CheckboxColumn missen
  pinned/alignment; data_editor mist row_height en de kolombreedtes zijn daar
  alleen small/medium/large. De reeds vóór deze stap gebruikte pixelbreedtes en
  row_height bewijzen dus geen volledige 1.40-compatibiliteit. Deze iteratie
  test de volledige app op 1.64.0; gebruik die versie voor lokale heracceptatie.
  Geen volledige compatibiliteitsmatrix of dependency-upgrade uitgevoerd.
- **A3:** de zes numerieke kolommen vragen uniform 65 px, rechts uitgelijnd waar
  ondersteund. Dit beperkt witruimte zonder waarden af te kappen in de geteste
  synthetische voorbeelden. `Onbekend` blijft ongewijzigd bronstatus.
- **A4:** volledige kolomnamen blijven behouden en staan ook in de koptooltip.
  De gecontroleerde publieke editor-/kolom-API heeft geen optie voor meerregelige
  kolomkoppen. Langere koppen kunnen dus visueel afgekapt blijven in 65 px;
  aanwijzen van de kop toont de volledige betekenis. Geen afkortingsbeleid,
  CSS-ingreep of niet-bestaande wrap-optie toegevoegd.
- **A5:** de tabel benut de containerbreedte (nieuwe runtime: `width="stretch"`,
  oudere signature: `use_container_width=True`); native horizontaal scrollen
  blijft bij onvoldoende ruimte beschikbaar. De aangevraagde kolombreedtes
  tellen op tot circa 1135 px in plaats van 1275 px. Streamlit kan ruimte
  verdelen; de browser bepaalt de uiteindelijke pixels. Sportlink houdt 320 px
  als kolomconfiguratie, volledige originele namen en dubbelkliktoegang;
  rijhoogte blijft 32 px.

Visueel vastzetten, tooltips, browserrespons en gedrag op smalle schermen zijn
niet met AppTest te bewijzen en horen bij de lokale acceptatie. Bij het vernieuwen
van de dienstentabel kan de native scrollpositie teruggezet worden.

### Gerichte prestatiecorrectie B

**Vastgesteld:** de oude weergave bouwde voor elk van 250 kandidaten negen
kolommen, tekstwidgets, een popover en een volledig uitzonderingsformulier,
ook wanneer alle popovers gesloten waren. Elke checkboxactie herhaalde dit.
Het aanbod afkappen zou de geaccepteerde vrije kandidaatkeuze aantasten.

**Minimale presentatiecorrectie:** één native `data_editor` toont alle kandidaten
in de door de bestaande applicatieservice geleverde volgorde, met meervoudige
Kies-checkboxen. Eén expander met kandidaatkeuze biedt dezelfde taakplicht- en
prioriteitstoelichting en het bestaande uitzonderingsformulier. Alleen deze
presentatie is vervangen, geen kandidaat-/prioriteits-/goedkeuringslogica.
Een gewijzigde geordende lijst voorstelidentiteiten krijgt een nieuwe editor-key,
zodat oude rijposities geen andere kandidaat kunnen selecteren.

Normale Streamlit-reruns en herbeoordeling tegen actuele tijdelijke planning
blijven bestaan. Er zijn geen fragmenten, berekeningscache, achtergrondtaken,
externe tabelbibliotheken of maatwerk-JavaScript toegevoegd. De gemeten
UI-winst maakt extra invalidatie-/cachestrategieën hier niet nodig.

De bestaande `tests/measure_planning_actions.py` is vóór en na gedraaid met
250 dezelfde synthetische personen, drie dienstwisselingen en drie toggles van
één kandidaat. Alleen het gebeurtenisprotocol is aangepast aan de native editor.
Dienstwisselingen worden in beide meetreeksen via dezelfde sessieselectie
geïnjecteerd; de echte editorcallback heeft afzonderlijke regressietests.
Programma is gesimuleerd; exports en SQLite staan uitsluitend in tijdelijke
mappen. AppTest/cProfile meten Python/server plus testdispatch, geen browserpaint,
echt bronverkeer of netwerk. Medianen, Python 3.11 / Streamlit 1.64.0 op deze Mac:

| Actie / fase | Totale AppTest-tijd | Daarin planningsscherm | Daarin kandidaatberekening |
| --- | ---: | ---: | ---: |
| Dienstkeuze vóór | 5340 ms | 5227 ms | 183 ms |
| Dienstkeuze na | 297 ms | 246 ms | 181 ms |
| Kandidaatkeuze vóór | 4168 ms | 4069 ms | 181 ms |
| Kandidaatkeuze na | 289 ms | 244 ms | 180 ms |

Dit is circa **94%** minder totale tijd voor dienstkeuze en **93%** voor
kandidaatkeuze in deze testopzet. De resterende grootste gemeten post is de
bestaande kandidaat-/taakplicht-/urenberekening (circa 180 ms), die voor iedere
selectie opnieuw controleert. Per actie nog steeds 0 CSV-herlezingen, 0 Programma-
aanvragen en één schema-initialisatie/validatie van circa 3 ms. Geen extra
optimalisatie van beleid, urenberekening of database uitgevoerd.

### Regressiebescherming en gewijzigde bestanden

- `streamlit_app.py`: native dienstselectie, compacter formaat, ondersteunde
  pin/alignment/breedte-opties en één kandidaat-editor/detailformulier.
- `tests/test_planning_tables_performance_v05.py`: eerste keuze, directe wissel,
  maximaal één, nieuwe kandidaatcontext, geen tijdelijke schrijfoperatie,
  kolomconfiguratie, oudere signatures, 250 kandidaten, gewijzigde rijvolgorde
  en juiste persoon in het gedeelde uitzonderingsformulier.
- `tests/ui_table_events.py`, `tests/conftest.py`: synthetische editor-events en
  het native JSON-stateprotocol. AppTest ondersteunt nog geen eigen editor-edit-
  helper en stuurt editorstate anders niet mee bij een volgende knopactie;
  tests modelleren hier de browser, zonder productiecode daarvoor te wijzigen.
- Bestaande kandidaatcontext-, planningacceptatie-, werkvoorraad- en tabelhoogte-
  tests gebruiken de nieuwe native tabel in plaats van individuele widgets.
  Goedkeuring, capaciteit, undo en bronfouten blijven inhoudelijk getoetst.
- Meetinstrument en documentatie: reproduceerbare vergelijking en actuele bediening.

Historische C/W/I/R-cases, backend, CSV-broncontracten, Programma API, No-Shows en
schema blijven ongewijzigd. De werkelijke CKC-exports/database zijn niet gelezen
of veranderd. Bestaande wijzigingen in de oorspronkelijke checkout zijn behouden.

### Lokale heracceptatie

1. Start de bestaande PR-checkout met de gebruikelijke lokale omgeving en kies
   Ledendienst Planning. Hervat de bedoelde sessie/periode en gevalideerde bron.
2. Kies een dienst in de tabel en klik daarna direct een andere aan: alleen de
   tweede blijft gekozen en de kandidaten horen direct bij die dienst.
3. Controleer bij horizontaal scrollen dat Kies links blijft staan (runtime 1.64),
   de numerieke waarden leesbaar zijn en volledige kolomkoppen via tooltip
   bereikbaar blijven. Controleer brede én smalle vensters.
4. Controleer volledige Sportlink-namen via dubbelklik, de 32 px rijen en de
   ongewijzigde bezetting/bronstatussen.
5. Selecteer meerdere kandidaten, ook een lage rang; controleer snellere respons.
   Open Kandidaattoelichting en uitzondering en kies verschillende personen.
   Een selectie alleen mag geen tijdelijke indeling maken. Boven capaciteit
   blijft bevestigen geblokkeerd; goedkeuren en undo volgen de bestaande regels.
6. Vernieuw bronnen/wissel periode en controleer dat oude kandidaatkeuzes niet
   kunnen worden bevestigd. Beoordeel de lokale gebruikssnelheid afzonderlijk.

PR #44 blijft open en ongemerged; technische tests zijn geen functionele acceptatie.


Technische eindverificatie bij deze vervolgstap: **93 gerichte tests geslaagd**,
**1124 volledige regressietests geslaagd** (7 nieuwe gevallen), syntax- en
`git diff --check` geslaagd. CI wordt na push op dezelfde PR gecontroleerd en
in de oplevering gemeld. Geen bestaande failures overgebleven; tijdens aanpassing
gevonden testadapterproblemen zijn opgelost en alle tests opnieuw uitgevoerd.


## Praktijkvervolg: selectie, scrollpositie en vertraging (25 oktober 2026)

Vertrekpunt `62da673`, bestaande branch `codex/actuele-kandidaatcontext`,
PR #44 naar `prototype-v0.5` / `5958b982`. Geen nieuwe PR of merge. De opdrachtgever
accepteert tabelopmaak, volledig kandidatenaanbod en goedkeuren/undo inhoudelijk;
de snelheid en het aanvankelijk als dubbele klik gemelde gedrag waren niet geaccepteerd.

### A — Vaststelling en gerichte correctie

**Lokale verduidelijking door opdrachtgever tijdens deze iteratie:** tweemaal
selecteren reproduceert niet meer. De feitelijke selectie lukt, maar de tabel
springt omhoog zodat de geselecteerde dienst uit beeld verdwijnt. Een afzonderlijke
fout die de eerste keuze inhoudelijk negeert is niet bewezen en wordt niet als
opgeloste oorzaak gepresenteerd.

**Vastgesteld in code:** `_select_service` verhoogde bij iedere keuze
`services-table-revision`; de editor kreeg steeds een nieuwe key en werd vervangen.
Daarmee verdween ook de eigen scrollpositie. De oude benchmark injecteerde een
sessiekeuze rechtstreeks en doorliep deze callback niet; hij kon dat niet bewijzen.

**Correctie op de geteste runtime 1.64.0:** dezelfde `st.data_editor` houdt nu een
stabiele key zolang dezelfde geordende diensten worden getoond. Alleen Kies
gebruikt een ondersteunde native `ButtonColumn`: een leeg/aangevinkt vakje is een
rijactie, geen op te stapelen celbewerking. De callback kiest één dienst of heft
een klik op de reeds gekozen dienst op. Er is geen tabelreset nodig. Kies blijft
55 px en vastgezet; alle overige kolommen, breedtes, uitlijning, tooltips,
volledige Sportlink-namen en 32 px rijhoogte blijven behouden. Geen externe grid,
JavaScript, nieuwe selectie buiten de tabel of functionele beslislogica toegevoegd.
De gewijzigde klikweergave moet lokaal nog worden beoordeeld.

Oudere runtimes zonder ButtonColumn behouden de bestaande checkboxfallback;
behoud van scrollpositie is daarvoor niet geclaimd. De eerder vastgestelde
onvolledige 1.40-compatibiliteit wordt niet uitgebreid tot een dependencyproject.
Gebruik Streamlit 1.64.0 voor de heracceptatie.

**Browserverificatie:** met een echte lokale Streamlit-server en de Codex-browser
naar de diensten onderaan gescrold, gekozen en gewisseld: de betreffende rijen
bleven zichtbaar. Kandidaatselectie, bevestigen en een browserreload zijn eveneens
uitgevoerd; na reload werkt een nieuwe keuze direct. De testserver gebruikt alleen
synthetische CSV-bytes, een gesimuleerd programma en tijdelijke SQLite. De echte
CKC-exportmap en database zijn door dit onderzoek niet geopend.

### B/C — Aangetoonde schaalbaarheidsoorzaak en herstel

De kleine eerdere benchmark bevatte uitsluitend 250 volwassenen zonder functies.
Die blijft een vergelijkingspunt, geen verklaring voor de CKC-praktijk. Aanvullend
zijn 1500 synthetische leden gebruikt, een derde minderjarig en een zesde met een
functie. Geen werkelijke CKC-populatie of persoonsgegevens gereconstrueerd.

**Vastgesteld:** `compare_required_hours` scande per persoon opnieuw uren,
meldingen en alle provenance. De taakplichtafleiding herberekende miljoenen keren
hetzelfde genormaliseerde adres en zocht minderjarigen ook tussen personen van
andere bekende huishoudens. Bronbewijs werd per persoon weer uit de volledige
bronverzameling gefilterd. Dit werk herhaalde bij iedere selectie.

**Herstel:** uitsluitend per-aanroep-lookup-tabellen voor bestaande adressen,
uren, meldingen, teams en provenance; onbekende adressen blijven expliciet in de
bestaande mogelijke-gezinsvergelijking. Dezelfde gronden, onzekerheden, supporting
personen en bronvolgorde blijven behouden. Er is geen cache tussen schermacties,
nieuwe vrijstellingsregel of wijziging van kandidaatselectie/prioritering. Voor
12, 100 en 250 gemengde synthetische referentieleden zijn de volledige controles
voor/na exact vergeleken, inclusief gronden, meldingen en bronfeiten. De bestaande
beleids- en urenregressies blijven ongewijzigd.

**Reruns:** dienstwisseling en kandidaatselectie ieder één scriptpoging.
Bevestiging gebruikt twee: de bestaande berekening en atomische goedkeuring,
gevolgd door de expliciete `st.rerun()` voor de bijgewerkte werkvoorraad. Dit is
geen verborgen CSV/API-verversing. De oude profiler sloeg de vóór die rerun
onderbroken scriptpoging niet op; het uitgebreide meetinstrument doet dat wel.
De bevestigingsroute is inhoudelijk niet herschreven.

### Meetresultaten en meetgrenzen

Zelfde Mac, Python 3.11, Streamlit 1.64.0, drie herhalingen per actie, dezelfde
synthetische populatie per vergelijking. Baselinecode is bevroren uit `62da673`,
zonder database/exports te kopiëren. Vergelijkingsreeksen voor selectie zijn
herhaald zonder parallelle tests; de resterende acties zijn eveneens zonder
parallelle regressietests gemeten. De oude directe sessie-injectie blijft via
`--legacy-selection` beschikbaar; standaard gebruikt de benchmark nu native events.

| Populatie / handeling | Totale AppTest-tijd vóór → na | Kandidaatberekening vóór → na | Scriptpogingen |
| --- | ---: | ---: | ---: |
| 250 volwassenen / dienst | 312 → 144 ms | 182 → 15 ms | 1 |
| 250 volwassenen / kandidaat | 309 → 143 ms | 182 → 15 ms | 1 |
| 250 volwassenen / bevestigen | 588 → 252 ms | 366 → 31 ms | 2 |
| 1500 gemengd / dienst | 14171 → 2548 ms | 14033 → 2411 ms | 1 |
| 1500 gemengd / kandidaat | 14512 → 2637 ms | 14330 → 2494 ms | 1 |
| 1500 gemengd / bevestigen | 28686 → 5204 ms | 28454 → 4983 ms | 2 |

Bij 1500 gemengde leden komt dit neer op circa 82% minder totale profieltijd.
Tijdens deze acties: **0 CSV-herlezingen, 0 Programma-aanvragen**; normalisatie
wordt niet opnieuw gestart. SQLite execute-tijd circa 4–5 ms per selectie en
9 ms per bevestiging; schema-validatie circa 3 ms per scriptpoging. De feitelijke
`approve_many` duurt circa 3 ms. De twee editors samen kosten circa 6 ms per
scriptpoging en de overige native datatables circa 3 ms. Deze cumulatieve
functietijden kunnen genest zijn en worden niet als onafhankelijke posten opgeteld.
De resterende grootste post is taakplicht-/urenafleiding en haar bronbewijs,
vooral bij veel functies/ondersteunende personen; die wordt bewust vers beoordeeld.

Dit zijn **Python/AppTest/cProfile-tijden inclusief profiler-overhead**, geen
volledige browserresponstijden. In de aparte browserproef met 250 personen werd
klik tot bijgewerkte eindmarker gemeten: dienst vóór circa 0,47–0,56 s en na
circa 0,29–0,46 s; kandidaat circa 0,46 → 0,36 s; bevestiging circa 0,54 → 0,34 s.
Dit zijn beperkte rookproeven inclusief browserbediening/meetoverhead, geen
statistisch browserbenchmarkresultaat. Scrollgedrag is visueel gecontroleerd.
De initiële browserverbinding/navigatie valt buiten deze actietijden.

**Niet bewezen:** de precieze 20 seconden op de ongelezen echte CKC-bronnen.
Wel bewezen: een omvang-/samenstellingsafhankelijk rekenprobleem en een grote
verbetering bij dezelfde synthetische werkbelasting. Lokale heracceptatie blijft
nodig; bronomvang, browser of lokale I/O worden niet zonder meting als schuldige aangewezen.

### Reproduceren en lokale Mac-diagnose

Vanuit de juiste PR-checkout, `code/Prototype`, met de bestaande omgeving:

```bash
python -B tests/measure_planning_actions.py --members 250
python -B tests/measure_planning_actions.py --members 1500 --mixed
python -B tests/serve_synthetic_planning.py --members 1500 --mixed --port 8531
```

De laatste opdracht start een lokale server op `127.0.0.1:8531`; bronnen/API en
SQLite blijven synthetisch. De getoonde tijdelijke map bevat `browser-runs.jsonl`:
één record per scriptpoging, ook voor de onderbroken bevestigingspoging. De caption
geeft de afgeronde run. Stop met Ctrl-C; de tijdelijke proefmap wordt opgeruimd.
De benchmark kan met `DVK_BENCHMARK_ROOT` en de browserproef met `--root` naar een
aparte code-only baseline wijzen. De standaardroute leest nooit de echte exports.

Alleen als een vertraging in de normale lokale app nader moet worden onderzocht:

```bash
DVK_PLANNING_PROFILE=1 python -m streamlit run streamlit_app.py
python -c 'from dvk.planning_diagnostics import output_path; print(output_path())'
```

De tweede opdracht toont de lokale tijdelijke locatie van
`dvk-planning-profile.jsonl`. De profiler staat zonder de vlag volledig uit.
Hij schrijft alleen tijden, aantallen, anonieme proces-runvolgorde, UTC-starttijd,
herkenbare fasecodes en voltooid/rerun/fout; geen argumenten, namen, relatienummers,
bronwaarden, credentials, volledige bestandspaden of exceptioninhoud. Nieuwe logs
krijgen lokale bestandsrechten 0600. Niets wordt geüpload. cProfile voegt overhead
toe; meet de ervaren respons daarnaast met de profiler uit.

Voer één actie tegelijk uit en noteer het tijdstip: dienst kiezen, kandidaat
selecteren/deselecteren en bevestigen. Fasen onderscheiden CSV lezen/normaliseren,
broncontext, kandidaat-/urenberekening, database, tabelopbouw en state-operaties;
`self_ms` groepeert niet-overlappende eigen functietijd. Cumulatieve fasetijden zijn
genest en mogen niet bij elkaar worden opgeteld. Twee opeenvolgende records rond
een bevestiging zijn verwacht. Stop de app na de diagnose en start opnieuw zonder
vlag. De profiler wijzigt geen gegevens; normale expliciete bevestiging/undo houden
hun bestaande gevolgen. Deel uitsluitend de timingrecords als nadere diagnose nodig is.

### Tests, gewijzigde onderdelen en heracceptatie

- `streamlit_app.py`: stabiele Kies-rijactie en optionele meetgrens, overige layout
  en publieke applicatieservices behouden.
- `dvk/member_duty.py`, `dvk/hours_control.py`: dezelfde afleiding met tijdelijke
  lookup-tabellen, originele bronvolgorde en eigen uren-/meldingsscope.
- `dvk/planning_diagnostics.py`: standaard uitgeschakelde lokale profiler.
- `tests/measure_planning_actions.py`, `tests/serve_synthetic_planning.py`:
  reproduceerbare drie-actieroute, alle scriptpogingen en echte browserproef.
- `tests/test_planning_selection_events_v05.py`, `test_planning_lookup_regression_v05.py`,
  `test_planning_diagnostics_v05.py`, `test_planning_browser_harness_v05.py`:
  10 nieuwe regressiegevallen; herhaald kiezen, na kandidaatkeuze/goedkeuring/undo,
  bronbewijs/actualiteit, privacy/exceptiongedrag en veilige browserproef.
- `tests/ui_table_events.py`, `test_planning_tables_performance_v05.py`,
  `test_planning_ui_names_v05.py`: native rijactieprotocol en bijpassende verwachtingen.
- Dit verslag en Prototype-README: actuele bediening, meetgrenzen en instructies.

**210 gerichte gevallen geslaagd (209 in de gerichte suite plus één aanvullende
UI-case); 1134 volledige regressietests geslaagd.**
De aanvullende UI-case selecteert twee kandidaten binnen capaciteit, bevestigt
beide atomair en controleert dat undo daarna precies één indeling verwijdert.
Geen bestaande failures overgebleven. Syntax- en diffcontrole volgen vóór commit;
CI wordt op dezelfde PR gecontroleerd. No-Shows, synchronisatie, broninvoer,
prioritering, capaciteit en atomische goedkeuring zijn functioneel ongewijzigd;
geen migratie of werkelijke database-/exportwijziging. De twee bestaande lokale
wijzigingen in de oorspronkelijke checkout blijven behouden.

Lokale heracceptatie met Streamlit 1.64.0, eerst zonder profiler:

1. Start de bijgewerkte bestaande PR-checkout en hervat de bedoelde planning.
2. Scroll binnen Diensten omlaag; kies een dienst en daarna rechtstreeks een
   andere. Alleen de laatste is aangevinkt; rij en kandidaatcontext blijven passend
   zichtbaar. Controleer ook horizontaal scrollen en de vaste Kies-kolom.
3. Selecteer/deselecteer kandidaten, selecteer meerdere binnen capaciteit,
   bevestig en maak ongedaan. Controleer bezetting en bronmeldingen.
4. Herlaad de pagina, hervat waar nodig en kies opnieuw. Bestaande duurzame
   planning blijft volgens de bestaande regels behouden; een keuze is geen indeling.
5. Beoordeel alle drie responstijden. Gebruik bij resterende hinder de optionele
   timingdiagnose hierboven; een groene CI is geen lokale functionele acceptatie.

PR #44 blijft open en ongemerged. De opdrachtgever accepteert deze correctie afzonderlijk.
