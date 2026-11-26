# Levensduur tijdelijke planning — oplevering

## Baseline, contract en proportionaliteit

- Baseline: `prototype-v0.5` @ `8ccdb4739b683195961bc8d99b981ccdef410d03`, inclusief gemergede PR #34.
- Werkbranch: `codex/tijdelijke-planning-levensduur`; PR-doel `prototype-v0.5`. Geen merge door Codex.
- Fase: v0.5-prototype, nog geen integrale releaseacceptatie; v0.4 op main blijft de geaccepteerde releasebaseline. BL-02 en BL-04 blijven ongewijzigd.
- Functionele opdracht: tijdelijke planning behouden tijdens reruns, navigatie en nieuwe browserverbindingen binnen hetzelfde proces; bij echte procesherstart opruimen vóór eerste planningstoegang. Eén actieve periode; bij periodewisseling met werk eerst bevestigen, bij annuleren behouden. Succesvolle bronverversing wist werk; fouten behouden bron en werk.
- Deze expliciete opdracht begrenst de eerdere FR-02-persistentiesemantiek. PR #15 is achterhaald en is niet hergebruikt. Geen gezamenlijke API-/CSV-afsluiting.
- Sportlink blijft bronhouder van feitelijke inroosteringen; planner beslist en voert zelf in Sportlink in. DVK schrijft niet naar Sportlink. Broncontracten, taakplicht, kandidaatregels en no-showregels zijn niet gewijzigd.
- Vastgesteld probleem: `temporary_planning` werd ook na procesherstart teruggelezen; periodekeuze kende geen bevestiging vóór verlies van werk. Een kleine runtimebewaking plus bestaande SQLite-transacties volstaat. Geen nieuwe databasearchitectuur, migratie, TTL of achtergrondtaak nodig.
- Gegevensstatus: actieve tijdelijke werkvoorraad is verwijderbaar. No-shows, intrekkingen, bookingcontext en andere duurzame gegevens blijven behouden. Alle tests gebruiken synthetische gegevens en wegwerpdatabases; geaccepteerde regressiefixtures zijn niet verwijderd.

## Wijzigingen en redenen

| Bestand | Reden |
| --- | --- |
| `dvk/planning_runtime.py` | Procesgebonden voorbereiding en één actieve periode per applicatiedatabase; publieke functies `prepare_planning()` en `choose_period()` |
| `streamlit_app.py` | Voorbereiden vóór eerste planningstoegang; waarschuwing, bevestigen en annuleren van periodewisseling; actieve periode hervatten in nieuwe browsersessie; oude dienst-/voorstelselecties wissen bij daadwerkelijke periodewisseling |
| `tests/test_planning_runtime_v05.py` | Negen regressies voor proces-/browserlevensduur, atomiciteit, gelijktijdige eerste toegang, fouten, navigatie, filters en behoud van duurzame context |
| `tests/test_planning_workqueue_v05.py` | Bestaande reloadfixture na procesvoorbereiding aanmaken; in bevestigingstest eerst periode kiezen en daarna dienst selecteren. Bestaande functionele assertions blijven behouden |
| Dit rapport | Herleiding, ontwerp, resultaten, grenzen en lokale acceptatie |

## Ontwerp en garanties

De geïmporteerde runtime-module bewaart een markering en actieve periode per canoniek databasepad in het procesgeheugen. Een `RLock` beschermt gelijktijdige eerste toegang. Dit is geen Streamlit Session State of cache en wordt niet opnieuw aangemaakt bij gewone script-reruns of nieuwe databaseobjecten.

Bij de eerste planningstoegang gebruikt voorbereiding een bestaande Unit of Work en `BEGIN IMMEDIATE`. Alleen de actieve tijdelijke posities worden verwijderd. De markering wordt pas na geslaagde commit toegevoegd. Een fout rolt de verwijderingen terug en verlaat het renderpad vóór planning, kandidaten of tijdelijke posities worden getoond. Een volgende toegang probeert opnieuw. De bestaande databasefoutgrens houdt taakplichtcontrole bereikbaar.

Een gewenste periode wordt vergeleken met de procesgebonden actieve periode. Zonder werk wordt direct gewisseld. Met werk blijft de oude periode actief totdat de planner expliciet bevestigt. Tijdens deze vraag worden geen diensten/kandidaten van de nog niet geactiveerde periode aangeboden. Annuleren herstelt de eerdere periodevelden. Na bevestiging worden alle posities transactioneel verwijderd; pas na commit verandert de actieve periode. Een fout kan daardoor geen gedeeltelijke clear of periodewisseling publiceren.

Een nieuwe browserverbinding begint met de reeds actieve periode, weergegeven via Aangepast. Dag/Week/Aangepast wisselen zonder wijziging van de werkelijke datums is geen periodewisseling. Bij Aangepast blijft de einddatum geldig wanneer de begindatum voorbij de oude einddatum wordt gezet. Gewone filters en schermwisselingen wissen geen werk.

De bestaande `NoShowApplicationService.synchronize()` blijft ongewijzigd, inclusief VRIJ-01. SQLite-repositories, opslagtabellen, schema 012 en duurzame no-showcontext blijven ongewijzigd. Andere opgeslagen voorstellen/beslissingen worden niet opgeschoond en worden niet opnieuw tot actieve werkvoorraad verheven.

## Tests en resultaten

Tests uitgevoerd met Python 3.11.16, Streamlit 1.64.0 en pytest 9.1.1 in een tijdelijke virtualenv. De bestaande repository-venv bevatte macOS-dataless bestanden en blokkeerde tijdens import/bestandslezing; daarom is een tijdelijke omgeving met dezelfde Streamlit-/pytest-versies gebruikt. Projectdependencies zijn niet aangepast. De baselinecontrole gebruikt een tijdelijke export van de exacte baselinecommit.

- Bestaande gerichte baselinecontrole: **70 geslaagd**, 0 mislukt, 0 overgeslagen.
- Gerichte runtime-/werkvoorraad-/navigatie-/bronregressie na wijziging: **79 geslaagd**, 0 mislukt, 0 overgeslagen.
- Volledige regressie: **693 geslaagd**, 0 mislukt, 0 overgeslagen.
- `git diff --check`: geslaagd.
- Werkelijke subprocessen bewijzen dat dezelfde database bij iedere nieuwe processtart wordt ontdaan van oude tijdelijke planning, terwijl nieuwe posities binnen dat proces behouden blijven en de overige tabellen exact gelijk blijven.
- Nieuwe AppTest-instanties bewijzen nieuwe browsersessies binnen hetzelfde proces. Een echte browser-refresh is niet afzonderlijk via browserautomatisering uitgevoerd; hiervoor staan de lokale acceptatiestappen hieronder.
- Tussentijds: één gerichte test faalde doordat een oude dienstselectie tegelijk met een periodewisseling werd gezet. Dat is na de nieuwe afspraak bewust ongeldig: de test kiest nu eerst de periode en daarna de dienst. De capaciteit-/bevestigingsassertions zijn behouden. De overige onderbrekingen betroffen de lokale testomgeving, geen verborgen functionele testfouten.
- CI-status en definitieve commit/PR staan in de oplevering. Technische regressie is geen functionele acceptatie.

## Korte lokale acceptatie

Gebruik uitsluitend een synthetische wegwerpomgeving. Start vanuit `code/Prototype` met:

```sh
.venv/bin/python -m streamlit run streamlit_app.py
```

1. Open Ledendienst Planning, kies een periode/dienst en bevestig een kandidaat. Controleer tijdelijke bezetting en werkvoorraad.
2. Wijzig een ander filter of herhaal een gewone interactie; planning blijft bestaan. Wissel naar Startscherm en Taakplichtcontrole en terug: hetzelfde resultaat.
3. Refresh de browser of open de app opnieuw in een nieuwe browsersessie, zonder de server te stoppen. De actieve periode en tijdelijke indelingen blijven beschikbaar.
4. Kies een andere periode: waarschuwing dat alle tijdelijke indelingen verloren gaan. Annuleren behoudt oude periode en werk. Opnieuw wijzigen en bevestigen verwijdert al het werk en toont de nieuwe periode. Met lege werkvoorraad verloopt wijzigen direct.
5. Maak opnieuw tijdelijke planning. Stop het Streamlit-proces in de terminal en start hetzelfde commando opnieuw met dezelfde database. Open planning: oude tijdelijke indelingen zijn weg. Nieuwe indelingen blijven daarna bij reruns behouden.
6. Controleer aanwezige synthetische no-showhistorie en intrekkingen: die blijven behouden. Foutinjectie en Sportlink-succes-/foutscenario's worden geautomatiseerd met synthetische bronnen gecontroleerd; geen echte Sportlink-mutaties of beschadiging van lokale databases nodig.

## Grenzen

Eén planner, één Streamlit-applicatieproces en één actieve periode; geen ondersteuning voor meerdere gelijktijdige applicatieprocessen toegevoegd. Opstartopruiming vindt plaats vóór de eerste planningstoegang, niet bij het alleen openen van het startscherm. Tijdens stilstand kunnen tijdelijke SQLite-rijen dus nog op schijf staan; ze worden vóór hergebruik verwijderd. Geen fysieke veilige-verwijdergarantie of afzonderlijke afsluitprocedure.

Geen resterend functioneel of architecturaal beslispunt binnen deze opdracht vastgesteld. Functionele acceptatie en merge blijven bij opdrachtgever.
