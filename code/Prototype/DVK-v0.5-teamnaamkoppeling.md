# DVK v0.5 — Teamnaamkoppeling Teams ↔ Programma

**PR #41 gemerged en functioneel geaccepteerd, inclusief datum-/tijdverwerking.**
De lokale CSV-padstandaardisatie wordt afzonderlijk beoordeeld.
Baseline: `prototype-v0.5` commit `1a1cd6b`; inhoudelijke basis: lokale verificatie
24 oktober en de daaropvolgende expliciete implementatieopdracht. v0.4 blijft de
geaccepteerde releasebaseline; integrale v0.5- en Programma-schermacceptatie blijven open.

## Contract en bronhouders

De Teams-export is bron voor officiële teamnamen en Speeldag; Programma is bron
voor wedstrijden, CKC-zijde en competitiecontext. Competitiegebonden Sportlink-ID's
zijn geen gedeelde teamidentiteit. `-1` en verschillende ID's voor hetzelfde team
zijn toegestaan als bronwaarden.

- Alleen precies één zijde met clubrelatiecode `BBDZ08H` bewijst de CKC-zijde.
  Pas daarna wordt het letterlijke `CKC `-prefix verwijderd. Geen fuzzy matching.
- Andere eenduidige teamnamen gebruiken hun officiële naam als canonieke `team_id`.
- Alleen naam `2` gebruikt ook CSV-Speeldag: `Algemeen/Zaterdag` of
  `Algemeen/Zondag`. De gedeelde sleutel wordt leesbaar weergegeven als
  `2 / Algemeen/Zaterdag` of `2 / Algemeen/Zondag`. Dit is een representatie van
  de afgesproken naam + Speeldag, geen nieuwe functionele koppelsleutel.
- Bij `2` bepaalt het woord zaterdag of zondag in API-veld `competitie` de keuze.
  De feitelijke wedstrijddatum doet niet mee. Geen of beide dagwoorden is onopgelost.
- Alleen `competitiesoort` gelijk aan `Rijnmond Cup` of `Rijnmondcup` activeert
  cupnormalisatie: `JO O13` → `O13`; O-/MO-leeftijd zonder teamnummer krijgt `-1`.
  Een bestaand teamnummer blijft behouden. Geen aanvullende omzettingen.
- De uitkomst moet exact één bestaand exportteam zijn. Meerdere ledenregels van
  hetzelfde team tellen als één teamkandidaat, zonder lidmaatschappen te verwijderen.

De zes geaccepteerde cupgevallen zijn `CKC JO O13` → `O13-1`, `CKC MO17` →
`MO17-1`, `CKC O10` → `O10-1`, `CKC O14` → `O14-1`, `CKC O23` → `O23-1`
en `CKC O17-1` → `O17-1`.

## Gebruik en herleidbaarheid

`RealTeamMembership` bewaart aanvullend de originele CSV-Teamwaarde en Speeldag.
De bestaande bronnaam in `team_id` blijft voor historische importconsumenten intact.
De v0.5-ingang `CkcProgrammaAdapter` zet deze bronlidmaatschappen en wedstrijden om
naar dezelfde opgeloste identiteit, zonder selectiebeleid in de adapter te plaatsen:

```python
from dvk.programma_team_adapter import CkcProgrammaAdapter
from dvk.programma_client import SportlinkProgrammaClient

adapter = CkcProgrammaAdapter(team_memberships=teams_import.team_memberships)
fetched = SportlinkProgrammaClient(adapter).fetch_rows(client_id=existing_client_id)
result = adapter.import_rows(fetched.rows)
# Geef deze twee gecontroleerde collecties samen door aan de bestaande planning:
team_memberships = result.team_memberships
matches = result.matches
# Bestaande overzichtsdiagnostiek kan result.signals gebruiken.
```

`result.links` bevat per wedstrijd de oorspronkelijke thuis-/uitnaam en clubcode,
CKC-zijde, oorspronkelijke CKC-naam, bron-ID, competitieomschrijving/-soort,
normalisatiestappen, kandidaten en matched/ambiguous/unmatched-uitkomst.
`result.signals` gebruikt de bestaande `DataQualitySignal`-vorm met ERROR-codes
`PROGRAM_TEAM_AMBIGUOUS`, `PROGRAM_TEAM_UNMATCHED` en
`CKC_TEAM_MEMBERSHIP_UNRESOLVED`. Team 2 zonder geldige Speeldag blijft expliciet
onopgelost. De bronregistraties blijven beschikbaar voor beoordeling.

Bij onopgeloste teamkoppelingen geven `result.matches` én
`result.team_memberships` een `UnresolvedProgramTeamsError`; een gedeeltelijk
gekoppelde bron kan dus niet via deze interface als wedstrijdloze kandidaatcontext
worden gebruikt. `result.program` is alleen de onderliggende datum-/statusaudit van
wel gekoppelde rijen; gebruik zijn gedeeltelijke matches niet voor planning.
Afgelaste wedstrijden houden hun audit en blijven buiten operationele matches.

Het v0.4-contract van `SportlinkProgrammaAdapter` en zijn geaccepteerde tests blijven behouden.
De nieuwe v0.5-ingang hergebruikt diens read-only aanvraag-, tijd- en statuscontract,
maar past competitie-ID's alleen in interne kopieën aan naar de opgeloste identiteit.
De oorspronkelijke invoerrijen blijven onaangetast en bron-ID's staan in `links`.

## Datumcompatibiliteit (correctie lokale acceptatie)

De lokale `python3` is Python 3.9.6; `datetime.fromisoformat` accepteert daar geen
compacte offsets zoals `+0200`. De adapter normaliseert daarom uitsluitend de
afsluitende offset naar `+02:00` (ook `+0100` → `+01:00`) vóór het bestaande parsen.
Net als Rooster2 `normalize_program()` blijft het een tijdzonebewust tijdstip dat
naar `Europe/Amsterdam` wordt omgerekend. DVK behoudt de tijdzone, inclusief beide
02:30-tijdstippen tijdens de wintertijdwisseling. De lokale kalenderdatum en
het UTC-tijdstip blijven behouden; geen extra tijdzonebeleid of pandas-afhankelijkheid.
Het project declareert nog steeds Python >=3.11; dit is een gerichte
invoercompatibiliteitscorrectie, geen algemene ondersteuningstoezegging voor 3.9.

## Regressie en grenzen

Alle toegevoegde fixtures zijn synthetisch. De nieuwe tests dekken zes cupgevallen
bij beide waargenomen schrijfwijzen, 15 synthetische team-2-wedstrijden (8 zaterdag,
6 zondag, 1 zondagbeker), verplaatste wedstrijddagen, verschillende competitie-ID's,
-1/leeg ID, ontbrekende/ambigue koppelingen, bronbehoud, volgorde-onafhankelijkheid,
geen gedeeltelijke kandidaatcontext en aansluiting op de bestaande selectie.
Historische geaccepteerde fixtures en v0.4-tests zijn niet aangepast.

Geen schemawijziging, migratie, databaseactie, No-Show-wijziging of Sportlink-writeback.
De regels voor meerdere wedstrijden/lidmaatschappen zijn ongewijzigd; hun eerder
vastgestelde eerste-matchgedrag is geen onderdeel van deze correctie. Ook
API-responsvalidatie/volledigheid uit het eerdere onderzoek is geen nieuwe
implementatiescope. De Ledendienst Planning schakelt hierdoor niet zelfstandig
om van demonstratiegegevens naar live Programma-data. Dat blijft een aparte
integratie-/acceptatiestap.

## Lokaal functioneel acceptatiescenario (macOS)

1. Gebruik de te toetsen checkout en de bestaande Pythonomgeving.
   Houd echte exports buiten de repository. Gebruik de bestaande runtime-instelling
   `SPORTLINK_CLIENT_ID`; zet de waarde niet in code, commandohistorie of gedeelde logs.
2. Voer vanuit `code/Prototype` uitsluitend de read-only controle uit:
   `python run_programma_team_validation.py`.
   De standaardlocatie en exacte namen staan in [Lokale Sportlink CSV-exports](README.md#lokale-sportlink-csv-exports).
   Een expliciet bestand blijft toegestaan met `--teams "/lokaal/pad/eigen-export.csv"`.
   De Teams-export blijft lokaal; de Programma-aanroep is een GET en opent geen database.
3. Controleer de aantallen matched/ambiguous/unmatched en de bronmeldingen. Opnieuw
   ophalen kan andere aantallen geven dan de 148 van de verificatie op 24 oktober.
   Nul uitzonderingen is alleen bewijs voor de werkelijk ontvangen bronperiode.
4. Voeg eventueel `--details` toe voor uitsluitend lokale teamcontext. Controleer
   de twee teams 2 op competitieomschrijving en Speeldag, de zes cupnamen en
   oorspronkelijke naam/normalisatiestappen. Deel geen ruwe export of respons.
5. Bij onbekende naam of onvoldoende competitiecontext toont de controle een
   ERROR-signaal en eindigt met code 2; gebruik de gedeeltelijke audit niet voor
   kandidaatselectie. Transport/CSV-fout eindigt met code 1; geen bronvervanging.
6. Controleer de gerichte tests met
   `python -m pytest -q tests/test_programma_team_linking_v05.py`.
   De teamnaamkoppeling is via PR #41 geaccepteerd. Vervolgwijzigingen vragen
   afzonderlijke beoordeling; geen zelfstandige acceptatie op basis van groene tests.
