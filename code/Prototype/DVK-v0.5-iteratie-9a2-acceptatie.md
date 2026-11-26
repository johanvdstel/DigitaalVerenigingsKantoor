# DVK v0.5 — Functionele acceptatie Iteratie 9A.2

**Datum:** 7 november 2026  
**Status:** functioneel geaccepteerd; draft-PR #69 open, niet gemerged bij vastlegging  
**PR:** https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/69  
**Baseline:** `f0d0b4022a6d7baa0d5f30bbc70ab02a7b4e6057`  
**Geteste codecommit:** `045afbdc467185a870da5220d9a910ccc05f9333`

## Scope

Bij nieuwe planning wordt de actuele kalenderweek voorgesteld, met mogelijkheid tot aanpassing vóór de start. Na expliciete bevestiging volgt één laadcyclus: lokale CSV-bestanden, Sportlink Programma en Sportlink Vrijwilligers. Bronstatus maakt onderscheid tussen leeg, fout en bruikbaar. Hervatten leest opgeslagen CSV-/Programma-context uit SQLite en behoudt feitelijke boekingen en tijdelijke indelingen zonder nieuwe bronaanroepen. Handmatige verversing en de bestaande vervangingsbevestiging staan onder Databronnen.

## Lokale functionele acceptatie

1. **Geslaagd:** actuele kalenderweek en alternatieve periode; bronnen laden pas na Start nieuwe planning en vervolgens automatisch.
2. **Geslaagd:** tijdelijke indeling aangemaakt, Streamlit herstart, bestaande planning hervat; dezelfde periode, wedstrijden, feitelijke bezetting en tijdelijke indeling aanwezig, geen nieuwe laadcyclus.
3. **Geslaagd:** in Databronnen is voor vervanging van bestaande bezetting expliciete bevestiging vereist; zonder bevestiging geen synchronisatie; tijdelijke indeling behouden.
4. **Geslaagd:** `Functies.csv` tijdelijk hernoemd; DVK meldt: 'Kandidaatbronnen niet geladen', vermeldt dat `Functies.csv` ontbreekt, geeft de exacte verwachte locatie en hersteladvies. Herstel naar de oorspronkelijke bestandsnaam is gevraagd, maar nog niet afzonderlijk bevestigd.

De functioneel verantwoordelijke heeft na deze vier stappen expliciet akkoord gegeven.

## Technische verificatie

Codex: 117 gerichte tests, 1.609 regressietests en 11 synthetische acceptatiescripts geslaagd. [GitHub CI #441](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/42420999174) is geslaagd op de oplevercommit. De technische tests dekken onder andere gedeeltelijke bronuitval, onbekende bezetting, veilige kandidaatvoorstellen, twee afzonderlijke afgeschermde boekingen en duurzaam hervatten.

## Afbakening en vervolg

Geen Sportlink-writeback, geen verplaatsing van de SQLite-database en geen opruiming van oude mappen. De integrale acceptatie van prototype v0.5 blijft Iteratie 10. PR #69 mag pas na afzonderlijke toestemming en actuele CI-controle worden gemerged. Vervolg: 9A.3 sessie-/regressiebescherming, 9A.4 lokale omgevingscontrole, 9A.5 afronding.
