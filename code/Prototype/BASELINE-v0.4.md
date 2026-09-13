# DVK Prototype v0.4 — functioneel geaccepteerde baseline

**Status:** functioneel geaccepteerd  
**Acceptatiedatum:** 13 september 2026  
**Werkstroom:** Ledendiensten & Vrijwilligersbeleid — real-data-integratie  
**Doelbranch:** `main`

## Baselinebesluit

DVK Prototype v0.4 is op 13 september 2026 functioneel geaccepteerd. v0.4 bouwt voort op de geaccepteerde v0.3-baseline en voegt read-only integratie met echte CKC/Sportlink-bronnen en expliciete bron/configuratie/afleidingssemantiek toe.

De bestaande C01–C22-, W01–W13- en I01/I02-contracten blijven regressiebasis. Nieuwe functionaliteit mag deze werking niet ongemerkt wijzigen.

## Architectuurcontract

De v0.4-keten is:

`bronnen → adapters → normalisatie → canonieke DVK-objecten → bestaande v0.3-engine → voorstel → menselijke beslissing → DutyAssignment`

Daarbij gelden blijvend:

- integraties in v0.4 zijn read-only;
- bronvelden, HTTP-details, Sportlink-filters en CKC-taakcodes blijven buiten de domeinregels;
- `DVK-voorstel ≠ CKC-besluit`;
- een `DutyAssignment` ontstaat alleen na menselijke goedkeuring;
- ontbrekende of ambigue broninformatie wordt niet stilzwijgend ingevuld of gegokt;
- familierelaties worden niet automatisch gefabriceerd;
- negatieve E blijft een geldige urenpositie;
- Sportlink geregistreerde A is bronfeit; DVK verwachte A is afleiding; verschil leidt tot signalering, niet automatische correctie.

## Geaccepteerde v0.4-cases

### R01–R09 — real-data import

- leden worden zonder ongewenste duplicatie naar canonieke personen verwerkt;
- bekende duplicaten worden expliciet gedetecteerd/geconsolideerd;
- onbekende extra bronkolommen blokkeren import niet;
- ontbrekende vereiste feiten leiden tot expliciete signalen;
- functies, commissies en teams worden met behoud van cardinaliteit gekoppeld;
- bronvarianten worden genormaliseerd zonder nieuw vrijstellingsbeleid te introduceren;
- A/B/C/D/E worden verwerkt en gereconcilieerd;
- negatieve E wordt behouden;
- verschil tussen verwachte A en geregistreerde A wordt gesignaleerd, niet gecorrigeerd.

### R10–R11 — Sportlink Programma

- het read-only Programma-endpoint wordt naar canonieke `Match`-objecten vertaald;
- CKC-thuis/uit wordt canoniek als `HOME`/`AWAY` vastgelegd;
- niet-operationele wedstrijden worden uit normale kandidaatcontext gehouden met behoud van auditinformatie;
- live CKC-bronvalidatie heeft de selectie en mapping bevestigd.

### R12 — ShiftCatalog

- taakcode, diensttype, duur, minimum- en maximumbezetting worden als CKC-configuratie ingelezen;
- taakcode is de natuurlijke sleutel;
- dubbele/ongeldige definities worden expliciet gesignaleerd;
- conditionele bezettingsregels zijn ondersteund;
- `maximum_staff` is registratie-/planningscapaciteit en doel voor kandidaatvoorstellen, niet de minimumbehoefte.

### R13/R13b — Sportlink Vrijwilligers en concrete diensttijden

- vrijwilligersregistraties worden via taakcode en datum/tijd aan diensten gekoppeld, nooit via naam als sleutel;
- ontbrekende unieke koppeling leidt tot signalering, niet gokken;
- concrete Sportlink-diensttijden blijven bronfeit;
- wanneer een concrete periode afwijkt van het cataloguspatroon, leidt DVK planbare segmenten af langs bekende catalogusgrenzen en werkelijke randtijden zonder delen te verliezen.

### R14 — staffing/open need

- open behoefte wordt afgeleid uit `minimum_staff` en bevestigde bezetting;
- `maximum_staff` blijft afzonderlijke capaciteit;
- de bezettingslogica sluit aan op de in R13b geaccepteerde dienstperioden en segmentering.

### R15 — taakcoderesolutie

- alleen exacte, unieke taakcodes worden gekoppeld;
- onbekende, afwijkende of ambigue codes worden expliciet als datakwaliteitsprobleem gesignaleerd;
- DVK trimt, corrigeert, vertaalt of gokt geen taakcode stilzwijgend.

### R16 — provenance

De herkomstsemantiek is expliciet:

- Sportlink/brondata: `SOURCE_FACT`;
- CKC ShiftCatalog: `CONFIGURATION`;
- door DVK berekende staffing/open need: `DERIVED`.

Afgeleide resultaten mogen niet als bronfeit worden gepresenteerd.

### R17 — integrale weekendketen

Een representatief weekendscenario loopt door de echte v0.4-componenten:

`ShiftCatalog → DutyService → Vrijwilligers/bezetting → Programma/Match → kandidaatbeoordeling → prioritering → AssignmentProposal → menselijke beslissing → DutyAssignment → D/E-update`

Goedkeuring alleen muteert de bronregistratie niet; pas de feitelijke assignment werkt de geplande positie bij. Afwijzing maakt geen assignment en verandert de urenpositie niet.

### R18 — regressie/eindacceptatie

De volledige bestaande baseline blijft groen naast R01–R17: C01–C22, W/I-cases en de geïntegreerde v0.3-keten.

## Technische acceptatie

De afsluitende GitHub Actions-run **#130** voor commit `bf3d8a01bd40ef9807d4dd1a8ef2ecd4d7800938` is volledig geslaagd:

- **118 tests passed**;
- R16–R18 geïntegreerde v0.4-eindacceptatie: **3 passed**;
- R15 taakcoderesolutie: geslaagd;
- R14 staffing/open need: geslaagd;
- R13/R13b Vrijwilligers en concrete tijden: geslaagd;
- R12 ShiftCatalog: geslaagd;
- R10/R11 Programma: geslaagd;
- R01–R09 real-data import: geslaagd;
- C01–C22 en volledige v0.3-regressieketen: geslaagd.

Eerdere `workflow_dispatch`-runs hebben bovendien de live read-only Programma- en Vrijwilligersbronnen gevalideerd. Credentials en client-id's maken geen deel uit van de baseline-documentatie of testoutput.

## Belangrijkste v0.4-modules

Naast de bestaande v0.3-engine zijn met name toegevoegd:

```text
dvk/
├── real_data_import.py
├── programma_adapter.py
├── programma_client.py
├── shift_catalog.py
├── vrijwilligers_adapter.py
├── vrijwilligers_client.py
├── staffing.py
└── task_code_resolution.py
```

De integratie-eindacceptatie staat in `tests/test_integrated_v04.py`. De volledige suite onder `tests/` blijft het uitvoerbare acceptatiecontract.

## Baselineregel voor vervolgontwikkeling

Vanaf 13 september 2026 geldt:

> **Prototype v0.4 is de functioneel geaccepteerde referentie voor de real-data-integratie van de werkstroom Ledendiensten. R01–R18 en de onderliggende v0.3-regressiebasis worden niet opnieuw ter discussie gesteld tenzij CKC bewust een functionele beleids- of ontwerpwijziging besluit.**

Vervolgontwikkeling wordt bovenop deze baseline uitgevoerd en moet de volledige regressiesuite groen houden.
