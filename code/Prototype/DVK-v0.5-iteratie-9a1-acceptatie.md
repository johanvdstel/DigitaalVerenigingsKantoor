# DVK v0.5 — Functionele acceptatie Iteratie 9A.1

**Datum:** 7 november 2026  
**Status:** functioneel geaccepteerd; PR #68 nog open, niet gemerged  
**PR:** https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/68  
**Geteste codecommit:** `06d1fe50bd30235fe2c9658e51395509082bf699`  
**Baseline:** `prototype-v0.5@f6a1d41801b2cfcdf57f118edcd499d75679cb59`

## Scope en uitkomst

De afzonderlijke functie **Ledendiensten → Databronnen** en de lokaal persistente configuratie van de Sportlink-exportmap (`~/.config/dvk/settings.json`) zijn functioneel geaccepteerd. De vijf verplichte en één optionele CSV-bron worden afzonderlijk gepresenteerd, naast de Programma- en Vrijwilligers-API-status. De bronbediening voor kandidaten is vanuit Planning naar Databronnen verplaatst. Er is geen databaseverplaatsing, automatische bronlading bij een nieuwe planning of Sportlink-writeback in deze deelstap.

## Lokale functionele waarnemingen

- De testversie start en de functie Databronnen verschijnt correct.
- De exportmap kan worden ingesteld en blijft na herstart behouden.
- Het ophalen van feitelijke Sportlink-inroosteringen werkt.
- Een tijdelijke indeling en bestaande Sportlink-bezetting blijven behouden bij navigatie tussen Planning en Databronnen, zonder herladen.

**Acceptatieobservatie:** de bediening vergt nog meerdere handmatige acties: kandidaatbronnen via **Brongegevens vernieuwen** en feitelijke inroosteringen via een aparte ophaalactie. Dit is onoverzichtelijk, maar behoort uitdrukkelijk tot **Iteratie 9A.2**. Daar worden CSV-bronnen, Programma API en Vrijwilligers API automatisch geladen na het definitief starten van een nieuwe planning; hervatten mag geen bronaanroepen veroorzaken. Dit is geen blokkerende afwijking voor 9A.1.

## Technische verificatie

Codex rapporteerde 105 gerichte tests, 1.602 regressietests en 11 synthetische acceptatiescripts geslaagd. GitHub CI-run #437 op de genoemde codecommit is geslaagd. De regressies voor afzonderlijke afgeschermde boekingen uit PR #67 zijn meegenomen. Twee AppTest-time-outs op de ongewijzigde baseline zijn op de oplevercommit niet opnieuw opgetreden.

## Grenzen en vervolg

- **9A.1:** functioneel geaccepteerd op 7 november 2026.
- **PR #68:** draft en open bij acceptatie; merge vereist afzonderlijke expliciete toestemming en controle van de actuele PR-head en CI.
- **9A.2:** standaard actuele kalenderweek, automatisch laden bij nieuwe planning, zonder herladen bij hervatten; afzonderlijk implementeren en accepteren.
- **9A.4:** lokale databasepad-/omgevingscontrole; geen oude database migreren zonder expliciete toestemming.
- **Iteratie 10:** integrale functionele acceptatie blijft open.
- Oude mappen en databases mogen niet worden verwijderd zonder afzonderlijke toestemming.
