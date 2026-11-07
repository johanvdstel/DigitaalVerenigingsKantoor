# DVK — Functionele backlog

**Status:** BL-19 functioneel geaccepteerd op 2 november 2026 (PR #61 open, niet gemerged); BL-14 (incl. voormalig BL-15) functioneel geaccepteerd op 31 oktober 2026, codecommit `be1cd1d` via gemergede PR #58; BL-17, BL-20, BL-21 en BL-03 functioneel geaccepteerd op 29 oktober 2026 (respectievelijk PR #53 en PR #55); BL-23 en BL-24 functioneel geaccepteerd op 30 oktober 2026 en via PR #56 gemerged; overige besluiten uit de integrale backlogreview blijven gelden. Integrale acceptatie prototype v0.5 blijft open  
**Scope:** prototype v0.5 en later; geen implementatieplanning of productiearchitectuur.  
**Verwijzingen:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md)

De backlog bevat openstaande functionaliteit, beleidsbesluiten en bronafhankelijkheden. De volgorde, afzonderlijke ontwikkelstappen en integrale acceptatiemijlpaal staan in de prototypeplanning. Statussen beschrijven wat is afgesproken; ze bewijzen niet dat code al bestaat.

## Afgerond

| ID | Onderwerp | Status / bewijs |
| --- | --- | --- |
| BL-03 | Achterstallige uren vorig seizoen | **Functioneel geaccepteerd op 29 oktober 2026**, op de synthetische implementatiecommit `e3b17fc83e88d9640bc011afc69a666b8b8dbe1a` van [PR #55](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/55) (gemerged op 29 oktober 2026). Lokale proeven: prioritering 8/4/0 bij actuele E=10, ontbrekende historische bron met zichtbare waarschuwing en bruikbare planning, bevestiging en undo. 1251 tests en CI #385 groen op geaccepteerde codecommit. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md). | 
| BL-01 | Adresgebaseerde huishoud- en minderjarigenregels B-05/B-06/B-07 | **Afgerond en functioneel geaccepteerd** in Stap 2 ronde 4; uitsluitend volledig geregistreerd adres als automatische huishoudsleutel; relevante leden op peildatum; geen ouder-/achternaamheuristiek. |
| BL-02 | Read-only taakplichtcontroledashboard | **Afgerond en functioneel geaccepteerd.** Lokale CKC-acceptatie: 650 relevante leden, 563 overeenkomsten, 87 afwijkingen, 0 niet betrouwbaar beoordeelbaar. Bron- en controlediagnose behouden. [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged naar `prototype-v0.5`. |
| BL-04 | DVK-frontend, hoofdmenu, licht portaal | **Afgerond en functioneel geaccepteerd op 19 oktober 2026.** Startscherm met acht functies in drie groepen, één per regel; zijbalk uitsluitend navigatie; instellingen op eigen scherm. Rooster Generator als uitgeschakelde knop. Correcties BL-04-01/03/04 verwerkt; BL-04-02 vervallen. 62 gerichte tests, 636 regressietests en CI groen. [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged naar `prototype-v0.5` (`68ae25fa`). CSV-uploads moeten na schermwisseling opnieuw worden geselecteerd. |

## Open / geprioriteerd

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |

| BL-05 | Duurzame plannerbeslissingen bij taakplichtafwijkingen | **Vervallen als ontwikkelopdracht (besluit 26 oktober 2026).** DVK blijft afwijkingen tussen de Sportlink-taakplichtregistratie en CKC-beleidsregels signaleren via de bestaande taakplichtcontrole. De planner beoordeelt deze en corrigeert zo nodig Sportlink. Geen aparte DVK-registratie van besluiten, redenen of taakplichtuitzonderingen. De 87 eerder geconstateerde afwijkingen hoeven niet eerst door de planner te zijn beoordeeld om BL-05 af te sluiten. | Geen DVK-ontwikkeling; bestaande taakplichtcontrole behouden |
| BL-06 | Urenoverdracht bij 18 jaar | **Vervallen als afzonderlijke DVK-ontwikkelopdracht (besluit 26 oktober 2026).** Bij meerderjarigheid kan de gezinsgebonden taakplicht naar een jonger minderjarig lid verschuiven; reeds gewerkte uren blijven bij het lid dat ze heeft verricht. DVK signaleert eventuele afwijkingen in verwachte taakplicht via de bestaande read-only taakplichtcontrole. Eventuele handmatige urenoverdracht of -correctie in Sportlink blijft mogelijk, maar valt volledig buiten DVK: geen signalering, goedkeuring, ondersteuning of verificatie van die overdracht. | Herziene beleidsafspraak B-08; bestaande taakplichtcontrole |
| BL-07 | Sportlink-urenbron en seizoensgegevens | **Functioneel gevalideerd en afgesloten (27 oktober 2026); geen aanvullend ontwikkelwerk.** Bron *Overzicht per periode*: A = Verplichte punten, B = Gecorrigeerde punten, C = Voldaan, D = Nog ingedeeld, E = Niet ingedeeld; E = A − B − C − D. Bronbestand bevat per definitie uitsluitend het huidige seizoen. Praktijksteekproef: openstaande uren en prioritering in Kandidaten en Voorstellen stemmen overeen met Sportlink-CSV. Geen afzonderlijke DVK-verificatie van handmatige urenoverdracht (BL-06). Dit is functionele acceptatie op basis van steekproef, geen volledige technische regressietest. | Afgesloten; B-13 en bronverificatie bijgewerkt |
| BL-08 | Functieclassificatie `Verzorger` | **Functioneel afgesloten (27 oktober 2026).** CKC kiest bewust om beide huidige Sportlink-registraties `Verzorger` als betaalde functie te classificeren, ondanks dat één functie feitelijk onbetaald is. Beide geven daarmee persoonlijke, maar geen huishoudvrijstelling (B-04). Met de huidige bezetting heeft dit geen huishoudelijk effect. Geen naamswijziging in Sportlink of persoonsgebonden uitzondering nodig voor afsluiting; een toekomstige wijziging van functienaam of CKC-beleid kan aanleiding zijn de classificatie opnieuw te beoordelen. Geen aanvullend BL-08-ontwikkelwerk. | B-04; functionele baseline |
| BL-09 | Bronactualiteit functies en commissies | **Functioneel afgesloten (27 oktober 2026).** Voor Functies en Commissies volstaat de datum van de laatste import; geen aparte waarschuwing voor ouderdom van deze bronnen. Weergave van deze datums valt onder BL-24. Geen nieuwe DVK-logica om ontbrekende einddatums van functies te raden. | BL-24 |
| BL-10 | Tijdelijke planning en Sportlink-synchronisatie | **Functioneel afgesloten (27 oktober 2026).** De functioneel verantwoordelijke bevestigt dat de integrale planningscyclus voldoende is geverifieerd en de vier resterende controlepunten zijn afgehandeld: actuele bezetting/beschikbaarheid, undo van tijdelijke indelingen, onderscheid tussen handmatige Sportlink-verwerking en DVK-planning, en bronverversing met de juiste wisgrens. Eerder lokaal geaccepteerde sessie- en bronverversingswerking blijft van kracht; voor de levenscyclus geldt het op 22 oktober geaccepteerde ontwerp Planningssessies (BL-16), niet de verouderde procesherstartregel. Geen resterende BL-10-ontwikkel- of verificatieactie. | BL-16; API Vrijwilligers; FR-02–FR-08 |
| BL-11 | No-shows en handmatige Sportlink-correctiewerkvoorraad | **Functioneel afgesloten (27 oktober 2026).** CKC accepteert de gerealiseerde DVK-no-showregistratie, intrekking, herregistratie, historie en bestaande sanctieafleiding als voldoende voor BL-11; geen resterende BL-11-verificatie of afzonderlijke correctiewerkvoorraad als oplevervoorwaarde. **Sportlink registreert zelf geen no-shows: DVK is de registratiebron.** Eventuele handmatige aanpassingen in Sportlink zijn daarvan te onderscheiden. Aanvullende eisen voor zelfstandig no-showbeheer worden uitsluitend onder BL-19 behandeld, met hergebruik van geaccepteerde functionaliteit. | BL-19; API Vrijwilligers; FR-09–FR-12 |

## BL-03 — Actueel bron- en foutcontract (Iteratie 2)

Historische bron: `~/Documents/DVK-Sportlink-exports/Overzicht per periode vorig seizoen.csv`, dezelfde CSV-kolomstructuur als de actuele urenexport. De planner levert het onmiddellijk voorafgaande seizoen; DVK leidt of verifieert dat bronseizoen niet zelfstandig. Koppeling uitsluitend op `Relatiecode`; `Niet ingedeeld` is de bronwaarde, getoetst aan A−B−C−D. Positieve achterstand telt sinds Iteratie 9 als tweede criterium na actuele E **binnen dezelfde kandidaatgroep gedurende het volledige lopende seizoen (januari–december)**; groepsprioriteit gaat vóór uren. De eerdere juli–december-beperking uit Iteratie 2 is vervangen. Nul betekent geen achterstand; negatieve waarden blijven als bronfeit behouden en geven geen krediet. Actuele A/B/C/D/E blijven ongewijzigd.

Bij ontbrekend, onleesbaar of structureel ongeldig historisch bestand blijft planning bruikbaar met een zichtbare waarschuwing. Ontbrekende ledenregels, dubbele relatiecodes, ongeldige getallen en formuleverschillen leveren voor de betrokken kandidaat onbekende/onbetrouwbare historische achterstand op; geen uitsluiting of stilzwijgende nul. Voor rangschikking neutraal, in toelichting onderscheiden van bekende nul, ontbrekende bron en maanden buiten toepassing. Andere geldige historische records blijven bruikbaar. Taakplichtcontrole blijft onafhankelijk van deze optionele bron.

De oude Excel-/seizoensidentificatie-aannames zijn door Johan vervangen. De gerichte wijziging van de W09-datumverwachting is afzonderlijk goedgekeurd; de testgegevens blijven behouden. BL-03 is op 29 oktober 2026 functioneel geaccepteerd op de geteste codecommit; PR #55 is op 29 oktober 2026 gemerged.

## BL-17 — Uitzonderingsregistratie verwijderen uit Kandidaten (26 oktober 2026)

**Status:** afgerond en functioneel geaccepteerd door Johan op 29 oktober 2026 via [PR #53](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/53), Iteratie 1. Sportlink bepaalt de kandidatenbasis; uitzonderingsinvoer verwijderd, historie behouden. Kandidaattoelichting verschijnt begrijpelijk per aangevinkte kandidaat. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md).

**Functioneel uitgangspunt:** in Ledendienst Planning is de in Sportlink geregistreerde taakplicht leidend voor de kandidatenbasis, ongeacht of die registratie volgens de CKC-beleidsregels juist is. De afzonderlijke taakplichtcontrole signaleert beleidsafwijkingen; de planner beoordeelt deze en corrigeert zo nodig Sportlink. DVK legt geen taakplichtuitzonderingen vast.

**Gerealiseerd (BL-17):**
- Verwijder de mogelijkheid om in de sectie **Kandidaten** van Ledendienst Planning uitzonderingen op de taakplicht te registreren.
- Verwijder de bijbehorende invloed van deze uitzonderingen op kandidaatselectie en voorstellen. Behoud de overige bestaande selectie-, geschiktheids- en prioriteitsregels.
- Ruim uitsluitend hiervoor gebruikte programmatuur en eventuele opslag zorgvuldig op; behoud relevante historie en voorkom onbedoeld gegevensverlies.
- Behoud de bestaande vrijheid van de planner om een voorstel niet over te nemen; dat is geen uitzonderingsregistratie.

**Acceptatie:** in Kandidaten is geen uitzonderingsregistratie meer beschikbaar en dergelijke sessiegebonden uitzonderingen beïnvloeden de kandidaten of voorstellen niet meer. Sportlink-taakplicht blijft leidend, taakplichtcontrole blijft werken, en bestaande voorstellen, tijdelijke indelingen, bevestiging/undo en sessiegedrag blijven regressievrij. Geen nieuwe persoonsgebonden uitzonderingsregistratie of Sportlink-writeback.

## BL-16 — Levenscyclus planningssessies (geïmplementeerd en functioneel geaccepteerd)

**Status:** ontwerp geaccepteerd op 22 oktober 2026; implementatie via [PR #38](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/38) op 23 oktober 2026 lokaal functioneel geaccepteerd en gemerged naar `prototype-v0.5`. SQLite-schema 13; 917 regressietests en CI #332 groen. Zie [DVK v0.5 — Functioneel ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md).

**Scope:** maximaal één duurzaam hervatbare planningssessie; expliciete start, hervatten, afsluiten en vervangen; drie navigatiesituaties bij Ledendienst Planning; periodekeuze vóór handmatige Vrijwilligers API-ophaalactie; bevestigde sessiegrenzen bij nieuwe planning, periodewisseling en vervangende synchronisatie; behoud bij browser- en procesherstart; geen gegevensverlies bij mislukte synchronisatie; No-Show-selectie en registratie uitsluitend vanuit de actieve gevalideerde bron. Historische No-Shows en intrekkingen blijven behouden.

**Opgelost in PR #38:** No-Show-selectie uitsluitend uit de actieve gevalideerde bron en periode, hercontrole bij registratie, volledige chronologisch gesorteerde keuzelijst, eenmalige resultaatmelding en herregistratie na intrekking met behoud van historie.

**Acceptatiegrens:** navigatie, browser- en Streamlit-herstart, bronvervanging met bevestiging, No-Show-registratie/intrekking/herregistratie en schema-upgrade zijn lokaal gecontroleerd. Mislukte synchronisatie, race tussen selectie en registratie, tijdelijke indelingen na computerherstart en periodewisseling mét tijdelijke indelingen zijn niet afzonderlijk lokaal beproefd; regressietests dekken deze scenario's. Integrale v0.5-acceptatie blijft open.

## Nieuwe beheerwensen (21 oktober 2026)

Deze wensen zijn afzonderlijke backlogrequirements en blokkeren de lopende Vrijwilligers API-integratie niet. Prioriteit voorlopig **normaal**; nadere uitwerking en acceptatie volgen afzonderlijk.

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |
| BL-14 | Dynamisch beheer Sportlink-taakcodes en DVK-dienstencatalogus | **Functioneel geaccepteerd op 31 oktober 2026; PR #58 gemerged naar `prototype-v0.5` (mergecommit `267c94779a04`).** Twee lokale CSV-bestanden `shift_definitions.csv` en `shift_week_pattern.csv` vervangen rechtstreeks gebruik van `Shift Catalog.xlsx`. Reguliere en gedateerde aanvullende regels, nachtdiensten, gebruikte taakcodes onafhankelijk van gekozen periode en aanvullende Sportlink-tijdvakken (ook bij overlap). Exacte dienstidentiteit: taakcode en feitelijk UTC-tijdvak; bargroepen blijven voor bezettingsprojectie gelden. Bevestigde `Reload catalog` start altijd een nieuwe sessie; ongeldige configuratie/annuleren behoudt de bestaande sessie. Geen onderhoudsscherm of writeback. Zie [Iteratie 4](code/Prototype/DVK-v0.5-iteratie4-BL14.md). | CKC-proef: 23 reguliere diensten in lokale catalogus, aanvullende Sportlink-diensten, bevestigde reload, validatiefouten, kandidaten en undo; periode-UI Dag/Week/Aangepast hergeaccepteerd. Codecommit `be1cd1d`; 55 gerichte tests, 1307 regressietests, CI #397 groen. Lokale CKC-bestanden niet in GitHub. Integrale v0.5-acceptatie blijft open. |
| BL-15 | Beheer DVK-dienstencatalogus | **Vervallen als afzonderlijk item (27 oktober 2026): samengevoegd met BL-14.** Geen apart onderhoudsscherm of tweede catalogusconfiguratie. | BL-14 |

## BL-18 — Herstructurering scherm Ledendienst Planning (afgerond en functioneel geaccepteerd)

**Status en plaatsing:** schermindeling afgesproken op 25 oktober 2026; via [PR #46](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/46) inclusief standaard uitgeklapte wedstrijdtabel op 26 oktober 2026 lokaal functioneel geaccepteerd en gemerged naar `prototype-v0.5`. Zie [uitvoering en acceptatiestappen](code/Prototype/DVK-v0.5-BL18-schermindeling.md). De eerder geaccepteerde functionaliteit uit PR #44 blijft behouden. BL-18 blijft het nummer voor deze herstructurering; BL-17 is toegekend aan het verwijderen van de uitzonderingsregistratie uit Kandidaten.

**Doel:** het scherm Ledendienst Planning onderverdelen in vijf duidelijk gescheiden en gemarkeerde secties:

1. **Instellingen:** periode-instellingen en seizoen van `Overzicht per periode`, bovenaan en direct zichtbaar.
2. **Databronnen:** databronnen, bronmeldingen kandidaatcontext, brongegevens vernieuwen en datakwaliteit. Detailinformatie waar mogelijk compact of inklapbaar, maar waarschuwingen die actie vereisen blijven zichtbaar.
3. **Diensten:** Sportlink-inroosteringen voor de gekozen periode, feitelijke Sportlink-inroosteringen ophalen, opgehaalde Sportlink-inroosteringen, dienstenstatistieken en dienstentabel. Dienstselectie blijft binnen de tabel.
4. **Kandidaten:** kandidaten en voorstellen, gevolgd door visueel onderscheiden actieve tijdelijke DVK-inroosteringen. Een dienstkeuze werkt direct door in de kandidaatcontext.
5. **Wedstrijden:** wedstrijdoverzicht voor de gekozen periode als tabel, standaard uitgeklapt en inklapbaar.

**Afbakening:** uitsluitend UI-indeling en presentatie; bestaande functionaliteit, applicatieservices, broncontracten, sessiegedrag, bevestiging/undo en CKC-beleid blijven behouden. Geen Sportlink-writeback, nieuwe beleidsregels of ongevraagde architectuurwijzigingen.

**Acceptatie:** vijf secties in afgesproken volgorde; instellingen direct zichtbaar; databronnen compact zonder belangrijke waarschuwingen te verbergen; dienstselectie en kandidaatcontext consistent; tijdelijke DVK-inroosteringen herkenbaar afzonderlijk; wedstrijden standaard zichtbaar (uitgeklapt); bestaande functionaliteit regressievrij. BL-18 is inclusief standaard zichtbare wedstrijden lokaal functioneel geaccepteerd op 26 oktober 2026; geen afzonderlijke zichtbaarheidscontrole meer open.

## BL-19 — Zelfstandig No-showmanagement (26 oktober 2026; aangescherpt 27 oktober 2026)

**Status:** functioneel geaccepteerd op 2 november 2026, codecommit `069e5a1388e1b66372062d411b5f44a6a6a5429d` van PR #61; nog niet gemerged. Onderdeel van prototype v0.5. De bestaande no-showregistratie, intrekkingsmogelijkheid en historie worden hergebruikt; BL-11 is als afzonderlijk backlogitem afgesloten.

**Plaats in de navigatie:** afzonderlijke functie **No-showmanagement** onder **Ledendiensten & Vrijwilligersbeleid**, los van **Ledendienst Planning**. Verplaats de bestaande No-showbediening uit Ledendienst Planning/Kandidaten zonder gegevensverlies.

**Functie 1 — No-show aanmelden (maximaal 14 kalenderdagen terug):** toon de daadwerkelijk in Sportlink ingeroosterde ledendiensten vanaf **vandaag min 14 kalenderdagen tot en met vandaag**, inclusief beide grensdagen. Alleen voor een feitelijk ingeroosterde persoon en dienst binnen deze periode mag een nieuwe No-show worden geregistreerd. Oudere en toekomstige diensten komen niet in aanmerking voor nieuwe registratie. De termijn wordt op de actuele kalenderdatum gebaseerd, niet op de actieve planningsperiode. Historische raadpleging via de Vrijwilligers API mag actieve planning, broncontext en tijdelijke DVK-indelingen niet verstoren. Onderzoek in het ontwerp de samenhang met bestaande actieve-bron-/periodecontroles.

**Functie 2 — Seizoensoverzicht en intrekken:** toon standaard **alle geregistreerde No-shows van het lopende seizoen**, inclusief ingetrokken registraties. Een actieve No-show kan ook **na de aanmeldtermijn van 14 dagen** worden ingetrokken; de termijn beperkt alleen **nieuwe aanmeldingen**. Behoud de eerder afgesproken mogelijkheid om via seizoensfilters ook eerdere seizoenen te raadplegen, plus filters op persoon en status en inzicht in herhaald gedrag: aantallen **niet-ingetrokken** No-shows per lid in het geselecteerde seizoen en over meerdere seizoenen. Ingetrokken No-shows blijven zichtbaar maar tellen niet als geldige No-show. Analyse is signalerend, zonder automatische nieuwe sancties.

**Acceptatie:** de twee functies zijn herkenbaar gescheiden; grensdagen van het 14-dagenvenster worden correct behandeld; aanmelden buiten het venster wordt ook bij directe acties geweigerd; alleen werkelijk ingeroosterde personen/diensten komen in aanmerking; intrekking blijft ongeacht leeftijd van registratie mogelijk; actuele en historische overzichten behouden actieve én ingetrokken historie; de bestaande planning blijft onaangetast; ongeldige of mislukte bronophaalacties wijzigen geen bestaande toestand. Geen Sportlink-writeback.

## BL-20 — Weekendfilter op teamspeeldag bij vrijwilligersvoorstellen

**Status:** afgerond en functioneel geaccepteerd door Johan op 29 oktober 2026 via [PR #53](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/53), Iteratie 1.

**Geaccepteerde werking:** het daadwerkelijke teamattribuut `Speeldag` uit Teams.csv bepaalt de weekendfilter voor spelers. Zaterdagspelers worden normaal niet op zondag aangeboden en zondagspelers normaal niet op zaterdag. Op de eigen speeldag en doordeweeks geldt deze beperking niet. Niet-spelende leden worden er niet door beperkt. Alle relevante spelerteamkoppelingen tellen: een speler van zowel een zaterdag- als zondagteam is op beide weekenddagen toegestaan. Bestaande wedstrijd- en overige geschiktheidsregels blijven gelden.

**Nooduitzondering (bevestigd in Iteratie 1):** uitsluitend wanneer overige geschikte kandidaten onvoldoende zijn voor de actuele minimumbezetting mogen spelers van de andere weekenddag herkenbaar als noodkandidaat worden aangeboden. Tijdelijke indelingen tellen mee; bevestiging begrenst noodselectie tot het minimum. Alle andere geschiktheidsregels en expliciete menselijke bevestiging blijven gelden.

**Bronwaarden (lokaal verduidelijkt):** `Algemeen/Vrijdag` is geldig voor recreatieve bondsteams en veroorzaakt geen weekendbeperking. Bij toch geregistreerde Sportlink-taakplicht en positieve open uren kan een vrijdagteamspeler op beide weekenddagen gewone kandidaat zijn. Een vrijdagkoppeling wijzigt beperkingen uit eventuele andere weekendteamkoppelingen niet. Recreatieve vrijstelling blijft onderdeel van Taakplichtcontrole; Sportlink blijft leidend voor planning. Ontbrekende, onbekende en tegenstrijdige speeldagen blokkeren kandidaten/voorstellen met een zichtbare bronfout, zonder planning of historie te wissen. De geaccepteerde afzonderlijke identiteiten van zaterdagteam 2 en zondagteam 2 blijven behouden.

**Acceptatiegrens:** Eén richting van de weekendfilter is lokaal waargenomen; de andere richting en noodkandidaten zijn uitsluitend synthetisch getoetst. Dubbele teamkoppelingen en ongeldige bronwaarden zijn synthetisch gedekt. Integrale v0.5-acceptatie blijft open. Een tijdens acceptatie ontbrekende zondagteamkandidaat bleek terecht uitgesloten door een overlappende wedstrijd; zonder die wedstrijd verscheen de kandidaat wel. Zie [verslag](code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md).

## BL-21 — Versieaanduiding op het DVK-hoofdscherm (26 oktober 2026)

**Status:** afgerond en lokaal functioneel geaccepteerd door Johan op 29 oktober 2026 via PR #53, Iteratie 1. De actieve branch, commit, worktree en eventuele lokale wijzigingen staan onder de hoofdtitel; ontbrekende Git-informatie krijgt een eerlijke melding.

**Wens:** toon direct onder de titel `CKC Digitaal Verenigingskantoor (DVK)` een kleine, subtiele aanduiding van de daadwerkelijk actieve applicatieversie, bijvoorbeeld `PR #46 (BL-18)` tijdens de acceptatie van die versie. Zo is bij lokaal testen direct zichtbaar welke codeversie draait.

**Uitwerking:** werk de aanduiding bij elke nieuwe versie bij; geef waar praktisch mogelijk de voorkeur aan een centraal beheerde of automatisch afgeleide versie-identificatie in plaats van losse handmatige tekst. Zorg dat de aanduiding overeenkomt met de werkelijk gestarte versie, ook bij gebruik van verschillende Git-branches/worktrees. Geen wijziging in de functionele werking.

**Acceptatie:** versieaanduiding staat leesbaar maar onopvallend onder de hoofdtitel; bij een volgende versie is zichtbaar dat de identificatie mee verandert. Bestaande schermwerking blijft ongewijzigd.

## BL-22 — Onderhoudbare CKC-beleidsregels voor taakplichtcontrole (26 oktober 2026)

**Status (ontwerpuitgangspunt bevestigd 27 oktober 2026):** open voor uitvoering binnen prototype v0.5; nog niet technisch geïnventariseerd of geïmplementeerd. Eerst bestaande regels en configuratie onderzoeken, daarna een minimale aanpassing voorstellen.

**Doel:** de CKC-beleidsregels voor het afleiden van de verwachte taakplicht afzonderlijk inzichtelijk, reviewbaar en eenvoudig onderhoudbaar maken, zonder dat voor gewone beleidswijzigingen onnodig Python-programmacode aangepast hoeft te worden.

**Leidende ontwerpkeuze (CKC, 27 oktober 2026):** bundel de CKC-beleidsregels en functieclassificaties bij voorkeur in **één gemakkelijk leesbaar, reviewbaar en versiebeheerd Python-bestand**, duidelijk gescheiden van technische verwerking. Dit volstaat voorlopig als onderhoudsoplossing. Onderzoek eerst hoe regels en mappings nu verspreid zijn en behoud reeds bruikbare bestaande configuratie waar passend; introduceer geen onnodige migratie of extra afhankelijkheden. **Geen Rules-tool, rules-engineproduct of beheerinterface** in deze iteratie. Een afzonderlijke Rules-tool kan pas later op basis van een nieuw besluit worden overwogen.

**Functionele randvoorwaarden:**
- De bestaande, functioneel geaccepteerde CKC-beleidsregels en taakplichtuitkomsten blijven behouden; wijzigingen aan het beleid zijn geen onderdeel van deze technische onderhoudbaarheidsverbetering.
- De taakplichtcontrole blijft de verwachte taakplicht uit bronfeiten en CKC-beleid afleiden, de toegepaste vrijstellingsgrond verklaren en afwijkingen ten opzichte van de Sportlink-registratie signaleren.
- **Ledendienst Planning gebruikt de in Sportlink geregistreerde taakplicht als leidende kandidatenbasis.** De regelconfiguratie mag geen afzonderlijke uitzonderingsadministratie of concurrerende taakplichtwaarheid voor de planning creëren (zie BL-05 en BL-17).
- Maak regels en mappings reviewbaar, traceerbaar en met gerichte regressietests controleerbaar. Vermijd onnodige abstrahering, migratie of nieuwe afhankelijkheden.

**Eerstvolgende stap:** gerichte technische inventarisatie van de huidige Python-implementatie, bestaande configuratie, beleidsregels en tests; daarna een minimaal wijzigingsvoorstel met expliciete acceptatiecriteria voorleggen vóór implementatie.

## BL-23 — In- en uitklapbare rubrieken Ledendienst Planning (27 oktober 2026)

**Status:** technisch geïmplementeerd in Iteratie 3; functioneel geaccepteerd op 30 oktober 2026 op commit `0aa8445d9f70d2f099f2599e117035f00d05e0a1`; PR #56 op 30 oktober 2026 gemerged naar `prototype-v0.5` (mergecommit `d9942c328e75a7235803319807504fbd36c522d4`). Zie [Iteratie 3-verslag](code/Prototype/DVK-v0.5-iteratie3-bronstatus-rubrieken.md).

**Wens:** maak de vijf bestaande rubrieken **Instellingen, Databronnen, Diensten, Kandidaten en Wedstrijden** afzonderlijk in- en uitklapbaar. Bij het openen van het scherm Ledendienst Planning zijn alle vijf standaard **ingeklapt**: alleen de rubrieknamen zijn zichtbaar. De planner kan één of meerdere rubrieken naar keuze openklappen, zonder dat het openen van de ene rubriek andere automatisch sluit.

**Randvoorwaarden en acceptatie:** behoud de in BL-18 geaccepteerde volgorde, inhoud, gegevens, waarschuwingen en functionaliteit. Dit wijzigt bewust de eerdere BL-18-startstand waarin Wedstrijden standaard uitgeklapt was; de nieuwe standaard is dat **alle vijf rubrieken ingeklapt** starten. Geen wijziging van onderliggende planning, selectie, bronverwerking of gegevensopslag. Controleer lokaal dat elke rubriek onafhankelijk werkt en dat bestaande functies na openklappen bereikbaar blijven.



## BL-24 — Compleet overzicht Bronstatus en actualiteit (27 oktober 2026)

**Status:** geïmplementeerd en functioneel geaccepteerd op 30 oktober 2026 op commit `0aa8445d9f70d2f099f2599e117035f00d05e0a1`; PR #56 op 30 oktober 2026 gemerged naar `prototype-v0.5` (mergecommit `d9942c328e75a7235803319807504fbd36c522d4`). Overzicht omvat zes CSV-bronnen (historie optioneel) en twee API-bronnen. Zie [Iteratie 3-verslag](code/Prototype/DVK-v0.5-iteratie3-bronstatus-rubrieken.md).

**Aanleiding:** in de sectie **Databronnen** toont de tabel **Bronstatus en actualiteit** momenteel alleen `Sportlink Vrijwilligers`. Dat is onlogisch bij een overzicht dat bronstatus en actualiteit pretendeert te tonen: **alle relevante bronnen, of geen onvolledig overzicht**.

**Gewenste werking:** toon consequent **alle gegevensbronnen die Ledendienst Planning gebruikt**, zowel de API-bronnen **Sportlink Vrijwilligers** en **Sportlink Programma** als de relevante lokale CSV-bronnen. Voor de CSV-bronnen **Functies** en **Commissies** volstaat conform het afsluitbesluit van BL-09 de datum van de laatste import, zonder waarschuwing uitsluitend vanwege de ouderdom van die gegevens. Vermeld per bron, voor zover bekend, de beschikbaarheids-/laadstatus, datum van ophalen of importeren en eventuele waarschuwingen. Toon ook bronnen die nog niet geladen of beschikbaar zijn, met een eerlijke status in plaats van ze stilzwijgend weg te laten. Vermijd verzonnen ophaaltijden of schijnzekerheid.

**Aanpak en acceptatie:** onderzoek eerst waarom alleen Sportlink Vrijwilligers wordt getoond en welke statusinformatie al beschikbaar is. Hergebruik bestaande bronmetadata; geen nieuwe infrastructuur zonder aantoonbare noodzaak. Controleer lokaal dat alle gebruikte bronnen consistent worden getoond en dat ontbrekende of verouderde bronnen herkenbaar blijven. Geen wijziging aan broninhoud of planninglogica.

## BL-13 — RPA voor invoer van goedgekeurde Ledendiensten in Sportlink

**Status:** toegevoegd op verzoek van Johan, 12 oktober 2026; vervolg na integrale acceptatie v0.5. Nog geen implementatie of functionele acceptatie.

**Doel:** een bevoegde planner laat een menselijk goedgekeurde DVK-indeling via de Sportlink-browserversie invoeren en krijgt per indeling een gecontroleerd resultaat terug. RPA verzorgt de uitvoering; kandidaatselectie en CKC-beleid blijven in DVK.

- **Bevestigd door opdrachtgever:** browseromgeving gebruiken; RPA opnemen in backlog en releaseplanning.
- **Uitgangspunt opdrachtgever, niet onafhankelijk geverifieerd:** geen beschikbare schrijf-API voor Ledendienstindelingen. Bij de proef opnieuw controleren.
- **Technisch voorstel:** Playwright met Python als kandidaat voor een afzonderlijke uitvoercomponent; definitieve keuze pas na de haalbaarheidsproef.
- **Nog onbewezen:** de benodigde Sportlink-schermen, rechten en terugleesmogelijkheden lenen zich voor betrouwbare automatisering.

### Afbakening en afhankelijkheden

Geen Sportlink-writeback in v0.5. Eerst Stap 3 Planning en BL-10 accepteren: betrouwbare personen-/dienstidentificatie, actuele bezetting, menselijke goedkeuring en synchronisatiegrens. Een tijdelijke DVK-planning of interne assignment bewijst geen Sportlink-registratie. De concrete betekenis van goedkeuring en uitvoering wordt voor de proef vastgelegd.

De eerste proef gebruikt een zichtbaar browservenster waarin de bevoegde planner zelf inlogt. Alleen vooraf goedgekeurde indelingen worden verwerkt. Geen automatische beleidsbeslissingen, uren-/sanctiecorrecties, communicatie of automatisering van de Voetbal.nl-app in deze scope.

### Fasering en acceptatie

| Onderdeel | Resultaat en acceptatie | Voorwaarde |
| --- | --- | --- |
| BL-13a — Haalbaarheidsproef | Eén expliciet goedgekeurde indeling invoeren; persoon, taak/dienst, datum en tijden vooraf uniek controleren; daarna feitelijke opslag teruglezen. Bestaande indeling overslaan; onderbreking veilig hervatten zonder dubbele invoer. Onduidelijk resultaat apart melden en niet als geslaagd afvinken. | Na integrale acceptatie v0.5; rechten, testwerkwijze en eventuele notificaties van Sportlink vooraf vaststellen |
| BL-13b — Pilot onder toezicht | Kleine goedgekeurde batch; resultaat per indeling, fouten en gedeeltelijke uitvoering zichtbaar; opnieuw controleren op gewijzigde bezetting en bij hervatten eerst teruglezen. Correctie-/stopprocedure en handmatige verwerking beschikbaar. | Positief proefresultaat en expliciete acceptatie van pilotscope |
| BL-13c — Beheerde productie-invoering | Bevoegdheden, veilige sessies, uitvoerregistratie, herstel, monitoring en onderhoud van schermkoppelingen geborgd; pilotacceptatie en productie-go/no-go. | Productieroadmap P1–P3 en voldoende praktijkbewijs |

**Status bevestigd 27 oktober 2026:** functionele uitgangspunten vastgesteld; BL-13 blijft open voor uitvoering na v0.5 en heeft een expliciete plek in de prototype-opleverplanning. Eerste afgebakende vervolgproef na v0.5; pilot pas na positief haalbaarheidsbesluit. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [productieroadmap](PRODUCTIE-ROADMAP.md). Exact releasenummer, datum, capaciteit en onderhoudseigenaar zijn nog te besluiten.

## Gegevensintegraties als afzonderlijke ontwikkelstappen

De **Vrijwilligers API** en **Programma API** zijn noodzakelijke bouwstenen voor Stap 3 Planning. Ze staan als aparte acceptatiestappen in [DVK-PROTOTYPE-PLANNING.md](DVK-PROTOTYPE-PLANNING.md), niet als verondersteld geheel nieuwe backlogfunctionaliteit. De Vrijwilligers API is via PR #38 lokaal geaccepteerd. Voor Programma zijn teamnaamkoppeling en datum-/tijdverwerking via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) lokaal geaccepteerd (141/141 gekoppelde operationele wedstrijden). De operationele schermintegratie en zichtbaarheid van wedstrijden zijn inmiddels eveneens functioneel geaccepteerd (BL-18/PR #46). **De Programma API-integratie is afgerond; geen afzonderlijke ontwikkelstap meer.** Het gebruik van wedstrijd- en teamgegevens in nieuwe kandidaatselectieregels, waaronder de teamspeeldagfilter, is een afzonderlijke backlogwens; geen heropening van de Programma API-integratie. [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseert de vijf lokale CSV-exportpaden; de standaardlocatie voor Teams.csv is lokaal functioneel gecontroleerd. Eerst de actuele adapters, broncontracten en werkelijke integratiestatus verifiëren; geen duplicatie.

## Niet in de backlog

**BL-12 — Integrale acceptatie prototype v0.5: administratief afgesloten als backlogitem (27 oktober 2026).** Dit is een **implementatie-/acceptatiemijlpaal**, geen functionele backlogwens of afzonderlijke ontwikkelopdracht. De mijlpaal blijft opgenomen in de [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en wordt op het passende moment beoordeeld; afsluiting van BL-12 betekent **niet** dat prototype v0.5 al integraal is geaccepteerd.

## Werkafspraken

**Nummeringsregel (26 oktober 2026):** ken ieder nieuw backlogitem direct het eerstvolgende beschikbare BL-nummer toe. Ga niet uit van niet-vastgelegde reserveringen. Komt later een ouder of eerder informeel gereserveerd onderwerp naar voren, dan krijgt het op dat moment het eerstvolgende beschikbare nummer; bestaande toegekende nummers blijven ongewijzigd.

1. Besluiten uit deze bespreking vormen geen stilzwijgende codewijziging. Functionele baseline, technische implementatie en tests worden traceerbaar bijgewerkt.
2. Echte CKC-bestanden (Sportlink CSV's, planner-Excel), persoonsgegevens en lokale databases blijven op de eigen computer; niet uploaden naar GitHub, Codex of ChatGPT. Alleen synthetische voorbeelden en niet-herleidbare aggregaten in repository.
3. Elke ontwikkelstap krijgt een afgebakende branch/PR, regressie en expliciete functionele acceptatie; geen merge zonder akkoord.
4. Productievereisten worden apart beheerd in [PRODUCTIE-ROADMAP.md](PRODUCTIE-ROADMAP.md).
5. De historische backlog is een gereconstrueerde werklijst; controleer bij uitvoering de actuele code en GitHub Issues voordat iets als ontbrekend wordt aangemerkt.

## Functionele bronnen

- [Herijkte functionele baseline Ledendiensten](code/Prototype/DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md)
- [Functioneel contract v0.5 vervolg](code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md)
- [Technische impactanalyse v0.5 vervolg](code/Prototype/TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md)
- [GitHub Issue #12](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/12) en [#14](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/14)


## Acceptatie BL-19 — Iteratie 5 (2 november 2026)

**2 november 2026 — Iteratie 5 / BL-19 functioneel geaccepteerd door CKC**, op codecommit `069e5a1388e1b66372062d411b5f44a6a6a5429d` van [PR #61](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/61), **nog niet gemerged**. Zelfstandig No-showmanagement (Sportlink-raadpleging en handmatige registratie), 15 kalenderdatums vandaag−14 t/m vandaag, actieve en ingetrokken historie, sanctietelling en intrekking geaccepteerd. Correcties BL-19-01 (datumkiezer), BL-19-02 (alfabetische persoonskeuzes), BL-19-03 (periode-uitleg) en BL-19-05 (historie met tien regels per pagina, registratiemoment nieuwste eerst en één detailpaneel) geaccepteerd. BL-19-04 en BL-19-06 bleken na nadere controle geen defect. 106 gerichte en 1371 regressietests geslaagd, CI #402 groen; paginering met meer dan tien regels, uitzonderingspaden en planningisolatie met synthetische tests gecontroleerd, niet volledig lokaal met echte CKC-scenario's. Geen Sportlink-writeback, schema- of sanctieregelwijziging. Integrale v0.5-acceptatie blijft open; volgende iteratie is **Iteratie 6 — BL-22**.

[Uitvoering en acceptatieverslag](code/Prototype/DVK-v0.5-iteratie5-BL19.md). De eerdere BL-19-omschrijving hierboven documenteert de oorspronkelijke functionele afbakening; de geaccepteerde handmatige route, werkelijke diensttijden, bronhercontrole, duplicaatwaarschuwingen en presentatiecorrecties staan in het acceptatieverslag.

## Acceptatie BL-22 — Iteratie 6 (2 november 2026)

**Functioneel geaccepteerd door CKC** op codecommit `d0be7dccb31eaeace038bfb867a7c25b2995dd70` van [draft-PR #62](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/62); **niet gemerged**. Vijf herkenbare stappen in actuele taakplichtafleiding, gedeelde B-02-predicate, bestaande CSV-classificatie behouden, [beleidsregelindex](docs/DVK-v0.5-CKC-beleidsregelindex-Ledendiensten.md) met elf synthetische voorbeelden. Geen nieuwe beleidsregels, Rules Engine of DVK-beheerscherm. CKC beoordeelt de index als compleet, maar lastig leesbaar voor niet-ingewijden. Eventuele toekomstige read-only weergave onder Ledendiensten uitsluitend op basis van latere behoefte en apart besluit. Technisch verslag: 1501 regressietests geslaagd, 768 equivalente synthetische situaties, CI #407 groen. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie6-BL22-acceptatie.md). Integrale v0.5-acceptatie blijft open.

## Iteratie 7add — Kleine UI-correcties Ledendienst Planning (afgesproken 2 november 2026)

**Status: afgesproken, nog niet geïmplementeerd. Uitvoeren ná Iteratie 6, afzonderlijke Codex-opdracht en visuele CKC-acceptatie.**

1. Verplaats de bestaande melding over ontbrekende gevalideerde Sportlink-roosterbezetting uit sectie **2 — Databronnen** naar sectie **3 — Diensten**, direct boven de knop voor het ophalen van roostergegevens. Gebruik exact: "De actuele bezetting van de vrijwilligersdiensten is nog niet beschikbaar voor deze roosterperiode. Haal de roostergegevens op via de onderstaande knop om de bezetting en resterende behoefte te kunnen bepalen". Behoud de bestaande conditie en gegevensverwerking; geen API- of berekeningswijziging.
2. Maak de dienstentabel bij standaard browserweergave compacter, met name de kolommen **Dienst** en **Sportlink**, zodat de laatste kolom **Vrije capaciteit** op een gemiddeld scherm (richtwaarde 1366 px, 100% zoom) zonder horizontaal scrollen volledig zichtbaar is. Behoud alle gegevens, leesbaarheid en tabelinteracties. Exacte breedtes op basis van de bestaande Streamlit-implementatie vaststellen.

Deze correcties wijzigen geen CKC-beleid, taakplicht of planning. Geen Sportlink-writeback.

### Statusaanvulling Iteratie 7add — functionele acceptatie (3 november 2026)

De hierboven als voorgenomen beschreven correcties zijn inmiddels **functioneel geaccepteerd door CKC** op codecommit `e4d6a9df5c599a47751ea79fa3366dd18ac7b3f5` in [draft-PR #63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63), nog niet gemerged. De waarschuwing staat nu in sectie 3 Diensten bij de Sportlink-synchronisatieknop. De tabelbreedtes Dienst 110 px, Sportlink 140 px en Vrije capaciteit 65 px zijn na twee visuele rondes geaccepteerd; waarden zijn zonder horizontaal scrollen zichtbaar, de laatste kolomkop mag afgekapt zijn, en volledige Sportlink-namen zijn via dubbelklik leesbaar. 131 gerichte tests, 1502 regressietests, 11 synthetische runners en CI #414 groen. Geen wijziging van CKC-beleid, bronnen, berekeningen of Sportlink-writeback. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie7add-acceptatie.md). Volgende mijlpaal is integrale v0.5-acceptatie; de lokale Streamlit-opstartvertraging wordt apart onderzocht.


## Actuele vervolgplanning na Planner-overleg — 3 november 2026

**Status: Iteratie 8 lokaal functioneel geaccepteerd (PR #65 nog niet gemerged); Iteratie 9 nog niet geïmplementeerd of geaccepteerd.** Deze sectie vervangt oudere uitspraken dat direct na Iteratie 7add de integrale v0.5-acceptatie volgt. Historische statusnotities blijven herkenbaar als momentopnamen. Iteraties 1, 2, 3, 4, 5, 6 en 7add zijn afgerond; [PR #63](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/63) is volgens de overdracht gemerged (mergecommit `db6fc1773362880663b8fe5b34b40e58434e107d`).

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


### Correctie afgeschermde Sportlink-inroosteringen — PR #67 (7 november 2026)

**Functioneel geaccepteerd door CKC** op codecommit `90d3ddea2e8b4a2b90c70ba78ecf692cbb00caa7` in [PR #67](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/67). Praktijkcontrole op de dienst met twee reguliere en twee identiek als `Afgeschermd` aangeleverde boekingen: alle vier regels afzonderlijk zichtbaar, beide afgeschermde regels tellen mee, **vrije capaciteit = 0**. Geen persoonsidentificatie uit afgeschermde regels; geen persoonsgebonden uren of no-showregistratie. De persoons- en no-showbescherming is technisch/regressiematig gecontroleerd, niet afzonderlijk handmatig beproefd. 1.597 regressietests geslaagd; CI #433 groen op de geaccepteerde codecommit. Geen wijziging van Iteratie 9-beleid; Iteratie 10 blijft de integrale functionele acceptatie. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-PR67-afgeschermde-inroosteringen-acceptatie.md).

**Afzonderlijke vervolgcorrectie:** configureerbare, blijvend bewaarde lokale Sportlink-exportmap, zonder gebruikersspecifiek hardcoded pad. Nieuwe lokale ontwikkelopstelling buiten iCloud; exportbestanden en Client-ID-configuratie buiten de Git-repository. Deze inrichting is geen onderdeel van PR #67 en wordt afzonderlijk uitgewerkt en geaccepteerd. Geen Sportlink-writeback.


## Iteratie 9A.1 — Databronnen en exportmap (7 november 2026)

**Functioneel geaccepteerd** op 7 november 2026; technische oplevering in [draft-PR #68](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/68), codecommit `06d1fe50bd30235fe2c9658e51395509082bf699`, CI #437 groen (1.602 regressietests volgens Codex). Afzonderlijke functie **Ledendiensten → Databronnen**; configureerbare Sportlink-exportmap, lokaal persistent via `~/.config/dvk/settings.json`; CSV- en API-status en handmatige bronverversing. Lokale controle: configuratie blijft na herstart behouden, Vrijwilligers-inroosteringen ophalen werkt en navigatie bewaart tijdelijke indelingen en bestaande bezetting. **Open voor 9A.2:** automatische CSV-, Programma- en Vrijwilligersbronlading bij definitieve nieuwe planning, zonder bronaanroepen bij hervatten; huidige meervoudige handmatige laadacties zijn als onoverzichtelijk beoordeeld. Geen databaseverplaatsing of opruimen oude mappen in 9A.1. PR #68 is nog niet gemerged; afzonderlijk mergeakkoord vereist. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a1-acceptatie.md). Iteratie 10 blijft integrale acceptatie.


## Iteratie 9A.2 — Automatisch laden bij nieuwe planning (functioneel geaccepteerd op 7 november 2026)

**Status:** functioneel geaccepteerd door CKC op codecommit `045afbdc467185a870da5220d9a910ccc05f9333` in [draft-PR #69](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/69), gericht op `prototype-v0.5`; **niet gemerged bij deze vastlegging**. [CI #441](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/42420999174) geslaagd; Codex rapporteert 117 gerichte tests, 1.609 regressietests en 11 synthetische acceptatiescripts geslaagd. Zie [acceptatieverslag](code/Prototype/DVK-v0.5-iteratie-9a2-acceptatie.md).

Bij een nieuwe planning is de huidige kalenderweek de standaard en kan de planner vooraf een andere periode kiezen. Pas na **Start nieuwe planning** worden de vijf verplichte en één optionele lokale CSV, Sportlink Programma en Sportlink Vrijwilligers automatisch geladen, met voortgang en onderscheiden bronstatus voor lege resultaten en fouten. Hervatten gebruikt de duurzaam in SQLite opgeslagen kandidaat- en wedstrijdcontext en bestaande gevalideerde bezetting, zonder nieuwe bronaanroepen; tijdelijke indelingen blijven behouden. Handmatige verversing blijft onder **Ledendiensten → Databronnen**, met expliciete bevestiging voor vervanging van bezetting. Bij ontbrekende verplichte bronnen zijn kandidaatvoorstellen niet veilig beschikbaar; bij mislukte Vrijwilligers-uitvraag is bezetting onbekend. Geen Sportlink-writeback.

**Lokale acceptatie:** (1) automatisch laden en periodekeuze geslaagd; (2) na Streamlit-herstart dezelfde periode, wedstrijden, bezetting en tijdelijke indeling zonder opnieuw laden; (3) vervanging zonder expliciete bevestiging geblokkeerd, tijdelijke indeling behouden; (4) tijdelijk hernoemde `Functies.csv` leidt tot een duidelijke foutmelding met exacte verwachte locatie en hersteladvies. De gebruiker is verzocht `Functies.csv.test` weer terug te noemen; herstel is niet afzonderlijk bevestigd. Geen productie- of integrale v0.5-acceptatie.

**Vervolg:** 9A.3 sessie- en regressiebescherming; 9A.4 lokale omgeving/databasepad verifiëren zonder ongevraagde migratie of opruiming; 9A.5 afronding en voorbereiding; Iteratie 10 integrale functionele acceptatie. Merge PR #69 uitsluitend na afzonderlijke toestemming.
