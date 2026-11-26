# DVK v0.5 — Functionele acceptatie Iteratie 9A.3

**Datum:** 8 november 2026  
**Status:** lokaal functioneel geaccepteerd door CKC; PR nog niet gemerged.  
**PR:** [#70](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/70)  
**Geaccepteerde codecommit:** `3a64213d47eb35b2a2baef9723c42f5957175170`  
**Branch:** `codex/iteratie-9a3-sessiebescherming` → `prototype-v0.5`

## Scope

Sessie- en regressiebescherming bij automatisch laden en handmatig vernieuwen van planningsbronnen: fouten mogen geen bestaande tijdelijke indelingen wissen; verouderde kandidaatvoorstellen mogen niet bruikbaar blijven; hervatten mag niet ongevraagd opnieuw laden. Technische regressies dekken daarnaast foutresponsen van de Vrijwilligers API, Programma-foutclassificatie en een onderbroken initiële laadactie.

## Lokale functionele acceptatie

1. **Hervatten na Streamlit-herstart — geslaagd.** De planner laadde wedstrijden en diensten handmatig nadat de applicatie een onbekende wedstrijdcontext en Sportlink-bezetting meldde. Na een tijdelijke indeling, stoppen en opnieuw starten van Streamlit bleven gekozen periode, wedstrijden, diensten en tijdelijke indeling behouden; geen ongevraagde bronverversing.
2. **Mislukte bronverversing in twee browservensters — geslaagd.** In venster 1 stond een geselecteerde dienst met kandidaatvoorstel. In venster 2 werd een afzonderlijke testexportmap ingesteld; `Functies.csv` werd daar tijdelijk hernoemd en `Brongegevens vernieuwen` gestart. DVK meldde correct het ontbrekende bestand en de verwachte locatie. Na verversen van venster 1 verscheen dezelfde foutstatus en waren kandidaatvoorstellen niet meer beschikbaar. De eerder vastgelegde tijdelijke DVK-indeling bleek behouden. Het testbestand en de oorspronkelijke exportmapinstelling zijn daarna volgens de gebruiker hersteld.
3. **Onderbroken initiële bronlading — geslaagd via synthetische test.** Lokaal uitgevoerd: `.venv/bin/python -m pytest -q tests/test_new_planning_9a2.py -k interrupted_initial_load`. Resultaat: **2 passed, 9 deselected in 2.61s**. Niet als handmatige procesonderbreking beproefd.

## Technische oplevering

Codex rapporteerde vóór lokale acceptatie 216 gerichte tests, 1.621 regressietests en 11 synthetische acceptatiescripts geslaagd; CI #445 groen op de codecommit. Deze technische resultaten zijn afzonderlijk van de lokale functionele acceptatie.

## Acceptatiegrens en vervolg

Dit akkoord geldt voor Iteratie 9A.3 op de genoemde **codecommit**. Documentatiecommits veranderen de geteste programmatuur niet; vóór merge blijft controle op eventuele codeverschillen vereist. PR #70 wordt uitsluitend na afzonderlijk expliciet akkoord gemerged. Iteratie 9A.4 behandelt de lokale omgeving en het databasepad; Iteratie 9A.5 de afronding en voorbereiding. Iteratie 10 blijft de integrale functionele acceptatie van prototype v0.5. Geen productieacceptatie of Sportlink-writeback.
