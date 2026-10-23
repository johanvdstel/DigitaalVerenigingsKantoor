# v0.5 — herstel no-showarchitectuur

## Baseline en scope

- Baseline: `prototype-v0.5`, exact `8eb32b920468dc260568a6117c0d1bd0aab7aa8a`.
- Werkbranch: `codex/v05-no-show-sportlink-herstel`, aangemaakt en gecontroleerd op die commit. Bestaande lokale branches zijn niet gereset, gemerged of overschreven.
- Gelezen grondslag: AGENTS.md, herijkte functionele baseline Ledendiensten, FUNCTIONEEL-CONTRACT-v0.5-vervolg.md en DVK-v0.5-gapanalyse-no-showarchitectuur.md, plus Johans expliciete naamcontract.
- PR #19 en ronde 2 van de functieclassificatie zijn niet gewijzigd. Er wordt niet zelfstandig gemerged.

## Architectuurherstel

Een no-show wordt uitsluitend geregistreerd op een geïmporteerde feitelijke Sportlink-inroostering. Tijdelijke DVK-planning en oude prototypeassignments verschijnen niet in de no-showkeuze en worden bij registratie geweigerd.

De bestaande v0.4-client en adapter blijven de bronroute. De adapter reconstrueert de aangetoonde volledige naam uit `Achternaam`, `Voorletter(s)`, `Tussenvoegsel(s)` en `Roepnaam` en koppelt alleen bij precies één match aan `Rel. code`. Ontbrekende onderdelen krijgen geen nieuwe formatteringsregel; ontbrekende en ambigue koppelingen leveren expliciete signalen op. De duurzame sleutel wordt afgeleid van relatiecode, vrijwilligerstaakcode en beide bronmomenten, genormaliseerd naar UTC. API-regelvolgorde, naam en locatie bepalen de sleutel niet.

Het oorspronkelijke no-showfeit bewaart een onveranderlijke snapshot van de gekoppelde persoon, taak, concrete dienst, brontijden, locatie en provenance. Intrekking blijft een afzonderlijk duurzaam feit met reden, actor en tijdstip. Seizoenteller en sanctieafleiding blijven volgens de bestaande semantiek werken, ook na bronverversing of heropenen van de database.

De nieuwe bron- en feitentabellen scheiden vervangbare Sportlink-brondata van duurzame DVK-feiten. Schema-stap 012 maakt lege tabellen aan; zij kopieert of converteert geen oude prototypegegevens. Oude tabellen en historische schema-stappen blijven bestaan maar leveren geen actieve no-showgegevens meer. Er is geen datamigratie of wijziging van een bestaande lokale demonstratiedatabase uitgevoerd.

Een volledige foutloze synchronisatie vervangt de huidige Sportlink-bron en verwijdert de tijdelijke planningswerkvoorraad volgens FR-07. Bij ontbrekende koppelingen, dienstbindingsfouten of transportfouten blijft de vorige bron/planning intact. Duurzame no-shows en intrekkingen blijven altijd behouden.

## Gewijzigde bestanden en reden

Alle paden hieronder zijn relatief aan `code/Prototype`.

| Bestand(en) | Reden |
| --- | --- |
| `dvk/model.py`, `dvk/real_data_import.py` | CSV-naamopbouw en expliciete Sportlink-persoonskoppeling via bestaande ledenparser. |
| `dvk/vrijwilligers_adapter.py` | Canonieke feitelijke inroostering, logische sleutel, snapshot en bronvalidatie. |
| `dvk/no_show.py` | Onveranderlijke broncontext aan het no-showfeit toevoegen. |
| `dvk/persistence/sportlink_bookings.py`, `dvk/persistence/sqlite.py` | Vervangbare broninroosteringen opslaan en ontsluiten. |
| `dvk/persistence/migrations.py`, `dvk/persistence/no_show_records.py` | Nieuwe feiten duurzaam en fysiek onveranderlijk opslaan, zonder oude prototypefeiten te migreren. |
| `dvk/application_services.py` | Bron-only registratie, atomische bronverversing en intrekking met bewaarde context. |
| `streamlit_app.py` | Bestaande read-only Sportlink-route toegankelijk maken en uitsluitend broninroosteringen tonen. |
| `tests/sportlink_fixtures.py` | Synthetische API-fixtures via dezelfde adapter, met concrete broncontext. |
| `tests/test_no_show_sportlink_v05.py` | 16 nieuwe regressies voor naamcontract, ambiguïteit, identiteit, bron-only service/UI, duurzame context en synchronisatie. |
| `tests/test_gate9_application_v05.py`, `tests/test_gate9_hardening_v05.py`, `tests/test_gate9_persistence_v05.py`, `tests/test_gate10b_persistence_v05.py`, `tests/test_gate10c_application_v05.py` | Achterhaalde prototypefixtures vervangen door Sportlink-bronfixtures met behoud van functionele regressiesemantiek. |
| `tests/test_gate10ade_ui_v05.py` | Bronfixtures, vaste testdatum en afzonderlijk bewezen AppTest-formuliercorrectie; assertions behouden. |
| `DVK-v0.5-no-show-ci-diagnose.md`, dit rapport | CI-oorzaak en architectuurherstel afzonderlijk vastleggen. |

## Verificatie

- Volledige regressiesuite: **303 geslaagd** met project-Streamlit 1.64.0.
- Volledige regressiesuite: **303 geslaagd** met geïsoleerde Streamlit 1.65.0.
- `git diff --check`: schoon.
- De oorspronkelijke baseline telt 287 tests. De eerdere PR #19 telt 391 door 104 afzonderlijke functieclassificatietests. Beide aantallen zijn op de betreffende commits met pytest-collectie geverifieerd. Dit herstel voegt 16 tests toe aan de baseline; bestaande casefamilies C/W/I/R zijn niet gewijzigd.
- Gerichte testselectie: **100 geslaagd**, inclusief de bestaande v0.4-client/adapter/import en de gewijzigde no-showservice-, opslag-, intrekking- en UI-tests. Een eerste selectiecommando verwees naar twee onjuiste testbestandsnamen en verzamelde geen tests; het gecorrigeerde commando is volledig geslaagd. GitHub-CI-status wordt bij oplevering gerapporteerd.

## Resterende beperkingen

Er is geen live Sportlink-uitvraag uitgevoerd; tests gebruiken synthetische bronresponsen. De UI gebruikt de bestaande concrete dienstcatalogus en expliciet ingevoerde taakcodes. Een bronregel zonder unieke overeenkomstige dienst wordt gesignaleerd en verhindert publicatie van de bronverversing. De koppeling van namen met ontbrekende onderdelen blijft bewust onopgelost totdat een aanvullend broncontract is geaccepteerd.

De afzonderlijke CI-oorzaak is een gewijzigde AppTest-formuliersimulatie in Streamlit 1.65, niet de architectuurafwijking. Zie het afzonderlijke diagnoserapport. Groene tests/CI vormen geen functionele acceptatie; acceptatie en merge blijven bij Johan/CKC.

## Reviewherstel — afzonderlijk tijdveld (5 oktober 2026)

Context: voortzetting op dezelfde werkbranch vanaf PR-head `225313a3d7e70a23fd60218ed1979893f5075635`; integratiebaseline blijft `prototype-v0.5` @ `8eb32b9`, functioneel geaccepteerde baseline blijft v0.4. De opdracht beperkt zich tot het blokkerende parsingpunt; bronhouder is Sportlink, met de bewezen Rooster2-verwerking als referentie.

Vastgesteld feit: `_parse_datetime()` keerde bij een datum met `T` direct terug en negeerde het afzonderlijke tijdveld. Daardoor werd de aangetoonde bronvorm `2026-10-10T00:00:00+0200` plus `10:00` ten onrechte 00:00; concrete dienstkoppeling en daarmee no-showregistratie konden mislukken. [Rooster2/app.py, normalize_volunteers](https://github.com/johanvdstel/Rooster2/blob/main/app.py#L579-L620) verwerkt datum- en tijdvelden apart, en gebruikt alleen de datum/tijdtimestamp als tijdbron wanneer het afzonderlijke veld ontbreekt. Geraadpleegde bestandsblob: `e7e2be506bb46f141e7fec6567a530340ce3f136`.

Geaccepteerde eis: datumdeel combineren met het afzonderlijke tijdveld en de bronoffset behouden, voor zowel `+0200` als `+0100`; bestaande ondersteunde vormen blijven werken. De minimale wijziging gebruikt de bestaande ISO-datum- en kloktijdparsing. Er is geen algemene parser, extra dependency, beleidswijziging of datamigratie toegevoegd.

Gewijzigde bestanden in deze vervolgcommit:

- `dvk/vrijwilligers_adapter.py`: bij een afzonderlijk tijdveld het geparste datumdeel en bron-tzinfo gebruiken; zonder tijdveld het oorspronkelijke timestampgedrag behouden.
- `tests/test_no_show_sportlink_v05.py`: twee bronvormtests (`2026-10-10T00:00:00+0200` en `2026-11-07T00:00:00+0100`, telkens 10:00–12:30), inclusief dienstkoppeling, offset, logische sleutel en duurzame no-showcontext. Zeven compatibiliteitscases dekken de bestaande datum-/tijdvormen en ISO-timestamps zonder afzonderlijk tijdveld. Bestaande verwachtingen zijn niet aangepast.
- Dit rapport: herleiding, scope en verificatie van het reviewherstel.

Verificatie: **81 gerichte tests geslaagd**; volledige suite **312 geslaagd** met zowel Streamlit 1.64.0 als geïsoleerde 1.65.0; `git diff --check` schoon. De groei van 303 naar 312 bestaat exact uit de negen nieuwe parsingregressies. GitHub CI wordt na push opnieuw gecontroleerd en in PR/eindrapportage vermeld. PR #19 blijft onaangeroerd en er wordt niet gemerged. De eerder genoemde beperkingen blijven gelden; deze correctie vereist geen nieuw functioneel of architectuurbesluit.
