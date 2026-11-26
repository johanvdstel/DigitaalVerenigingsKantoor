# DVK v0.5 — functionele acceptatie PR #67

**Datum:** 7 november 2026  
**Baseline:** `prototype-v0.5@d168576cc5d1e2ea1260c6b64c35f56d33b49e6e` (PR #66)  
**Correctie:** [PR #67](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/67), codecommit `90d3ddea2e8b4a2b90c70ba78ecf692cbb00caa7`  
**Besluit:** CKC functioneel akkoord; integrale v0.5-acceptatie blijft open.

## Aanleiding en contract

Twee verschillende afgeschermde Sportlink-boekingen voor dezelfde dienst kregen eerder dezelfde technische sleutel, waardoor synchronisatie vastliep. Iedere werkelijk aangeleverde afgeschermde regel moet als afzonderlijk bezettingsfeit behouden blijven. Het technische voorkomensnummer is **geen** persoonsidentiteit. Geen persoonskoppeling, persoonsgebonden uren of no-show voor afgeschermde boekingen; overige duplicaatcontrole en bronvervangingsbevestiging blijven behouden.

## Functionele praktijkcontrole

CKC heeft de nieuwe lokaal draaiende DVK-versie op de geaccepteerde commit bekeken met werkelijke Sportlink-bezetting. Voor één dienst waren twee herkenbare reguliere boekingen en **twee afzonderlijke regels `Afgeschermd`** zichtbaar. Beide afgeschermde regels telden mee; **vrije capaciteit = 0**. CKC bevestigde expliciet de correcte weergave en capaciteit en gaf functioneel akkoord. De controle betrof zichtbaarheid en bezetting; no-showweigering, persoonskoppeling en herhaalde synchronisatie zijn niet afzonderlijk handmatig met deze live situatie getest.

## Technische onderbouwing en grenzen

Volgens PR #67: 180 gerichte tests, 31 identiteitstests, 1.597 volledige regressietests geslaagd; CI #433 succesvol op de geaccepteerde codecommit. Regressies omvatten 1/2/3 identieke afgeschermde regels, gemengde bezetting, 1→3→2→0, herhaalde synchronisatie, herordening, databaseheropening, oude payloads, no-show/sanctieweigering en rollback. Geen schema- of beleidswijziging en geen Sportlink-writeback. Afgeschermde personen worden niet over opeenvolgende bronmomenten geïdentificeerd.

## Afzonderlijk vervolg

De nieuwe lokale ontwikkelomgeving buiten iCloud start met Python 3.11.16 en Streamlit 1.67.0. Sportlink-exports zijn naar een aparte lokale gegevensmap gekopieerd en de Client-ID kan vanuit een lokaal configuratiebestand geladen worden. De applicatie gebruikt echter nog het oude vaste exportpad; configureerbare, persistente exportmap volgt via een afzonderlijke correctie en hoort niet bij PR #67. De oude Documenten-mappen worden pas na controle van de nieuwe bronlocatie opgeruimd.

**Volgende mijlpaal:** Iteratie 10, integrale functionele acceptatie van prototype v0.5.
