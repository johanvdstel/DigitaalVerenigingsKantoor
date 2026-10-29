# DVK — Prototypeplanning v0.5

**Status:** Iteratie 1 (BL-17/20/21) functioneel geaccepteerd op 29 oktober 2026 via PR #53; Iteratie 2 (BL-03) is lokaal functioneel geaccepteerd op 29 oktober 2026; PR #55 staat nog open en is niet gemerged. Integrale v0.5-acceptatie blijft open.
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
| 4 | BL-03 — Achterstallige uren | Optionele historische Sportlink-CSV via relatiecode; dienstmaanden juli t/m december; geen wijziging actuele urenbalans. | **Functioneel geaccepteerd op 29 oktober 2026; PR #55 open, merge nog niet toegestaan** |
| 5 | Stap 3 — Ledendienst Planning | Taakplicht + Vrijwilligers + Programma + achterstanden combineren voor zinvolle kandidaten, prioriteit, bezetting en tijdelijke planning. | **Na bronacceptaties** |
| Afgesloten/vervallen | BL-05 t/m BL-11 | BL-05 en BL-06 vervallen als afzonderlijke DVK-functies; BL-07 t/m BL-11 functioneel afgesloten volgens backlog. | **Geen afzonderlijk uitvoerwerk** |
| PR #44 geaccepteerd en gemerged; vóór integrale v0.5-acceptatie | BL-18 — Herstructurering Ledendienst Planning | Vijf gescheiden secties: Instellingen, Databronnen, Diensten, Kandidaten, Wedstrijden; behoud bestaande functionaliteit en afzonderlijke lokale UI-acceptatie. | **Afgerond en lokaal functioneel geaccepteerd op 26 oktober 2026; nieuwe inklapwens valt onder BL-23; [verslag](code/Prototype/DVK-v0.5-BL18-schermindeling.md)** |
| Afgerond | BL-17, BL-20, BL-21 — Iteratie 1 | Sportlink-kandidatenbasis, verwijderde uitzonderingsinvoer, teamspeeldagfilter/noodselectie, directe begrijpelijke toelichting en actieve versie. | **Functioneel geaccepteerd op 29 oktober 2026 via PR #53; zie acceptatieverslag** |
| Open | BL-14 (incl. BL-15), BL-19 | Catalogus dynamisch inlezen; zelfstandig No-showmanagement. | **Nog te implementeren en accepteren** |
| Open | BL-22 t/m BL-24 | Centraal leesbaar Python-regelbestand (na inventarisatie); inklapbare rubrieken; volledig bronstatusoverzicht. | **Nog te implementeren en accepteren** |
| Mijlpaal | Integrale functionele acceptatie v0.5 | Echte CKC-bronnen lokaal, samenhang tussen taakplicht, bronnen, planning, sync, no-shows, portaal; afwijkingen expliciet beoordeeld. | **Nog open** |

## Vastgestelde resterende uitvoeringsvolgorde prototype v0.5 (28 oktober 2026)

De opdrachtgever heeft onderstaande **werkplanning** bevestigd. De volgorde is leidend, maar geen onwrikbaar watervalplan: bij aantoonbare technische afhankelijkheden kunnen werkzaamheden worden gecombineerd of verschoven, na afstemming. Er zijn nog **geen kalenderdata of tijdsramingen** vastgesteld. Elke iteratie krijgt gerichte technische controle, regressietests en afzonderlijke lokale functionele acceptatie.

| Volgorde | Iteratie | Backlog | Uitvoering en acceptatie |
| --- | --- | --- | --- |
| 1 — afgerond | Kandidaten en versiebeheer | BL-17, BL-20, BL-21 | Functioneel geaccepteerd door Johan op 29 oktober 2026 via PR #53; codeversie `9016c8a`. 1209 regressietests en CI #381 groen. Eén weekendrichting en noodkandidaten uitsluitend synthetisch gedekt; zie acceptatieverslag. |
| 2 — functioneel geaccepteerd | Achterstallige uren | BL-03 | Historische CSV gekoppeld via relatiecode; tweede prioriteitscriterium uitsluitend juli t/m december op dienstdatum, geen actuele urenmutatie. Planner borgt het vorige seizoen. Foutafhandeling houdt planning bruikbaar. **Lokaal functioneel geaccepteerd op 29 oktober 2026**, PR #55 nog open; zie Iteratie-2-acceptatieverslag. |
| 3 | Bedieningsgemak en bronstatus | BL-23, BL-24 | Vijf rubrieken onafhankelijk inklapbaar (bij openen allemaal ingeklapt); compleet en eerlijk overzicht van gebruikte API- en CSV-bronnen met status en import-/ophaalmomenten. |
| 4 | Dynamische dienstencatalogus | BL-14 (inclusief voormalig BL-15) | Eerst bestaande code en cataloguscontract inventariseren; vervolgens lokale `Shift Catalog.xlsx` dynamisch gebruiken voor relevante taakcodes, dienstmomenten en bezettingsnormen. Geen afzonderlijk beheerscherm. |
| 5 | Zelfstandig No-showmanagement | BL-19 | No-showbediening uit Ledendienst Planning verplaatsen; aanmelden voor werkelijk ingeroosterde diensten binnen de laatste 14 kalenderdagen inclusief vandaag; seizoensoverzicht met historie en intrekking van oudere actieve registraties. Geen gegevensverlies of Sportlink-writeback. |
| 6 | Onderhoudbaarheid beleidsregels | BL-22 | Bestaande regels en tests inventariseren; CKC-regels bij voorkeur in één goed leesbaar en reviewbaar Python-bestand centraliseren zonder beleidsuitkomsten te veranderen. Geen Rules-tool of beheerinterface. |
| Eindmijlpaal | Integrale functionele acceptatie v0.5 | Voormalig BL-12 | Met echte CKC-gegevens uitsluitend lokaal de samenhang van taakplicht, bronnen, planning, sessies, no-shows en portaal toetsen; expliciete acceptatie door opdrachtgever. |

**Na integrale acceptatie van v0.5:** BL-13a RPA-haalbaarheidsproef, daarna alleen bij positief besluit BL-13b (pilot) en BL-13c (beheerde productie-invoering). Dit is geen onderdeel van de resterende v0.5-ontwikkeliteraties. De Sportlink-verwerking blijft tot die tijd handmatig.

Stap 3 mag niet afhankelijk zijn van onbevestigde aannames over de twee API's; beide API-integraties zijn afzonderlijk functioneel geaccepteerd. De bovenstaande iteraties completeren de nog openstaande v0.5-scope.

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

De goedgekeurde W09-datumcorrectie en B-13 zijn traceerbaar bijgewerkt. [Uitvoering en acceptatieverslag](code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md). **Functioneel geaccepteerd op 29 oktober 2026 op codecommit `e3b17fc`; PR #55 nog niet gemerged.**

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
