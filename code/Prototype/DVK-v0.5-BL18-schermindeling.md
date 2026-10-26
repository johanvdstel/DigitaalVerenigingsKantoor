# BL-18 — Schermindeling Ledendienst Planning

Datum: 26 oktober 2026. Baseline: `prototype-v0.5` / `d1a62232ece0fefc67b1d8fab78451816e925f17`
(inclusief gemergede PR #44 en #45). Werkbranch: `codex/bl18-schermindeling`.
Status: geïmplementeerd voor afzonderlijke lokale UI-acceptatie; geen functionele acceptatie of merge.
`main` blijft de geaccepteerde v0.4-releasebaseline; v0.5 is nog niet integraal geaccepteerd.

## Inventarisatie en verplaatsing

| Bestaand onderdeel | Nieuwe sectie / presentatie |
| --- | --- |
| Sessiehervatting, nieuwe planning, periodekeuze en bevestigingswaarschuwingen | 1 — Instellingen; direct zichtbaar |
| Seizoen van Overzicht per periode (operationele modus) | 1 — Instellingen; direct zichtbaar |
| Gegevensmodus, lokale exportlocatie, bronvernieuwing, kandidaatbronstatus en bronmeldingen | 2 — Databronnen; meldingsdetails ingeklapt, belangrijke samenvattingen zichtbaar |
| Bronstatus en actualiteit | 2 — Databronnen; bestaande tabel in compacte expander |
| Datakwaliteit | 2 — Databronnen; signalen direct zichtbaar |
| Sportlink-ophalen, vervangingsbevestiging, resultaat, bronperiode, aantallen en taakcodestatus | 3 — Diensten; bestaande ophaalexpander en zichtbare statusinformatie |
| Feitelijke Sportlink-inroosteringen en administratieve naamdetails | 3 — Diensten; bestaande detail-expanders |
| Periode, dienstenstatistieken en dienstentabel met Kies-rijactie | 3 — Diensten; tabelinstellingen en selectiecode ongewijzigd |
| Kandidaten, toelichting/uitzondering en menselijke bevestiging | 4 — Kandidaten |
| Actieve tijdelijke DVK-inroosteringen en undo | 4 — Kandidaten; eigen kop, scheidingslijn en toelichting, onder de voorstellen |
| Bestaande No-showregistratie en intrekking | 4 — Kandidaten; afzonderlijk onderdeel na de tijdelijke planning, alle controles behouden |
| Wedstrijdoverzicht | 5 — Wedstrijden; tabel in standaard ingeklapte expander |

## Minimale technische ingreep en invarianten

Uitsluitend `streamlit_app.py` verandert applicatiepresentatie. Vijf vaste
Streamlit-containers bepalen de zichtbare volgorde. Twee vaste subcontainers
plaatsen Sportlink-bediening vóór de statistieken/dienstentabel. Bestaande
uitvoeringsvolgorde blijft behouden, inclusief bronvernieuwing/rerun en het
gebruik van tijdelijke indelingen bij de synchronisatiebevestiging. Geen extra
bronaanroepen, kandidaatberekeningen, applicatieservices of opslagstructuren.
De seizoenwidget blijft in dezelfde operationele conditie en gebruikt dezelfde key.

De Kies-rijactie, callback, table key, kolombreedtes, vaste rijhoogte en native
editor blijven ongewijzigd. Binnen deze nieuwe indeling blijft de widgetidentiteit
stabiel tijdens dienstwisselingen, kandidaatkeuze en bevestiging/undo. De eenmalige
wisseling naar deze versie verplaatst UI-elementen; een eerder opgeslagen
browser-scrollpositie van de oude versie wordt niet gemigreerd.

Bronfeiten/provenance, capaciteitsregels, prioritering, sessiehervatting,
bevestigen/undo, No-shows, database en beide read-only Sportlink-ketens blijven
ongewijzigd. Historische C/W/I/R-cases en broncontracten zijn niet aangepast.
De broncontractreconstructie blijft concept waar die niet afzonderlijk is
geaccepteerd; BL-18 neemt daarover geen nieuw besluit.

Testtabellen worden via hun bestaande widgetkey gevonden: door de gewenste
presentatievolgorde is de dienstentabel niet meer de eerste dataframe op het
scherm. Alleen de oude UI-volgordeverwachtingen worden aan BL-18 aangepast;
inhoudelijke verwachtingen blijven behouden.

## Verificatie

**29 gerichte UI-tests geslaagd; volledige regressiesuite: 1138 geslaagd.**
Vier nieuwe BL-18-gevallen toetsen sectievolgorde/plaatsing, zichtbare
bronsamenvatting bij ingeklapte details, directe kandidaatcontext met stabiele
widgetidentiteit en de ingeklapte wedstrijdtabel. Bestaande UI-tests toetsen
tevens bevestigen, deselecteren, undo, herladen, bronfouten en No-showintrekking.
Syntaxcontrole en `git diff --check` slagen.

Browserproef op localhost met 250 synthetische personen en Streamlit 1.64.0:
instellingen direct zichtbaar; vijf secties in volgorde; na scrollen naar zondag
blijven keuze en wisseling naar de volgende dienst in beeld. De Kies-kolom blijft
bij horizontaal scrollen bereikbaar. Wedstrijden staat standaard ingeklapt.
AppTest verifieert de inhoudelijke controles; deze browserproef verifieert de
visuele scrollpositie. Dit vervangt geen lokale CKC-acceptatie.

De oorspronkelijke `.venv` wachtte bij de eerste teststart op het inlezen van
macOS-bestanden met vlag `dataless`. Die run is gestopt vóór testuitvoer; de
uiteindelijke tests en beide vergelijkingsversies gebruiken dezelfde tijdelijke
Python 3.11-omgeving buiten Documenten met Streamlit 1.64.0. De bestaande
omgeving is niet aangepast.

Timingproef: bestaand `tests/measure_planning_actions.py`, baseline-app uit
`d1a6223` tegenover de BL-18-app, dezelfde ongewijzigde domeincode en runtime;
mediaan van drie volledige AppTest-acties met cProfile, inclusief reruns.
Geen gelijktijdige regressietestbelasting. Het betreft server/script-tijd,
geen browsermeting en geen verwachting voor echte CKC-bronnen.

| Populatie | Actie | Baseline → BL-18 (ms) |
| --- | --- | --- |
| 250 volwassenen | Dienst kiezen | 86 → 88 |
| 250 volwassenen | Kandidaat kiezen | 85 → 86 |
| 250 volwassenen | Bevestigen | 164 → 168 |
| 1500 gemengd | Dienst kiezen | 2659 → 2539 |
| 1500 gemengd | Kandidaat kiezen | 2585 → 2571 |
| 1500 gemengd | Bevestigen | 5232 → 5083 |

Er worden tijdens deze selecties/bevestigingen geen CSV-bestanden opnieuw gelezen
of Programma-aanvragen uitgevoerd. Bevestigen houdt dezelfde twee scriptpogingen;
selectie één. Deze kleine UI-ingreep introduceert geen nieuwe berekeningsroute.
De exacte praktijkresponstijd en schermwaardering blijven lokale acceptatiepunten.
De eerste overlappende 1500-personenmetingen zijn niet gebruikt; bovenstaande
vergelijking is daarna volledig sequentieel herhaald.

## Gewijzigde bestanden en reden

- `streamlit_app.py`: vaste presentatiecontainers, sectiekoppen en scheiding
  voorstellen/tijdelijke indelingen; wedstrijd- en bronstatusexpanders.
- `tests/test_planning_sections_bl18.py`: vier gerichte synthetische UI-regressies.
- `tests/test_navigation_v05.py`, `tests/test_planning_ui_names_v05.py`:
  expliciete oude presentatievolgorde aangepast aan het geaccepteerde BL-18-besluit;
  No-show- en broncontroles inhoudelijk behouden.
- `tests/test_candidate_context_ui_v05.py`, `tests/test_planning_runtime_v05.py`,
  `tests/test_planning_workqueue_v05.py`, `tests/test_volunteer_planning_integration_v05.py`,
  `tests/measure_planning_actions.py`: dienstentabel op widgetkey zoeken in plaats
  van op de oude positie als eerste dataframe; functionele verwachtingen ongewijzigd.
- `BACKLOG.md`, `DVK-PROTOTYPE-PLANNING.md`, dit verslag: uitvoering traceerbaar
  gemaakt; lokale UI-acceptatie blijft expliciet open.

Geen functionele afwijkingen van de opdracht. De bestaande No-showbediening is
behouden als afzonderlijk onderdeel onder Kandidaten, zodat geen bestaande
functionaliteit verdwijnt en er precies vijf hoofdsecties zijn. Geen migratie,
beleidswijziging of wijziging in publieke applicatieservices.
CI-status en commit staan in de afzonderlijke PR; niet zelfstandig mergen.

Uitsluitend synthetische exports, HTTP-stubs en tijdelijke SQLite-databases.
Geen echte CKC-bestanden of operationele database gelezen of gewijzigd.

## Lokale functionele acceptatie op macOS

1. Gebruik de nieuwe PR-branch met Streamlit 1.64.0, de bijbehorende bestaande
   lokale configuratie en de bedoelde lokale database. Verplaats, kopieer of reset
   geen database voor deze schermtest. Start vanuit `code/Prototype`:
   `python -m streamlit run streamlit_app.py`.
2. Open Ledendienst Planning en hervat zo nodig de bedoelde sessie. Controleer
   de vijf genummerde secties in volgorde. Periode en seizoen zijn direct zichtbaar
   onder Instellingen; de seizoenwidget hoort zoals voorheen bij operationele gegevens.
3. Controleer Databronnen: vernieuw bewust de CSV/Programma-context. Belangrijke
   bronwaarschuwingen blijven zichtbaar; open de details om afzonderlijke bronregels
   en herkomst te bekijken. Controleer de bestaande datakwaliteitsmeldingen.
4. Controleer onder Diensten de Sportlink-bronperiode en aantallen. Haal alleen
   opnieuw op wanneer dat gewenst is; bevestig bronvervanging uitsluitend wanneer
   tijdelijke indelingen mogen vervallen. Controleer de bestaande succes/foutmelding.
5. Scroll binnen de dienstentabel naar een late rij. Kies en wissel van dienst:
   laatste keuze blijft zichtbaar, Kies blijft bij horizontaal scrollen bereikbaar,
   en Kandidaten toont direct de context van de gekozen dienst. Vergelijk de
   ervaren reactietijd met de geaccepteerde PR #44-versie bij dezelfde bronnen.
6. Selecteer/deselecteer kandidaten; zonder bevestiging ontstaat geen indeling.
   Bevestig een bewuste keuze binnen capaciteit. Controleer het duidelijke
   onderscheid tussen voorstellen en actieve tijdelijke DVK-inroosteringen, de
   gewijzigde bezetting en undo. Controleer deselecteren van de dienst.
7. Herlaad/hervat en controleer de bestaande sessie en tijdelijke indelingen.
   No-showbediening blijft in sectie Kandidaten beschikbaar met dezelfde broncontroles;
   voer alleen een gewenste, geldige registratie/intrekking uit.
8. Wedstrijden staat standaard ingeklapt. Klap open en controleer de ongewijzigde
   tabel voor de gekozen periode. Deel uitsluitend bevindingen zonder persoonsgegevens.

CI bewijst technische regressievrijheid; CKC beslist afzonderlijk over lokale
functionele acceptatie en merge.
