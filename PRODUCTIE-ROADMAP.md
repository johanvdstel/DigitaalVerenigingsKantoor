# DVK — Productieroadmap

**Status:** richtinggevend kader, status bijgewerkt op 24 oktober 2026 na PR #41 en #42; nog geen goedgekeurd technisch ontwerp of aanbestedings-/hostingbesluit.  
**Moment:** na functionele acceptatie van prototype v0.5, met architectuurvoorwaarden die nu al meewegen.  
**Gerelateerd:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Functionele backlog](BACKLOG.md).

De prototypebaseline omvat sinds [PR #38](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/38) een lokaal geaccepteerde Vrijwilligers API-integratie, duurzame planningssessies en No-Show-historie (SQLite-schema 13). [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) voegde de lokaal geaccepteerde Programma-teamkoppeling en datumverwerking toe; [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseerde de lokale CSV-exportpaden. De volledige Programma-integratie en integrale v0.5-acceptatie blijven open. Dit is **geen** productieacceptatie en wijzigt de nog openstaande integrale v0.5-acceptatie of de hieronder beschreven productievoorwaarden niet.

## Doel en afbakening

Het prototype bewijst functionele bruikbaarheid. De **productiefase** maakt DVK veilig, beheersbaar, herstelbaar en duurzaam inzetbaar voor bevoegde CKC-medewerkers en vrijwilligers, bij voorkeur in een **gehoste omgeving**. Productie is geen automatische omzetting van de lokale Streamlit-app of SQLite-bestanden.

## Productiewerkstromen

| Werkstroom | Vereisten en te onderzoeken keuzes | Bewijs voor acceptatie |
| --- | --- | --- |
| Hosting en infrastructuur | Beheerde hosting, bij voorkeur binnen EU/EER; netwerksegmentatie, TLS, gescheiden omgevingen (ontwikkeling/test/productie), configuratie en uitrolproces. Cloudprovider en platform nog te kiezen. | Beheermodel, infrastructuurontwerp, deployment- en hersteltest |
| Duurzame database | Relationele database (bijv. PostgreSQL als kandidaat), schema-/datamigraties, transacties, toegangsbeheer, back-ups, herstel en bewaarbeleid. Geen productieafhankelijkheid van lokale prototype-SQLite. | Migratieproef, integriteit, back-up/restore-test |
| Veilige importfunctionaliteit | Beheerde Sportlink API-import en veilige handmatige Excel/CSV-import waar nodig; uploadbeperkingen, schema-/bestandsvalidatie, duplicaatdetectie, bronherkomst, peildatum, staging, expliciete bevestiging en veilige foutafhandeling. | Test met synthetische en gecontroleerde CKC-data, rollback-/foutscenario's |
| API-koppelingen | Vrijwilligers en Programma met veilige authenticatie, secretsbeheer, retries/rate limits, time-outs, bronstatus en monitoring. Behoud Sportlink als bronhouder; schrijfbevoegdheden alleen na apart besluit. | Contract-, integratie- en storingsproeven |
| RPA-uitvoer Ledendiensten (BL-13) | Afzonderlijke browseruitvoer van menselijk goedgekeurde indelingen; Playwright + Python als kandidaat. Veilige sessies/rechten, unieke bronidentificatie, controle op gewijzigde bezetting, voorkomen dubbele invoer, teruglezen, herstel en onderhoud bij schermwijzigingen. Eerst lokale proef en pilot; geen v0.5-writeback. | Positieve BL-13a/b-acceptatie; uitvoer- en herstelproef; eigenaar en handmatige terugvalprocedure |\n| Identity management | Persoonlijke gebruikersaccounts; passende authenticatie, MFA voor bevoegde rollen, accountuitgifte, intrekking en herstel; eventueel federatie/SSO onderzoeken. | In-/uitdienst- en toegangsproeven |
| Autorisatie | Rollen en rechten per module en handeling, least privilege, server-side afdwinging, functiescheiding voor gevoelige beslissingen. | Autorisatiematrix en negatieve toegangsproeven |
| Security en privacy | Versleuteling onderweg en waar passend in opslag, secretsbeheer, kwetsbaarhedenbeheer, logging zonder onnodige persoonsgegevens, AVG-grondslag, dataminimalisatie, bewaartermijnen en verwerkersafspraken. DPIA-behoefte beoordelen. | Securityreview, privacybeoordeling, pentest/gerichte beveiligingstests |
| Audit en beheer | Herleidbare mutaties en plannerbeslissingen, auditretentie, monitoring/alarmering, incidentrespons, patchbeheer en gecontroleerde releases. | Auditproef, incident- en beheerprocedures |
| Continuïteit | Beschikbaarheidseisen, hersteldoelen (RPO/RTO), back-ups, restore-tests, operationeel eigenaarschap en support. | Herstel- en overdrachtsoefening |
| Migratie en ingebruikname | Overdracht van relevante duurzame DVK-feiten; géén automatische migratie van demo- of tijdelijke werkvoorraad; datakwaliteit, gebruikersacceptatie, opleiding en gecontroleerde livegang. | Migratieplan, acceptatie en go/no-go |

## Architectuurprincipes die al gelden tijdens v0.5

1. **Scheid domein-/applicatielogica van Streamlit en navigatie.** De UI moet later vervangbaar blijven.
2. **Scheid persistentie via interfaces/repositories.** Databasekeuze mag de beleidsregels niet bepalen.
3. **Scheid bronfeiten, tijdelijke werkvoorraad en duurzame DVK-feiten.** Sportlink blijft bronhouder van feitelijke inroosteringen en eigen urenregistratie.
4. **Read-only richting Sportlink in v0.5.** Productie-writeback is geen impliciete vervolgstap en vraagt afzonderlijke bevoegdheids-, API- en procesbesluiten.
5. **Beveilig autorisatie buiten de UI.** Een verborgen knop is geen toegangscontrole.
6. **Verwerk echte CKC-data zorgvuldig.** In de prototypefase blijven bronbestanden lokaal; geen persoonsgegevens in GitHub, Codex of ChatGPT.

## Voorgestelde productiefasering

| Fase | Resultaat | Besluitpunt |
| --- | --- | --- |
| P0 — Inventarisatie | Gebruikers/rollen, processen, data, volumes, wettelijke en beheervereisten; risicoanalyse. | Scope en eigenaarschap |
| P1 — Architectuurkeuze | Hosting, database, identity provider, integratie- en importontwerp, beveiligingsmodel, kostenindicatie. | Architectuur- en budgetakkoord |
| P2 — Productiebouw | Infrastructuur, database, veilige import, IAM/autorisatie, auditing, beheer en migraties. | Technische gereedheid |
| P3 — Productieacceptatie | Functionele regressie in productieachtige omgeving, beveiligings-/privacytoets, hersteltest en gebruikersacceptatie. | Go/no-go |
| P4 — Gecontroleerde livegang | Dataoverdracht, gebruikersinrichting, monitoring, support en nazorg. | Formele ingebruikname |

## Nog te besluiten

- Hostingprovider, locatie, kosten, contracten en verantwoordelijke beheerorganisatie.
- Identiteitsbron/SSO, MFA-niveau, rollen, beheerders en autorisatiebeleid.
- Definitief databasesysteem en migratie van duurzame feiten.
- Toegestane bronkanalen, bewaartermijnen, importfrequentie en eigenaarschap.
- Privacyrollen, verwerkersovereenkomsten en noodzaak van DPIA.
- Beschikbaarheid, hersteldoelen, support en operationeel budget.
- Scope en uitvoeromgeving van RPA voor Ledendienstindelingen (BL-13); backlogopname gevraagd op 12 oktober 2026, implementatie en productiebevoegdheid nog niet geaccepteerd. Eventuele overige Sportlink-schrijfkoppelingen blijven apart te besluiten.

**Geen productiestap uitvoeren of productiegeschiktheid claimen zonder afzonderlijke toets en expliciet akkoord.**

## Plaats van RPA in de productiefasering

**Voorstel, 12 oktober 2026:** BL-13a start als lokale haalbaarheidsproef na integrale v0.5-acceptatie; BL-13b volgt als kleine pilot onder toezicht. RPA hoeft de eerste read-only productielivegang niet te blokkeren: handmatige Sportlink-invoer blijft mogelijk.

- **P0/P1:** scope, bevoegde planner, rechten, eventuele Sportlink-notificaties, uitvoeromgeving en onderhoudseigenaar onderzoeken; definitieve techniek pas na de proef.
- **P2:** na positief proefresultaat de uitvoercomponent en resultaatregistratie beheerd inbouwen, inclusief veilige herstart en controle op dubbele of inmiddels gewijzigde indelingen.
- **P3:** pilotresultaten, autorisatie, terugleescontrole, gedeeltelijke uitvoering, sessieverloop en herstel toetsen; apart go/no-go voor externe mutaties.
- **P4:** gecontroleerd activeren voor bevoegde planners, met monitoring, support en handmatige terugval.

Deze planning autoriseert geen daadwerkelijke Sportlink-mutaties. Exacte datums en releasenummers zijn nog niet vastgesteld. De uitvoercomponent blijft gescheiden van de DVK-domeinlogica, zodat een later beschikbare schrijf-API onderzocht kan worden zonder het selectiebeleid te vervangen.
