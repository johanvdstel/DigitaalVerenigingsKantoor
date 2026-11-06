# Ronde 4 — specificatie van onvoldoende gezinsgegevens

## Context en begrenzing

Werkbranch: `codex/v05-stap2-ronde4-taakplichtdashboard`. HEAD en schone werkboom vóór wijziging gecontroleerd op exact `f207a45ce5a730f0ed4890cebe38342cd6adf071`. Integratiebaseline `prototype-v0.5`: `35396c354d6efed2ac6db86ee61c5604834a4334`, ancestry gecontroleerd. Geen nieuwe branch gemaakt.

Context gecontroleerd in ontwikkelworkflow, herijkte functionele baseline B-05/B-06/B-07/B-10 en eerdere ronde-4-rapporten. Functioneel geaccepteerde v0.4- en C/W/I/R-regressies blijven referentie; v0.5 is integratieontwikkeling, geen integrale functionele acceptatie. Sportlink houdt de bronfeiten, CKC bepaalt beleid en Johan accepteert functioneel.

Geaccepteerde eis uit deze opdracht: bestaande gezinsonzekerheden concreet toelichten, zonder andere besluiten, uren, selecties, bronmeldingen of onzekerheidsgronden. Vastgesteld probleem: de presenter vertaalt meerdere `family_data_insufficient`-gronden naar dezelfde tekst en dedupliceert die, terwijl de afleiding al een ondersteunende identiteit en persoonsfeiten bewaart. Een verklarende structuur in de presenter en één uitklapbare tabel zijn daarom voldoende. Geen domeinwijziging, nieuwe opslag, adapterwijziging, migratie of historische reconstructie. Alleen synthetische tests; echte exports en de lokale gebruikersdatabase zijn niet gelezen of gewijzigd.

## Gekozen oplossing en gewijzigde functies

- `dvk/duty_control_presenter.py`: nieuwe verklarende dataclass `FamilyDiagnostic`, nieuw `family_diagnostics(expectation)` en aanvullend veld op `DutyControlRow`. `present_controls` koppelt deze uitleg aan de bestaande rij. Alleen bestaande `family_data_insufficient`-gronden worden toegelicht, uitsluitend vanuit hun `source_facts` en ondersteunende identiteit. Andere gronden, hoofdtekst, status en uren blijven ongewijzigd.
- `streamlit_app.py`: uitklapbare **Nadere uitleg bij onvoldoende gezinsgegevens**, met een scrollbare tabel van 360 pixels. Kolommen tonen beoordeeld lid, vergelijking met, van wie de gegevens zijn, betrokken lid, criterium, oorzaak en uitleg. De tabel volgt het bestaande filter en toont ook onzekerheid bij een reeds vaststaande vrijstelling. Geen technische identifiers, adressen, oudernamen of geboortedatums in deze nieuwe tabel.
- `tests/test_family_diagnostics_dashboard_v05.py`: elf synthetische ontwikkeltests, inclusief daadwerkelijke UI-weergave en verboden database-/Sportlink-toegang tijdens het laden van de dashboarddetails.
- `tests/test_duty_population_dashboard_v05.py`: verwacht aantal tabelaanroepen van zeven naar acht vanwege de expliciet gevraagde detailtabel; dezelfde begrensde-hoogtecontrole blijft op iedere tabel gelden.
- Dit rapport: grondslag, voorbeelden, verificatie en beperkingen.

`member_duty.py`, `_possible_family`, B-05/B-06/B-07, B-02, populatieselectie, Sportlink-urenvergelijking en Bron- en controlediagnose zijn niet gewijzigd. Geen nieuwe onzekerheidsgrond toegevoegd. De volledige context van iedere vergelijking blijft behouden; herhaalde oorzaken bij verschillende vergelijkingen worden niet stilzwijgend samengevoegd.

## Voorbeelden met synthetische leden

| Gegevens van | Betrokken lid | Criterium | Oorzaak |
| --- | --- | --- | --- |
| Beoordeeld lid | Lid Y | Adres | Postcode ontbreekt of is niet bruikbaar |
| Beoordeeld lid | Lid Y | Adres | Huisnummer ontbreekt of is niet bruikbaar |
| Beoordeeld lid | Lid Y | Ouders | Geen bruikbare ouderregistratie beschikbaar |
| Ander vergeleken lid | Lid O | Ouders | Geen bruikbare ouderregistratie beschikbaar |
| Ander vergeleken lid | Ander synthetisch lid | Adres | Adresgegevens conflicteren tussen bronregels |
| Ander vergeleken lid | Ander synthetisch lid | Ouders | Ouderregistraties conflicteren tussen bronregels |

Bij een bestaande grond zonder ondersteunend ander lid: “Zowel het oudercriterium als het adrescriterium is bij dit lid niet bruikbaar voor de gezinsregel.”

Bij een bestaande vergelijking met verschillende volledige adressen: “De volledige woonadressen verschillen; het oudercriterium kan niet volledig worden beoordeeld. De bestaande gezinsregel houdt deze vergelijking daarom onzeker.”

Bij andere bestaande vergelijkingsonzekerheid: “Een gezinsverband met dit andere lid is niet aangetoond; het ouder- of adrescriterium kan niet volledig worden beoordeeld. De bestaande gezinsregel houdt deze vergelijking daarom onzeker.”

Dit zijn verklaringen van bestaande beslisvoorwaarden, geen nieuwe conclusie dat betrokken leden een gezin vormen. Lege toevoeging geeft geen ontbrekend-adresmelding.

## Diagnostische beperkingen

- De huidige ouderregistratie maakt geen verschil tussen “één ouder is terecht geregistreerd” en “een tweede ouder ontbreekt”. Eén bruikbare ouderregistratie wordt daarom niet als onvolledig aangemerkt; alleen daadwerkelijk ontbrekende/onbruikbare of conflicterende registraties worden toegelicht. Een verwachting van een tweede ouder wordt niet verzonnen.
- De canonieke adresconflictindicator bewijst een conflict tussen bronregels, maar specificeert niet het conflicterende veld. De uitleg noemt daarom geen verondersteld postcode-/huisnummerconflict.
- Een afwezige toevoegingskolom en een lege toevoeging zijn in de bestaande canonieke feiten niet onderscheiden; geen nieuwe broninterpretatie toegevoegd.
- Postcodevaliditeit wordt uitsluitend volgens de bestaande bruikbaarheid bepaald, niet met een nieuwe formaatcontrole.
- Als een ondersteunend persoonsfeit ontbreekt, wordt geen ontbrekend bronveld verondersteld. De huidige afleiding levert voor deze grond de betrokken persoonsfeiten; bestaande andere grondteksten blijven intact.
- Gelijke namen blijven gelijk weergegeven. Interne identiteit en vergelijkingscontext blijven afzonderlijk in de verklarende structuur bewaard; er worden geen adressen of identifiers toegevoegd om namen kunstmatig uniek te maken.
- De 111 werkelijke gevallen zijn niet opnieuw onderzocht. De wijziging specificeert hun eventuele bestaande oorzaken, maar lost de onderliggende onzekerheid niet op en verandert de beoordeling niet.

## Daadwerkelijk uitgevoerde verificatie

Bestaande projectomgeving `code/Prototype/.venv/bin/python`, geen nieuwe afhankelijkheden.

- Vooraf: member-duty, dashboard, populatie en database-isolatie: **118 passed in 2.50s**.
- Definitieve gerichte suite inclusief elf nieuwe tests: **129 passed in 2.42s**.
- Rechtstreekse vergelijking met de presenter uit exacte startcommit via `git show`: **tien synthetische scenario's geslaagd**. Alle zes bestaande rijvelden, tellingen, filters, bronfeiten en bestaande beoordelingen vóór/na identiek. Scenario's omvatten ontbrekende postcode/huisnummer, conflicten, verschillende volledige adressen, meerdere mogelijke gezinsleden en een reeds vaststaande vrijstelling.
- Volledige regressiesuite: **594 passed in 5.41s**.
- `git diff --check`: schoon.

Nieuwe tests controleren per scenario expliciet dat presenterdiagnose de volledige publieke vergelijking niet verandert, dat status/verwachte uren dezelfde zijn en dat bronmeldingen behouden blijven. UI-test toont de daadwerkelijke detailtabel, controleert het ontbreken van een relatiecodekolom en controleert dat de tabel het gekozen filter volgt. SQLite-connecties en Sportlink-fetch zijn in die uploadtest verboden. Volledige suite omvat de bestaande planning, no-shows en geaccepteerde regressies.

Twee nieuwe tests faalden aanvankelijk: een conflicterend eigen adres levert zowel een eigen grond als een vergelijkingsgrond op, zodat er vier verklarende conflictregels zijn; de test verwacht nu beide bestaande contexten expliciet. De synthetische UI-test voegde eerst een urenregel met te weinig velden voor de bestaande fixtureheader toe; die overbodige regel is verwijderd. De validatie is niet versoepeld. Twee testaanroepen gebruikten aanvankelijk ten onrechte een relatief `.venv`-pad vanaf de repositoryroot en startten niet; bovenstaande aanroepen zijn werkelijk vanuit Prototype uitgevoerd.

## Oplevering

Geen functioneel of architecturaal besluit nodig voor deze verklarende uitbreiding. De brede werking van `_possible_family` blijft precies zoals zij was. Geen push, PR, merge, nieuwe CI-run of wijziging aan gebruikersdata. CI-status voor deze lokale correctie is niet beschikbaar. Commit-ID volgt in de eindrapportage.

Johan beoordeelt de nieuwe uitleg lokaal; deze oplevering is nog niet functioneel geaccepteerd.
