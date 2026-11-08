# DVK — Prototypeplanning v0.5

**Status:** Iteratie 1 (BL-17/20/21) functioneel geaccepteerd op 29 oktober 2026 via PR #53; Iteratie 2 (BL-03) is lokaal functioneel geaccepteerd op 29 oktober 2026; PR #55 is op 29 oktober 2026 gemerged; Iteratie 3 (BL-23/24) functioneel geaccepteerd op 30 oktober 2026 en PR #56 gemerged. Iteratie 4 (BL-14 incl. voormalig BL-15) functioneel geaccepteerd op 31 oktober 2026; PR #58 gemerged op codecommit `be1cd1d` (mergecommit `267c94779a04`). Integrale v0.5-acceptatie blijft open.
**Doel:** van geaccepteerde taakplichtcontrole naar bruikbare CKC-ledendienstplanning met echte brongegevens.  
**Gerelateerd:** [Backlog](BACKLOG.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md).

## Mijlpalen en stappen

| Volgorde | Stap | Gewenst resultaat / acceptatie | Status |
| --- | --- | --- | --- |
| Afgerond | Stap 2 ronde 4 — taakplichtcontrole | Read-only afleiding, vergelijking met Sportlink A, bron- en controlediagnose; lokaal functioneel geaccepteerd en [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged. | **Afgerond** |
| Afgerond | BL-04 — DVK-portaal | Startscherm en modulenavigatie; lokaal geaccepteerd en [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged. | **Afgerond (19 oktober 2026)** |
| Voorbereiding afgerond | Vrijwilligers API-responsvalidatie (PR #34) en tijdelijke planning (PR #35) | Ongeldige bronresponsen worden vóór publicatie geweigerd; tijdelijke planning bleef volgens de toen geaccepteerde afspraak behouden bij navigatie en verviel bij procesherstart; deze laatste afspraak is vervangen door het op 22 oktober 2026 geaccepteerde [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). | **Afgerond en lokaal geaccepteerd waar van toepassing; geen volledige live API-integratie** |
| Afgerond | Integratie Vrijwilligers API en BL-16 — duurzame planningssessies | Actuele Sportlink-inroosteringen en bezetting; bronrevisie, sessiehervatting, bevestigde vervanging, No-Show-selectie en registratie met historie. [PR #38](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/38). | **Lokaal functioneel geaccepteerd (23 oktober 2026); 917 regressietests, CI #332 groen** |
| 3 | Integratie Programma API | Wedstrijden en relevante team-/wedstrijdcontext betrouwbaar ophalen/vertalen voor kandidaatbeoordeling; bronstatus en foutafhandeling testen. | **Afgerond en lokaal functioneel geaccepteerd via PR #41 en BL-18/PR #46; kandidaatfilter BL-20 geaccepteerd in Iteratie 1/PR #53** |
| 4 | BL-03 — Achterstallige uren | Optionele historische Sportlink-CSV via relatiecode; dienstmaanden juli t/m december; geen wijziging actuele urenbalans. | **Functioneel geaccepteerd op 29 oktober 2026; PR #55 gemerged op 29 oktober 2026** |
| 5 | Stap 3 — Ledendienst Planning | Taakplicht + Vrijwilligers + Programma + achterstanden combineren voor zinvolle kandidaten, prioriteit, bezetting en tijdelijke planning. | **Na bronacceptaties** |
| Afgesloten/vervallen | BL-05 t/m BL-11 | BL-05 en BL-06 vervallen als afzonderlijke DVK-functies; BL-07 t/m BL-11 functioneel afgesloten volgens backlog. | **Geen afzonderlijk uitvoerwerk** |
| PR #44 geaccepteerd en gemerged; vóór integrale v0.5-acceptatie | BL-18 — Herstructurering Ledendienst Planning | Vijf gescheiden secties: Instellingen, Databronnen, Diensten, Kandidaten, Wedstrijden; behoud bestaande functionaliteit en afzonderlijke lokale UI-acceptatie. | **Afgerond en lokaal functioneel geaccepteerd op 26 oktober 2026; nieuwe inklapwens valt onder BL-23; [verslag](code/Prototype/DVK-v0.5-BL18-schermindeling.md)** |
| Afgerond | BL-17, BL-20, BL-21 — Iteratie 1 | Sportlink-kandidatenbasis, verwijderde uitzonderingsinvoer, teamspeeldagfilter/noodselectie, directe begrijpelijke toelichting en actieve versie. | **Functioneel geaccepteerd op 29 oktober 2026 via PR #53; zie acceptatieverslag** |
| Iteratie 4 afgerond; Iteratie 5 open | BL-14 (incl. BL-15), BL-19 | BL-14 lokaal functioneel geaccepteerd en gemerged; BL-19 is de volgende iteratie. | **BL-14 afgerond op 31 oktober 2026; BL-19 open** |
| Open | BL-22 | Centraal leesbaar Python-regelbestand (na inventarisatie). | **Nog te implementeren en accepteren** |
| Iteratie 3 | BL-23, BL-24 | Inklapbare rubrieken en acht bronnen in bronstatusoverzicht. | **Functioneel geaccepteerd op 30 oktober 2026 op `0aa8445d9f70d2f099f2599e117035f00d05e0a1`; PR #56 op 30 oktober 2026 gemerged naar `prototype-v0.5` (mergecommit `d9942c328e75a7235803319807504fbd36c522d4`); aanvullende lokale visuele controle geslaagd.** Zie [Iteratie 3-verslag](code/Prototype/DVK-v0.5-iteratie3-bronstatus-rubrieken.md). |
| Mijlpaal | Integrale functionele acceptatie v0.5 | Echte CKC-bronnen lokaal, samenhang tussen taakplicht, bronnen, planning, sync, no-shows, portaal; afwijkingen expliciet beoordeeld. | **Nog open** |

## Vastgestelde resterende uitvoeringsvolgorde prototype v0.5 (28 oktober 2026)

De opdrachtgever heeft onderstaande **werkplanning** bevestigd. De volgorde is leidend, maar geen onwrikbaar watervalplan: bij aantoonbare technische afhankelijkheden kunnen werkzaamheden worden gecombineerd of verschoven, na afstemming. Er zijn nog **geen kalenderdata of tijdsramingen** vastgesteld. Elke iteratie krijgt gerichte technische controle, regressietests en afzonderlijke lokale functionele acceptatie.

| Volgorde | Iteratie | Backlog | Uitvoering en acceptatie |
| --- | --- | --- | --- |
| 1 — afgerond | Kandidaten en versiebeheer | BL-17, BL-20, BL-21 | Functioneel geaccepteerd door Johan op 29 oktober 2026 via PR #53; codeversie `9016c8a`. 1209 regressietests en CI #381 groen. Eén weekendrichting en noodkandidaten uitsluitend synthetisch gedekt; zie acceptatieverslag. |
| 2 — functioneel geaccepteerd | Achterstallige uren | BL-03 | Historische CSV gekoppeld via relatiecode; tweede prioriteitscriterium uitsluitend juli t/m december op dienstdatum, geen actuele urenmutatie. Planner borgt het vorige seizoen. Foutafhandeling houdt planning bruikbaar. **Lokaal functioneel geaccepteerd op 29 oktober 2026**, PR #55 gemerged; zie Iteratie-2-acceptatieverslag. |
| 3 — afgerond en functioneel geaccepteerd | Bedieningsgemak en bronstatus | BL-23, BL-24 | Vijf rubrieken onafhankelijk inklapbaar (bij openen allemaal ingeklapt); compleet en eerlijk overzicht van gebruikte API- en CSV-bronnen met status en import-/ophaalmomenten. |
| 4 — afgerond | Dynamische dienstencatalogus | BL-14 (inclusief voormalig BL-15) | Twee lokale CSV-bestanden in plaats van rechtstreeks `Shift Catalog.xlsx`; aanvullende catalogus- en Sportlink-diensten, gebruikte taakcodes en bevestigde Reload catalog. Functioneel geaccepteerd op 31 oktober 2026 met lokale CKC-weekcatalogus van 23 reguliere diensten, aanvullende Sportlink-dienstmomenten, reload, kandidaatselectie en undo; de drie periodekeuzes zijn hergeaccepteerd. PR #58 gemerged op `267c94779a04`. Zie [Iteratie 4](code/Prototype/DVK-v0.5-iteratie4-BL14.md). Geen afzonderlijk beheerscherm. |
| 5 — functioneel geaccepteerd (2 november 2026), PR #61 nog open | Zelfstandig No-showmanagement | BL-19 | No-showbediening uit Ledendienst Planning verplaatsen; aanmelden voor werkelijk ingeroosterde diensten binnen de laatste 14 kalenderdagen inclusief vandaag; seizoensoverzicht met historie en intrekking van oudere actieve registraties. Geen gegevensverlies of Sportlink-writeback. |
| 6 | Onderhoudbaarheid beleidsregels | BL-22 | Bestaande regels en tests inventariseren; CKC-regels bij voorkeur in één goed leesbaar en reviewbaar Python-bestand centraliseren zonder beleidsuitkomsten te veranderen. Geen Rules-tool of beheerinterface. |
| Eindmijlpaal | Integrale functionele acceptatie v0.5 | Voormalig BL-12 | Met echte CKC-gegevens uitsluitend lokaal de samenhang van taakplicht, bronnen, planning, sessies, no-shows en portaal toetsen; expliciete acceptatie door opdrachtgever. |

**Na integrale acceptatie van v0.5:** BL-13a RPA-haalbaarheidsproef, daarna alleen bij positief besluit BL-13b (pilot) en BL-13c (beheerde productie-invoering). Dit is geen onderdeel van de resterende v0.5-ontwikkeliteraties. De Sportlink-verwerking blijft tot die tijd handmatig.

Stap 3 mag niet afhankelijk zijn van onbevestigde aannames over de twee API's; beide API-integraties zijn afzonderlijk functioneel geaccepteerd. De bovenstaande iteraties completeren de nog openstaande v0.5-scope.

### Acceptatie Iteratie 4 — BL-14 (31 oktober 2026)

CKC heeft de implementatie van BL-14 (inclusief voormalig BL-15) functioneel geaccepteerd op codecommit `be1cd1d52ae1dad7a10d35d7e89c3874e285e7ad` van [PR #58](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/58), gemerged naar `prototype-v0.5` als `267c94779a04413f9f523ec147335842bef3af5c`. Lokale tests bevestigen dynamische CSV-catalogus, reguliere en aanvullende Sportlink-dienstmomenten, bezetting, validatie en bevestigde reload, kandidaatselectie, tijdelijke planning en undo. De CKC-weekcatalogus bevat na lokale aanpassing 23 reguliere diensten, correct getoond; lokale CKC-bestanden zijn niet in GitHub geplaatst en de synthetische 29-diensten-regressies blijven behouden. De UI-keuzes Dag, Week en Aangepast tonen direct de juiste roosterperiode en zijn hergeaccepteerd. 55 gerichte tests en 1307 regressietests geslaagd; CI #397 groen. Volgende iteratie: **Iteratie 5 — BL-19, zelfstandig No-showmanagement**. Integrale acceptatie v0.5 blijft open. Zie [Iteratie 4-verslag](code/Prototype/DVK-v0.5-iteratie4-BL14.md).

### Acceptatie Iteratie 1 (29 oktober 2026)

Eén richting van de weekendfilter is lokaal waargenomen; de andere richting en noodkandidaten zijn uitsluitend synthetisch getoetst. Dubbele teamkoppelingen en ongeldige bronwaarden zijn synthetisch gedekt. Integrale v0.5-acceptatie blijft open. Versieaanduiding, Sportlink leidend, verwijderde uitzonderingsinvoer, bevestiging/undo, overige beschikbaarheid en de directe begrijpelijke kandidaattoelichting zijn lokaal geslaagd. [Verslag](code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md). Volgende stap: [overdracht Iteratie 2 — BL-03](code/Prototype/DVK-v0.5-overdracht-iteratie2-BL03.md).

### Aanvullende afgeronde voorbereidingen (21 oktober 2026)

- **PR #34 — VRIJ-01:** ongeldige of lege Vrijwilligers API-responsen worden vóór publicatie geweigerd; bestaande bronfeiten en tijdelijke planning blijven behouden bij een mislukte verversing. Gemerged naar `prototype-v0.5` (merge-commit `8ccdb473`). Dit is bronveiligheid, **geen** bewijs dat de volledige live API-integratie is geaccepteerd.
- **PR #35 — tijdelijke planning:** werkvoorraad blijft behouden tijdens schermwisselingen en browser-refresh binnen hetzelfde applicatieproces; een periodewisseling met tijdelijke indelingen vereist waarschuwing en expliciete bevestiging; volgens de destijds geaccepteerde implementatie werd de werkvoorraad na een echte applicatieherstart gewist; **dit is inmiddels een achterhaalde functionele regel**, vervangen door het [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). Lokaal vijf acceptatiescenario's geslaagd; 693 regressietests en CI groen. Gemerged naar `prototype-v0.5` (merge-commit `e7d173e7`). Duurzame no-showgegevens blijven buiten deze wisacties.
- **Historische stand 21 oktober 2026 — toen resterend:** BL-03, BL-14, BL-17, BL-19 t/m BL-24 en integrale v0.5-acceptatie; de Programma API-integratie is afgerond. De Vrijwilligers API-integratie en duurzame sessies zijn via PR #38 lokaal geaccepteerd.

### Afronding BL-04

BL-04 is lokaal visueel geaccepteerd en via [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged naar `prototype-v0.5` (`68ae25fa`). BL-04-01: functiespecifieke instellingen direct onder de betreffende schermtitels; BL-04-03: overbodige toelichting verwijderd, Rooster Generator als uitgeschakelde knop; BL-04-04: acht functies uniform één per regel op het startscherm. BL-04-02 is vervallen en niet geïmplementeerd; Planning blijft bewust met demonstratiegegevens werken. 62 gerichte tests, 636 regressietests en CI groen. Bekende beperking: CSV-uploads van Taakplichtcontrole na schermwisseling opnieuw selecteren. Volgende stap: afzonderlijke verificatie en acceptatie Vrijwilligers API.

## Acceptatie per stap

- **Vooraf:** controleer actuele code, bestaande adapters, tests en GitHub Issues. Beschrijf alleen bewezen hiaten.
- **Functioneel:** leg concrete invoer, verwachte uitvoer, bronherkomst, foutscenario's en grenzen vast; toets met opdrachtgever.
- **Technisch:** synthetische tests, volledige regressie, privacycontrole en CI groen; geen writeback naar Sportlink in v0.5.
- **Integratie:** echte CKC-brondata alleen lokaal op de computer van opdrachtgever; geen persoonsgegevens in commits, logs of PR's.
- **Governance:** aparte branch/PR; niet mergen zonder expliciete goedkeuring.

## Bijzonderheden en afhankelijkheden

### Taakplicht (Stap 2)
De read-only controle is functioneel geaccepteerd: 650 leden, 563 overeenkomsten, 87 afwijkingen, 0 onbetrouwbaar beoordeelbaar. De 87 afwijkingen liggen bij de planner; terugkoppeling voedt BL-05, niet het reeds geaccepteerde dashboard.

### Vrijwilligers API
Er bestaan reeds Sportlink Vrijwilligers-client-/adapterbouwstenen in het prototype. Bepaal vóór nieuwe code welke verbinding, broncontracten en actuele bezetting werkelijk werken. Bevestig authenticatie, leesrechten, peildatum, bronidentiteit, synchronisatiegrens en veilige foutafhandeling. Geen aannames dat live toegang al operationeel is.

### Programma API

De gerichte teamnaamkoppeling van 24 oktober 2026 is via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) gemerged en functioneel geaccepteerd, inclusief datum-/tijdverwerking. Lokale controle: 141 ontvangen, 141 gekoppeld, 0 bronmeldingen, 141 operationele wedstrijden. Operationele schermintegratie is inmiddels via BL-18/PR #46 functioneel geaccepteerd. De v0.5-import gebruikt Teams-naamidentiteit, bewaart Speeldag en competitiecontext en maakt onopgeloste koppelingen expliciet. Zie [implementatie en lokaal acceptatiescenario](code/Prototype/DVK-v0.5-teamnaamkoppeling.md). Dit wijzigt geen beleid voor meerdere wedstrijden/lidmaatschappen; de Programma-integratie is inmiddels met de schermintegratie onder BL-18 afgerond.
Onderzoek bestaande client-/adapterbouwstenen en beschikbaarheid van wedstrijdgegevens. Leg teamkoppeling, tijdstippen, thuis/uit, actualiteit en eventuele onvolledigheid expliciet vast voordat kandidaatselectie met deze bron wordt geaccepteerd.

### Lokale Sportlink CSV-exports

[PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) is op 24 oktober 2026 lokaal functioneel geaccepteerd en gemerged. Standaardmap: `$HOME/Documents/DVK-Sportlink-exports/`; vaste bestanden: `Leden.csv`, `Functies.csv`, `Commissies.csv`, `Teams.csv` en `Overzicht per periode.csv`. Het Programma-controlescript vond `Teams.csv` zonder expliciet pad en verwerkte 141/141 wedstrijden; de overige vier bestanden zijn synthetisch getest, niet afzonderlijk met echte exports geaccepteerd. Expliciete paden en handmatige Streamlit-uploads blijven ondersteund. De exports blijven lokaal en worden handmatig ververst.

### Achterstallige uren (BL-03)

Historische bron: `~/Documents/DVK-Sportlink-exports/Overzicht per periode vorig seizoen.csv`, dezelfde CSV-kolomstructuur als de actuele urenexport. De planner levert het onmiddellijk voorafgaande seizoen; DVK leidt of verifieert dat bronseizoen niet zelfstandig. Koppeling uitsluitend op `Relatiecode`; `Niet ingedeeld` is de bronwaarde, getoetst aan A−B−C−D. Positieve achterstand telt als tweede criterium na actuele E voor diensten in **juli tot en met december** (`7 <= on_date.month <= 12`); januari t/m juni niet. Nul betekent geen achterstand; negatieve waarden blijven als bronfeit behouden en geven geen krediet. Actuele A/B/C/D/E blijven ongewijzigd.

Bij ontbrekend, onleesbaar of structureel ongeldig historisch bestand blijft planning bruikbaar met een zichtbare waarschuwing. Ontbrekende ledenregels, dubbele relatiecodes, ongeldige getallen en formuleverschillen leveren voor de betrokken kandidaat onbekende/onbetrouwbare historische achterstand op; geen uitsluiting of stilzwijgende nul. Voor rangschikking neutraal, in toelichting onderscheiden van bekende nul, ontbrekende bron en maanden buiten toepassing. Andere geldige historische records blijven bruikbaar. Taakplichtcontrole blijft onafhankelijk van deze optionele bron.

De goedgekeurde W09-datumcorrectie en B-13 zijn traceerbaar bijgewerkt. [Uitvoering en acceptatieverslag](code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md). **Functioneel geaccepteerd op 29 oktober 2026 op codecommit `e3b17fc`; PR #55 gemerged.**

### Stap 3 — Planning
Controleer de volledige keten: beschikbare diensten, feitelijke Sportlink-bezetting, actuele taakplicht, kandidaatgeschiktheid op basis van wedstrijdcontext, prioriteit en achterstand, tijdelijke DVK-planning, undo, handmatige Sportlink-verwerking en correcte synchronisatie. Houd no-shows gekoppeld aan feitelijke Sportlink-inroosteringen.

## Eindmijlpaal v0.5 (voormalig BL-12)

Acceptatie is een **besluit**, geen backlogfeature. Toets gezamenlijk:
1. brongegevens, provenance, actualiteit en foutafhandeling;
2. taakplicht, vrijstellingen, afwijkingen en plannerbeslissingen;
3. kandidaatselectie, achterstanden, tijdelijke planning en sync;
4. no-shows, intrekkingen en correctieopvolging;
5. DVK-portaal en begrijpelijke modulenavigatie.

Vastgelegde restpunten en bewuste beperkingen mogen expliciet worden geaccepteerd; geen stilzwijgende productierijpverklaring. **Prototypeacceptatie is geen productieacceptatie.**

## Na het prototype

De aparte [productieroadmap](PRODUCTIE-ROADMAP.md) behandelt hosting, echte database, veilige imports, identity & access management, security, privacy, operations en migratie. Productiearchitectuur wordt later gekozen; v0.5 houdt businesslogica en UI/gegevensinfrastructuur gescheiden.

## Releasevervolg — RPA (BL-13), toegevoegd 12 oktober 2026

**Bevestigd door opdrachtgever op 27 oktober 2026:** RPA (BL-13) behoudt een expliciete plaats in de prototype-opleverplanning, met de eerste afgebakende vervolgproef na integrale functionele acceptatie van v0.5. De bestaande v0.5-stappen en read-only scope blijven gelden. Er zijn nog geen vaste kalenderdata of geaccepteerde versienummers voor dit vervolg.

| Volgorde / releasevenster | Onderdeel | Besluit / acceptatie |
| --- | --- | --- |
| Huidige v0.5 | Portaal (BL-04 afgerond), afzonderlijke API-acceptaties, achterstanden, Stap 3 Planning en integrale verificatie | Resterende planning afronden; Sportlink-verwerking blijft handmatig |
| Eerstvolgende vervolgiteratie na acceptatie v0.5 | BL-13a — RPA-haalbaarheidsproef | Eén goedgekeurde indeling, teruglezen, dubbele invoer voorkomen en onderbreking veilig hervatten; go/no-go voor pilot |
| Volgende pilotrelease na positieve proef | BL-13b — Kleine batch onder toezicht | Resultaat per indeling en veilige herstart; actuele bezetting opnieuw controleren; fouten naar planner |
| Productierelease na pilotacceptatie en productievoorwaarden | BL-13c — Beheerde RPA-invoering | Voorwaarden P1–P3 uit productieroadmap, operationeel beheer en expliciete productie-go/no-go |

**Motivering:** eerst bewijzen dat DVK met actuele bronnen de juiste voorstellen en synchronisatie levert; daarna pas de externe invoer automatiseren. Zo wordt RPA een vervangbare uitvoercomponent en blijft de bestaande functionele baseline toetsbaar.

**Afhankelijkheden:** Stap 3 Planning, BL-10, unieke bronidentificatie, goedgekeurde indelingen en actuele bezetting. De proef kan lokaal onder toezicht plaatsvinden; een gehoste productierobot is daarvoor geen vereiste. P1 kan de uitvoeromgeving alvast onderzoeken, maar P2-productiebouw volgt pas na positief proefresultaat.

**Aannames / open punten:** Sportlink-browserschermen en rechten zijn nog niet beproefd; ontbreken van een schrijf-API is een uitgangspunt van opdrachtgever. Playwright + Python is een technische kandidaat, geen definitief architectuurbesluit. Exacte datum, releasenummer, beschikbare capaciteit en onderhoudseigenaar worden bij start bepaald. Geen vervroeging van writeback naar v0.5 en geen wijziging van CKC-beleid.

De gedetailleerde scope en acceptatiecriteria staan bij [BL-13](BACKLOG.md#bl-13--rpa-voor-invoer-van-goedgekeurde-ledendiensten-in-sportlink).

## Geaccepteerd ontwerp planningssessies (22 oktober 2026)

Het [functioneel ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md) is door CKC geaccepteerd als functionele baseline en **via PR #38 geïmplementeerd en lokaal functioneel geaccepteerd op 23 oktober 2026**. Een sessie blijft voortaan bij browser-/procesherstart bestaan, kan worden hervat en wordt alleen na expliciete bevestiging afgesloten of vervangen. Periodewisseling en succesvolle vervangende Sportlink-synchronisatie zijn eveneens gecontroleerde sessiegrenzen. No-Show-registratie gebruikt uitsluitend de actieve gevalideerde bron; historische No-Shows blijven duurzaam bewaard. Dit vervangt uitsluitend de tegenstrijdige eerdere herstartafspraak; PR #35 blijft historisch als afgeronde implementatiestap geregistreerd. Technische uitvoering en lokale acceptatie zijn afgerond voor BL-16; integrale acceptatie van prototype v0.5 blijft open. Schema 13 ondersteunt historische No-Show-herregistraties na intrekking.


### Acceptatie Iteratie 5 — BL-19 (2 november 2026)

**2 november 2026 — Iteratie 5 / BL-19 functioneel geaccepteerd door CKC**, op codecommit `069e5a1388e1b66372062d411b5f44a6a6a5429d` van [PR #61](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/61), **nog niet gemerged**. Zelfstandig No-showmanagement (Sportlink-raadpleging en handmatige registratie), 15 kalenderdatums vandaag−14 t/m vandaag, actieve en ingetrokken historie, sanctietelling en intrekking geaccepteerd. Correcties BL-19-01 (datumkiezer), BL-19-02 (alfabetische persoonskeuzes), BL-19-03 (periode-uitleg) en BL-19-05 (historie met tien regels per pagina, registratiemoment nieuwste eerst en één detailpaneel) geaccepteerd. BL-19-04 en BL-19-06 bleken na nadere controle geen defect. 106 gerichte en 1371 regressietests geslaagd, CI #402 groen; paginering met meer dan tien regels, uitzonderingspaden en planningisolatie met synthetische tests gecontroleerd, niet volledig lokaal met echte CKC-scenario's. Geen Sportlink-writeback, schema- of sanctieregelwijziging. Integrale v0.5-acceptatie blijft open; volgende iteratie is **Iteratie 6 — BL-22**. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie5-BL19.md). **Iteratie 6 — BL-22** is de eerstvolgende ontwikkeliteratie; de integrale v0.5-acceptatie en daarna BL-13 blijven afzonderlijke mijlpalen.

### Acceptatie Iteratie 6 — BL-22 (2 november 2026)

**Functioneel geaccepteerd door CKC** op `d0be7dccb31eaeace038bfb867a7c25b2995dd70` in [draft-PR #62](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/62), **niet gemerged**. De eerder beschreven voorkeur voor één centraal Python-regelbestand is na inventarisatie bewust vervangen door vijf herkenbare taakplichtstappen, één kleine gedeelde B-02-domeinfunctie en behoud van de bestaande CSV-functieclassificatie. [Leesbare beleidsregelindex](docs/DVK-v0.5-CKC-beleidsregelindex-Ledendiensten.md) met elf synthetische demonstraties, zonder nieuwe UI of Rules Engine. CKC accepteert de index met de kanttekening dat deze voor niet-ingewijden moeilijk leesbaar is. 1501 regressietests en CI #407 groen; integrale v0.5-acceptatie blijft open. [Acceptatieverslag](code/Prototype/DVK-v0.5-iteratie6-BL22-acceptatie.md).

### Iteratie 7add — UI-correcties (volgende uitvoeringsronde)

**Afgesproken, nog niet uitgevoerd.** (1) Roosterbezettingsmelding uit Databronnen verplaatsen naar Diensten, boven de ophaalknop, met de door CKC vastgestelde plannervriendelijke tekst (zie [backlog](BACKLOG.md)). (2) Kolommen Dienst en Sportlink compacter zodat Vrije capaciteit bij standaard browserbreedte zonder horizontaal scrollen zichtbaar is; richtwaarde 1366 px, 100% zoom. Alleen presentatie; bronvalidatie, API-gedrag en berekeningen ongewijzigd. Eigen Codex-opdracht, regressies en lokale visuele acceptatie. **Daarna** blijft de integrale functionele acceptatie van prototype v0.5 de eindmijlpaal; BL-13 RPA volgt afzonderlijk na v0.5.

### Acceptatie Iteratie 7add — UI-correcties (3 november 2026)

**Functioneel geaccepteerd door CKC** op codecommit `e4d6a9df5c599a47751ea79fa3366dd18ac7b3f5` in [draft-PR #63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63), nog niet gemerged. De waarschuwing over nog niet opgehaalde actuele Sportlink-bezetting staat bij de synchronisatieknop in sectie 3 Diensten. Na twee correctierondes zijn Dienst 110 px, Sportlink 140 px en Vrije capaciteit 65 px geaccepteerd. Bij de lokale visuele controle waren de waarden van Vrije capaciteit volledig zichtbaar zonder horizontaal scrollen; de kop mag afgekapt zijn. Dienstnamen zijn voldoende leesbaar en volledige Sportlink-namen zijn via dubbelklik beschikbaar. 131 gerichte tests, 1502 volledige regressietests, 11 synthetische runners en CI #414 geslaagd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie7add-acceptatie.md). De **volgende mijlpaal is integrale functionele acceptatie van prototype v0.5**. Onderzoek van de langdurige lokale Streamlit-opstart wordt apart gepland; BL-13/RPA blijft een afzonderlijk vervolgtraject na v0.5.


## Actuele vervolgplanning na Planner-overleg — 3 november 2026

**Actuele status 4 november 2026: Iteratie 8 gemerged via PR #65; Iteratie 9 lokaal functioneel geaccepteerd op codecommit `67dd98e` in PR #66, nog niet gemerged.** Deze sectie vervangt oudere uitspraken dat direct na Iteratie 7add de integrale v0.5-acceptatie volgt. Historische statusnotities blijven herkenbaar als momentopnamen. Iteraties 1, 2, 3, 4, 5, 6 en 7add zijn afgerond; [PR #63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63) is volgens de overdracht gemerged (mergecommit `db6fc1773362880663b8fe5b34b40e58434e107d`).

| Stap | Onderwerp | Status |
| --- | --- | --- |
| 8 | Databronnen en schermindeling | Lokaal functioneel geaccepteerd op `6925532`; draft-PR #65 nog niet gemerged |
| 9 | Kandidaatselectie en prioritering | Gepland; onderstaande functionele uitgangspunten overeengekomen, contract- en codetoets nog nodig |
| 10 | Integrale functionele acceptatie v0.5 | Geplande acceptatiemijlpaal, geen reguliere ontwikkeliteratie |
| Daarna | BL-13 — RPA Sportlink | Afzonderlijk traject; eerst haalbaarheidsproef |

### Iteratie 8 — functioneel geaccepteerd, PR #65 nog niet gemerged

**Status 3 november 2026:** Iteratie 8 is door CKC lokaal functioneel geaccepteerd op codecommit `69255327dcf5fc35a578bc12ace985afa0ffe900` in [draft-PR #65](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/65), **nog niet gemerged**. De vier UI-onderdelen zijn visueel goedgekeurd; catalogus-herladen met annuleren en bevestigen is lokaal geslaagd. Technisch: 1506 regressietests, 11 synthetische acceptatiescripts en [CI #422](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41730239295) geslaagd. Iteratie 9 blijft gepland en niet geïmplementeerd; Iteratie 10 blijft de integrale acceptatiemijlpaal.

1. **UI-1 — Schermindeling:** vijf standaard ingeklapte rubrieken in volgorde Instellingen, Databronnen, Wedstrijden, Diensten, Kandidaten; bestaande werking behouden.
2. **UI-2 — Dienstencatalogus:** knop **Dienstencatalogus (roosterindeling) opnieuw laden** met uitleg onder Diensten, direct boven **Feitelijke Sportlink-inroosteringen ophalen**. Bestaande bevestiging, annulering, sessievervanging en bescherming van duurzame no-showfeiten behouden. Beide paden lokaal geslaagd.
3. **UI-3 — Bronactualiteit:** acht bronnen met één kolom **Laatst ingelezen door DVK**; CSV toont bestaand DVK-inleesmoment, API toont begin van DVK-ophaalactie (geen Sportlink-actualisatietijd); onbekende tijden **Onbekend**. Historische urenbron heeft type **CSV**; de bron blijft functioneel optioneel.
4. **UI-4 — Operationele bronnen:** demonstratie-/bronkeuzeradio verwijderd uit de gewone Planner. Operationele Sportlink- en CKC-bronnen standaard; synthetische tests behouden zonder nieuwe gebruikersroute of stille demonstratieterugval.

**Acceptatiegrens:** dit is lokale functionele acceptatie van Iteratie 8 op de genoemde codecommit, niet de merge van PR #65, niet de integrale v0.5-acceptatie en geen productieacceptatie. Geen nieuwe Sportlink-schrijfbevoegdheid.

### Iteratie 9 — overeengekomen functionele uitgangspunten, nog niet gebouwd

- **Teamclassificatie:** Sportlink-teamnamen die beginnen met `JO`, `O` of `MO`, direct gevolgd door een leeftijdscategorie tot en met 20, gelden als jeugd (bijv. `JO7`, `O9-1`, `JO19-2`, `MO15`, `MO17-2`, `O20`). `O23`/`MO23` en alle andere teamnamen (bijv. `CKC 1`, `VR1`, `Zon2`) gelden als senioren. Dit vervangt voor deze selectie het individuele leeftijdsonderscheid.
- **Zaterdagochtend:** dienststart vóór 12:30: eerst geschikte ouders/verzorgers van spelers uit thuisspelende jeugdteams met overlappende wedstrijd; daarna geschikte spelers van thuisspelende seniorenteams zonder wedstrijdconflict. Dienststart is bepalend, ook wanneer de dienst na 12:30 eindigt. Voor jeugdwedstrijden geldt aanvang + twee uur.
- **Zaterdagmiddag:** dienststart vanaf 12:30: eerst geschikte spelers van thuisspelende seniorenteams zonder wedstrijdconflict. Jeugdouders niet in de middagvoorkeursgroep. Seniorenspelers mogen ook 's ochtends worden voorgesteld zonder wedstrijdconflict. Bestaande wedstrijdmarges blijven gelden.
- **Noodgroepen:** na voorkeursgroepen eerst geschikte kandidaten van teams zonder wedstrijd (noodoptie 1), daarna geschikte kandidaten van uitspelende teams zonder wedstrijdconflict (noodoptie 2). Zaterdag- en zondagteams niet mengen. Toepassing van jeugdouder-/seniorenspelerregels binnen noodgroepen nog toetsen.
- **Rangschikking binnen elke groep:** eerst meeste openstaande uren van huidig seizoen; bij gelijke actuele achterstand meeste openstaande uren van vorig seizoen. Groepsprioriteit gaat vóór uren. De UI toont dezelfde volgorde.
- **Historische achterstand:** achterstand van vorig seizoen telt het gehele huidige seizoen mee; eerdere beperking tot juli–december vervalt; geen afbouwfactor. Dit is een **nieuwe geplande beleidswijziging**, niet de al geïmplementeerde BL-03-regel.
- **Behoud:** taakplicht, vrijstellingen, ouderrelaties, geschiktheid, wedstrijdmarges, bronvalidatie en menselijke goedkeuring blijven gelden. Geen automatische Sportlink-writeback.

**Nog open:** volledige combinatietoets aan bestaande code, functionele contracten en geaccepteerde regressies; precisering van noodgroepen en eventuele tegenstrijdigheden. Geen zelfstandige interpretaties of implementatie zonder CKC-besluit.

### Acceptatie en afzonderlijk aandachtspunt

Iteratie 10 beoordeelt integraal bronnen en actualiteit, taakplicht, selectie en wedstrijdcontext, historische uren, tijdelijke planning en goedkeuring, Sportlink-bezetting/synchronisatie, no-shows en portaalnavigatie. Eerdere acceptaties waar mogelijk hergebruiken. Prototypeacceptatie is geen productieacceptatie. De trage lokale Streamlit-start blijft een afzonderlijk bij voorkeur read-only technisch onderzoek zonder vastgestelde oorzaak; niet zonder bewijs aan PR #63 toeschrijven. BL-13 blijft een later afzonderlijk traject zonder verleende Sportlink-schrijfbevoegdheid.


### Iteratie 9 — functioneel geaccepteerd (4 november 2026)

CKC heeft Iteratie 9 lokaal functioneel geaccepteerd op codecommit `67dd98efe2fb5a2c696d6bb864b4f818a1e24755` in [PR #66](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/66) (nog niet gemerged bij deze vastlegging). [CI #429](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/41878191393) is groen; Codex rapporteert 1.584 geslaagde regressietests, waaronder 78 nieuwe synthetische tests. Handmatig geslaagd: zaterdag-ochtend- en middaggroepen, uitsluiting bij wedstrijdconflict, jeugd-thuis zonder overlap met juiste thuiswedstrijdverklaring, actuele uren en historische achterstand als prioriteit, expliciete bevestiging en undo. De BL-20-noodgroep van de andere weekenddag bij minimumtekort is uitsluitend synthetisch getest; een aanvullende handmatige proef werd door een **bestaande** fout bij synchronisatie van feitelijke Sportlink-inroosteringen geblokkeerd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie9-acceptatie.md).

**Actueel beleid na Iteratie 9:** jeugdteams zijn JO/O/MO met leeftijdscategorie t/m 20, andere teams senioren; groepsprioriteit vóór actuele E, daarna positieve historische achterstand vorig seizoen en stabiele persoonssleutel. Historie telt het gehele lopende seizoen mee (januari–december), zonder wijziging van actuele A/B/C/D/E. De eerdere juli–december-beperking van BL-03 is hiermee vervangen. Jeugd-thuis zonder wedstrijdoverlap valt in de noodgroep 'zonder wedstrijd' maar behoudt de feitelijke thuiswedstrijdcontext. BL-20 blijft de laatste minimumgebonden noodgroep. Iteratie 10 blijft de integrale functionele acceptatie van v0.5, zonder nieuwe functionaliteit.

**Afzonderlijk vervolg buiten Iteratie 9:** bij de Sportlink-week 9–15 november 2026 werden twee verschillende personen als 'Afgeschermd' voor dezelfde dienst aangeleverd. De bestaande boekingssleutel kan dan botsen; concrete API-records zijn nog niet onderzocht. CKC heeft besloten dat iedere aangeleverde 'Afgeschermd'-regel afzonderlijk als bezette plaats zichtbaar moet blijven, zonder automatische persoonskoppeling, persoonsgebonden uren of no-show, en zonder blokkade van de overige synchronisatie. De technische uitwerking en regressietests volgen in een afzonderlijke opdracht; de overige duplicaatcontrole blijft behouden. De extra avonddienst 22:30–23:55 is waargenomen maar niet als oorzaak vastgesteld.


### Correctie na Iteratie 9 — afgeschermde Sportlink-inroosteringen (7 november 2026)

CKC heeft [PR #67](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/67), codecommit `90d3ddea2e8b4a2b90c70ba78ecf692cbb00caa7`, **functioneel geaccepteerd**. Twee afzonderlijke `Afgeschermd`-regels verschijnen naast twee reguliere boekingen en vullen gezamenlijk de capaciteit volledig (**vrije capaciteit 0**). Afgeschermde regels blijven anoniem, zonder persoonskoppeling, persoonsgebonden uren of no-show. Die laatste beschermingen zijn regressiematig getoetst, niet afzonderlijk lokaal. Technische validatie: 1.597 tests geslaagd en CI #433 groen op codecommit. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-PR67-afgeschermde-inroosteringen-acceptatie.md). **Iteratie 10** blijft de integrale functionele v0.5-acceptatie; dit akkoord is geen integrale of productieacceptatie.

**Voorafgaand afzonderlijk technisch vervolg:** een configureerbare en persistente Sportlink-exportmap, zodat de lokale gegevens buiten iCloud en buiten GitHub kunnen staan. Geen wijziging aan de functionele scope van PR #67. De nieuwe lokale Python-/Streamlit-installatie is gestart; de nieuwe exports zijn gekopieerd, maar de applicatie gebruikt vooralsnog het oude hardcoded exportpad. Oude Documenten-mappen pas na controle van de nieuwe gegevensbron opruimen.


## Iteratie 9A — Voortgang per deelstap (7 november 2026)

**9A.1 — Configureerbare exportmap en zelfstandige functie Databronnen: functioneel geaccepteerd.** [Draft-PR #68](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/68) op codecommit `06d1fe50bd30235fe2c9658e51395509082bf699`, CI #437 groen. Lokale controle bevestigt blijvend ingestelde map, werkend ophalen van Sportlink-inroosteringen en sessiebehoud met tijdelijke indelingen en bezetting bij navigatie. [Acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a1-acceptatie.md). PR nog niet gemerged; merge pas na expliciet akkoord.

**9A.2 — Volgende ontwikkelstap:** nieuwe planning standaard op actuele kalenderweek; bij definitieve start automatisch CSV-exports, Programma API en Vrijwilligers API laden; hervatten zonder CSV-herlezing of API-aanroepen. Bij gedeeltelijke bronuitval duidelijke bronstatus en begrenzing van onbetrouwbare functies; geen stilzwijgende lege resultaten. Dit adresseert de tijdens 9A.1 geconstateerde onoverzichtelijke handmatige laad- en synchronisatieknoppen.

**9A.3:** sessie- en regressiebescherming bij automatisch laden. **9A.4:** lokale database en ontwikkelomgeving controleren, geen migratie van oude database zonder toestemming. **9A.5:** documentatie, PR-afronding en voorbereiding Iteratie 10. Oude mappen uitsluitend na aparte toestemming verwijderen. **Iteratie 10** blijft de afzonderlijke integrale functionele acceptatie.


## Iteratie 9A.2 — Automatisch laden bij nieuwe planning (functioneel geaccepteerd op 7 november 2026)

**Status:** functioneel geaccepteerd door CKC op codecommit `045afbdc467185a870da5220d9a910ccc05f9333` in [draft-PR #69](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/69), gericht op `prototype-v0.5`; **niet gemerged bij deze vastlegging**. [CI #441](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/42420999174) geslaagd; Codex rapporteert 117 gerichte tests, 1.609 regressietests en 11 synthetische acceptatiescripts geslaagd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a2-acceptatie.md).

Bij een nieuwe planning is de huidige kalenderweek de standaard en kan de planner vooraf een andere periode kiezen. Pas na **Start nieuwe planning** worden de vijf verplichte en één optionele lokale CSV, Sportlink Programma en Sportlink Vrijwilligers automatisch geladen, met voortgang en onderscheiden bronstatus voor lege resultaten en fouten. Hervatten gebruikt de duurzaam in SQLite opgeslagen kandidaat- en wedstrijdcontext en bestaande gevalideerde bezetting, zonder nieuwe bronaanroepen; tijdelijke indelingen blijven behouden. Handmatige verversing blijft onder **Ledendiensten → Databronnen**, met expliciete bevestiging voor vervanging van bezetting. Bij ontbrekende verplichte bronnen zijn kandidaatvoorstellen niet veilig beschikbaar; bij mislukte Vrijwilligers-uitvraag is bezetting onbekend. Geen Sportlink-writeback.

**Lokale acceptatie:** (1) automatisch laden en periodekeuze geslaagd; (2) na Streamlit-herstart dezelfde periode, wedstrijden, bezetting en tijdelijke indeling zonder opnieuw laden; (3) vervanging zonder expliciete bevestiging geblokkeerd, tijdelijke indeling behouden; (4) tijdelijk hernoemde `Functies.csv` leidt tot een duidelijke foutmelding met exacte verwachte locatie en hersteladvies. De gebruiker is verzocht `Functies.csv.test` weer terug te noemen; herstel is niet afzonderlijk bevestigd. Geen productie- of integrale v0.5-acceptatie.

**Vervolg:** 9A.3 sessie- en regressiebescherming; 9A.4 lokale omgeving/databasepad verifiëren zonder ongevraagde migratie of opruiming; 9A.5 afronding en voorbereiding; Iteratie 10 integrale functionele acceptatie. Merge PR #69 uitsluitend na afzonderlijke toestemming.

## Iteratie 9A.3 — Sessie- en regressiebescherming (functioneel geaccepteerd op 8 november 2026)

**Acceptatiebasis:** codecommit `3a64213d47eb35b2a2baef9723c42f5957175170`, [draft-PR #70](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/70) naar `prototype-v0.5`; nog niet gemerged bij deze vastlegging. CKC heeft lokaal vastgesteld dat hervatten na herstart geen automatische bronverversing veroorzaakt en de tijdelijke indeling bewaart. Een opzettelijk ontbrekende `Functies.csv` in een aparte testmap veroorzaakte een duidelijke bronfout, ook in een tweede browservenster; verouderde kandidaatvoorstellen verdwenen, maar de bestaande tijdelijke indeling bleef behouden. Onderbroken initiële bronlading: 2 synthetische tests geslaagd (9 overige gedeselecteerd). Codex rapporteerde 216 gerichte tests, 1.621 regressietests, 11 synthetische acceptatiescripts en groene CI #445. [Volledig acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a3-acceptatie.md).

**Vervolgvolgorde:** 9A.4 controle van lokale ontwikkelomgeving en databasepad, zonder ongevraagde migratie of opruiming; 9A.5 afronding en voorbereiding; Iteratie 10 integrale functionele acceptatie van prototype v0.5. Deze acceptatie is geen productie- of integrale v0.5-acceptatie. Merge van PR #70 vereist apart akkoord.

## Iteratie 9A.4 — Lokale omgeving gecontroleerd (8 november 2026)

**Functioneel geaccepteerd door CKC, zonder codewijziging.** In `~/Development/DigitaalVerenigingsKantoor/code/Prototype/` staat de actieve SQLite-database `dvk_v05.sqlite` (14 MB; lokaal gewijzigd op 8 november). In `~/Development/DVK-Data/Sportlink-Exports/` zijn de vijf verplichte en één optionele Sportlink-CSV aanwezig, plus `shift_definitions.csv` en `shift_week_pattern.csv`. De recursieve zoekactie naar vaste oude `Documents/`-paden in Python-bronbestanden leverde geen treffers op (virtuele omgeving en caches uitgezonderd). De controle is beperkt tot deze lokale waarnemingen en is geen garantie voor alle mogelijke runtime-configuraties. Geen noodzaak aangetoond voor databaseverplaatsing, migratie of codewijziging. Oude mappen blijven staan totdat CKC expliciet toestemming geeft voor opruiming.

**Volgende stap:** Iteratie 9A.5 — administratieve afronding en voorbereiding van Iteratie 10. Iteratie 10 is de afzonderlijke integrale functionele acceptatie van v0.5.

## Iteratie 9A.5 — Afronding en acceptatievoorbereiding (8 november 2026)

**Afgesproken werkwijze:** bestaande lokale acceptaties zijn geïnventariseerd. Vier oude DVK-mappen in `~/Documents/` (`DigitaalVerenigingsKantoor`, `DVK-Iteratie2`, `DVK-Sportlink-exports`, `DVK-lokale-backups`) zijn na afzonderlijke expliciete toestemming door de gebruiker naar de macOS-Prullenmand verplaatst; niet definitief gewist. Actieve code, database en exportgegevens onder `~/Development/` blijven leidend. In de oude repository waren twee gewijzigde bestanden en een oude SQLite-database aangetroffen; het risico van verlies van unieke historische inhoud is bewust aanvaard.

**Iteratie 10 — vastgesteld concept van integrale functionele acceptatie, vanuit de normale taakuitvoering van de planner:**
1. Nieuwe planningsperiode voorbereiden: periode, brongegevens, wedstrijden en bezetting.
2. Openstaande ledendiensten invullen: kandidaten, taakplicht, prioriteiten en beleidsregels.
3. Planning onderbreken en hervatten: bewaarde context en tijdelijke indelingen.
4. Afwijkingen verwerken: bronproblemen, bezettingswijzigingen en vervanging.
5. Planning als geheel beoordelen: overzicht, volledigheid, consistentie en bruikbaarheid.
6. Afzonderlijk als laatste: no-showmanagement, registratie, intrekking, sancties en vervangende diensten.

Rondes 1–5 vormen één herkenbare CKC-planningsopgave; ronde 6 is een zelfstandig administratief proces. Per ronde: geslaagd / geslaagd met aandachtspunt / niet geslaagd. Hergebruik eerdere detailacceptaties; alleen gerichte herstel- en heracceptatietests bij gebreken. Geen nieuwe functionaliteit, geen Sportlink-writeback en geen productieacceptatie. Tijdelijke DVK-indelingen zijn niet gelijk aan definitieve Sportlink-verwerking.

**Vervolg na Iteratie 10:** afzonderlijke **Iteratie 11 — Planner Dashboard**, overeenkomstig de eerdere bespreking 'Dashboard artist impression': het planningsscherm omvormen tot één overzichtelijk dashboard met behoud van geaccepteerde planningslogica. Eerst afzonderlijk ontwerp, implementatie en functionele acceptatie; pas **daarna BL-13 (RPA Sportlink)**. Dashboardherontwerp behoort niet tot de scope of acceptatiecriteria van Iteratie 10.
