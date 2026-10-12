# DVK v0.5 — Stap 2 ronde 4: read-only taakplichtcontrole

## Context, gezag en proportionaliteit

Baselinebranch: `prototype-v0.5`, na ophalen van GitHub exact op commit `35396c354d6efed2ac6db86ee61c5604834a4334`. Werkbranch: `codex/v05-stap2-ronde4-taakplichtdashboard`. GitHub-baseline vóór wijzigingen geverifieerd met ancestrycontrole. De aanvankelijk geopende vorige werkbranch is niet als baseline gebruikt.

Ontwikkelfase: v0.5-integratie, geen integrale functionele acceptatie. De functioneel geaccepteerde v0.4-baseline en C/W/I/R-cases blijven regressiebasis. Context gecontroleerd in AGENTS.md, ontwikkelworkflow, BASELINE-v0.4, herijkte B-01–B-14-baseline en ronde-3-rapport; code en ronde-1/2/3-tests onderzocht. Sportlink is bronhouder van leden, functies, commissies, teams en geregistreerde uren; CKC bepaalt beleid, de Vrijwilligerscommissie beoordeelt verschillen.

Vastgesteld feit: de publieke brongebonden afleiding/vergelijking bestaan al; Streamlit biedt nog geen dashboard hiervoor. Geaccepteerde eis uit deze ronde: verbind uitsluitend die keten aan een lokale read-only controle, met menselijke uitleg, expliciete datum/periode, drie filters en consistente tellingen. Minimale technische toevoeging: tekststreams in de bestaande adapter, een kleine applicatie/presentergrens en een afzonderlijk Streamlit-gedeelte. Zonder tekststreams zouden uploads eerst naar schijf moeten; zonder presenter zouden technische domeincodes in de UI terechtkomen. Geen nieuwe beleidsregels, architectuurlaag voor opslag, migratie of historische reconstructie. Alleen synthetische ontwikkeltests; geaccepteerde fixtures blijven ongewijzigd.

## Gewijzigde bestanden

| Bestand | Doel |
| --- | --- |
| `dvk/real_data_import.py` | Laat dezelfde `read_rows` ook een in-memory tekststream lezen; bestaande paden en parser blijven werken. |
| `dvk/duty_control_presenter.py` | Valideert lokale uploads, geeft expliciete importcontext door, gebruikt publieke broncontrole en presenteert bestaande gronden/signalen; rijen, filters en tellingen delen dezelfde uitkomsten. |
| `streamlit_app.py` | Afzonderlijke read-only sectie met vijf uploaders, datum/periode in de zijbalk, tellingen, filters, tabel en diagnose. |
| `tests/test_duty_control_dashboard_v05.py` | 37 synthetische regressies inclusief daadwerkelijke AppTest-rendering. |
| Dit rapport | Baseline, architectuur, verificatie en overdracht. |

## Architectuur en UI

Route: vijf CSV-uploads als bytes → UTF-8-tekststreams → `SportlinkRealDataAdapter.load_exports` → `RealDataImportResult` met canonieke feiten/provenance → publieke `compare_required_hours(as_of)` → bestaande `derive_member_duties()` en vergelijking → presenter → Streamlit-tabel. Streamlit bevat geen nieuwe CKC-beleidslogica. De presenter vertaalt resultaten; hij bepaalt geen taakplicht of vrijstelling.

Onderaan de bestaande Ledendienst Planning staat **Taakplichtcontrole — read-only**. Daar selecteert de gebruiker Leden, Functies, Commissies, Teams en Overzicht per periode. Onder het afzonderlijke kopje Taakplichtcontrole in de zijbalk staan peildatum en expliciete periode/seizoenscontext. Verwerking start wanneer alle vijf bestanden en de periode aanwezig zijn; context wordt niet uit bestandsnamen geraden. Wijziging van invoer bouwt de controle opnieuw, zodat geen verouderde resultaten onder nieuwe context worden getoond.

Kolommen: Lid, DVK verwachte A, Waarom, Sportlink-A, Controlestatus en secundair Relatiecode. Namen dienen voor leesbaarheid; alle koppelingen blijven via relatiecode. Ondersteunende huishoud-/gezinsleden verschijnen met naam. Alle gronden blijven behouden; ook waarschuwingen en ERROR-signalen worden gepresenteerd. Onbekende DVK-A of niet-eenduidige geregistreerde A verschijnt als `—`. Een betrouwbare afleiding kan bij onbetrouwbare urenpositie nog zichtbaar zijn met onbetrouwbare controlestatus, conform ronde 3.

Filters: Alle, Alleen afwijkingen, Alleen niet betrouwbaar beoordeelbaar. Tellingen: totaal, overeenkomst, afwijking en niet betrouwbaar beoordeelbaar; tellingen gaan over de volledige controlepopulatie. Alle toont precies de volledige populatie die de bestaande controleketen oplevert. Afgewezen/niet-koppelbare bronregels die geen controlelid opleveren blijven zichtbaar in de bron- en controlediagnose. Geen aanvullende populatiereconstructie op naam.

Ontbrekende invoer geeft een instructie; ontbrekende kolommen, encodingfouten, ongeldige datums en onleesbare CSV-regels geven leesbare fouten. CSV-syntax en afwijkende aantallen velden worden geweigerd, niet gerepareerd. Adapter-datakwaliteitssignalen blijven behouden. Geen uploads in SQLite, bestanden op schijf, cache of permanente dashboardstate; uploads blijven in het lokale Streamlit-proces/geheugen.

## Verificatie

- Schone kopie van exacte baselinecommit: **506 passed**.
- Nieuwe dashboardtests: **37 tests**; alle geslaagd in de volledige suite.
- Gerichte suite: dashboard, ronde 1/2/3 en relevante bestaande UI-regressies; **229 passed in 1.54s**.
- Volledige eindregressie vanuit `code/Prototype`: **543 passed in 3.92s**.
- `git diff --check`: schoon.

Nieuwe dekking: drie controlestatussen, persoonlijke/huishoudvrijstelling, oudste/jongere minderjarige, onbekende functie, ontbrekende/ambigue urenpositie, alle bestaande DutyGround-codes, alle filters, gemengde tellingen, minimale vijf imports in geheugen, Teams zonder Functie, B-02 op dezelfde regel, naam versus identiteit, onbekende A, expliciete context, CSV-fouten en daadwerkelijke initiële Streamlit-rendering. Volledige suite omvat de bestaande planning-, kandidaat-, no-show- en UI-regressies.

Tijdens ontwikkeling: een nieuwe synthetische test gebruikte eerst de vervallen algemene titel Trainer en faalde terecht; de test gebruikt nu de bestaande geaccepteerde titel Assistenttrainer. Twee onbedoeld overlappende volledige aanroepen leverden een AppTest-timeout en een planningassertie op; daarna is de exacte baseline afzonderlijk groen geverifieerd. De planningassertie bleek ook in een afzonderlijke eindrun op te treden doordat de nieuwe datumkiezer in het hoofdscherm de AppTest-widgetvolgorde veranderde. De controlecontext staat nu apart in de zijbalk; bestaande code/testverwachtingen zijn niet aangepast. Daarna slaagt de volledige suite. Twee schrijfaanroepen gebruikten een dubbel relatief Prototype-pad, wijzigden niets en zijn met het juiste pad herhaald.

## Scope, risico's en overdracht

Geen Sportlink-mutaties, acceptatie-/correctie-/afhandel-/negeerknoppen, B-14-besluitopslag, productiegegevens, permanente bronopslag, kandidaatselectie- of no-showwijzigingen, teruggebrachte Teams.Functie of opportunistische refactor. Domeinregels en geaccepteerde fixtures ongewijzigd. B-02 blijft uitsluitend de bestaande adapterregel; filters gebruiken uitsluitend de bestaande controlestatus.

Geen nieuw functioneel of architecturaal besluit nodig voor de geïmplementeerde scope. De werkelijke CKC-populatie en leesbaarheid moeten nog door Johan lokaal met de vijf echte exports worden beoordeeld. Automatische regressie bewijst geen functionele acceptatie. UTF-8 blijft het bestaande adaptercontract; andere encodings worden expliciet geweigerd. Geen bronactualiteit gegokt uit bestandsmetadata.

Geen merge. Er is lokaal een oplevercommit; SHA in de eindrapportage. Geen PR geopend en geen CI-run voor deze branch beschikbaar. Lokale functionele acceptatie en review volgen afzonderlijk.
