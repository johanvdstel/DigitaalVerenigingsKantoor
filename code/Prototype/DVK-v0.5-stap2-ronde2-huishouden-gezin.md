# DVK v0.5 — Stap 2 ronde 2: huishouden en minderjarig gezin

## Context en grondslag

- Gecontroleerde startbranch: `origin/prototype-v0.5`; exacte startcommit: `115e365ca5e33aa5c5377313e8c35e3e4e8c3c07`, na PR #23.
- Werkbranch: `codex/v05-step2-ronde2-huishouden-gezin`; PR-doel: `prototype-v0.5`. Niet zelfstandig mergen.
- Ontwikkelfase: v0.5-integratie, geen integrale functionele releaseacceptatie. De functioneel geaccepteerde technische v0.4-baseline en C/W/I/R-cases blijven regressiebasis.
- Gelezen context: AGENTS.md, ontwikkelworkflow, BASELINE-v0.4, herijkte functionele baseline Ledendiensten (B-01–B-14), vervolgcontract en beide ronde-1-rapporten.
- Geaccepteerde eisen: de expliciete ronde-2-opdracht van Johan, aansluitend op B-05/B-06/B-07/B-10/B-11. De opdracht bevestigt de daadwerkelijke kolomnamen en specificeert postcode + huisnummer als minimale adresvolledigheid, met toevoeging wanneer ingevuld.
- Bronhouder: Sportlink voor leden, adres, ouderregistraties, functies, commissies en Teams. CKC bepaalt classificatie en beleidsuren; DVK leidt de verwachting af. De Vrijwilligerscommissie stelt A menselijk vast en registreert dat handmatig in Sportlink. Deze ronde vergelijkt dat besluit nog niet met DVK.

## Vastgestelde afwijking en minimale oplossing

Vastgesteld in `dvk/real_data_import.py`: de bestaande optionele adres-/oudervelden worden nog niet gevuld. Vastgesteld in `dvk/duty.py`: historische prototypegevallen vergelijken vrije adresstrings en expliciete relaties op één gedeelde ouder. De ronde-1-classificatie staat nog los van brongebonden taakplicht.

De minimale brongebonden aanvulling bewaart de historische case-engine en fixtures. De publieke ingang is `RealDataImportResult.derive_member_duties(as_of, policy=None)`; deze roept de afzonderlijke domeinafleiding aan. Zo gebruikt de ronde-2-route de werkelijke bronfeiten en classificatie zonder historische C/W/I/R-verwachtingen te herschrijven. De legacy-case-engine, UI en planning zijn niet omgeschakeld in deze bronstap. Gebruik voor ronde 2 deze nieuwe ingang, niet de legacy `derive_duty_qualification`.

Proportionaliteit: zonder mapping blijven de afgesproken vergelijkingsfeiten onbeschikbaar; zonder directe paarvergelijking blijft de oude één-ouderregel leidend; zonder driewaardige uitkomst zou ontbrekend bewijs als taakplicht worden gepresenteerd. Geen migratie, opslaguitbreiding, reconstructie, refactor of nieuwe beleidsconfiguratie nodig. Prototype-/operationele bestanden worden niet gewijzigd. Nieuwe tests zijn synthetische ontwikkelregressies; bestaande geaccepteerde fixtures blijven intact.

## Uitvoering en acceptatiecriteria

| Bestand | Reden en gedrag |
| --- | --- |
| `dvk/model.py` | Optionele straat, plaats en contact-via-ouder als broncontext; afzonderlijke conflictindicatoren voor adres/ouders. Bestaande positionele velden blijven staan. |
| `dvk/real_data_import.py` | Exacte mapping van `Postcode`, `Huisnummer`, `Toevoeging`, `Straatnaam`, `Plaats`, `Contact via ouder/verzorger`, beide oudernaamvelden en bestaande `Geb.dat.`/`Rel. code`. Veldprovenance bewaart oorspronkelijke waarden, ook van dubbele regels. Conflicten worden expliciet gesignaleerd, niet samengevoegd tot een fictief volledig adres/gezin. Met `duty_path=None` wordt geen urenbron gelezen. |
| `dvk/member_duty.py` | B-05/B-06/B-07 met ronde-1-classificatie, peildatum en configureerbare uren. Geen vrije adresfallback, fictieve ouderpersonen, relaties of transitieve clusters. |
| `tests/test_member_duty_v05.py` | 41 nieuwe gerichte regressies, inclusief echte headers in synthetische CSV's en volledige import → classificatie → afleiding. |
| Dit rapport | Context, herleiding, publieke ingang, verificatie en beperkingen. |

Adresidentiteit normaliseert uitsluitend postcodehoofdletters/spaties en omringende witruimte van huisnummer/toevoeging. Een ingevulde toevoeging is onderdeel van de identiteit. Straat/plaats blijven broncontext. Oudernamen worden als volledige registraties vergeleken, met behoud van cardinaliteit en zonder belang van volgorde; een gedeelde achternaam is geen bewijs.

Per lid bevat de uitkomst `status` (`taakplichtig`, `vrijgesteld`, `niet betrouwbaar beoordeelbaar`), `expected_required_hours` (beleidsuren, 0 of onbekend/None), afzonderlijke gronden, ondersteunende personen/criteria, oorspronkelijke geclassificeerde registraties, relevante canonieke bronfeiten en provenance, peildatum en beleidsversie. Uitkomstsemantiek blijft `DERIVED`; bronprovenance blijft `SOURCE_FACT`.

B-03/B-02 bepalen relevante spelende minderjarigen. De afmelddatum is de eerste niet-actieve dag. De oudste wordt uitsluitend onder rechtstreeks kwalificerende minderjarigen gezocht. Een bewezen persoonlijke of huishoudelijke vrijstelling blijft geldig wanneer een andere grond onvoldoende bewijs heeft; die onzekerheid blijft afzonderlijk zichtbaar. Betaalde functies en eretitels behouden hun afzonderlijk verklaarbare categorie in de ondersteunende ronde-1-classificatie en geven geen huishoudvrijstelling.

B-10 voorkomt een nieuwe beleidskeuze bij gelijke geboortedatums: DVK kiest geen kind op naam of relatiecode, maar toont onzekerheid. Een eventuele toekomstige verdeelregel vereist een functioneel besluit. Onbekende functieclassificaties, relevante ontbrekende geboortedatums, onbekend lidmaatschap en onvoldoende/conflicterende vergelijkingsgegevens worden eveneens zichtbaar gemaakt. Geen automatische planning of registratie volgt uit deze afleiding.

## Verificatie

- Exacte startbaseline, vóór wijzigingen: **416 tests geslaagd**.
- Nieuwe ronde-2-tests plus bestaande real-data-import en functieclassificatie: **173 tests geslaagd** (41 + 28 + 104).
- Volledige regressiesuite na laatste codewijziging: **457 tests geslaagd**.
- Geen bestaande tests of fixtures gewijzigd; geen verwachtingen versoepeld.
- `git diff --check`: schoon.

De eerste testaanroep via systeem-Python kon niet starten omdat pytest daar ontbreekt; alle gerapporteerde verificaties gebruiken de bestaande `code/Prototype/.venv/bin/python -m pytest`. Een eerste aanmaakcommando voor de nieuwe module gebruikte een onjuist relatief pad en maakte geen bestand; dit is gecorrigeerd vóór de nieuwe tests. Er waren geen falende testasserties.

CI-status en commit worden na push in PR/eindrapportage vermeld. Groene CI bewijst technische regressie, geen functionele acceptatie.

## Grenzen en resterende punten

- Geen nieuwe import, vergelijking of aanpassing van A/B/C/D/E. Bestaande legacy-urenimport blijft voor de bestaande regressies beschikbaar; ronde 2 gebruikt `duty_path=None`.
- Geen migraties, Sportlink-mutaties, urenoverdracht, plannerbesluitopslag, UI-ombouw of automatische scheduling.
- Geen actuele persoonsdata of live Sportlink-bronnen gebruikt; gecontroleerde headers zijn expliciet door Johan verstrekt, inhoudelijke regressies zijn synthetisch.
- Geen nieuwe functionele regel ingevoerd. Gelijke geboortedatums blijven onder B-10 onzeker; een verdeelregel is niet nodig om deze bronstap correct op te leveren.
- De oude case-engine blijft historische prototypecompatibiliteit; een latere UI/planner-aansluiting moet expliciet de nieuwe brongebonden ingang gebruiken. Dit rapport presenteert de legacy-route niet als herijkte ronde-2-implementatie.
