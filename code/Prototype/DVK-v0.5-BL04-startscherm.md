# BL-04 — Startscherm en modulenavigatie

## Context en herleiding

- Integratiebaseline: `prototype-v0.5` op `3a436fbcd2a47ca9653ae2e858ea233c7642539e` (actueel opgehaald bij start).
- Werkbranch: `codex/bl04-startscherm-navigatie`; PR-doel: `prototype-v0.5`. Geen merge door Codex.
- Vastgesteld: `main` blijft de geaccepteerde v0.4-releasebaseline. De herijkte Ledendienstenbaseline van 2 oktober en Stap 2 ronde 4/BL-02 zijn functioneel geaccepteerd; integrale v0.5-acceptatie en aparte API-acceptaties staan open (BACKLOG en prototypeplanning).
- Geaccepteerde eis: F-01–F-08 uit `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md`, nader afgebakend door de BL-04-opdracht: drie hoofdgroepen, afzonderlijke toegang tot planning en taakplichtcontrole, externe Rooster Generator en vijf niet beschikbare toekomstige modules. Taakplichtcontrole blijft inhoudelijk een functie binnen Ledendienst Planning (F-04), geen nieuwe hoofdmodule.
- Bronhouders: Sportlink voor bronfeiten, CKC voor beleid en menselijke besluiten. `DVK-BRONCONTRACTEN-v0.5.md` is expliciet een reconstructieconcept; deze wijziging maakt daarvan geen nieuw importcontract.
- Gegevensstatus: uitsluitend tijdelijke synthetische testbestanden/databases; geaccepteerde casefamilies en regressiefixtures blijven ongewijzigd. Geen migratie of reconstructie.

## Concrete afwijking en minimale oplossing

Vastgesteld in de beginsituatie: `streamlit_app.py` rendert planning en taakplichtcontrole direct achter elkaar; daardoor start SQLite-initialisatie ook wanneer de gebruiker uitsluitend CSV-controle nodig heeft. Er is geen startscherm of moduleoverzicht.

De bestaande ingang blijft behouden. Kleine renderfuncties en navigatieknoppen in de zijbalk selecteren precies één scherm. Het standaard startscherm en taakplichtcontrole initialiseren geen database en roepen geen Sportlink-client aan. De bestaande foutgrens voor bekende SQLite-opslag-/schemafouten blijft beperkt tot planning; programmeerfouten worden niet verborgen. De domeinlogica, importverwerking en planningsacties zijn niet gewijzigd.

Dit is proportioneel voor het prototype: de bewezen afhankelijkheid wordt vermeden door schermselectie, zonder nieuw portaalframework, opslaglaag of productievoorzieningen. De vijf toekomstige modules hebben uitgeschakelde knoppen en geen render-/actiepad. Rooster Generator krijgt alleen een externe statusvermelding; er is geen geverifieerde URL toegevoegd.

## Initialisatie, sessie- en widgetstatus

- Alleen openen van planning gebruikt de bestaande `SQLiteDatabase.initialize()`. Een ontbrekende planningsdatabase kan daar volgens bestaand gedrag worden aangemaakt; BL-04 wijzigt die initialisatie niet. Startscherm/taakplichtcontrole maken geen database aan. Herhaald navigeren met een reeds geïnitialiseerde database laat de bytes ongewijzigd in de regressietest.
- Navigatiecallbacks wijzigen uitsluitend de schermkeuze in sessiestatus. Bestaande bevestigings-, sync-, undo- en no-showacties blijven achter hun bestaande expliciete bediening.
- De eenvoudige widgetwaarden voor planningsmodus, begindatum, einddatum, controlepeildatum, seizoen en controlefilter worden binnen dezelfde Streamlit-sessie tegen widgetcleanup beschermd. De bestaande validatie en datumgrenzen blijven gelden; gewijzigde widgetgrenzen kunnen Streamlit aanleiding geven een datumwidget opnieuw te initialiseren.
- Uploadwidgets en actiegebonden widgets worden niet kunstmatig bewaard. Bij schermwisselingen kunnen selecties, formulieren, toelichtingen en uploads vervallen. Dit voorkomt hergebruik van gedeeltelijk ingevulde acties. Bestaande niet-widget sessiestatus en databasefeiten volgen hun bestaande levensduur.
- Getest met Streamlit AppTest en vijf synthetische uploads: een gewone filterheruitvoering behoudt de uploads, verlaten van taakplichtcontrole en terugkeer levert vijf lege uploadwidgets op. De UI vraagt dan opnieuw alle vijf bestanden te selecteren. Geen claim van uploadbehoud bij schermwisseling of na een nieuwe sessie.
- Nog niet afzonderlijk beproefd: visuele browseracceptatie en browserherverbinding. Lokale acceptatie hieronder blijft nodig; technische regressie is geen functionele acceptatie.

## Gewijzigde bestanden en regressiebescherming

| Bestand | Reden |
| --- | --- |
| `streamlit_app.py` | Startscherm, gegroepeerde navigatie, afzonderlijke taakplicht-renderfunctie, begrensde widgetretentie en uploadtoelichting |
| `tests/test_navigation_v05.py` | Default, status van modules, juiste inhoud, navigatierondgang zonder databasewijzigingen, scalar- en uploadlevensduur |
| `tests/test_dashboard_database_isolation_v05.py` | Planning expliciet openen; na databasefout via echte navigatie naar werkende controle; bestaande database- en foutgrenscontroles behouden |
| `tests/test_duty_control_dashboard_v05.py` | Bestaande dashboardtest expliciet op controlescherm starten |
| `tests/test_duty_population_dashboard_v05.py` | Bestaande populatie-/seizoentests expliciet op controlescherm starten |
| `tests/test_family_diagnostics_dashboard_v05.py` | Bestaande bron-/gezinsdiagnose expliciet op controlescherm starten |
| `tests/test_gate10ade_ui_v05.py` | Bestaande no-showactietests expliciet op planningsscherm starten |
| `tests/test_planning_workqueue_v05.py` | Bestaande bevestiging-/undo-/herlaadtests via navigatie naar planning |
| Dit document | Herleiding, ontwerpkeuzes, beperkingen en lokale acceptatie |

## Lokale acceptatie

Start vanuit `code/Prototype`:

```sh
.venv/bin/python -m streamlit run streamlit_app.py
```

1. Open een nieuwe sessie: welkom en drie hoofdgroepen staan klaar; planning draait nog niet.
2. Open Ledendienst Planning: periode, diensten, kandidaten en bestaande werkvoorraad zijn bereikbaar. Keer terug via Startscherm.
3. Open Taakplichtcontrole: geen planning/no-showinhoud; laad uitsluitend synthetische exports. Controleer peildatum, seizoen en filter.
4. Wissel filter: controle blijft zichtbaar. Ga naar Startscherm en terug: peildatum/seizoen/filter blijven behouden, bestanden moeten opnieuw worden geselecteerd.
5. Controleer vijf uitgeschakelde toekomstknoppen en de externe, niet geïntegreerde status van Rooster Generator.
6. Bevestig dat alleen expliciete planningsacties werkvoorraad wijzigen. Gebruik voor handmatige proef een wegwerpbare synthetische database; beschadig geen lokale operationele gegevens. Databasefoutisolatie wordt geautomatiseerd op tijdelijke databases getest.

Geen functioneel of architecturaal beslispunt vastgesteld binnen BL-04. Andere backlogpunten en productievoorzieningen blijven buiten scope.

## Verificatieresultaat

- Bestaande gerichte uitgangscontrole: 57 geslaagd.
- Na schermisolatie: 103 dashboard-/database-/no-showtests geslaagd.
- Definitieve gerichte BL-04/database-/werkvoorraadcontrole: 28 geslaagd (inclusief vier nieuwe navigatietests en echte synthetische uploadinteracties in AppTest).
- Volledige regressie na alle code- en testaanpassingen: **634 geslaagd**, geen skips (Python 3.11, lokale venv).
- `git diff --check`: geslaagd.
- Tussentijdse fouten zijn opgelost: tests met oude aanname van direct zichtbare planning/controle kregen een expliciete schermkeuze; twee eerste navigatieasserties zijn gecorrigeerd omdat AppTest uitgeschakelde knoppen terecht weigert en planning zelf een bestaande, afzonderlijke CSV-upload voor persoonskoppeling heeft. Geen domeinverwachtingen versoepeld.
- CI-status en commit staan in de PR/oplevering; functionele browseracceptatie blijft bij opdrachtgever.
