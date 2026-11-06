# DVK v0.5 — gerichte gapanalyse no-showarchitectuur

**Status:** geactualiseerd na CKC-verduidelijkingen over Sportlink Vrijwilligers-API, Leden-CSV en inroostering; technische herstelimplementatie nog niet uitgevoerd.  
**Referentie:** `prototype-v0.5`, `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` FR-01–FR-12 en `AGENTS.md` §4a.  
**Scopegrens:** PR #19 (functieclassificatie) blijft afzonderlijk; geen merge of codewijziging als onderdeel van deze analyse.

## 1. Vaststaande functionele afspraken

1. Sportlink is bronhouder van feitelijke ledendienstinroosteringen. De planner verwerkt tijdelijke DVK-voorstellen handmatig in Sportlink; een succesvolle nieuwe Sportlink-synchronisatie vervangt de tijdelijke DVK-planningsposities.
2. Een no-show mag uitsluitend op een feitelijke Sportlink-inroostering worden geregistreerd; nooit op uitsluitend tijdelijke DVK-planning.
3. Nieuwe no-shows zijn onveranderlijke, zelfstandige en duurzame DVK-feiten met voldoende dienstcontext en Sportlink-herkomst. Intrekkingen blijven afzonderlijke duurzame DVK-feiten met reden, actor en tijdstip; ingetrokken no-shows tellen niet mee.
4. Bestaande oude no-shows en eventuele intrekkingen uit achterhaalde prototypefunctionaliteit zijn wegwerpbare testgegevens: **geen migratie of historisch herkomstonderzoek**. Geaccepteerde regressiegevallen blijven inhoudelijk beschermd maar krijgen passende nieuwe synthetische fixtures.
5. CKC geeft aan dat Voetbal.nl niet toestaat dezelfde persoon tweemaal op dezelfde dienst in te roosteren. Dit is een bronwaarborg; geen aanleiding voor een nieuwe DVK-workflow voor dubbele inschrijvingen.

## 2. Vastgestelde bestaande integratie en identificatie

De al functioneel geaccepteerde v0.4-integratie `dvk/vrijwilligers_client.py` roept read-only `https://data.sportlink.com/vrijwilligers` aan met `vrijwilligerstaakcode`, `aantaldagen`, `client_id`, `weekoffset` en de veldselectie `naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag`. `dvk/vrijwilligers_adapter.py` zet de individuele registraties om in `VolunteerBooking` en koppelt ze via taakcode en datum/tijd aan een `DutyService`.

De Leden-CSV bevat de afzonderlijke velden achternaam, voorletters, tussenvoegsels, roepnaam en de unieke `Rel. code`. Volgens de CKC-toelichting bouwt Sportlink de API-naam uit deze naamonderdelen op. Vergelijk daarom niet twee verschillende weergavekolommen letterlijk: reconstrueer de API-weergave uit de ledenvelden, koppel de resulterende naam aan één `Rel. code`, en gebruik daarna die relatiecode als persoonsidentiteit. Een ontbrekende of niet-eenduidige overeenkomst wordt gesignaleerd zonder automatische gok. Dit is gewone regressiedekking, geen apart onderzoekstraject.

**Afgesproken logische sleutel voor één feitelijke inroostering:**

```text
(Rel. code, vrijwilligerstaakcode, begindatum/-tijd, einddatum/-tijd)
```

De vrijwilligerstaakcode is de parameter van de API-uitvraag; de overige dienstvelden komen uit de API. Deze sleutel is onafhankelijk van API-resultaatvolgorde en van de uiteindelijke naampresentatie. Locatie en oorspronkelijke naam blijven nuttig als context/provenance, maar hoeven geen extra unieke sleutelvelden te worden. De door CKC beschreven Voetbal.nl-inroosterbeperking geldt als functionele waarborg tegen dubbele inschrijving op dezelfde dienst. Een normale importconsistentiecontrole volstaat; geen afzonderlijke ontwerpopdracht voor hypothetische dubbele inschrijvingen.

## 3. Geconstateerde implementatiegaten

| Onderdeel | Huidige situatie | Gerichte correctie |
|---|---|---|
| Tijdelijke DVK-planning | Afzonderlijke `temporary_planning`-repository, inclusief terugdraaien. | Behouden; niet als feitelijke Sportlink-indeling behandelen. |
| Feitelijke bron | v0.4 Vrijwilligers-API en adapter bestaan al. | Hergebruiken; geen nieuwe API-client of algemene importlaag. |
| Persoonsidentiteit | `VolunteerBooking` bevat nu een `volunteer_name`, geen gekoppelde `Rel. code`. | API-naam deterministisch reconstrueren uit ledenvelden en koppelen aan relatiecode. |
| Registratie-identiteit | De adapter gebruikt nu een taakcode plus regelnummer als provenance-sleutel. | Logische sleutel baseren op relatiecode, taakcode en begin-/eindtijd; geen afhankelijkheid van API-regelvolgorde. |
| No-showservice | `NoShowApplicationService.register()` controleert uitsluitend een legacy `duty_assignments`-record. | Alleen feitelijke via Sportlink verkregen indelingen toelaten. |
| Duurzame context | `NoShowEvent` verwijst slechts naar `assignment_id`; latere weergave hangt af van legacy indeling. | Bewaar bij registratie voldoende immutable persoon-, dienst- en broncontext om ook na volgende synchronisatie raadpleegbaar te zijn. |
| UI | De no-showkeuzelijst leest legacy DVK-indelingen. | Selecteer feitelijke Sportlink-inroosteringen via de applicatieservice; presenteer leesbare namen en diensten. |
| Tests | UI-fixtures construeren zelf legacy `DutyAssignment`-records. | Vervang door synthetische brongetrouwe API-/ledenfixtures; behoud semantiek van no-show, intrekking en teller; test weigering van uitsluitend tijdelijke planning. |
| CI PR #19 | Bestaande intrekkings-UI-test mist in CI de verwachte succesmelding. | Onderzoek afzonderlijk; architectuurverschil is niet bewezen als oorzaak. |

## 4. Proportionaliteitscontrole volgens AGENTS.md

- **Feit:** de relevante read-only Sportlink-API en adapter zijn al geïmplementeerd en geaccepteerd in v0.4; de bestaande no-showservice gebruikt nog legacy indelingen.
- **Geaccepteerde eis:** een no-show vergt een feitelijke Sportlink-inroostering; nieuwe no-shows en intrekkingen blijven duurzame DVK-feiten.
- **Concrete technische noodzaak:** koppel de bestaande API-booking aan `Rel. code`, vorm de afgesproken logische sleutel, en sluit de no-showservice, opslag, UI en tests daarop aan.
- **Niet nodig:** extra export, nieuwe API, verkennende naamstudie, aparte dubbele-inschrijvingworkflow, migratie van oude prototypegegevens of opportunistische refactor.
- **Nog technisch uit te werken:** exacte implementatie van de immutable no-showsnapshot en het behoud daarvan bij verversing van API-data; oorzaak van de rode CI-test.

## 5. Afgebakende technische vervolgopdracht — nog niet uitvoeren

1. Hergebruik de bestaande v0.4 Vrijwilligers-API, adapter en Leden-CSV-inleesroute. Implementeer de deterministische naamopbouw en koppeling aan `Rel. code` met gerichte regressietests.
2. Definieer de feitelijke inroostering met de afgesproken logische sleutel en leg bij nieuwe no-shows een immutable context/provenancesnapshot vast. Herhaalde API-opvragingen mogen bestaande nieuwe no-shows en intrekkingen niet aantasten.
3. Herijk no-showservice, opslag en UI om uitsluitend feitelijke Sportlink-inroosteringen te gebruiken. Tijdelijke DVK-planning blijft hiervan uitgesloten.
4. Gooi verouderde prototype-no-shows, intrekkingen en bijbehorende achterhaalde fixtures weg; geen datamigratie. Bewaak de geaccepteerde functionele testsemantiek met nieuwe synthetische brongetrouwe fixtures.
5. Onderzoek onafhankelijk daarvan de rode GitHub Actions-test van PR #19 op de betrokken branches; pas tests niet enkel aan om CI groen te krijgen.
6. Voer gerichte tests en de volledige regressiesuite uit. Geen wijziging of merge van PR #19 zonder afzonderlijke acceptatie.

**Beslisgrens:** deze gapanalyse is documentatie. Codewerk, testwijzigingen en merges blijven afzonderlijke gecontroleerde stappen.
