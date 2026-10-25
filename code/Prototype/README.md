# DVK Prototype v0.4 — functioneel geaccepteerde baseline

**Status: functioneel geaccepteerd op 13 september 2026.**

Dit is het uitvoerbare prototype van het Digitaal Verenigingskantoor (DVK) voor de werkstroom Ledendiensten & Vrijwilligersbeleid. Prototype v0.4 bouwt voort op de volledig behouden v0.3-baseline en voegt read-only real-data-integratie toe.

De formele actuele baseline staat in [`BASELINE-v0.4.md`](BASELINE-v0.4.md). [`BASELINE-v0.3.md`](BASELINE-v0.3.md) blijft de historische en regressieve grondslag voor C01–C22, W01–W13 en I01/I02.

## v0.4 in één oogopslag

Prototype v0.4 voegt aan de bestaande v0.3-engine toe:

- real-data-import van leden-, functie-, commissie-, team- en urenfeiten;
- read-only Sportlink Programma-integratie voor wedstrijden;
- CKC ShiftCatalog als expliciete configuratiebron voor diensten en bezetting;
- read-only Sportlink Vrijwilligers-integratie voor concrete vrijwilligersregistraties;
- behoud en segmentering van afwijkende concrete dienstperioden;
- afleiding van staffing/open need;
- expliciete signalering van onbekende of ambigue taakcodes;
- provenance met onderscheid `SOURCE_FACT`, `CONFIGURATION` en `DERIVED`;
- integrale koppeling van echte-bronachtige data aan de bestaande kandidaat-, voorstel-, menselijke-beslissing- en assignmentketen.

De formele v0.4-regressiesuite telt **118 tests**, inclusief **3/3 R16–R18 geïntegreerde eindacceptatietests**. De post-acceptatie presentatierun is aanvullend en verandert het formele R01–R18-acceptatiecontract niet.

## Architectuur

```text
Bronnen
  ├── Sportlink/exportdata
  ├── Sportlink Programma API
  ├── Sportlink Vrijwilligers API
  └── CKC ShiftCatalog
          │
          ▼
      adapters
          │
          ▼
   normalisatie
          │
          ▼
canonieke DVK-objecten
          │
          ▼
 bestaande v0.3-engine
          │
          ├── taakplicht / urenpositie
          ├── kandidaatselectie
          ├── prioritering
          └── adviesplanning
          │
          ▼
 AssignmentProposal
          │
          ▼
 menselijke beslissing
     ├── afwijzen → geen mutatie
     └── goedkeuren
             │
             ▼
       DutyAssignment
             │
             ▼
        D omhoog, E omlaag
```

Kernprincipe blijft:

> **DVK-voorstel ≠ CKC-besluit.**

## v0.4 integratielagen

### Real-data import

`dvk/real_data_import.py` normaliseert echte CKC-exportfeiten naar canonieke DVK-objecten en legt provenance en datakwaliteitssignalen vast. Ontbrekende of ambigue informatie wordt niet stilzwijgend ingevuld.

### Sportlink Programma

`dvk/programma_client.py` verzorgt de read-only HTTP-toegang. `dvk/programma_adapter.py` vertaalt bronregels naar canonieke `Match`-objecten, inclusief `HOME/AWAY`, statusverwerking en provenance. Niet-operationele wedstrijden worden niet als normale kandidaatcontext gebruikt.

### ShiftCatalog

`dvk/shift_catalog.py` behandelt de CKC ShiftCatalog als `CONFIGURATION`. Taakcode is de natuurlijke sleutel. Minimumbezetting bepaalt de noodzakelijke staffing; maximumbezetting blijft afzonderlijke registratie-/planningscapaciteit.

### Sportlink Vrijwilligers

`dvk/vrijwilligers_client.py` en `dvk/vrijwilligers_adapter.py` verwerken concrete registraties read-only. Koppeling aan diensten gebeurt via taakcode en datum/tijd, niet via de naam van de vrijwilliger als sleutel.

Afwijkende concrete Sportlink-dienstperioden blijven volledig bronfeit. DVK mag daaruit planbare segmenten afleiden langs catalogusgrenzen en werkelijke randtijden, maar mag geen periode stilzwijgend weggooien of verzinnen.

### Staffing en taakcoderesolutie

`dvk/staffing.py` leidt bezetting en open behoefte af. Deze uitkomsten hebben provenance `DERIVED`.

`dvk/task_code_resolution.py` koppelt uitsluitend exacte, unieke taakcodes. Onbekende, afwijkende en ambigue codes worden expliciet gesignaleerd; DVK gokt of corrigeert niet stilzwijgend.

## Provenancecontract

v0.4 maakt het onderscheid expliciet:

- `SOURCE_FACT` — feiten uit Sportlink of andere brondata;
- `CONFIGURATION` — CKC-inrichting, zoals ShiftCatalog;
- `DERIVED` — door DVK berekende uitkomsten, zoals staffing/open need.

Dit voorkomt dat een DVK-afleiding later ten onrechte als bronfeit wordt behandeld.

## Acceptatiebasis

De actuele regressiebasis bestaat uit:

- **C01–C22** — geaccepteerde v0.2-masterset;
- **W01–W13** — geaccepteerde v0.3-werkstroomcases;
- **I01/I02** — import- en UI/enginecontract uit v0.3;
- **R01–R18** — v0.4 real-data- en integratieacceptatie.

De v0.4-stappen zijn functioneel geaccepteerd als:

1. R01–R09 — real-data-import;
2. R10–R11 — Sportlink Programma;
3. R12 — ShiftCatalog;
4. R13/R13b — Sportlink Vrijwilligers en afwijkende concrete tijden;
5. R14 — staffing/open need;
6. R15 — onbekende/ambigue taakcodes;
7. R16 — provenance;
8. R17 — integrale weekendketen;
9. R18 — volledige regressie/eindacceptatie.

Zie [`BASELINE-v0.4.md`](BASELINE-v0.4.md) voor het formele acceptatiecontract.

## Presentatierun

`run_v04_demo.py` is een post-acceptatie demonstratierunner voor projectpresentaties. Hij gebruikt de bestaande, geaccepteerde v0.4-productiecomponenten en maakt zichtbaar welke input DVK ontvangt, wat DVK afleidt, waarom een kandidaat wordt geprioriteerd, waar een mens beslist en welke output daarna ontstaat.

De presentatierun bevat vier deterministische scenario's:

1. **Goedkeuring end-to-end** — ShiftCatalog en brondata leiden tot open behoefte, kandidaatselectie, uitlegbare prioriteit, een DVK-voorstel, menselijke goedkeuring, `DutyAssignment` en een gewijzigde urenpositie.
2. **Afwijzing zonder assignment** — een mens wijst het DVK-voorstel af; er ontstaat geen assignment en de urenpositie verandert niet.
3. **Onbekende taakcode** — DVK signaleert de onbekende code expliciet en gokt of fuzzy-matcht niet.
4. **Afwijkende diensttijd** — het volledige concrete broninterval blijft behouden; DVK leidt alleen planbare segmenten af.

De demo is nadrukkelijk **geen vervanging van de formele pytest-suite**. De regressietests bewaken het acceptatiecontract; de demo maakt hetzelfde gedrag begrijpelijk en presenteerbaar voor projectleden.

Vanaf `code/Prototype/`:

```bash
python run_v04_demo.py
```

GitHub Actions voert de presentatierun naast de volledige regressiesuite uit, zodat zowel technische regressie als de reproduceerbare presentatie-uitvoer zichtbaar blijft.

## Belangrijkste structuur

```text
code/Prototype/
├── 22 cases.md
├── ontwerp-dvk-prototype-v0.2.md
├── ontwerp-dvk-prototype-v0.3.md
├── BASELINE-v0.3.md
├── BASELINE-v0.4.md
├── README.md
├── pyproject.toml
├── run_v04_demo.py
├── run_*.py
├── dvk/
│   ├── model.py
│   ├── workstream_model.py
│   ├── duty.py
│   ├── engine.py
│   ├── candidate_selection.py
│   ├── prioritization.py
│   ├── recommendation_planner.py
│   ├── proposals.py
│   ├── assignments.py
│   ├── real_data_import.py
│   ├── programma_adapter.py
│   ├── programma_client.py
│   ├── shift_catalog.py
│   ├── vrijwilligers_adapter.py
│   ├── vrijwilligers_client.py
│   ├── staffing.py
│   └── task_code_resolution.py
└── tests/
    ├── test_integrated_v03.py
    ├── test_integrated_v04.py
    └── ...
```

## Uitvoeren

Vanaf `code/Prototype/`:

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest -q
python run_v04_demo.py
```

GitHub Actions voert de volledige regressiesuite, afzonderlijke acceptatiestappen en de presentatierun uit. Live Programma- en Vrijwilligersvalidatie wordt alleen in de daarvoor ingerichte handmatige workflowcontext uitgevoerd; gevoelige credentials worden niet in code, baseline of logs opgenomen.

## Scopegrens van v0.4

v0.4 valideert de read-only real-data-integratie en de volledige functionele keten. Buiten deze baseline vallen onder meer:

- automatisch schrijven naar Sportlink;
- productie-e-mail/notificaties;
- productie-authenticatie en -autorisatie;
- persistente workflow-/auditopslag;
- het vervangen van menselijke CKC-besluitvorming door automatische indeling.

## Baselineregel

Vanaf 13 september 2026 geldt:

> **Prototype v0.4 is functioneel geaccepteerd en vormt de actuele regressiebaseline voor de real-data-integratie van Ledendiensten. Nieuwe ontwikkeling moet R01–R18 én de onderliggende v0.3-baseline behouden, tenzij CKC expliciet een functionele wijziging besluit.**

## v0.5 — Teamnaamkoppeling Programma

De v0.5-ingang is `CkcProgrammaAdapter`, met teamlidmaatschappen uit de CKC Teams-export. De historische `SportlinkProgrammaAdapter` blijft de v0.4-interface. Gebruik voor kandidaatcontext de gecontroleerde `result.matches` en `result.team_memberships`, niet de interne auditweergave. Naamkoppeling, bronmeldingen, read-only lokale verificatie en acceptatiegrenzen staan in [DVK-v0.5-teamnaamkoppeling.md](DVK-v0.5-teamnaamkoppeling.md). De operationele aansluiting in PR #44 is beschreven bij de actuele kandidaatcontext; integrale v0.5-acceptatie blijft open.

## Lokale Sportlink CSV-exports

Gebruik op macOS de map **Documenten/DVK-Sportlink-exports** in Finder.
Het interne pad is `$HOME/Documents/DVK-Sportlink-exports/` (ook op Nederlandstalig macOS).
Maak de map zelf aan en plaats daarin de handmatig geëxporteerde bestanden:

| Sportlink-export | Exacte bestandsnaam |
| --- | --- |
| Leden | `Leden.csv` |
| Functies | `Functies.csv` |
| Commissies | `Commissies.csv` |
| Teams | `Teams.csv` |
| Overzicht per periode | `Overzicht per periode.csv` |

DVK haalt deze CSV's niet automatisch op en vernieuwt of herschrijft ze niet.
Vernieuw de exports handmatig in Sportlink; plaats ze daarna onder deze namen in
de map. Alleen de vindplaats en bestandsnaam zijn gestandaardiseerd. Kolommen,
scheidingstekens, UTF-8-verwerking en inhoudelijke controles blijven ongewijzigd.
De enige definitie voor standaardmap en bestandsnamen staat in
`dvk/sportlink_exports.py`; onderstaande ingangen gebruiken die definitie.

### Inventarisatie en toepassing

| Bestaande ingang | Gedrag na standaardisatie |
| --- | --- |
| `SportlinkRealDataAdapter.read_rows(path, dataset)` | Een expliciet pad blijft werken; `path=None` leest het bijbehorende standaardbestand. |
| `SportlinkRealDataAdapter.load_exports(...)` | Weggelaten paden lezen de vijf standaardbestanden. Elk expliciet pad of bestaande tekststream heeft voorrang. **Expliciet `duty_path=None` blijft de urenimport overslaan**, zoals in de bestaande taakplichtafleiding. |
| `run_programma_team_validation.py` | Zonder `--teams` wordt het standaard Teams-bestand gebruikt. `--teams` blijft een expliciet bestand van iedere locatie/naam accepteren; `--details` is ongewijzigd. |
| Streamlit Taakplichtcontrole | In PR #44: automatisch lezen bij functiegebruik; Brongegevens vernieuwen herleest de map. Bestanden en laadtijd zijn zichtbaar; geen vijf uploads meer. |
| Streamlit Databronnen / persoonskoppeling | In PR #44: Leden.csv wordt opnieuw uit dezelfde map gelezen bij expliciete synchronisatie. Persoonskoppeling en synchronisatiegevolgen blijven behouden. |
| Historische `SportlinkCsvImportAdapter.load_directory(...)` en `run_import_cases.py` | Ongewijzigd: v0.3 gebruikt geaccepteerde Engelstalige fixtures met **andere kolommen**, waaronder `members.csv`, `duty_hours.csv` en `teams.csv`. Dit zijn niet de vijf werkelijke Sportlink-exports. |
| Configuratie-CSV's (functiemapping, dienstencatalogus) | Ongewijzigd: dit zijn versiebeheerde configuratiebestanden, geen lokale exports. |
| Tests en voorbeelden | Historische geaccepteerde namen/fixtures blijven intact. Nieuwe padtests gebruiken uitsluitend synthetische exports in tijdelijke mappen. |

Er waren geen vaste Downloads-paden of andere hardgecodeerde persoonlijke
exportlocaties in de onderzochte repository. De bestaande presenter verwerkt tekststreams in geheugen; in PR #44 levert de gedeelde lokale bronservice die streams. Expliciete Python-paden/streams blijven ondersteund. Periode/seizoen blijft de bestaande expliciete invoer.

### Lokale controle en foutmeldingen

Gebruik vanaf `code/Prototype`, met de bestaande Pythonomgeving en reeds ingestelde
`SPORTLINK_CLIENT_ID`, hetzelfde read-only controlescript:

```bash
python run_programma_team_validation.py
python run_programma_team_validation.py --details
```

Een bestaand expliciet pad blijft toegestaan, bijvoorbeeld:

```bash
python run_programma_team_validation.py --teams "/lokaal/pad/eigen-export.csv" --details
```

De Python-import kan de standaardmap eveneens gebruiken:

```python
from dvk.real_data_import import SportlinkRealDataAdapter

source = SportlinkRealDataAdapter().load_exports()
# Of behoud expliciete argumenten/tekststreams; alleen weggelaten paden vallen terug.
# source = SportlinkRealDataAdapter().load_exports(teams_path="/lokaal/andere-naam.csv")
# source = SportlinkRealDataAdapter().load_exports(duty_path=None)  # bewust geen urenbron
```

Ontbrekende bestanden geven de ontbrekende naam, de verwachte locatie en de
opdracht de betreffende Sportlink-export daar te plaatsen. Onleesbare bestanden
geven een expliciete leesfout. Er worden geen mappen of lege vervangbestanden
aangemaakt en er wordt niet stilzwijgend met lege gegevens doorgegaan. Het
controlescript eindigt bij een bestandsfout met code 1 en doet dan geen API-aanroep;
de bestaande configuratiecontrole blijft gelden. Andere CLI-opties en exitcodes
zijn ongewijzigd.

Voor lokale acceptatie: plaats de vijf bestanden in de Finder-map, voer de
bovenstaande controle zonder `--teams` uit en vergelijk die met een run met een
expliciet Teams-pad. Controleer team 2, Rijnmond Cup, datum/tijd en bronmeldingen
zoals bij de geaccepteerde PR #41. Controleer in Streamlit dat de lokale bronnen bij functiegebruik worden ingelezen
en dat Brongegevens vernieuwen ze opnieuw leest. Gebruik voor een ontbrekend-bestandproef uitsluitend een synthetisch
of niet-bestaand expliciet pad; verwijder geen echte exports.

De standaardmap ligt buiten de repository. Gerichte Git-ignorepatronen beschermen
ook lokale kopieën met de standaardnamen, gedateerde/exportnamen en een map met
de standaardmapnaam binnen een checkout. Geaccepteerde fixtures en configuratie-CSV's
blijven zichtbaar en ongewijzigd. Plaats echte exports nooit in Git, tests of gedeelde logs.

Root README, backlog en productieroadmap bevatten geen lokale bestandsnamen die
moeten veranderen; er wordt geen productieopslag of nieuwe importworkflow vastgelegd.


## Operationele kandidaatcontext — ontwikkeling v0.5

De werkbranch `codex/actuele-kandidaatcontext` sluit de vijf lokale exports en de
Programma API aan op de bestaande kandidaten- en voorstelketen. De v0.5-taakplicht
wordt op de dienstdatum afgeleid; BL-03 wordt niet toegepast. Technisch geldige
Programma-lijsten, ook lege, worden vertrouwd volgens het CKC-besluit. Zie de
[werking, beperkingen en lokale acceptatiestappen](DVK-v0.5-actuele-kandidaatcontext.md).
De geaccepteerde v0.4-baseline en historische cases blijven ongewijzigd.


Zie voor de actuele PR #44-vervolgbediening, capaciteitsselectie, herleidbare
bronmeldingen en de daaropvolgende native tabel-/prestatieverbeteringen het
[vervolgacceptatieverslag](DVK-v0.5-vervolgacceptatie-ABC-DE.md).


Voor het praktijkvervolg vanaf `62da673` (stabiele scrollpositie bij dienstkeuze,
gemeten lookup-optimalisatie en optionele privacyveilige tijdmeting) zie het
[praktijkverslag en lokale heracceptatie](DVK-v0.5-vervolgacceptatie-ABC-DE.md#praktijkvervolg-selectie-scrollpositie-en-vertraging-25-oktober-2026).
Alleen de synthetische browserproef starten: `python -B tests/serve_synthetic_planning.py`.
Deze vervolgstap is technisch getest en wacht op lokale functionele heracceptatie.
