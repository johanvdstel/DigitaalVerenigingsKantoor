# Iteratie 6 — BL-22: functionele acceptatie en overdracht

**Datum:** 2 november 2026  
**Besluit:** functioneel geaccepteerd door CKC; **niet gemerged**.  
**Acceptatiebasis:** codecommit `d0be7dccb31eaeace038bfb867a7c25b2995dd70`, [draft-PR #62](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/62), doelbranch `prototype-v0.5`. De latere commits op dezelfde PR-branch betreffen uitsluitend documentatie en wijzigen deze geaccepteerde code niet.

## Doel en gerealiseerde scope

BL-22 verbetert onderhoudbaarheid en reviewbaarheid van bestaande CKC-beleidsregels Ledendiensten **zonder beleids- of gedragswijziging**. Opgeleverd:

- Vijf herkenbare stappen in `dvk/member_duty.py` voor lidmaatschap, persoonlijke functies, huishoudfuncties, minderjarigen en definitieve taakplichtafleiding.
- Eén gedeelde, pure B-02-kwalificatiefunctie `is_bond_team_player` voor **één afzonderlijke geparseerde teamregistratie**. Import en weekendplanning behouden hun eigen verwerking en gevolgen.
- Bestaande CSV-functieclassificatie ongewijzigd.
- [CKC-beleidsregelindex](../../docs/DVK-v0.5-CKC-beleidsregelindex-Ledendiensten.md) buiten de applicatie, met B-01–B-14/E, elf synthetische demonstraties en verwijzingen naar code en tests.
- Geen nieuwe UI, Rules Engine, Sportlink-writeback of nieuwe beleidsinterpretatie.

De bestaande operationele kandidatenbasis blijft gebaseerd op geregistreerde Sportlink-taakplicht. De afzonderlijke taakplichtcontrole blijft de CKC-verwachting afleiden.

## Technische verificatie (Codex-rapportage)

- Baseline `prototype-v0.5` op `4699e036147e051b2958fe0e71496ae104b0d864`.
- Werkbranch `codex/iteratie-6-bl22`; implementatiecommit `d0be7dccb31eaeace038bfb867a7c25b2995dd70`.
- 768 synthetische vóór/na-situaties zonder verschil in verwachtingen, gronden, bewijs, controles of toelichtingen.
- 393 karakteriseringstests vóór én na; 514 gerichte tests; 1501 volledige regressietests geslaagd, nul mislukt of overgeslagen.
- Elf bestaande synthetische runners met exitcode 0; CI #407 geslaagd.
- De elf bekende historische root-tests buiten de ingestelde tests-map vallen niet onder deze regressieclaim.
- Geen echte CKC-persoonsgegevens of live Sportlink-aanvragen voor deze technische verificatie gebruikt.

Details: [technisch opleveringsverslag](DVK-v0.5-iteratie6-BL22.md).

## Functioneel acceptatiebesluit CKC

CKC heeft de beleidsregelindex bekeken en verklaard dat deze **compleet lijkt**, maar **voor een niet-ingewijde niet gemakkelijk leesbaar** is. Met die expliciete kanttekening is **akkoord gegeven op Iteratie 6 / BL-22**.

De leesbaarheidskanttekening is geen blokkerend gebrek voor BL-22. Een toekomstige read-only functie **'Beleidsregels bekijken'** onder Ledendiensten blijft een mogelijkheid **uitsluitend bij later vastgestelde behoefte**; niet opgenomen in de huidige scope.

De acceptatie betreft de oplevering op de genoemde implementatiecommit en het beoordeelde document. De aanvullende correctie in de B-02-documentatieverwijzing en formele projectdocumentatie zijn administratieve wijzigingen na acceptatie; geen nieuwe functionele code. Indien alsnog code of beleidsinhoud wijzigt, is afzonderlijke beoordeling vereist.

## Afbakening en vervolg

- Geen integrale functionele acceptatie van prototype v0.5; die blijft een afzonderlijke eindmijlpaal.
- Geen toestemming om PR #62 te mergen; daarvoor is een nieuw expliciet besluit nodig.
- **Iteratie 7add** is de eerstvolgende kleine UI-correctieronde: verplaats de roosterbezettingsmelding naar sectie 3 — Diensten met de afgesproken tekst en maak de kolommen Dienst/Sportlink compacter zodat Vrije capaciteit op een gemiddeld standaardscherm zichtbaar is. Zie [backlog](../../BACKLOG.md) en [prototypeplanning](../../DVK-PROTOTYPE-PLANNING.md).
- BL-13 RPA blijft een afzonderlijk vervolgtraject na integrale v0.5-acceptatie.

**Status bij vastlegging:** functioneel geaccepteerd, documentatie bijgewerkt op de bestaande PR-branch, merge nog niet uitgevoerd.
