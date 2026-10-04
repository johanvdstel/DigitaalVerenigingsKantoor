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
