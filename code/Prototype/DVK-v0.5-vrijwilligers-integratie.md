# Vrijwilligers API → Ledendienst Planning

## Grondslag en scope

Baseline: `prototype-v0.5` @ `1399493e70bd35b356a0108e87a0ff8ec614b5af`, inclusief PR #22, #34, #35, #36 en #37.
Werkbranch: `codex/vrijwilligers-planning-integratie`. V0.4 blijft de geaccepteerde releasebaseline; deze v0.5-integratie vereist nog lokale functionele acceptatie.

Geaccepteerde eisen: oorspronkelijke integratieopdracht en aanvullende bevestiging dat `Shift Catalog.xlsx` de configuratiebron is; 29 diensten iedere seizoenweek, kantine CKC, vrijdaguitzondering, geen uitzonderingskalender. Sportlink levert uitsluitend inroosteringen. Succes vervangt de actuele bronset en verwijdert alle tijdelijke planning; mislukking behoudt beide. Duurzame no-shows blijven zelfstandig bewaard. Geen PR #15-afsluitconcept.

## Configuratie en Rooster Generator

De twee CSV-bestanden onder `dvk/configuration/shift_*` zijn de tekstuele, controleerbare representatie van de aangeleverde Excel-catalogus. Ze worden ingelezen door de bestaande `ShiftCatalogAdapter`; het weekpatroon wordt door `ShiftCatalog.bindings()` tot concrete diensten gemaakt. Geen tweede catalogus, onderhoudscherm of Excel-runtimeafhankelijkheid. Het originele bestand is niet toegevoegd aan Git.

| Taakcode | Omschrijving | Diensten/week | Min/max |
| --- | --- | --- | --- |
| 701 | Bar korte inzet | 9 | 1/2 |
| 741 | Bar weekend | 8 | 2/4; vrijdag 1/2 |
| 761 | Bar Zo-Do | 6 | 1/2 |
| 442 | Commissiekamer | 6 | 1/2 |

721 is expliciet niet gebruikt. Verdeling maandag–zondag: 3, 3, 4, 3, 2, 12, 2. Zaterdag zijn er zes gelijktijdige bar-/commissiekamerparen. Alle diensten hebben een timezone-aware begin/einde en een ID uit taakcode, datum en begintijd.

Onderzocht: `johanvdstel/Rooster2/app.py`, versie 3.6.7.3, blob `e7e2be506bb46f141e7fec6567a530340ce3f136`. Deze heeft dezelfde vier taakcodes en onafhankelijke bar-/CK-tijdsloten, maar voegt barcodes samen en heeft geen volledige bezettingscatalogus. Woensdag, donderdag en het laatste CK-zaterdagslot wijken af van de aangeleverde Excel. De expliciete opdracht maakt de Excel leidend; er zijn geen Rooster2-standaarden overgenomen die daarmee botsen. De bestaande dynamische baruitbreiding uit bookings/activiteiten is geen catalogusbron voor DVK.

## Keten en publicatie

`ShiftCatalog → concrete diensten → vaste taakcodeset → bestaande GET-client → bestaande adapter/naamcontract → SQLite-bookings → planningservice → dashboard`.

Alle actieve codes worden eenmaal opgevraagd, ook wanneer een code geen diensten op de gekozen dag heeft. De UI biedt geen beperkbare taakcodeset of aanvraagparameters. De bredere respons wordt op de gekozen periode gefilterd na datumparsing. Een onleesbare regel wordt niet stilzwijgend weggefilterd. Binnen de periode blijven unieke exacte dienst- en naamkoppeling vereist. Afwijkende intervallen blokkeren de verversing; er worden geen fictieve diensten uit bookings gemaakt.

`NoShowApplicationService.synchronize()` behoudt VRIJ-01 en publiceert pas na alle fetches en normalisaties. Boekingen, opruiming tijdelijke planning en metadata van de geslaagde bronset worden in dezelfde transactie vastgelegd. De metadata gebruikt de bestaande `dvk_records`-opslag via de bookingrepository: geen schemawijziging of migratie. Een laatste poging wordt afzonderlijk geregistreerd met veilige statusinformatie. Een fout overschrijft de laatste geslaagde bronset niet.

De planningservice leest alle bookings zonder de bestaande `recent(50)`-limiet. Zij gebruikt alleen bookings met passende taakcode, concrete dienstidentiteit en exacte tijdgrenzen. Bronbezetting wordt via `calculate_staffing_need()` gecombineerd met tijdelijke planning. Een andere geselecteerde periode of taakcodeset wordt niet als gedekt voorgesteld. Zonder passende geslaagde bron zijn bezetting en behoefte onbekend; een geldige lege geslaagde bron betekent nul.

## Aanvraagvenster: bewijs en acceptatiegrens

De [Sportlink-artikelbeschrijving](https://sportlinkservices.freshdesk.com/nl/support/solutions/articles/9000062942) beschrijft `weekoffset` als verschuiving van het startvenster; de [parameterlijst](https://sportlinkservices.freshdesk.com/nl/support/solutions/articles/9000211117-lijst-met-parameters-in-club-dataservice) vermeldt voor Vrijwilligers `weekoffset` en `aantaldagen`. Deze documentatie is geen bewijs van live servergedrag op kalendergrenzen.

Technische keuze: `request_window()` behoudt minimaal het bestaande venster -1/60 en verbreedt het waar nodig. De start ligt minstens een volle week vóór de geselecteerde begindatum; dagen worden tot en met de einddatum geteld vanaf de maandag van de verschoven week. Dit dekt zowel een dagrelatieve als een maandagrelatieve ankerinterpretatie. Synthetische grensgevallen omvatten verleden, toekomst en jaarwisseling. De exacte responsdekking en eventuele serverlimieten moeten lokaal worden vergeleken met Sportlink, met name bij lege bronnen en ruimere perioden. Er is geen live validatie vanuit Codex uitgevoerd en geen absolute garantie over ongemelde serverafkapping geclaimd.

## Persoonskoppeling, demonstratie en privacy

Het exacte naamcontract blijft ongewijzigd: `Achternaam, Voorletter(s) Tussenvoegsel(s) (Roepnaam)`, precies één match naar relatiecode. Een ontbrekend tussenvoegsel leidt in de bestaande implementatie tot geen geconstrueerde naam; geen nieuwe formatteringsregel, fuzzy matching of terugval naar `Naam` toegevoegd. Bij zulke leden blokkeert de synchronisatie met een expliciete melding. Een nieuwe naamvorm vergt apart bevestigd broncontract.

De standaardweergave gebruikt de catalogus en gevalideerde bronbezetting. De afzonderlijke demonstratieweergave behoudt bestaande synthetische kandidaatselectie, wedstrijden, achterstanden, bevestiging en undo; verversen naar Sportlink is daar uitgeschakeld. Echte kandidaatselectie en persoonsconflicten op Sportlink-bookings zijn niet operationeel en worden ook niet zo gepresenteerd. PR #35-levensduur blijft ongewijzigd.

Credentials blijven runtime-only. Transportmeldingen nemen geen exceptiontekst/URL meer over; synthetische tests bevatten expres een nepcredential in netwerkfouten. Geen exports, databases of originele API-responsen toegevoegd. Bronprovenance met persoonsgegevens blijft uitsluitend in de lokale database.

De bestaande CI-workflow heeft nog twee live-uitvragen bij `workflow_dispatch`. Dit wijkt af van de huidige afspraak dat echte CKC-data uitsluitend lokaal worden verwerkt, hoewel de v0.4-baseline deze eerdere validaties vermeldt. Reguliere PR-regressie is synthetisch. De workflow is niet gewijzigd: afzonderlijk voorstel is de twee live-stappen uit CI te verwijderen en live bronacceptatie alleen lokaal uit te voeren. Deze iteratie start geen handmatige live-workflow.

## Lokaal acceptatiescript (uitsluitend door opdrachtgever)

Gebruik een lokale, niet door Git gevolgde database en de bestaande Python-omgeving. Gebruik geen gedeelde cloudomgeving. Stel `SPORTLINK_CLIENT_ID` veilig in de lokale omgeving in; deel de waarde niet. Vanuit `code/Prototype`:

```sh
.venv/bin/python -m streamlit run streamlit_app.py
```

1. Open Ledendienst Planning met **Sportlink en DVK-catalogus**. Kies een volledige actuele seizoenweek. Verwacht 29 diensten; aantallen per code volgens bovenstaande tabel. Vergelijk alle begin-/eindtijden met `Shift Catalog.xlsx`, met name woensdag/donderdag en zaterdag CK 20:00–22:30. Vrijdag heeft 741 min 1/max 2. Alle locaties zijn Kantine CKC.
2. Vóór eerste verversing: bezetting en behoefte staan op Onbekend. Kies de lokale Leden-CSV met de vier naamvelden en relatiecode. Klik bewust op synchroniseren. Deze actie verwijdert bij succes alle tijdelijke planning, ook als de bron leeg is.
3. Vergelijk per code het controleoverzicht en per concrete dienst de bezetting met Sportlink voor exact dezelfde week. Controleer meerdere personen op één dienst, codes zonder bookings en volledig onbezet gebleven diensten. Nul betekent uitsluitend nul na geslaagde verversing.
4. Controleer weekbegin/-einde met bookings aan beide randen. Herhaal voor een toekomstige week, een langere periode en een periode rond een winter-/zomertijdovergang. Controleer ook de vorige week wanneer daar vergelijkingsmateriaal voor bestaat. Bij twijfel over serverdekking: niet accepteren; geef alleen geanonimiseerde datumgrenzen en aantalsverschillen door.
5. Kies een andere periode zonder te verversen. De vorige bronperiode en het vorige succesmoment blijven zichtbaar; de nieuwe periode krijgt geen schijnbaar actuele bezetting. Ververs voor de nieuwe periode en controleer dat alleen die bronperiode actueel wordt.
6. Gebruik de demonstratie om de bestaande kandidaatselectie te testen: selecteren alleen doet niets; bevestigen voegt tijdelijke planning toe; undo verwijdert die; navigatie en browser-refresh behouden werk. Wisselen van periode met werk vraagt bevestiging. Stop/start van het echte applicatieproces wist werk, niet bookings/no-shows.
7. Met tijdelijke planning aanwezig: test een mislukte verversing door lokaal de verbinding te verbreken. Verwacht begrijpelijke melding, vorige bookings en werk behouden, vorig succesoverzicht zichtbaar plus mislukte poging. Herstel verbinding; alleen een volledig geslaagde verversing wist werk. Deel geen foutdump met URL of credentials.
8. Controleer met een lokale periode waarvan bekend is dat alle vier codes leeg zijn: geslaagde bronset, alle codes zichtbaar met nul, catalogusdiensten blijven bestaan en tijdelijke planning vervalt.
9. Controleer ontbrekende of dubbele naamkoppeling uitsluitend met wegwerp/synthetische invoer; verwacht geen publicatie. Een leeg tussenvoegsel wordt momenteel niet automatisch opgelost. Geen export aanpassen om een echte identiteit kunstmatig passend te maken.
10. Bestaande duurzame no-shows en intrekkingen moeten na verversing en echte herstart behouden blijven. Maak geen fictieve no-show op echte CKC-inroosteringen voor een technische proef. Synthetische regressies toetsen dit afzonderlijk.

Rapporteer alleen: geslaagd/mislukt per stap, gekozen datumbereik, geanonimiseerde aantallen per taakcode en eventuele ontbrekende functionele afspraak. Geen namen, relatiecodes, exports, screenshots met persoonsgegevens, databases, ruwe responsen of credentials naar GitHub/Codex/ChatGPT.

## Technische verificatie

Nieuwe synthetische regressies: `tests/test_volunteer_planning_integration_v05.py`. Bestaande demo-UI-tests kiezen nu expliciet Demonstratie; de controle op een door de gebruiker versmalbaar aanvraagvenster is vervangen door een gewone rerun, omdat aanvraagparameters voortaan applicatie-eigendom zijn. De tabelhoogtecontrole omvat de gevraagde negende tabel. De bestaande gedragsassertions zijn behouden.

Volledige regressie: **713 geslaagd**, 0 mislukt, 0 overgeslagen (Python 3.11.16, Streamlit 1.64.0, pytest 9.1.1; bestaande tijdelijke testvenv). Baseline telt 693 tests; deze iteratie voegt 20 synthetische cases toe. `git diff --check` geslaagd. Twee tussentijdse fouten betroffen de negende tabel en behoud van de demonstratieselectie bij geannuleerde periodewisseling; beide zijn hersteld met behoud van de oorspronkelijke gedragscontroles. CI en commit staan in de PR-oplevering. Er is nog geen functionele live-acceptatie.

Gerichte ketenregressie: **137 geslaagd** (nieuwe integratie, client/adapter, no-shows, catalogus, tijdelijke planning en proceslevensduur).

| Gewijzigd bestand onder `code/Prototype` | Reden |
| --- | --- |
| `dvk/configuration/shift_definitions.csv` | Vier actieve definities en vrijdagregel uit de aangeleverde catalogus |
| `dvk/configuration/shift_week_pattern.csv` | De 29 bevestigde weekdiensten |
| `dvk/shift_catalog.py` | Bestaande adapter hergebruiken; concrete diensten en unieke identiteit genereren |
| `dvk/volunteer_planning.py` | Volledige taakcodeset, periodevenster, bronstatus en planninggegevens via publieke service |
| `dvk/application_services.py` | Bestaande publicatiepad uitbreiden met volledige codeset, periodefilter en atomaire succesmetadata |
| `dvk/persistence/sportlink_bookings.py` | Alle bookings lezen en verversingsmetadata in bestaande opslag bewaren |
| `dvk/vrijwilligers_adapter.py` | Brede uitvraag expliciet beperken tot de actieve bronperiode |
| `dvk/vrijwilligers_client.py` | Geen transportexceptiontekst met mogelijke credentials doorgeven |
| `streamlit_app.py` | Werkelijke bezetting, onbekende bronstatus, taakcontroleoverzicht en afzonderlijke demonstratie |
| `tests/test_volunteer_planning_integration_v05.py` | 20 nieuwe synthetische regressiecases |
| `tests/test_planning_workqueue_v05.py` | Bestaande demo-UI-cases expliciet als demonstratie uitvoeren |
| `tests/test_planning_runtime_v05.py` | Demo expliciet kiezen; behoud bij rerun zonder vrij instelbare uitvraagparameters |
| `tests/test_duty_population_dashboard_v05.py` | Bestaande hoogtecontrole uitbreiden naar de gevraagde negende tabel |
| Dit rapport | Herleiding, beperkingen, wijzigingsreden, testresultaat en lokaal acceptatiescript |
