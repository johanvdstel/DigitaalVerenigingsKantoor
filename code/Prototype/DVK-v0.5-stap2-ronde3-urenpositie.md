# DVK v0.5 — Stap 2 ronde 3: urenpositie

## Context en herleiding

- Startbranch: `prototype-v0.5`; exacte startcommit: `9b50f7e8fdadc7885d2aadeb1ab9bf6a9f921274`.
- Werkbranch: `codex/v05-step2-ronde3-urenpositie`; PR-doel: `prototype-v0.5`. Geen zelfstandige merge.
- Ontwikkelfase: v0.5-integratie. De technisch/functioneel geaccepteerde v0.4-baseline met C/W/I/R blijft regressiebasis; deze tests zijn ontwikkelregressies, geen integrale v0.5-acceptatie.
- Gecontroleerde context: AGENTS.md, `docs/ontwikkelworkflow-codex.md`, Prototype README, herijkte functionele baseline B-01–B-14 en ronde-2-rapport/implementatie/tests.
- Geaccepteerde eis: de expliciete ronde-3-opdracht bevestigt zes werkelijke kolommen, hun betekenis, E=A-B-C-D en de koppeling Relatiecode ↔ Rel. code; B-09/B-10 vereisen uitlegbare vergelijking en betrouwbare fallback.
- Bronhouders: Sportlink bewaart de administratieve urenpositie en leden-/functie-/commissie-/teamregistraties. CKC bepaalt beleid; DVK leidt de verwachting af; de Vrijwilligerscommissie stelt A menselijk vast en registreert dit handmatig in Sportlink.

## Vastgestelde afwijking en proportionaliteit

Vastgesteld in `dvk/real_data_import.py`: alle zes headers en de juiste E-formule bestaan al, maar de historische A-vergelijking gebruikt een extern meegegeven getal. De ronde-2-afleiding is nog niet aangesloten. Alleen E heeft veldprovenance, met een berekende waarde onder SOURCE_FACT. Ongeldige urenregels worden expliciet afgewezen, maar verliezen hun oorspronkelijke veldwaarden. Numerieke float-conversie kan grote gehele waarden afronden.

Minimale oplossing: gebruik de bestaande import/mapping/formule, voeg een afzonderlijke domeincontrole met publieke ingang toe en bewaar de zes bronvelden, ook voor afgewezen regels. Exacte numerieke parsing voorkomt afronding en weigert niet-eindige waarden. Zonder deze maatregelen zou A zonder ronde-2-gronden worden vergeleken en zou bronbewijs verloren gaan of als berekening worden gepresenteerd. Er is geen migratie, opslag of historische reconstructie nodig. Alleen synthetische ontwikkeldata toegevoegd; geaccepteerde fixtures ongewijzigd.

## Bestanden en acceptatiecriteria

| Bestand | Reden |
| --- | --- |
| `dvk/real_data_import.py` | Publieke `compare_required_hours(as_of, policy=None)`, veldprovenance van de zes minimale kolommen vóór validatie, exacte gehele numerieke parsing. |
| `dvk/hours_control.py` | Domeincontrole aangesloten op `derive_member_duties`; driewaardige status, verwachting met gronden/bronfeiten, geregistreerde A, urenrecords, provenance en signalen. |
| `tests/test_hours_control_v05.py` | 42 synthetische ontwikkelregressies voor de opdracht en betrouwbaarheid van parsing/koppeling. |
| Dit rapport | Context, broncontract, verificatie, beperkingen en overdracht. |

De publieke controle levert de volledige door ronde 2 afgeleide ledenpopulatie, inclusief relevante leden en verklaarbare vrijstellingen. Geen UI/planner wordt omgeschakeld. Na functionele review is de historische `expected_required_hours`-importparameter verwijderd: de actuele brongebonden A-controle haalt haar verwachting uitsluitend uit ronde 2, met dezelfde configureerbare beleidsuren en peildatum.

`RequiredHoursControl.status` is `overeenkomst`, `afwijking` of `niet betrouwbaar beoordeelbaar`. De complete `expectation` bewaart de DVK-gronden, ondersteunende bronfeiten, beleidsversie en peildatum. Een verschil geeft `REQUIRED_HOURS_REASSESSMENT`: herbeoordeling van een eerdere menselijke registratie, geen uitspraak dat Sportlink fout is.

Technische toepassing van de betrouwbaarheidseis: een ontbrekende/afgewezen urenpositie, meerdere urenposities, onbekende ronde-2-verwachting of relevant ERROR-signaal levert geen zekere A-status. Ook bij een E-formuleverschil blijven verwachte en geregistreerde A zichtbaar, maar is de controlestatus onzeker. Waarschuwingen over actualiteit blijven zichtbaar zonder arbitraire ouderdomsgrens. Importsignalen over niet-koppelbare regels blijven in `RealDataImportResult.signals`; ze worden niet op naam aan een lid toegewezen.

E uit de export blijft in `source_remaining_hours`; berekende E staat apart in `position.E`. Negatieve correcte E is geldig. Positieve B verlaagt E; negatieve B verhoogt E. De bronprovenance bewaart oorspronkelijke tekst en alleen opgeschoonde brontekst als normalized_value; de berekende E wordt niet als bronfeit opgeslagen. Meerdere bronregels blijven herkenbaar via relatiecode plus regelnummer. Extra kolommen worden niet in de urenprovenance opgenomen.

## Minimale downloadprocedure

Voor `Overzicht per periode` zijn uitsluitend vereist:

1. `Relatiecode`
2. `Verplichte punten` (A: menselijk vastgestelde registratie)
3. `Gecorrigeerde punten` (B)
4. `Voldaan` (C)
5. `Nog ingedeeld` (D)
6. `Niet ingedeeld` (aangeleverde E)

`Volledige naam` is hoogstens menselijke controlecontext en nooit koppelsleutel. Adres, telefoon, e-mail, ouders, nationaliteit, bankvelden en andere ledenvelden zijn voor deze export geen importvereiste. Onbekende extra kolommen blokkeren de import niet. Later wordt voor iedere andere Sportlink-export eveneens een expliciete minimale kolomselectie vastgesteld. Seizoenscontext blijft de bestaande expliciet meegegeven `source_period`; er is geen nieuwe seizoenherkenning ingevoerd.

## Verificatie

- Voorgeschreven baseline-suite vanuit `code/Prototype`: **457 passed**.
- Gerichte ronde-3-, ronde-2- en bestaande importtests: **111 passed** (42 + 41 + 28).
- Volledige regressiesuite: **499 passed**.
- `git diff --check`: schoon.
- Geen bestaande tests, caseverwachtingen of fixtures gewijzigd.

Een eerste baseline-aanroep vanuit de repositoryroot verzamelde daarnaast 11 oude `test_prototype_cases.py`-tests buiten de voorgeschreven suite: 11 failed, 457 passed. Die falen al op de startcommit en vallen buiten deze iteratie. Een eerste gerichte aanroep vanuit dezelfde verkeerde directory kon `dvk` niet importeren en stopte tijdens collection. Beide aanroepen zijn herhaald vanuit de in workflow en CI voorgeschreven `code/Prototype`; daar zijn bovenstaande resultaten behaald. Geen falende asserties in de voorgeschreven suite.

Commit en CI-status worden bij de PR/eindrapportage vermeld. Groene CI vormt geen functionele acceptatie.

## Grenzen en beslispunten

Geen automatische Sportlink-correcties, urenoverdracht, B-14-besluitopslag, UI/dashboard, kandidaatselectie, planning, no-showwijziging of historische reconstructie. Geen live exports of persoonsgegevens gebruikt. Hele punten/uren blijven het bestaande importercontract; fracties worden expliciet afgewezen, niet afgerond. De opdracht geeft geen nieuwe fractie-afspraak.

Geen functioneel of architecturaal besluit nodig voor deze ronde. Functionele review/acceptatie blijft nodig vóór merge. Integrale v0.5-acceptatie, echte broninhoudvalidatie en latere workflowaansluiting blijven buiten deze oplevering.

## Correctie na functionele review: één brongebonden A-controle

Start van deze correctie: dezelfde werkbranch/PR #25, gecontroleerde head `86e0d6b4cf5626581f15e674c6358206b3202d9e`. Oorspronkelijke ronde-3-startbasis blijft ongewijzigd. De expliciete reviewopdracht autoriseert verwijdering van de dubbele importvergelijking en herijking van tests die uitsluitend die route bewaken; geen nieuwe functionele ronde.

### Repository-breed afhankelijkheidsonderzoek

Vastgesteld met `rg` in de volledige repository, inclusief verborgen bestanden (uitgezonderd Git-objecten en de virtuele omgeving):

- `SportlinkRealDataAdapter.load_exports(expected_required_hours=...)`, `DutyImportRecord.expected_required_hours`, `required_hours_mismatch` en de producer van `REQUIRED_HOURS_MISMATCH` stonden uitsluitend in `dvk/real_data_import.py`.
- De enige aanroep met de externe verwachting stond in `tests/test_real_data_import_v04.py::test_r09_expected_a_mismatch_is_signalled_not_corrected`. Geen applicatie-, UI-, planner- of andere importer-aanroep gebruikt die parameter/property/waarde.
- `dvk/season_closing.py` en de bijbehorende test gebruiken `DutyImportRecord`, maar alleen registratie en bron-/berekende urenpositie; de verwijderde velden zijn daar geen afhankelijkheid.
- Het ronde-3-rapport beschreef behoud van de parameter. De technische impactanalyse vermeldde de oude importerwaarschuwing als toen ondersteunde functionaliteit. Beide documenten zijn bijgewerkt.
- `member_duty.py` en `hours_control.py` gebruiken gelijknamige afgeleide verwachtingsvelden; die zijn noodzakelijk voor de gezaghebbende route en blijven intact.
- De historische case-engine `duty.py` heeft een eigen `expected_required_hours()` en het kleine-letter-signaal `sportlink_required_hours_mismatch`, met gebruik in dashboard, W/I/policy-tests en case-runners. Dit is de afzonderlijke historische case-route, niet een afhankelijkheid van de verwijderde importerparameter. Deze geaccepteerde historische route is buiten de correctiescope en ongewijzigd. De uitspraak “één gezaghebbende A-controle” geldt voor de actuele brongebonden v0.5-route, niet voor iedere historische case-engine in de repository.

Verwijdering is veilig binnen de expliciete opdracht: geen geaccepteerde v0.5-gebruiker is afhankelijk van de genoemde importvergelijking. R09's geaccepteerde functionele eis — verschil signaleren zonder automatische correctie — blijft behouden via de nieuwe brongebonden controle. Alleen de test van de expliciet vervallen dubbele route is herijkt; BASELINE-v0.4 en overige historische cases/fixtures blijven ongewijzigd.

### Wijzigingen en regressiebescherming

| Bestand | Correctie |
| --- | --- |
| `dvk/real_data_import.py` | Externe verwachtingsparameter, recordveld, mismatchproperty en oud importsignaal verwijderd. Import doet alleen bronmapping, numerieke/koppelvalidatie en E-formulecontrole. |
| `tests/test_real_data_import_v04.py` | R09 vergelijkt nu de bron-A=10 met de uit bestaande vrijstellende functies afgeleide A=0 via `compare_required_hours()`; verwacht `afwijking` en `REQUIRED_HOURS_REASSESSMENT`, behoud van A=10 en afwezig oud importsignaal. Geen testcase verwijderd. |
| `tests/test_hours_control_v05.py` | Twee nieuwe tests: betrouwbare bronpositie met A=3 geeft geen importerwaarschuwing, daarna precies één domeinsignaal voor herbeoordeling; publieke import-API/record hebben geen externe verwachting of mismatchproperty meer. |
| `TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md` | Historische beschrijving aangevuld met actuele verwijdering en gezaghebbende route. |
| Dit rapport | Afhankelijkheden, veilige verwijdering, architectuurgrens en nieuwe verificatie. |

Er bestaat nu voor de actuele brongebonden v0.5-route uitsluitend `derive_member_duties()` → `compare_required_hours()`. De domeincontrole is ongewijzigd, genereert `REQUIRED_HOURS_REASSESSMENT` bij verschil en muteert geen bronfeiten/importsignalen. E-semantiek/formulecontrole, B-05/B-06/B-07, classificatie, UI, planning, no-shows en B-14 zijn ongewijzigd.

### Nieuwe verificatie

- Gerichte suite vóór correctie: **111 passed**.
- Ronde-3-tests: **44 passed**; ronde-2-tests: **41 passed**; bestaande importtests inclusief herijkte R09: **28 passed**; gezamenlijk **113 passed**.
- Volledige regressiesuite na correctie: **501 passed**.
- Repository-brede zoekcontrole: geen verwijderde API/property of oud hoofdletter-importsignaal in productiecode; resterende exacte namen staan alleen als afwezigheidsasserties of historische toelichting. Afgeleide verwachtingsvelden en de expliciet onderscheiden historische case-route blijven aanwezig.
- `git diff --check`: schoon.
- Een eerste append voor de twee nieuwe tests gebruikte vanuit `code/Prototype` onterecht opnieuw dat pad en maakte geen wijziging; het pad is gecorrigeerd, waarna beide tests zijn uitgevoerd. Geen falende testasserties.

Commit en onafhankelijke CI-uitkomst van deze correctie worden bij PR #25 en in de eindrapportage vastgelegd. Geen merge; functionele acceptatie blijft vereist. Geen nieuw besluitpunt of resterende afhankelijkheid van de verwijderde route aangetroffen.
