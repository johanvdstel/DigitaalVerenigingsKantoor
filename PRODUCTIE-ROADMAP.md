# DVK — Productieroadmap

**Status:** richtinggevend kader; nog geen goedgekeurd technisch ontwerp of aanbestedings-/hostingbesluit.  
**Moment:** na functionele acceptatie van prototype v0.5, met architectuurvoorwaarden die nu al meewegen.  
**Gerelateerd:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Functionele backlog](BACKLOG.md).

## Doel en afbakening

Het prototype bewijst functionele bruikbaarheid. De **productiefase** maakt DVK veilig, beheersbaar, herstelbaar en duurzaam inzetbaar voor bevoegde CKC-medewerkers en vrijwilligers, bij voorkeur in een **gehoste omgeving**. Productie is geen automatische omzetting van de lokale Streamlit-app of SQLite-bestanden.

## Productiewerkstromen

| Werkstroom | Vereisten en te onderzoeken keuzes | Bewijs voor acceptatie |
| --- | --- | --- |
| Hosting en infrastructuur | Beheerde hosting, bij voorkeur binnen EU/EER; netwerksegmentatie, TLS, gescheiden omgevingen (ontwikkeling/test/productie), configuratie en uitrolproces. Cloudprovider en platform nog te kiezen. | Beheermodel, infrastructuurontwerp, deployment- en hersteltest |
| Duurzame database | Relationele database (bijv. PostgreSQL als kandidaat), schema-/datamigraties, transacties, toegangsbeheer, back-ups, herstel en bewaarbeleid. Geen productieafhankelijkheid van lokale prototype-SQLite. | Migratieproef, integriteit, back-up/restore-test |
| Veilige importfunctionaliteit | Beheerde Sportlink API-import en veilige handmatige Excel/CSV-import waar nodig; uploadbeperkingen, schema-/bestandsvalidatie, duplicaatdetectie, bronherkomst, peildatum, staging, expliciete bevestiging en veilige foutafhandeling. | Test met synthetische en gecontroleerde CKC-data, rollback-/foutscenario's |
| API-koppelingen | Vrijwilligers en Programma met veilige authenticatie, secretsbeheer, retries/rate limits, time-outs, bronstatus en monitoring. Behoud Sportlink als bronhouder; schrijfbevoegdheden alleen na apart besluit. | Contract-, integratie- en storingsproeven |
| Identity management | Persoonlijke gebruikersaccounts; passende authenticatie, MFA voor bevoegde rollen, accountuitgifte, intrekking en herstel; eventueel federatie/SSO onderzoeken. | In-/uitdienst- en toegangsproeven |
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
- Scope van een eventuele toekomstige Sportlink-schrijfkoppeling (niet besloten).

**Geen productiestap uitvoeren of productiegeschiktheid claimen zonder afzonderlijke toets en expliciet akkoord.**
