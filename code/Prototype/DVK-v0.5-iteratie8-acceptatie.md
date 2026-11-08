# DVK v0.5 — Iteratie 8: functionele acceptatie

**Datum:** 3 november 2026  
**Beoordelaar:** CKC / functioneel opdrachtgever  
**Status:** lokaal functioneel geaccepteerd; [draft-PR #65](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/65) nog niet gemerged.  
**Doelbranch:** `prototype-v0.5`  
**Geaccepteerde codecommit:** `69255327dcf5fc35a578bc12ace985afa0ffe900`

## Scope en lokale acceptatie

| Onderdeel | Afspraak | Acceptatie |
| --- | --- | --- |
| UI-1 | Standaard ingeklapte secties: Instellingen, Databronnen, Wedstrijden, Diensten, Kandidaten | Visueel akkoord |
| UI-2 | Knop **Dienstencatalogus (roosterindeling) opnieuw laden** en toelichting onder Diensten, boven **Feitelijke Sportlink-inroosteringen ophalen** | Visueel akkoord; annuleren en bevestigen lokaal geslaagd |
| UI-3 | Acht bronregels, één kolom **Laatst ingelezen door DVK**, `Onbekend` indien nodig; historische urenbron type `CSV` | Visueel akkoord na correctie |
| UI-4 | Geen demonstratie-/bronkeuzeradio in de gewone Planner; operationele bronnen standaard, synthetische tests behouden | Visueel akkoord |

Bij annuleren van de catalogusherlaadactie bleef de bestaande sessie behouden. Bij bevestigen is het opnieuw laden met een nieuwe planningssessie lokaal geslaagd. De bestaande contracten beschermen duurzame no-showregistraties en intrekkingen; er is geen Sportlink-writeback toegevoegd.

## Betekenis van tijdstippen

Voor CSV-bronnen is de tijd het bestaande DVK-inleesmoment. Voor Sportlink Programma en Vrijwilligers is het bestaande tijdstip het **begin** van de DVK-laad-/ophaalactie, niet het exacte voltooiingsmoment en niet de bronactualisatietijd bij Sportlink. De presentatie gebruikt één begrijpelijke kolom; de bronbetekenis blijft in de toelichting onderscheiden. Er is geen nieuwe timestampregistratie of extra API-aanroep toegevoegd.

## Technische verificatie

- 70 gerichte tests geslaagd na de laatste correctie.
- 1506 tests in de volledige regressiesuite geslaagd.
- 11 synthetische acceptatiescripts geslaagd.
- Geen mislukte of overgeslagen tests in de definitieve runs.
- [CI #422](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41730239295) geslaagd op de geaccepteerde codecommit.

## Acceptatiegrens en vervolg

De lokale functionele acceptatie betreft **uitsluitend Iteratie 8 op de genoemde codecommit**. De daaropvolgende documentatiecommits wijzigen geen applicatiecode. PR #65 blijft draft tot afzonderlijke merge-toestemming; de integrale functionele acceptatie van prototype v0.5 blijft open.

**Iteratie 9:** kandidaatselectie en prioritering, gepland en nog niet geïmplementeerd. De reeds overeengekomen uitgangspunten en nog open vragen staan in [prototypeplanning](../../DVK-PROTOTYPE-PLANNING.md) en [backlog](../../BACKLOG.md).  
**Iteratie 10:** integrale functionele acceptatie v0.5.  
**Daarna:** BL-13/RPA als afzonderlijk traject, zonder impliciete Sportlink-schrijfbevoegdheid.

De trage lokale Streamlit-start blijft een afzonderlijk onderzoekspunt; geen onderdeel van Iteratie 8.
