# BL-18 — Schermindeling Ledendienst Planning

Datum: 26 oktober 2026. Baseline: `prototype-v0.5` / `d1a62232ece0fefc67b1d8fab78451816e925f17`
(inclusief gemergede PR #44 en #45). Werkbranch: `codex/bl18-schermindeling`.
Status: BL-18 lokaal functioneel geaccepteerd op 26 oktober 2026, met één laatste wijzigingsverzoek: wedstrijden standaard zichtbaar (uitgeklapt). Alleen die standaardzichtbaarheid vereist nog lokale controle; PR #46 blijft ongemerged.
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
| Wedstrijdoverzicht | 5 — Wedstrijden; tabel in standaard uitgeklapte expander |

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

## Verificatie oorspronkelijke implementatie

**29 gerichte UI-tests geslaagd; volledige regressiesuite: 1138 geslaagd.**
Vier nieuwe BL-18-gevallen toetsen sectievolgorde/plaatsing, zichtbare
bronsamenvatting bij ingeklapte details, directe kandidaatcontext met stabiele
widgetidentiteit en de standaardstand van de wedstrijdtabel. Bestaande UI-tests toetsen
tevens bevestigen, deselecteren, undo, herladen, bronfouten en No-showintrekking.
Syntaxcontrole en `git diff --check` slagen.

Browserproef op localhost met 250 synthetische personen en Streamlit 1.64.0:
instellingen direct zichtbaar; vijf secties in volgorde; na scrollen naar zondag
blijven keuze en wisseling naar de volgende dienst in beeld. De Kies-kolom blijft
bij horizontaal scrollen bereikbaar. De toen geteste versie toonde Wedstrijden standaard ingeklapt; het definitieve besluit hieronder vervangt die standaardstand.
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
Praktijkresponstijd en schermwaardering zijn inmiddels lokaal geaccepteerd; alleen de standaardzichtbaarheid van Wedstrijden staat nog open.
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

Stappen 1–7 zijn inmiddels lokaal geaccepteerd. Alleen stap 8 betreft de laatste controle.

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
8. Laatste lokale controle: open sectie 5 — Wedstrijden. De ongewijzigde tabel
   voor de gekozen periode moet direct zichtbaar zijn, zonder uitklapactie.
   De overige BL-18-onderdelen zijn al lokaal geaccepteerd.

CI bewijst technische regressievrijheid; CKC beslist afzonderlijk over lokale
functionele acceptatie en merge.

## Laatste correctie — definitief functioneel besluit (26 oktober 2026)

Vertrekpunt: `aa9dd9f`, dezelfde branch en PR #46. CKC heeft BL-18 lokaal
functioneel geaccepteerd, met het verzoek de wedstrijdtabel standaard zichtbaar
te tonen omdat deze sectie onderaan staat. Uitsluitend `expanded=True` voor
het bestaande wedstrijdoverzicht; wedstrijdgegevens, periode en overige bediening
blijven gelijk. De twee relevante UI-verwachtingen volgen dit nieuwe besluit;
bronmeldingsdetails blijven ingeklapt. Backlog en prototypeplanning zijn bijgewerkt.

De eerdere synthetische browser- en prestatiemetingen blijven historische
resultaten van de oorspronkelijke BL-18-versie, geen nieuwe metingen van deze
correctie. Alleen de standaardzichtbaarheid vereist nog lokale CKC-controle.
Verificatie van deze correctie: 4 gerichte BL-18-UI-tests geslaagd; volledige regressiesuite 1138 tests geslaagd (54,61 s). Uitsluitend synthetische bronnen en tijdelijke databases. `git diff --check` geslaagd. Geen nieuwe browser- of prestatiemeting nodig voor deze standaardstand; alleen de standaardzichtbaarheid volgt nog lokaal. CI-status en commit worden bij PR #46 gerapporteerd.
