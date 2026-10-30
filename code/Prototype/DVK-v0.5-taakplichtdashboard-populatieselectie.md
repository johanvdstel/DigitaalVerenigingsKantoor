# Ronde 4 — beoordelingspopulatie en scrollbare overzichten

## Context, gezag en proportionaliteit

Bestaande werkbranch: `codex/v05-stap2-ronde4-taakplichtdashboard`. Exact startpunt vóór wijzigingen gecontroleerd: `ffd9a7b1619ab5d68063c1e897db955c617f20da`. Integratiebaseline: `prototype-v0.5`, commit `35396c354d6efed2ac6db86ee61c5604834a4334`. Geen andere branch gemaakt. De geaccepteerde functionele v0.4-baseline en C/W/I/R-regressies blijven referentie; v0.5 is nog in ontwikkeling en niet integraal geaccepteerd.

Relevante documenten: AGENTS.md, ontwikkelworkflow, herijkte functionele B-01–B-14-baseline, FUNCTIONEEL-CONTRACT-v0.5-vervolg, ronde-4-dashboardrapport en stabilisatierapport. Sportlink houdt bronfeiten; CKC bepaalt beleid; Johan beslist over functionele acceptatie. De actuele opdracht accepteert expliciet de selectietabel voor lidstatussen, afzonderlijke selectieproblemen, seizoeninvoer en scrollbare overzichten.

Vastgesteld probleem: de dashboardpresenter toonde alle canonieke personen die de bestaande vergelijking oplevert. Dat selecteert geen relevante beoordelingspopulatie. Bovendien vallen conflicterende ledenregels en ongeldige afmelddatums soms al vóór canonieke personen weg. Alleen canonieke personen tellen zou daarom een onvolledige selectieverantwoording geven. De extra selectiecomponent is uitsluitend nodig voor deze opdracht; geen nieuwe opslag, bronmapping, migratie of beleidswijziging. Testgegevens zijn uitsluitend synthetisch. Echte CKC-exports en gebruikersdatabases zijn niet gelezen of gewijzigd.

## Ontwerpbesluiten en bewijs

**Geaccepteerde eis B-03:** afmelddatum is de eerste dag zonder geldig lidmaatschap. De bestaande `SportlinkRealDataAdapter.current_membership` gebruikt strikt `as_of < end_date`. De selectie hergebruikt dit; op de afmelddatum zelf wordt uitgesloten.

**Geaccepteerde eis uit deze opdracht:** Definitief wordt meegenomen zolang het lidmaatschap op de peildatum geldig is. Oud lid en Afmelding in de toekomst worden met hun afmelddatum beoordeeld. In behandeling, Afgewezen en Aspirant lid worden uitgesloten. Onbekende statussen vormen een selectieprobleem, ook als een afmelddatum aanwezig is. De al bestaande status Afgemeld blijft volgens B-03 beoordeeld. Ontbrekende noodzakelijke afmelddatums worden niet gegokt. Conflicterende dubbele identiteit/lidmaatschapsgegevens en ongeldige afmelddatums worden afzonderlijke selectieproblemen.

**Vastgesteld feit:** de Leden-adapter vult `Membership.end_date`, maar importeert geen aanmelddatum en laat `Membership.start_date` leeg. De bestaande peildatumfunctie heeft geen begindatumargument. Daarom wordt geen nieuwe aanmelddatumkolom of historische begindatuminterpretatie toegevoegd. Selectie volgt de bestaande semantiek; zij bewijst niet dat een lid al vóór een onbekende historische aanmelding lid was. Aanvullende historische aanmeldsemantiek zou een afzonderlijk bron-/beleidsbesluit vereisen.

**Vastgesteld feit:** `dvk/no_show.py:season_id` en GATE10-no-show-intrekking.md / technische impactanalyse leggen 1 juli–30 juni vast. Die bestaande functie levert het initiële, aanpasbare seizoensvoorstel; alleen de weergave verandert van een slash naar `JJJJ-JJJJ`. Een eenmaal ingevulde waarde blijft bij peildatumwijziging behouden. De UI valideert viercijferige opeenvolgende jaren, geeft ook vóór uploads een begrijpelijke fout en toont geen oude resultaten bij ongeldige invoer. De expliciete waarde blijft als `source_period` aan dezelfde importketen doorgegeven; geen periode afgeleid uit bestanden en geen overschrijving van bronwaarden. De bestaande publieke loader blijft buiten de UI expliciete periodewaarden ondersteunen.

**Selectie en beoordeling blijven gescheiden:** unieke, niet-lege relatiecodes uit de ingelezen Leden-regels vormen de telbasis. Identieke dubbele regels tellen eenmaal. Conflicterende dubbelen tellen eenmaal als selectieprobleem. Regels zonder relatiecode blijven met hun bestaande diagnose zichtbaar; zij zijn niet betrouwbaar als unieke leden telbaar. De vier tellingen sluiten: uniek = meegenomen + uitgesloten + selectieprobleem. Alleen meegenomen leden verschijnen in de beoordeling; de drie bestaande beoordelingsuitkomsten en filters blijven intact. De vergelijking wordt met de volledige broncontext uitgevoerd en pas daarna voor presentatie geselecteerd, zodat huishoud-/gezinsinformatie behouden blijft.

**Diagnose ongewijzigd:** de adapter, signalen, codes, berichten en bron-/controlekolommen zijn niet aangepast. De adapter kan bijvoorbeeld Oud lid nog als UNKNOWN_MEMBERSHIP_STATUS signaleren; die bestaande melding wordt niet onderdrukt. Selectieverantwoording is een afzonderlijke weergave, geen vervanging of wijziging van diagnose.

**Scrollen:** alle zeven `st.dataframe`/`st.data_editor`-tabellen hebben expliciete hoogtes van maximaal 360 pixels. Taakplichtbeoordeling, selectieverantwoording en diagnose gebruiken dezelfde 360 pixels, met compacte aantallen. Bestaande planningtabellen met 210/230 pixels behouden die hoogte; Databronnen en Datakwaliteit krijgen alleen een hoogte van 360 pixels. Kandidaten stonden al in een begrensde container van 330 pixels. Standaard Streamlit-tabellen behouden kolomkoppen, horizontale navigatie en sorteren; de bestaande filters blijven werken. Geen paginering, afkappen van data, extra afhankelijkheden of nieuwe tabelinteractie. De kandidaatcontainer is geen dataframe en biedt geen vaste kolomkoppen; die bestaande bediening is niet geherstructureerd.

## Gewijzigde bestanden en reden

- `dvk/duty_control_selection.py`: expliciete, read-only selectie op bestaande canonieke lidmaatschapsfeiten, met unieke bronidentiteiten en afzonderlijke redenen.
- `dvk/duty_control_presenter.py`: selectieresultaten/tellingen verbinden aan het dashboard; bestaande vergelijking en diagnose behouden; seizoenssuggestie en invoervalidatie.
- `streamlit_app.py`: afzonderlijke selectieverantwoording, uitleg en validatie van het seizoen, tabelhoogtes en compacte aantallen. Planning/no-showgedrag ongewijzigd; daar uitsluitend twee bestaande dataframehoogtes toegevoegd op grond van de aanvullende scrollopdracht.
- `tests/test_duty_population_dashboard_v05.py`: 32 nieuwe synthetische ontwikkelregressies voor statussen, datumgrenzen, dubbelen, tellingsaansluiting, diagnosebehoud, seizoenen en daadwerkelijke UI-weergave met 100 beoordelingsrecords.
- `tests/test_dashboard_database_isolation_v05.py`: de eerdere synthetische seizoentekst vervangen door geldig `2026-2027`; beoordelingstabel via Controlestatus-kolom gevonden omdat de selectietabel nu ervoor staat. Bestaande assertions voor read-only verwerking blijven behouden.
- Dit rapport: context, herleiding, verificatie en beperkingen.

Taakplichtregels, B-02 op dezelfde Teams-record, bronadapter, urenvergelijking, SQLite-migraties en geaccepteerde fixtures zijn ongewijzigd.

## Daadwerkelijk uitgevoerde tests

Bestaande projectomgeving gebruikt: `code/Prototype/.venv/bin/python`, pytest 9.1.1. Geen afhankelijkheden geïnstalleerd.

- Uitgangssituatie: dashboard + database-isolatie: **45 passed in 1.79s**.
- Definitieve gerichte suite: nieuwe populatie-/UI-tests + dashboard + database-isolatie: **77 passed in 1.96s**.
- Volledige pytest-regressie vanuit `code/Prototype`: **583 passed in 4.67s**.
- Python-compilecontrole van selectie, presenter en Streamlit-app geslaagd; `git diff --check` schoon.

Nieuwe tests bewijzen onder andere dat alle 100 beoordelingsrecords in de dataframe zitten, dat de twee uitgesloten/onzekere leden apart zichtbaar zijn, dat diagnose behouden blijft, dat filters blijven werken en dat een handmatig seizoen behouden blijft bij peildatumwijziging. Alle tabelaanroepen worden op begrensde hoogte gecontroleerd, inclusief de werkelijk gerenderde drie dashboardtabellen. De bestaande database-isolatietest blokkeert SQLite-connecties en Sportlink-fetch tijdens verwerking van alle vijf synthetische uploads en blijft groen. De volledige suite bevat planning, no-shows, intrekkingen en de bestaande taakplicht- en C/W/I/R-regressies.

Tijdens ontwikkeling faalde de eerdere uploadtest terecht op de inmiddels ongeldige tekst 'Synthetisch seizoen'; alleen de invoerfixture is aangepast aan de nieuwe eis. Een nieuwe UI-test gebruikte aanvankelijk een niet-bestaand AppTest-protobufveld `height`; hoogte wordt nu via de echte dataframe-aanroepen gecontroleerd, zonder de gedragseis te versoepelen. Enkele lees-/schrijfcommando's gebruikten een dubbel relatief Prototype-pad en wijzigden niets; de bedoelde bewerkingen zijn daarna met het juiste pad uitgevoerd. Beide testfouten zijn opgelost en bovenstaande definitieve suites daadwerkelijk uitgevoerd.

Geen push, PR, merge of nieuwe CI-run. CI-status voor deze lokale correctie is niet beschikbaar. De commit-ID staat in de eindrapportage.

## Beperkingen en overdracht

Selectie bewijst alleen het bestaande lidmaatschapscontract met beschikbare bronfeiten; onbekende historische aanmeldgegevens worden niet gereconstrueerd. Naamloos/niet-koppelbaar bronmateriaal blijft in de diagnose. Onbekende statussen worden niet stilzwijgend opgelost. Het seizoensvoorstel blijft een voorstel dat de gebruiker met de geladen export moet vergelijken.

AppTest bewijst gegevensbehoud en componenthoogtes; de feitelijke browserbediening van verticale/horizontale scrollbars en de leesbaarheid met lokale CKC-data moeten nog lokaal worden beoordeeld. Standaard Streamlit-functionaliteit gebruikt, zonder aanvullende afhankelijkheden. Bekende deprecationwaarschuwing voor het bestaande `use_container_width` blijft buiten de scope.

Geen nieuw functioneel of architecturaal besluit nodig voor de uitgevoerde opdracht. Eventuele uitbreiding met historische aanmelddata vereist afzonderlijke besluitvorming. Deze oplevering is gereed voor beoordeling en pas functioneel geaccepteerd na de lokale controle door Johan.
