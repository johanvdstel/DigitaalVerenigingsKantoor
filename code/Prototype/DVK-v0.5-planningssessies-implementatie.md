# PR #38 — BL-16: duurzame planningssessies

## Grondslag en uitgangssituatie

Werkbranch `codex/vrijwilligers-planning-integratie`, uitgangscommit `7f3846d2dcd92acac9299167c80f1255cf4a4063`. Geen nieuwe branch of PR. Doel blijft `prototype-v0.5`; de oorspronkelijke PR-baseline is `1399493e70bd35b356a0108e87a0ff8ec614b5af`. De aanvullende ontwerpbaseline is de gemergede PR #39, commit `129f58eeb2e9d3315b8c7dd4e97f4b3d7f97581f`. BACKLOG, prototypeplanning en het functionele sessieontwerp zijn uit die commit overgenomen. V0.4 op main blijft de geaccepteerde releasebaseline; integrale v0.5-acceptatie staat open.

Geaccepteerde eis: BL-16 en de afrondingsopdracht van CKC vervangen uitsluitend de tegenstrijdige PR #35-regel dat een procesherstart tijdelijke planning wist. Sportlink blijft bronhouder; verwerking in Sportlink blijft handmatig. De CKC-catalogus blijft onafhankelijke configuratie. Bestaande lokale prototypegegevens zijn voor deze eenmalige overgang wegwerpbaar; een conversie is niet opgedragen. Nieuwe No-Shows en intrekkingen zijn duurzame DVK-feiten.

Vastgesteld in de uitgangscode: `planning_runtime` bewaarde de periode uitsluitend in procesgeheugen en verwijderde bij eerste procesgebruik de werkvoorraad. De planning controleerde wel de exacte bronperiode, maar No-Show-selectie en -registratie misten dezelfde actieve-brongrens. Hervat- en afsluitbediening ontbraken; bronvervanging had geen voorafgaande bevestiging. Deze concrete afwijkingen bepalen de wijzigingsscope.

Hergebruikt: client, adapter, naamkoppeling, originele namen, Afgeschermd, taakgroep/positieve overlap, bezettingsberekeningen, catalogus, tijdelijke-planningsrepository, menselijke goedkeuring/undo, No-Show-feiten en sanctie-/intrekkingslogica, SQLite-transacties en schemavalidatie. Geen wijziging van kandidaatbeleid, taakplicht, Sportlink-writeback of andere backlogonderwerpen.

## Implementatie en bestanden

- `dvk/planning_session.py`: typed actieve sessie, gedeelde bron-/periodecontrole, geautoriseerde start/vervanging en afsluiting. Destructieve sessiehandelingen vereisen bevestiging plus de verwachte sessie. Schrijven gebeurt na `BEGIN IMMEDIATE`; fouten rollen terug.
- `dvk/persistence/planning_session.py`, `sqlite.py`: één sessierecord onder een vaste sleutel in de bestaande `dvk_records`-opslag, beschikbaar via de unit of work.
- `dvk/planning_runtime.py`: eerdere toegangspunten gebruiken voortaan duurzame opslag; openen/herstarten wist niets. Streamlit gebruikt rechtstreeks de geautoriseerde sessieapplicatieservice.
- `dvk/application_services.py`: synchronisatie controleert sessie, periode en vervangingsbevestiging vóór ophalen en controleert de sessie opnieuw onder de schrijflock vóór publicatie. Bookings, verwijderen tijdelijke indelingen, succes-/pogingmetadata en nieuwe bronrevisie worden gezamenlijk gecommit. Bij schrijffouten volgt rollback, ook als een aanroeper de fout opvangt. No-Show-selectie gebruikt alleen een actieve gevalideerde bron; registratie vereist dezelfde selectie-revisie en controleert opnieuw periode, identiteit en bronherkomst.
- `dvk/volunteer_planning.py`: planning gebruikt dezelfde actieve-broncontrole, met behoud van de bestaande exacte catalogustaakcodeset. Foutcategorieën en uitvraagstatus blijven beschikbaar. Een mislukte poging krijgt uitsluitend afzonderlijke pogingmetadata; actieve sessie, geslaagde bronstatus, brontijdstip, boekingen en werkvoorraad blijven intact.
- `dvk/persistence/sportlink_bookings.py`: gerichte verwijdering van actuele bronmetadata bij expliciete afsluiting/vervanging.
- `streamlit_app.py`: drie navigatiesituaties, hervatten, nieuwe planning en bevestiging van periode-/bronvervanging. Een normale rerun of terugkeer behoudt de niet-widgetgebonden hervatmarkering. Een nieuwe WebSocket-/browsersessie heeft die markering niet en vraagt hervatten. Browser-refresh kan zo'n nieuwe gebruikerssessie openen, maar verliest geen opgeslagen planning. De UI geeft de getoonde No-Show-bronrevisie mee bij bevestiging.
- Tests: `test_planning_runtime_v05.py` volgt de expliciet vervangen PR #35-regel; `test_planning_session_source_v05.py` voegt bron-/sessiegrenzen en foutinjectie toe. De bestaande planning-, identiteit-, UI-, schema-, Gate 9- en Gate 10-tests krijgen synthetische sessie-/revisieopzetten en waar nodig de hervat-/bevestigingsstap. Bestaande sanctie-, identiteit-, bezettings- en intrekkingsverwachtingen blijven gelden. Een identieke geslaagde heruitvraag heeft bewust een nieuwe bronrevisie; boekingen en overige bronmetadata blijven gelijk.

De vooraf aanwezige caption in Streamlit en de lokale wijziging in `DVK-v0.5-vrijwilligers-integratie.md` blijven behouden en buiten de commit.

## Opslag en integriteit

Het sessierecord bevat sessie-ID, begin-/einddatum en eventueel de revisie van de gevalideerde bron. De bestaande primaire sleutel van `dvk_records` dwingt maximaal één actieve sessie af. De bronmetadata bevat dezelfde sessie/revisie en de reeds bestaande status, taakcodes, bronperiode, tijdstip en administratieve aandachtspunten. Tijdelijke indelingen en hun bestaande status blijven in `temporary_planning`.

Een revisie is selectiemetadata, geen nieuwe persoons- of boekingsidentiteit; zij wordt niet als technische identificatie in normale gebruikersweergaven getoond. De gedeelde applicatiecontrole accepteert bronmetadata alleen bij overeenkomende sessie, revisie, periode en succesvolle status. No-Show-selectie filtert ook op de concrete lokale startdatum van de boeking.

Geen nieuwe tabellen, kolommen of schema-stappen: schemaversie blijft **12**. De twaalf migraties, de referentieschema-opbouw, uniciteitsregels, foreign keys en immutable triggers blijven ongewijzigd. Er is geen conversie van oude prototypegegevens of automatische reconstructie. Een oude bron zonder nieuwe sessiebinding wordt niet als actuele bron gebruikt. De reguliere initialisatie valideert het schema en bouwt een leeg bestand reproduceerbaar op.

Bronvervanging wijzigt uitsluitend actuele bron/werkvoorraad/sessiemetadata. Historische No-Shows behouden hun eigen immutable boekingssnapshot; intrekkingen verwijzen naar die duurzame feiten, niet naar de vervangbare actuele sessie. Sessiesluiting raakt die tabellen niet. De bestaande FK- en triggerbescherming blijft gelden.

## Technische verificatie

Uitsluitend synthetische data en tijdelijke SQLite-bestanden; geen echte CKC-export, echte lokale database of live API gelezen.

Gerichte run: **232 geslaagd**, 0 mislukt/overgeslagen:

```text
python -m pytest -q tests/test_planning_session_source_v05.py tests/test_planning_runtime_v05.py tests/test_planning_ui_names_v05.py tests/test_schema_validation_v05.py tests/test_no_show_sportlink_v05.py tests/test_volunteer_identity_v05.py tests/test_volunteer_planning_integration_v05.py
```

Volledige run vanuit `code/Prototype`: `python -m pytest -q`; **892 geslaagd**, 0 mislukt/overgeslagen. Lokale runtime: Python 3.11.16, Streamlit 1.64.0. CI-resultaat en definitieve commit worden bij oplevering in PR #38 gerapporteerd.

Aangetoond: lege start, duurzame periode/bron/werkvoorraad, normale navigatie/reruns, nieuwe AppTest-browsersessies inclusief hervatvraag, procesherstart via een afzonderlijk Python-proces, annuleren/bevestigen, geen bron vóór validatie, succesvolle en mislukte vervanging, gedeeltelijke API-fout, rollback bij publicatiefouten op meerdere opslagpunten, gewijzigde sessie tijdens ophalen, registratie zonder revisie, verkeerde periode en bronwijziging tussen selectie en daadwerkelijke registratie. Ook dezelfde boekingssleutel na heruitvraag is dan ongeldig voor de oude selectie. Historische feiten/intrekkingen blijven behouden; bestaande schemavalidatie-, migratie-, C/W/I/R- en overige regressies blijven groen.

Tussentijdse tests faalden door de oude wis-/hervatverwachtingen en ontbrekende sessie-/revisieopzetten. Die opzetten zijn aangepast aan BL-16. Ook een verkeerd geplaatste fixture-import in de testopzet is hersteld. De ongewijzigde domeinverwachtingen en de nieuwe, strengere foutproeven slagen in de uiteindelijke runs.

## Eenmalige lokale reset — uitsluitend later door Johan

Deze procedure is geen opdracht aan Codex om haar uit te voeren. Codex heeft niets gereset. Spreek het acceptatiemoment afzonderlijk af.

1. Stop Streamlit in de terminal met Ctrl+C en wacht tot de opdrachtprompt terug is. Sluit ook eventuele andere DVK/Streamlit-processen die dezelfde prototypeomgeving gebruiken. Voer de reset niet uit terwijl de applicatie nog draait.
2. Open in Finder precies `/Users/johanvanderstel/Documents/DigitaalVerenigingsKantoor/code/Prototype/`. Controleer dat dit de checkout is waarmee je de bijgewerkte branch start.
3. Controleer de exacte bestandsnaam **dvk_v05.sqlite**. Dit is het bestand dat Ledendienst Planning naast `streamlit_app.py` gebruikt. Pak geen ander SQLite-bestand aan.
4. Maak buiten de repository een uitsluitend lokale map met een eigen datum/tijd onder bijvoorbeeld `~/Documents/DVK-lokale-backups/`. Verplaats alleen `dvk_v05.sqlite` naar die map. Mochten na volledig stoppen nog exact `dvk_v05.sqlite-wal`, `dvk_v05.sqlite-shm` of `dvk_v05.sqlite-journal` aanwezig zijn, verplaats die samen met dit bestand naar dezelfde map. Bewaar de set bij elkaar; upload niets. Dit archiveert de oude prototypeomgeving en laat de actieve databaseplaats leeg. Geen brede zoek-/verwijderopdracht uitvoeren.
5. Laat CSV-/Excel-bronexports, `.env`, credentials, virtuele omgeving, configuratie en alle Git-bestanden ongemoeid. Die hoeven niet te worden verwijderd of opnieuw ingesteld.
6. Start vanuit dezelfde bestaande lokale omgeving in `code/Prototype` de normale opdracht: `.venv/bin/python -m streamlit run streamlit_app.py`. Gebruik de bestaande lokale credentialconfiguratie; neem geen credentials op in commandoverslagen.
7. Open Ledendienst Planning. De normale initialisatie maakt en valideert een nieuwe database. Er hoort geen hervatvraag of oude bezetting te verschijnen; de catalogus blijft zichtbaar en bronbezetting is Onbekend. Bij een databasefout stoppen en de foutcategorie melden; geen extra bestanden wissen of automatisch repareren.

Door deze eenmalige schone start ontbreken alle gegevens uit de oude prototype-database: opgeslagen imports/snapshots, runs/versierecords, voorstellen/beslissingen, tijdelijke indelingen, bronboekingen/-metadata en oude No-Show-/sanctie-/intrekkingsfeiten. Dit is uitsluitend toegestaan voor de expliciet wegwerpbare huidige prototypeomgeving. Nieuwe sessies en duurzame feiten worden bij toekomstige herstarts juist behouden. Het lokale archief is geen conversie naar het nieuwe sessiemodel.

## Lokaal acceptatieprotocol

1. Begin na de afzonderlijk afgesproken reset op deze branch. Open Ledendienst Planning, kies 19–25 oktober 2026 en klik **Start nieuwe planning**. Controleer 29 diensten en Onbekend tot succesvolle bronvalidatie; geen eerdere No-Show-keuzes.
2. Selecteer onder Databronnen de lokale Leden-CSV en synchroniseer. Controleer namen, Afgeschermd, geen namen, min/max, bezetting, overlap, taakcodetotalen, bronstatus/-tijdstip en de ongewijzigde tabelbediening (Kies, volledige read-only namen, 320 px/32 px, dubbelklik).
3. Controleer tijdelijke indelingen/undo met de bestaande afzonderlijke demonstratie. Operationele kandidaatselectie met echte leden/wedstrijden blijft de eerder bekende vervolgbeperking; deze opdracht voegt die niet toe. Noteer de werkvoorraad en periode.
4. Navigeer naar Taakplichtcontrole/Home en terug. De planning en tijdelijke indelingen blijven gelijk; geen hervatvraag tijdens dezelfde gebruikerssessie.
5. Refresh, sluit/heropen de browser, herstart Streamlit en herstart later de computer. Open telkens Ledendienst Planning. Bij een nieuwe gebruikerssessie verschijnt de bewaarde periode met **Bestaande planning hervatten / Nieuwe planning starten**. Hervatten herstelt brongegevens, bronstatus/tijdstip en de tijdelijke werkvoorraad.
6. Kies Start nieuwe planning en annuleer: alles blijft behouden. Herhaal en bevestig pas na eigen controle dat tijdelijke indelingen niet langer nodig zijn en noodzakelijke Sportlink-verwerking is afgehandeld. De oude werkvoorraad verdwijnt, de catalogus blijft beschikbaar en de nieuwe planning vereist periodekeuze en synchronisatie.
7. Test periodewisseling eerst met annuleren en daarna met bevestigen. Ook zonder tijdelijke indelingen is bevestiging verplicht. Voor de nieuwe periode blijven bronbezetting en No-Show-keuzes onbekend/leeg totdat opnieuw succesvol is gesynchroniseerd.
8. Test vervangende synchronisatie. Zonder expliciete verklaring is de knop geblokkeerd. Bij succes vervangen brongegevens en verdwijnen tijdelijke indelingen. Bij een gecontroleerde lokale verbindingsfout blijven vorige bron, tijdstip, sessie en tijdelijke indelingen gelijk; de afzonderlijke foutpoging is wel zichtbaar. Herstel daarna de lokale verbinding. Een gedeeltelijke API-fout en schrijffouten zijn geautomatiseerd synthetisch getest; forceer daarvoor geen beschadiging in de acceptatiedatabase.
9. Controleer registratie op betrouwbaar gekoppelde actieve boekingen, ontbreken van Afgeschermd/ambigue keuzes, duurzame opslag en intrekking met toelichting. Controleer dat eerdere geregistreerde feiten/intrekkingen na nieuwe planning, periodewisseling en bronvervanging behouden blijven. Gebruik uitsluitend door CKC bedoelde acceptatieregistraties; foutieve registraties via de bestaande intrekking afhandelen.
10. Deel alleen niet-herleidbare uitkomsten en foutcategorieën. Laat PR #38 open; merge pas na een afzonderlijk functioneel acceptatiebesluit.

## Grenzen van het bewijs en resterende aandachtspunten

Nog niet aangetoond: de echte CKC-keten met deze nieuwe sessiebediening, daadwerkelijke browser-/computerherstart op de Mac, native dubbelklikweergave in de gebruikte browser en correcte handmatige verwerking in Sportlink. AppTest simuleert nieuwe gebruikerssessies; de subprocessproef bewijst opslagheropening na procesbeëindiging, geen fysieke stroomuitval/herstelgarantie. CI is technische regressiebescherming en geen functionele acceptatie.

De bestaande lokale prototype-identiteit blijft in gebruik; dit is geen productie-IAM of multi-userarchitectuur. De bestaande API-boekingsidentificatie- en naamkoppelingsbeperkingen blijven beschreven in het identiteitsrapport. Een foutieve/inconsistente database blijft een expliciete fout en wordt niet automatisch vervangen. Geen nieuwe CKC-beleids- of architectuurbesluiten zijn nodig voor de geïmplementeerde BL-16-regels; lokale functionele acceptatie en het resetmoment blijven besluiten van Johan/CKC.
