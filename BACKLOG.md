# DVK — Functionele backlog

**Status:** bijgewerkt op 26 oktober 2026; BL-05 herijkt, opruimactie uitzonderingsregistratie afzonderlijk opgenomen; BL-18 en Programma API-status gecorrigeerd; overige openstaande punten nog niet herbeoordeeld  
**Scope:** prototype v0.5 en later; geen implementatieplanning of productiearchitectuur.  
**Verwijzingen:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md)

De backlog bevat openstaande functionaliteit, beleidsbesluiten en bronafhankelijkheden. De volgorde, afzonderlijke ontwikkelstappen en integrale acceptatiemijlpaal staan in de prototypeplanning. Statussen beschrijven wat is afgesproken; ze bewijzen niet dat code al bestaat.

## Afgerond

| ID | Onderwerp | Status / bewijs |
| --- | --- | --- |
| BL-01 | Adresgebaseerde huishoud- en minderjarigenregels B-05/B-06/B-07 | **Afgerond en functioneel geaccepteerd** in Stap 2 ronde 4; uitsluitend volledig geregistreerd adres als automatische huishoudsleutel; relevante leden op peildatum; geen ouder-/achternaamheuristiek. |
| BL-02 | Read-only taakplichtcontroledashboard | **Afgerond en functioneel geaccepteerd.** Lokale CKC-acceptatie: 650 relevante leden, 563 overeenkomsten, 87 afwijkingen, 0 niet betrouwbaar beoordeelbaar. Bron- en controlediagnose behouden. [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged naar `prototype-v0.5`. |
| BL-04 | DVK-frontend, hoofdmenu, licht portaal | **Afgerond en functioneel geaccepteerd op 19 oktober 2026.** Startscherm met acht functies in drie groepen, één per regel; zijbalk uitsluitend navigatie; instellingen op eigen scherm. Rooster Generator als uitgeschakelde knop. Correcties BL-04-01/03/04 verwerkt; BL-04-02 vervallen. 62 gerichte tests, 636 regressietests en CI groen. [PR #32](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/32) gemerged naar `prototype-v0.5` (`68ae25fa`). CSV-uploads moeten na schermwisseling opnieuw worden geselecteerd. |

## Open / geprioriteerd

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |
| BL-03 | Achterstallige uren vorig seizoen | **Hoge prioriteit, v0.5.** Planner bevestigt beschikbaar Excel-overzicht; bestand/kolommen nog te ontvangen en lokaal te verifiëren. Koppeling bij voorkeur op Sportlink-lidnummer, met seizoen, openstaande uren en controle op duplicaten/ontbrekende matches. Achterstand beïnvloedt kandidaatprioritering **tot en met 31 december**; vanaf 1 januari niet meer. Niet optellen bij Sportlink A van het nieuwe seizoen. **Wijziging B-13** t.o.v. eerdere grens 1 december: functionele baseline, configuratie en regressietests expliciet bijwerken vóór implementatie. | Excel van planner; bronsemantiek en seizoensidentificatie |
| BL-05 | Duurzame plannerbeslissingen bij taakplichtafwijkingen | **Vervallen als ontwikkelopdracht (besluit 26 oktober 2026).** DVK blijft afwijkingen tussen de Sportlink-taakplichtregistratie en CKC-beleidsregels signaleren via de bestaande taakplichtcontrole. De planner beoordeelt deze en corrigeert zo nodig Sportlink. Geen aparte DVK-registratie van besluiten, redenen of taakplichtuitzonderingen. De 87 eerder geconstateerde afwijkingen hoeven niet eerst door de planner te zijn beoordeeld om BL-05 af te sluiten. | Geen DVK-ontwikkeling; bestaande taakplichtcontrole behouden |
| BL-06 | Urenoverdracht bij 18 jaar | **Vervallen als afzonderlijke DVK-ontwikkelopdracht (besluit 26 oktober 2026).** Bij meerderjarigheid kan de gezinsgebonden taakplicht naar een jonger minderjarig lid verschuiven; reeds gewerkte uren blijven bij het lid dat ze heeft verricht. DVK signaleert eventuele afwijkingen in verwachte taakplicht via de bestaande read-only taakplichtcontrole. Eventuele handmatige urenoverdracht of -correctie in Sportlink blijft mogelijk, maar valt volledig buiten DVK: geen signalering, goedkeuring, ondersteuning of verificatie van die overdracht. | Herziene beleidsafspraak B-08; bestaande taakplichtcontrole |
| BL-07 | Sportlink-urenbron en seizoensgegevens | **Functioneel gevalideerd en afgesloten (27 oktober 2026); geen aanvullend ontwikkelwerk.** Bron *Overzicht per periode*: A = Verplichte punten, B = Gecorrigeerde punten, C = Voldaan, D = Nog ingedeeld, E = Niet ingedeeld; E = A − B − C − D. Bronbestand bevat per definitie uitsluitend het huidige seizoen. Praktijksteekproef: openstaande uren en prioritering in Kandidaten en Voorstellen stemmen overeen met Sportlink-CSV. Geen afzonderlijke DVK-verificatie van handmatige urenoverdracht (BL-06). Dit is functionele acceptatie op basis van steekproef, geen volledige technische regressietest. | Afgesloten; B-13 en bronverificatie bijgewerkt |
| BL-08 | Functieclassificatie `Verzorger` | **Wacht op CKC-broncorrectie.** Onderscheid betaalde en onbetaalde functie in Sportlink nog niet betrouwbaar; huidige tijdelijke classificatie niet persoonsgebonden hardcoden. Na correctie lokaal opnieuw controleren. Blokkeert ander v0.5-werk niet. | CKC/Sportlink |
| BL-09 | Bronactualiteit functies en commissies | **Bewaken binnen v0.5.** Bestaande bron- en controlediagnose behouden; verouderde of onvolledige bronfeiten signaleren, geen ontbrekende functiedatums verzinnen. Geen aparte ontwikkelronde tenzij controle een concrete tekortkoming aantoont. | Nieuwe bronexports |
| BL-10 | Tijdelijke planning en Sportlink-synchronisatie | **v0.5, duurzame sessies en Vrijwilligers-bronverversing lokaal geaccepteerd via PR #38; integrale planningsverificatie open.** PR #34 borgt afwijzing van ongeldige Vrijwilligers-responsen vóór publicatie en behoud van bestaande gegevens bij mislukte verversing. PR #35 borgde behoud tijdens navigatie/refresh, bevestigde periodewisseling en destijds wissen bij procesherstart; vijf lokale acceptatiescenario's geslaagd. **De herstartregel is inmiddels functioneel achterhaald** door het op 22 oktober 2026 geaccepteerde [ontwerp Planningssessies](code/Prototype/DVK-v0.5-planningssessies.md). Nog te toetsen in de volledige API-/planningsketen: actuele bezetting en beschikbaarheid, undo, handmatige Sportlink-verwerking en succesvolle bronverversing als wisgrens. Alleen aantoonbare gaps herstellen. | API Vrijwilligers; FR-02–FR-08 |
| BL-11 | No-shows en handmatige Sportlink-correctiewerkvoorraad | **v0.5, registratie, intrekking en sanctieafleiding lokaal geaccepteerd via PR #38; handmatige correctiewerkvoorraad en integrale verificatie blijven open.** Controleer koppeling aan feitelijke Sportlink-inroostering, duurzame no-show, intrekking, sanctieafleiding en status openstaand/afgehandeld van handmatige correctie. Hergebruik geaccepteerde functionaliteit. | API Vrijwilligers; FR-09–FR-12 |

## BL-17 — Uitzonderingsregistratie verwijderen uit Kandidaten (26 oktober 2026)

**Status:** BL-17 toegekend op 26 oktober 2026; afgesproken opruimactie voor prototype v0.5, nog niet geïmplementeerd. **Bewust opnemen in de prototypeplanning**; bij voorkeur combineren met de afzonderlijk vastgelegde teamspeeldagfilter-iteratie (BL-20).

**Functioneel uitgangspunt:** in Ledendienst Planning is de in Sportlink geregistreerde taakplicht leidend voor de kandidatenbasis, ongeacht of die registratie volgens de CKC-beleidsregels juist is. De afzonderlijke taakplichtcontrole signaleert beleidsafwijkingen; de planner beoordeelt deze en corrigeert zo nodig Sportlink. DVK legt geen taakplichtuitzonderingen vast.

**Uit te voeren:**
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
| BL-14 | Beheer op te vragen Sportlink-taakcodes | **Nieuwe wens; na eerste Vrijwilligers API-integratie.** Onderhoudscherm voor bevoegde DVK-gebruiker om de vaste set uit te vragen Sportlink-taakcodes toe te voegen, te wijzigen en te deactiveren, zonder codewijziging. Synchronisatie vraagt altijd de volledige actieve set op; het dashboard toont per uitgevraagde taakcode de resultaten voor de gekozen periode, inclusief nul inroosteringen. Nieuwe Sportlink-taakcodes worden niet automatisch ontdekt; beheer vereist expliciete opname. | Werkende en geaccepteerde Vrijwilligers API-integratie; vast taakcodecontract |
| BL-15 | Beheer DVK-dienstencatalogus | **Nieuwe wens; na eerste bronintegratie.** Onderhoudscherm voor bevoegde DVK-gebruiker als vervanging van het huidige Excel-onderhoud van de eigen dienstencatalogus. Onderhoud van bestaande catalogusgegevens (zoals diensttype, gekoppelde taakcode, weekpatroon en bezettingsnormen) conform te verifiëren broncontract. Catalogus bepaalt alle concrete diensten per week, ook volledig onbezet; Vrijwilligers API levert uitsluitend feitelijke inroosteringen. Migratie en beheeropslag pas bij uitwerking bepalen; geen nieuwe catalogusarchitectuur veronderstellen. | Bestaande Excel-catalogus en cataloguscontract verifiëren; integratie met concrete dienstmomenten |

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

## BL-19 — Zelfstandig No-showmanagement (26 oktober 2026)

**Status:** BL-19 toegekend op 26 oktober 2026; functionele richting aangevuld, nog niet ontworpen of geïmplementeerd. Onderdeel van prototype v0.5.

**Plaats in de navigatie:** afzonderlijke functie **No-showmanagement** onder **Ledendiensten & Vrijwilligersbeleid**, los van **Ledendienst Planning**. Verplaats de bestaande No-showbediening uit Ledendienst Planning/Kandidaten; hergebruik bestaande registratie-, intrekkings- en historiefuncties zonder verlies van gegevens.

**Functie 1 — No-show registreren:** de planner kiest een verstreken periode vóór vandaag, haalt de daadwerkelijk in Sportlink ingeroosterde ledendiensten via de Vrijwilligers API op en selecteert daaruit de betreffende persoon en dienst om een No-show vast te leggen. Niet-ingeroosterde personen mogen niet worden geregistreerd. Historische bronraadpleging mag de actieve planningssessie, actuele broncontext of tijdelijke DVK-indelingen niet vervangen of verstoren. Onderzoek in het functionele ontwerp hoe dit samengaat met de bestaande actieve-bron-/periodecontroles.

**Functie 2 — No-shows beheren en analyseren:** overzicht van registraties **over alle seizoenen**, met het huidige seizoen als standaardfilter en filters op seizoen, persoon en status. Toon ook ingetrokken registraties en behoud de volledige historie. Maak herhaald gedrag inzichtelijk door per lid het aantal **niet-ingetrokken** No-shows in het geselecteerde seizoen en over meerdere seizoenen te tonen. Ingetrokken No-shows blijven raadpleegbaar maar tellen niet mee als geldige No-show. Analyse is signalerend en leidt niet zelfstandig tot nieuwe sancties; bestaand CKC-beleid blijft leidend.

**Acceptatie:** beide functies zijn afzonderlijk herkenbaar; een geldige historische Sportlink-inroostering kan worden geregistreerd; intrekking en historie blijven werken; overzichten over meerdere seizoenen onderscheiden actieve en ingetrokken registraties; bestaande planning blijft onaangetast; ongeldige of mislukte bronophaalacties wijzigen geen bestaande toestand. Geen Sportlink-writeback.

## BL-20 — Weekendfilter op teamspeeldag bij vrijwilligersvoorstellen (26 oktober 2026)

**Status:** BL-20 toegekend op 26 oktober 2026; nog niet ontworpen of geïmplementeerd. Onderdeel van prototype v0.5.

**Doel:** gebruik de speeldag van het team in de Teams-export om kandidaten/voorstellen voor ledendiensten in het weekend te filteren. **Spelers van zondagteams niet aanbieden op zaterdag; spelers van zaterdagteams niet aanbieden op zondag.** Op de eigen weekenddag is deze specifieke filter geen belemmering. Voor diensten op maandag t/m vrijdag geldt deze restrictie niet.

**Afbakening:** pas de filter toe bij het samenstellen van vrijwilligerskandidaten en voorstellen; overige bestaande geschiktheids-, prioriteits- en capaciteitsregels blijven behouden. Verifieer vóór implementatie de feitelijke Teams-exportkolom en betekenis, de koppeling van personen aan teams, en de afhandeling van ontbrekende of onbekende speeldagen en niet-spelende leden. Een speler hoort volgens het CKC-uitgangspunt niet in twee teams voor te komen. Als een speler toch zowel aan een zaterdagteam als een zondagteam gekoppeld is, wordt die speler door deze speeldagfilter op **beide weekenddagen toegestaan** (niet uitgesloten); dit is een expliciete uitzondering, geen stilzwijgende datacorrectie. Geen aannames over ontbrekende bronwaarden.

**Acceptatie:** zondagteamspelers ontbreken in zaterdagvoorstellen, zaterdagteamspelers ontbreken in zondagvoorstellen; de omgekeerde eigen-speeldagcombinaties worden door deze filter niet uitgesloten; doordeweekse voorstellen blijven ongewijzigd. Tests dekken expliciet ook de dubbele teamkoppeling (zaterdag én zondag: op beide dagen toegestaan) en de nog vast te leggen behandeling van ontbrekende bronwaarden.

## BL-21 — Versieaanduiding op het DVK-hoofdscherm (26 oktober 2026)

**Status:** BL-21 toegekend op 26 oktober 2026; uitvoeren bij de eerstvolgende geschikte code-update, niet als onderdeel van PR #46 (BL-18).

**Wens:** toon direct onder de titel `CKC Digitaal Verenigingskantoor (DVK)` een kleine, subtiele aanduiding van de daadwerkelijk actieve applicatieversie, bijvoorbeeld `PR #46 (BL-18)` tijdens de acceptatie van die versie. Zo is bij lokaal testen direct zichtbaar welke codeversie draait.

**Uitwerking:** werk de aanduiding bij elke nieuwe versie bij; geef waar praktisch mogelijk de voorkeur aan een centraal beheerde of automatisch afgeleide versie-identificatie in plaats van losse handmatige tekst. Zorg dat de aanduiding overeenkomt met de werkelijk gestarte versie, ook bij gebruik van verschillende Git-branches/worktrees. Geen wijziging in de functionele werking.

**Acceptatie:** versieaanduiding staat leesbaar maar onopvallend onder de hoofdtitel; bij een volgende versie is zichtbaar dat de identificatie mee verandert. Bestaande schermwerking blijft ongewijzigd.

## BL-22 — Onderhoudbare CKC-beleidsregels voor taakplichtcontrole (26 oktober 2026)

**Status:** nieuwe functionele wens voor prototype v0.5; nog niet technisch geïnventariseerd, ontworpen of geïmplementeerd. Eerst de bestaande implementatie en configuratie onderzoeken; scope en planning daarna gericht vaststellen.

**Doel:** de CKC-beleidsregels voor het afleiden van de verwachte taakplicht afzonderlijk inzichtelijk, reviewbaar en eenvoudig onderhoudbaar maken, zonder dat voor gewone beleidswijzigingen onnodig Python-programmacode aangepast hoeft te worden.

**Leidende ontwerpkeuze:** **zo licht en simpel mogelijk**, passend binnen de bestaande Python-architectuur. **Geen nieuw rules-engineproduct, apart platform of externe tool uitsluitend voor deze beleidsregels.** Onderzoek eerst welke regels en functiemappings al configureerbaar zijn, welke nog in Python zijn vastgelegd en welke minimale scheiding zinvol is. Een leesbaar, versiebeheerd configuratiebestand (bijvoorbeeld YAML of JSON) met beperkte bestaande Python-verwerking is een mogelijke uitkomst, **geen vooraf opgelegde technische oplossing**. Een nieuw onderhoudsscherm is niet vereist.

**Functionele randvoorwaarden:**
- De bestaande, functioneel geaccepteerde CKC-beleidsregels en taakplichtuitkomsten blijven behouden; wijzigingen aan het beleid zijn geen onderdeel van deze technische onderhoudbaarheidsverbetering.
- De taakplichtcontrole blijft de verwachte taakplicht uit bronfeiten en CKC-beleid afleiden, de toegepaste vrijstellingsgrond verklaren en afwijkingen ten opzichte van de Sportlink-registratie signaleren.
- **Ledendienst Planning gebruikt de in Sportlink geregistreerde taakplicht als leidende kandidatenbasis.** De regelconfiguratie mag geen afzonderlijke uitzonderingsadministratie of concurrerende taakplichtwaarheid voor de planning creëren (zie BL-05 en BL-17).
- Maak regels en mappings reviewbaar, traceerbaar en met gerichte regressietests controleerbaar. Vermijd onnodige abstrahering, migratie of nieuwe afhankelijkheden.

**Eerstvolgende stap:** gerichte technische inventarisatie van de huidige Python-implementatie, bestaande configuratie, beleidsregels en tests; daarna een minimaal wijzigingsvoorstel met expliciete acceptatiecriteria voorleggen vóór implementatie.

## BL-23 — In- en uitklapbare rubrieken Ledendienst Planning (27 oktober 2026)

**Status:** nieuwe UI-wens voor prototype v0.5; nog niet geïmplementeerd.

**Wens:** maak de vijf bestaande rubrieken **Instellingen, Databronnen, Diensten, Kandidaten en Wedstrijden** afzonderlijk in- en uitklapbaar. Bij het openen van het scherm Ledendienst Planning zijn alle vijf standaard **ingeklapt**: alleen de rubrieknamen zijn zichtbaar. De planner kan één of meerdere rubrieken naar keuze openklappen, zonder dat het openen van de ene rubriek andere automatisch sluit.

**Randvoorwaarden en acceptatie:** behoud de in BL-18 geaccepteerde volgorde, inhoud, gegevens, waarschuwingen en functionaliteit. Dit wijzigt bewust de eerdere BL-18-startstand waarin Wedstrijden standaard uitgeklapt was; de nieuwe standaard is dat **alle vijf rubrieken ingeklapt** starten. Geen wijziging van onderliggende planning, selectie, bronverwerking of gegevensopslag. Controleer lokaal dat elke rubriek onafhankelijk werkt en dat bestaande functies na openklappen bereikbaar blijven.



## BL-24 — Compleet overzicht Bronstatus en actualiteit (27 oktober 2026)

**Status:** nieuwe UI-wens voor prototype v0.5; nog niet onderzocht of geïmplementeerd. Voorlopig opgenomen in de open documentatie-PR #52, die pas na gezamenlijke backlogreview wordt gemerged.

**Aanleiding:** in de sectie **Databronnen** toont de tabel **Bronstatus en actualiteit** momenteel alleen `Sportlink Vrijwilligers`. Dat is onlogisch bij een overzicht dat bronstatus en actualiteit pretendeert te tonen: **alle relevante bronnen, of geen onvolledig overzicht**.

**Gewenste werking:** toon consequent **alle gegevensbronnen die Ledendienst Planning gebruikt**, zowel de API-bronnen **Sportlink Vrijwilligers** en **Sportlink Programma** als de relevante lokale CSV-bronnen. Vermeld per bron, voor zover bekend, de beschikbaarheids-/laadstatus, datum van ophalen of importeren en eventuele waarschuwingen. Toon ook bronnen die nog niet geladen of beschikbaar zijn, met een eerlijke status in plaats van ze stilzwijgend weg te laten. Vermijd verzonnen ophaaltijden of schijnzekerheid.

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

**Prioriteit / plek:** eerste afgebakende vervolgproef na v0.5; pilot pas na positief haalbaarheidsbesluit. Zie [prototypeplanning](DVK-PROTOTYPE-PLANNING.md) en [productieroadmap](PRODUCTIE-ROADMAP.md). Exact releasenummer, datum, capaciteit en onderhoudseigenaar zijn nog te besluiten.

## Gegevensintegraties als afzonderlijke ontwikkelstappen

De **Vrijwilligers API** en **Programma API** zijn noodzakelijke bouwstenen voor Stap 3 Planning. Ze staan als aparte acceptatiestappen in [DVK-PROTOTYPE-PLANNING.md](DVK-PROTOTYPE-PLANNING.md), niet als verondersteld geheel nieuwe backlogfunctionaliteit. De Vrijwilligers API is via PR #38 lokaal geaccepteerd. Voor Programma zijn teamnaamkoppeling en datum-/tijdverwerking via [PR #41](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/41) lokaal geaccepteerd (141/141 gekoppelde operationele wedstrijden). De operationele schermintegratie en zichtbaarheid van wedstrijden zijn inmiddels eveneens functioneel geaccepteerd (BL-18/PR #46). **De Programma API-integratie is afgerond; geen afzonderlijke ontwikkelstap meer.** Het gebruik van wedstrijd- en teamgegevens in nieuwe kandidaatselectieregels, waaronder de teamspeeldagfilter, is een afzonderlijke backlogwens; geen heropening van de Programma API-integratie. [PR #42](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/42) standaardiseert de vijf lokale CSV-exportpaden; de standaardlocatie voor Teams.csv is lokaal functioneel gecontroleerd. Eerst de actuele adapters, broncontracten en werkelijke integratiestatus verifiëren; geen duplicatie.

## Niet in de backlog

Voormalig **BL-12 — Integrale acceptatie prototype v0.5** is een **implementatie-/acceptatiemijlpaal**, geen functionele backlogwens. Deze staat daarom in de [prototypeplanning](DVK-PROTOTYPE-PLANNING.md).

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
