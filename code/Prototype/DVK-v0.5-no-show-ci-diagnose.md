# Afzonderlijke diagnose van de rode no-show-UI-test

Werkbaseline: `prototype-v0.5` @ `8eb32b920468dc260568a6117c0d1bd0aab7aa8a`.
Herstelbranch: `codex/v05-no-show-sportlink-herstel`.

## Vastgesteld bewijs

- De betrokken test `test_revocation_ui_requires_explicit_confirmation_and_shows_current_season_counter` slaagt lokaal met Streamlit 1.64.0.
- Met uitsluitend Streamlit 1.65.0 uit een geïsoleerde tijdelijke map, en dezelfde Python/project/dependency-omgeving, faalt dezelfde ongewijzigde test op de exacte succesmelding.
- Na `text_area.set_value("Uitdrukkelijk besluit").run()` zonder formulierbevestiging is de tekstwaarde met 1.65.0 weer leeg. De latere bevestigingsklik geeft `Een toelichting voor intrekking is verplicht.`; de ontbrekende succesmelding volgt dus uit lege formulierinvoer, niet uit no-showarchitectuur of sanctieafleiding.
- De geïnstalleerde 1.65.0-broncode van `streamlit/testing/v1/element_tree.py`, `ElementTree.get_widget_states`, serialiseert staged formulierwaarden alleen bij een geactiveerde submitknop. Voor oningediende formulieren gebruikt zij de laatst gecommitte waarde. Deze formuliersimulatie is gewijzigd ten opzichte van 1.64.0.
- Door na de controle op niet-schrijven selectie en toelichting opnieuw te stagen en ze samen met de submitklik te verwerken, verschijnt exact `No-show ingetrokken. Actuele no-showteller voor Jeugdlid Thuis in seizoen 2026/2027: 1.`. De juiste no-show wordt ingetrokken, met de oorspronkelijke reden en actor.

## Minimale correctie

Alle bestaande assertions blijven behouden, inclusief niet-schrijven vóór bevestiging, de exacte succesmelding, leeggemaakt tekstveld, onveranderlijk oorspronkelijke feit, reden, actor, tijdstip en het ontbreken van technische identifiers in de weergave. Alleen de AppTest-interactie is aangepast zodat de uiteindelijke submit de ingevulde formulierwaarden bevat.

Er is geen Streamlit-pin, productcodewijziging of testversoepeling nodig voor deze CI-oorzaak. PR #19 is niet gewijzigd. Dit bewijst uitsluitend de oorzaak en correctie van de CI-test; het afzonderlijke Sportlink-no-showarchitectuurherstel volgt uit FR-09/FR-10 en heeft zijn eigen regressievereisten.

## Lokale verificatie

- Relevante baselinetests vóór wijziging: 56 geslaagd.
- Volledige suite na minimale testcorrectie met Streamlit 1.64.0: 287 geslaagd.
- Volledige suite na minimale testcorrectie met geïsoleerde Streamlit 1.65.0: 287 geslaagd.
- De normale projectomgeving is ongewijzigd; de diagnoseversie staat uitsluitend in een tijdelijke map.

## Afbakening en testaantallen

Johan heeft het afzonderlijke naamcontract verduidelijkt: `Achternaam, Voorletter(s) Tussenvoegsel(s) (Roepnaam)`, gekoppeld aan precies één `Rel. code`. Die verduidelijking is gebruikt voor het architectuurherstel en verandert deze CI-diagnose niet.

Onafhankelijke pytest-collectie op git-archieven bevestigt 287 tests op baseline `8eb32b9` en 391 op PR #19-commit `b7854abb05e227a476ba2c2158e2ee721db30a2f`. Het verschil van 104 komt exact uit het daar toegevoegde `tests/test_function_classification_v05.py`. PR #19 is geen ancestor van deze herstelbaseline. Er zijn dus geen 104 tests uit deze herstelbranch verwijderd. Met de 16 nieuwe architectuurtests telt deze PR 303 tests; beide Streamlit-versies doorlopen die volledige suite.

De architectuurfixtures gebruiken feitelijke synthetische Sportlink-inroosteringen. De UI-fixture fixeert bovendien de datum vóór de eerste render, zodat een los rerun niet eerst de selectie van twee gelijk gelabelde diensten beïnvloedt. Dit is fixture-isolatie; de bestaande controles op menselijke labels en afzonderlijke technische sleutels blijven behouden.
