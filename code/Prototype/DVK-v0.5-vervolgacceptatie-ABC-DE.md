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
