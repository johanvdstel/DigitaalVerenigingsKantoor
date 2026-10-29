# Iteratie 2 — BL-03 historische achterstand

**Status:** technisch geïmplementeerd; geen functionele acceptatie, backlogafsluiting of merge.
**Baseline:** prototype-v0.5 op `881d807138f951a69d651e8ee37b68042fe319a4`; bij start identiek aan actuele GitHub-integratiebranch.
**Werkbranch:** `codex/iteratie-2-historische-achterstand`.
**Werkmap:** `/private/tmp/dvk-iteratie-2`.

## Context, bewijs en geaccepteerde eisen

Geaccepteerde releasebaseline blijft v0.4 op main. Iteratie 1 is geaccepteerd via PR #53; integrale v0.5-acceptatie staat open. Sportlink is bronhouder van de urenexport en geregistreerde taakplicht; CKC/Johan bepaalt beleid. De planner borgt dat de historische CSV het onmiddellijk voorafgaande seizoen bevat.

Expliciete implementatieopdracht: gebruik `~/Documents/DVK-Sportlink-exports/Overzicht per periode vorig seizoen.csv`, dezelfde structuur als de huidige urenexport. Geen Excel, automatische seizoensherkenning, aanvullende seizoensmetadata of nieuwe database. Historische bron-E (`Niet ingedeeld`) is uitsluitend een prioriteitsfactor voor diensten in juli tot en met december. Negatief is geen krediet; actuele A/B/C/D/E veranderen nooit.

Vastgesteld vóór wijziging: `prioritization.py` had al de achterstandenparameter en sorteerde op actuele E, historische achterstand, wedstrijdvoorkeur en persoonssleutel. `candidate_context.py` schakelde historische prioritering expliciet uit. Parser, getalvalidatie en relatiecodesleutel waren al aanwezig. De historische decembergrens en W09-verwachting weken af van de opdracht.

Johan heeft na signalering afzonderlijk expliciet akkoord gegeven op de gerichte W09-datumaanpassing. W09-testdata blijven ongewijzigd; op 1 december telt de achterstand nu wel mee. Het W09-label en demonstratiescript weerspiegelen die wijziging; geen alternatieve historische beleidsvariant ingevoerd. Andere geaccepteerde fixtures zijn niet aangepast.

## Minimaal ontwerp en herleiding

- De bestaande CSV-parser en omzetting van A/B/C/D/E worden gedeeld. Alleen de bestaande omzetting is in `parse_duty_record` ondergebracht om dubbele importlogica te voorkomen. De bestaande import behoudt zijn gedrag; historische verwerking gebruikt de optionele strikte CSV-modus.
- Een klein in-memory bronresultaat houdt historische bronrecords, signalen en beschikbaarheid apart. Geen persistentiemodel of schemawijziging. Geldige negatieve E en aangeleverde E bij formuleverschil blijven als bronwaarde aanwezig; een afwijking wordt nooit stilzwijgend herberekend.
- Een afzonderlijke methode in de bestaande lokale bronservice leest de historische CSV. De algemene lijst met vijf bronnen is ongewijzigd. Taakplichtcontrole leest het nieuwe bestand niet.
- Historische records koppelen op relatiecode aan de actuele personenbasis; naam is geen sleutel. Dubbele relatiecodes (ook identieke regels), ongeldige getallen, onbekende relaties en formuleverschillen worden niet als geldige achterstand gebruikt. Overige geldige records blijven bruikbaar.
- Ontbrekend/onleesbaar/structureel ongeldig bestand: zichtbare bronwaarschuwing, normale planning blijft mogelijk. Ontbrekende/onbetrouwbare waarde: neutraal in rangschikking, maar expliciet onbekend in uitleg. Ook een weggelaten achterstandenmapping wordt niet als bewezen nul verklaard.
- Dienstdatum bepaalt `7 <= on_date.month <= 12`. Januari t/m juni geen historische prioriteitsfactor. Rangorde en overige selectie-/wedstrijd-/teamspeeldagregels blijven behouden.
- UI presenteert afgeleide uitkomsten: optionele bronwaarschuwingen, problemen met menselijke namen waar beschikbaar en de bestaande directe kandidaatdetails. Geen nieuwe beleidslogica in Streamlit.

## Gewijzigde bestanden en reden

| Bestand(en) | Reden |
| --- | --- |
| dvk/real_data_import.py | Bestaande urenregelomzetting hergebruiken; optionele strikte CSV-parsing. |
| dvk/historical_backlog.py | Historische bron-E bewaren, koppelen/valideren en onbetrouwbare waarden uitsluiten van de prioriteitsfactor. |
| dvk/local_csv_sources.py | Historische bron apart en optioneel lezen. |
| dvk/candidate_context.py | Bronresultaat meenemen en bestaande prioritering aansluiten. |
| dvk/prioritization.py | Juli–december, positieve factor, onderscheid onbekend/beschikbaar/buiten periode. |
| dvk/candidate_presenter.py, streamlit_app.py | Begrijpelijke uitleg en zichtbare niet-blokkerende meldingen. |
| tests/test_historical_backlog_v05.py | Synthetische import-, fout-, koppel-, datum-, rangorde-, balans- en onafhankelijkheidsproeven. |
| tests/test_historical_backlog_ui_v05.py | Ontbrekende/geldige/dubbele/structureel ongeldige historie bij verversen, zichtbare uitleg en behoud bevestiging/undo. |
| tests/test_workstream_v03.py | Uitsluitend goedgekeurde W09-datumverwachting; bestaande testgegevens behouden. |
| dvk/workstream_cases.py, run_priority_cases.py | W09-label en datumgrensdemonstratie laten aansluiten op goedgekeurd beleid. |
| tests/test_candidate_context_v05.py, tests/test_candidate_presenter_v05.py | Vervallen BL-03-uitschakeltekst en oude datumtekst vervangen; bronmock behandelt afzonderlijke optionele bron. |
| tests/serve_synthetic_planning.py | Bestaande geïsoleerde browserproef uitbreiden met optionele synthetische historie; geen echte bronbestanden nodig. |
| README.md, code/Prototype/README.md | Actuele technische toestand en verwijzing naar acceptatieprotocol. |
| BACKLOG.md, DVK-PROTOTYPE-PLANNING.md | CSV, foutcontract en toepassingsmaanden; functionele acceptatie blijft open. |
| DVK-BRONCONTRACTEN-v0.5.md | Afzonderlijk bevestigd historisch contract; overige conceptstatus blijft behouden. |
| DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md | Goedgekeurde B-13-wijziging en scheiding actuele/historische uren. |
| DVK-v0.5-overdracht-iteratie2-BL03.md, dit verslag | Verouderde aannames vervangen en overdraagbare technische bewijs-/acceptatiebasis vastleggen. |

PRODUCTIE-ROADMAP.md is gelezen en niet gewijzigd: deze prototypewijziging introduceert geen productievoorziening, migratie of hostingbesluit. Historische v0.3-ontwerpdocumenten en afgesloten Iteratie-1-verslagen blijven tijdgebonden bewijs; de actuele B-13 en deze opdracht bepalen de huidige regel.

## Verificatie

Runtime: Python 3.11.16, bestaande omgeving `/private/tmp/dvk-bl18-venv`.

- Gerichte gezamenlijke run: 193 tests geslaagd; daarna aanvullende regressie toegevoegd voor een weggelaten mapping, meegenomen in de definitieve volledige suite.
- Definitieve volledige suite: **1251 geslaagd**, 0 mislukt/overgeslagen, in 74,54 seconden.
- Alle elf synthetische scripts uit CI: exit 0 (run_cases, run_workstream_cases, run_import_cases, run_candidate_cases, run_priority_cases, run_dashboard, run_proposal_cases, run_assignment_cases, run_dashboard_actions, run_integrated_acceptance, run_v04_demo).
- Syntaxcontrole van app, historische adapter, kandidaatcontext en synthetische browserlauncher geslaagd. Diff-check schoon na verwijderen van overgenomen trailing whitespace in een gewijzigde documentatieregel.
- Nieuwe tests omvatten 30 juni, 1 juli, 30 november, 1 december, 31 december en 1 januari voor twee opeenvolgende kalenderjaren; positieve/nul/negatieve E; onbekend/onbeschikbaar; foutieve getallen/kolommen/regels; UTF-8-fout; duplicaten; formuleverschillen; naam-onafhankelijke koppeling; huidige E vóór historie; wedstrijdvoorkeur en stabiele tie-breaker; ongewijzigde actuele balans; onafhankelijke Taakplichtcontrole; UI-verversing en bevestiging/undo. Bestaande Iteratie-1- en versieproeven draaien in de volledige suite mee.
- De eerste nieuwe UI-proef faalde op tekstzoeken in een door pandas verkorte tabelweergave. De test leest nu de volledige Melding-kolom. Geen functionele verwachting versoepeld.
- Geen echte CKC-exports, bestaande databases of credentials gelezen. Tests gebruiken synthetische HOME en tijdelijke databases. Geen bank-/persoonsgegevens toegevoegd. Oorspronkelijke lokale wijzigingen blijven ongemoeid.

Commit, PR en CI voor de exacte opgeleverde head worden in de oplevering vermeld; geen functionele acceptatie of merge.

## Praktische lokale acceptatie — uitsluitend synthetisch

Gebruik de bestaande browserlauncher. Deze kopieert de app tijdelijk, levert brondata in geheugen en gebruikt een tijdelijke synthetische database. De bestaande lokale exports worden niet gelezen. De versiecaption meldt bij deze tijdelijke kopie eerlijk dat Git-informatie niet beschikbaar is; de echte appversie is afzonderlijk geautomatiseerd getest.

```bash
cd /private/tmp/dvk-iteratie-2/code/Prototype
/private/tmp/dvk-bl18-venv/bin/python -B tests/serve_synthetic_planning.py --members 3 --historical --port 8532
```

1. Open `http://127.0.0.1:8532`. De proefperiode is 19–25 oktober 2026. Bronbezetting is al synthetisch geladen; gebruik geen live Sportlink-synchronisatieknop.
2. Selecteer een dienst met vrije plaatsen op zaterdag of doordeweeks. Alle drie volwassenen hebben actuele E=10; historische E is respectievelijk 0, 4 en 8. Verwacht volgorde SYNTH-2, SYNTH-1, SYNTH-0, met menselijke namen in de tabel.
3. Vink kandidaten aan. Details tonen 8/4 historische uren of bekende nul; actuele E blijft 10. Alleen bevestiging maakt een tijdelijke indeling; controleer undo.
4. Stop met Ctrl+C. Start dezelfde opdracht zonder `--historical`. Bronwaarschuwing zichtbaar; kandidaten blijven beschikbaar. Details melden onbeschikbare historie, geen bewezen nul. Gebruik dezelfde bronverversingsknop om de werking te bekijken; de synthetische bron wordt opnieuw geleverd.
5. Datumgrenzen en onbetrouwbare/ontbrekende persoonswaarden zijn zonder echte bronmutaties reproduceerbaar met:

```bash
/private/tmp/dvk-bl18-venv/bin/python -m pytest -q tests/test_historical_backlog_v05.py tests/test_historical_backlog_ui_v05.py
```

Deze proeven omvatten ook vernieuwing van geldige naar ongeldige historie, behoud van tijdelijke planning en expliciete bevestiging/undo. Noteer handmatig geslaagd/afwijking/niet beproefd. Deel geen echte persoonsinformatie. Functionele acceptatie volgt uitsluitend na Johans besluit en afzonderlijke controle van de opgeleverde commit.

## Resterende beperkingen

De planner is verantwoordelijk voor juiste vervanging van de historische export per seizoen; DVK verifieert het bronseizoen niet. Er is geen automatische achtergrondverversing. Negatieve bronwaarden blijven bewaard maar leveren geen krediet op. Live CKC-data en een handmatige browseracceptatie zijn niet door Codex beproefd. Geen aanvullende technische maatregelen zonder aantoonbare noodzaak.
