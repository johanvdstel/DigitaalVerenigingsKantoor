# DVK v0.5 — Functionele acceptatie Iteraties 10A, 10A.1 en 10A.2

**Acceptatiedatum:** 26 november 2026. **Besluit:** alle drie onderdelen functioneel geaccepteerd door CKC. **Integratie:** [draft-PR #73](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/73), doelbranch `prototype-v0.5`, nog **niet gemerged**. Geaccepteerde functionele code `76ca2c4525b68a5ca67c32a37b3bc73e0459aa61`; een afzonderlijke test-only correctie volgde op `600826287bd5c27c0474a98597f3f3da99b8cca5`. Formele documentatie vastgelegd na de lokale functionele acceptatie.

## Aanleiding en functionele eisen

**Iteratie 10A:** binnen de bestaande zaterdagse jeugd-thuisgroep met wedstrijd-/dienstoverlap moet een thuisaftrap **tijdens de dienst** eerder komen dan een aftrap vóór de dienst. De beginwaarde van de dienst telt mee, de eindwaarde niet. Alleen binnen dezelfde groep gaat dit vóór resterende taakplicht E en positieve historische achterstand. Geen wijziging aan geschiktheid, conflictveto, groepsindeling, BL-20, minimumbezetting of de overige prioriteitsregels.

**Iteratie 10A.1:** de oorspronkelijke afhankelijkheid van zaterdag/zondag-woorden in de API-competitieomschrijving bleek te kwetsbaar bij CKC 2-oefenwedstrijden. Een unieke CKC-teamnaam koppelt direct; gelijknamige teams vereisen een unieke match tussen de **feitelijke lokale wedstrijddag** en de vaste Teams.csv-`Speeldag`. Competitieomschrijving telt niet mee. De bestaande cupnormalisatie en bronverantwoording blijven.

**Iteratie 10A.2:** de werkelijke Programma API bevatte een niet-eenduidig koppelbare operationele oefenwedstrijd `CKC 2` op dinsdag 1 december 2026 om 20:15 (+0100). Een onopgeloste wedstrijd mag niet de gehele planning blokkeren. DVK negeert deze wedstrijd voor kandidaat-/conflict-/voorkeurslogica, behoudt de audit en toont `WARNING` plus het aantal overgeslagen wedstrijden. Andere gekoppelde wedstrijden blijven beschikbaar; niet-operationele uitsluitingen zijn informatief. Overige bronfouten behouden hun eigen blokkerende contract.

## Lokaal acceptatiebewijs

| Onderdeel | Uitgevoerde controle | Oordeel |
| --- | --- | --- |
| Actieve codeversie | `codex/dvk-iteratie-10a · 76ca2c4525b6` in `/private/tmp/dvk-iteration10a` | Geslaagd |
| Programma API en bronstatus | 26-11-2026 22:21: **63 gekoppelde operationele wedstrijden**; **1 overgeslagen**, 1 aanvraag, 0 herhalingen, 0 definitieve fouten; status **Beschikbaar met waarschuwingen** | Geslaagd |
| Bronmeldingen | `CKC 2`, `Oefenwedstrijd`, status `Te spelen`, `2026-12-01T20:15:00+0100` zichtbaar als **Wedstrijd niet meegenomen in de kandidaatcontext**; competitie leeg | Geslaagd |
| Bruikbare planning | Kandidaatvoorstellen verschenen normaal na **Brongegevens vernieuwen** | Geslaagd |
| Tijdsvoorkeur 10:00–11:30 | Aftrap 10:15 vóór 09:00 binnen jeugd-thuisgroep, ook boven hogere E/historie van kandidaat 09:00 | Geslaagd volgens lokale plannerbeoordeling |
| Tijdsvoorkeur 08:30–10:00 | Omgekeerde voorrang: aftrap 09:00 vóór 10:15; toelichting en tijdelijk indelen/ongedaan maken beoordeeld | Geslaagd volgens lokale plannerbeoordeling |

De bronwaarschuwing is expliciet door CKC geverifieerd; de eerdere blokkade is opgeheven. Bestaande planningssessies vernieuwen bronnen niet automatisch en bewaren een eventueel oud blokkerend snapshot totdat de planner expliciet vernieuwt. Dat gedrag is regressiematig geborgd en komt overeen met het sessiecontract; een aparte herhaalde lokale hervatproef is binnen 10A.2 niet gerapporteerd.

## Expliciet geaccepteerde restrisico's

1. **Verplaatste wedstrijden:** bij gelijknamige zaterdag-/zondagteams kan de werkelijke wedstrijddag eenduidig, maar inhoudelijk naar het verkeerde team leiden. Dat kan conflictcontrole of voorkeur beïnvloeden.
2. **Overgeslagen wedstrijden:** bij onopgeloste teamkoppeling ontbreekt de wedstrijd in de operationele context. Een kandidaat kan dan ondanks een daadwerkelijke wedstrijd worden voorgesteld, of een passende wedstrijdvoorkeur missen.

CKC accepteert beide risico's bewust, mede gezien de huidige situatie: slechts één zondagteam (geen uitbreiding verwacht) en doordeweekse bardiensten met vaste bezetting. Dit is context voor risicoacceptatie, **geen nieuwe beleidsvoorwaarde in de code**. De planner houdt de eindbeslissing.

## Technische afronding en regressiebewijs

- Iteratie 10A.2: 373 gerichte tests en 11 synthetische acceptatiescripts geslaagd; toen nog één reeds bekend datumafhankelijk no-showtestprobleem in de volledige suite.
- In het dubbele wintertijduur gebruikte de no-showservice de fixtureklok van 1 november 2026, terwijl de testapp-bronraadpleging nog de echte uitvoeringsdatum gebruikte. De eerdere boeking van 25 oktober viel daardoor buiten het registratievenster en de verwachte keuzelijst ontbrak.
- Commit `600826287bd5c27c0474a98597f3f3da99b8cca5` past **uitsluitend** `code/Prototype/tests/test_bl19_no_show_management_v05.py` aan: de testapp gebruikt dezelfde fixtureklok. De vier functionele assertions, testgegevens en productiecode zijn intact.
- Losse test geslaagd, 484 no-showgerelateerde tests geslaagd; volledige lokale suite en [GitHub CI #461](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/45902598378): **1.698 geslaagd, nul mislukt**. CI en codewijziging zijn rechtstreeks in GitHub geverifieerd.

## Afsluiting en vervolg

Dit betreft **functionele acceptatie van het prototype**, niet productieacceptatie of feitelijke Sportlink-mutaties. PR #73 blijft draft en ongemerged totdat de documentatie is gecontroleerd en CKC expliciet toestemming geeft voor de merge. Daarna volgt **Iteratie 11 — Planner Dashboard** volgens de eerdere artist impression, met behoud van geaccepteerde domein-/planningslogica; pas na Iteratie 11 volgt **BL-13 — RPA Sportlink**.
