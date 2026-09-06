# Functioneel Ontwerp DVK Prototype v0.3
## Werkstroom Ledendiensten – Fase 1: Signaleren en voorstellen

**Versie:** v0.3  
**Status:** kandidaat-definitief functioneel ontwerp vóór implementatie

## 1. Doel en scope

Prototype v0.3 bouwt voort op de in Prototype v0.2 bewezen logica voor Ledendienstverplichtingen.

Waar v0.2 vooral antwoord gaf op de vraag wie volgens de CKC-regels een Ledendienstverplichting heeft en waarom, moet v0.3 aantonen dat DVK deze kennis kan inzetten in een operationele werkstroom:

> Kan DVK vanuit betrouwbare bronfeiten en expliciete CKC-beleidsregels de Ledendienstverplichtingen bepalen en bewaken en verklaarbare voorstellen voor indeling maken, terwijl de Vrijwilligerscommissie de regie en beslissingsbevoegdheid behoudt?

De functionele keten is:

**bronfeiten → import/normalisatie → taakplicht afleiden → urenpositie bepalen → openstaande dienst → geschikte kandidaten → prioritering → verklaarbaar DVK-voorstel → menselijke beoordeling → goedkeuring of afwijzing**

Prototype v0.3 moet deze keten niet uitsluitend met handmatig geconstrueerde testobjecten bewijzen. Zo vroeg mogelijk worden leden, urenposities, teams, wedstrijden en diensten aangeboden via downloadbestanden met een structuur alsof deze uit Sportlink komen. Een aparte importlaag vertaalt deze bronrepresentatie naar canonieke DVK-objecten.

Daarnaast wordt zo vroeg mogelijk een eenvoudig operationeel dashboard toegevoegd waarmee de Vrijwilligerscommissie urenposities, openstaande diensten en kandidaatselecties kan bekijken en beoordelen. Het dashboard bevat geen eigen businesslogica, maar gebruikt uitsluitend de onderliggende DVK-regels en modellen.

Buiten scope blijven automatische communicatie, reminders, no-show-opvolging, escalatie na niet verschijnen, volledig autonome inroostering, autonome beleidsvorming en een rechtstreekse productie-API-koppeling met Sportlink.

## 2. Hoofdprincipe

DVK bepaalt en verklaart wat uit feiten en vastgesteld CKC-beleid kan worden afgeleid, doet een voorstel waar een keuze nodig is, maar de Vrijwilligerscommissie neemt het operationele indelingsbesluit.

Steeds worden onderscheiden:

1. **bronfeit** — gegeven uit een gezaghebbende bron;
2. **bronrepresentatie** — bijvoorbeeld een Sportlink-downloadbestand waarin bronfeiten administratief zijn vastgelegd;
3. **canoniek DVK-object** — genormaliseerde representatie binnen DVK;
4. **afgeleide kwalificatie** — reproduceerbare conclusie uit bronfeiten;
5. **CKC-beleidsregel** — expliciet door CKC vastgesteld;
6. **DVK-besluit** — deterministische toepassing van feiten en regels;
7. **signalering** — constatering die menselijke aandacht vraagt;
8. **voorstel** — door DVK berekende voorkeursoptie;
9. **menselijke beslissing** — goedkeuring of afwijzing door de Vrijwilligerscommissie;
10. **vervolgactie** — handeling die uit die beslissing volgt.

DVK mag ontbrekende feiten of ontbrekend beleid nooit zelf invullen.

De regels mogen niet afhankelijk zijn van CSV-kolomnamen, een dashboard of een specifieke Sportlink-exportvorm. Alleen de importlaag kent de vorm van de bronbestanden; de functionele regels werken op canonieke DVK-objecten.

## 3. Actoren en verantwoordelijkheden

### 3.1 Vrijwilligerscommissie

De Vrijwilligerscommissie is operationeel proceseigenaar. Zij beoordeelt DVK-indelingsvoorstellen, keurt deze goed of af, motiveert een afwijzing, behandelt uitzonderingen en blijft eindverantwoordelijk voor de feitelijke indeling.

### 3.2 DVK

DVK leest en combineert bronfeiten, normaliseert brondata, leidt taakplicht af, controleert de administratieve vastlegging in Sportlink, bepaalt de urenpositie, zoekt beschikbare diensten, bepaalt geschikte kandidaten, prioriteert kandidaten, maakt verklaarbare voorstellen en legt gebruikte feiten, regels en afleidingen vast. DVK stelt geen nieuw beleid vast.

### 3.3 Lid / jeugdlid / ouder of verzorger

Het taakplichtige lid is steeds het administratieve subject van de Ledendienstverplichting.

Voor de operationele kandidaatselectie in v0.3 geldt een eenvoudige uitvoerdersregel:

- bij een taakplichtig lid **jonger dan 18 jaar** is de uitvoerdercategorie `parent_guardian`;
- bij een taakplichtig lid **van 18 jaar of ouder** is de uitvoerdercategorie `member`.

De dienst blijft in alle gevallen administratief gekoppeld aan het taakplichtige spelende lid.

In communicatie over Ledendienstbeleid kan CKC minderjarige leden de mogelijkheid bieden om een daarvoor toegestane dienst zelf uit te voeren. Eventuele leeftijds- en dienstspecifieke beperkingen, zoals geen bardienst onder 16 jaar, behoren daarmee niet tot de kern van kandidaatselectie in Prototype v0.3.

### 3.4 Bronsystemen

Sportlink is een belangrijke bron voor lidmaatschap, voetbaldeelname, functies, teamindeling, taakuren, reeds ingedeelde en voldane uren, beschikbare Ledendiensten en relevante wedstrijdcontext voor zover beschikbaar.

Een bronsysteem levert feiten of administratieve registraties. DVK bepaalt daaruit, met expliciete CKC-regels, kwalificaties, beleidsgevolgen, signaleringen en voorstellen.

Voor Prototype v0.3 mag Sportlink-data eerst via bestanden worden aangeboden. Deze bestanden vormen een realistische simulatie van de toekomstige bronkoppeling en worden via een expliciete import-/adapterlaag verwerkt.

## 4. Functioneel proces

### Stap 0 – Brondata importeren en normaliseren

DVK moet leden, urenposities, teamindelingen, wedstrijden en openstaande diensten kunnen inlezen uit bronbestanden die functioneel representatief zijn voor Sportlink-downloads.

Voor v0.3 is CSV de voorkeursvorm voor deze eerste importgrens, omdat deze eenvoudig te inspecteren, te testen en later door echte Sportlink-downloads te vervangen is.

Minimaal worden voorzien:

- leden;
- geregistreerde taakuren A/B/C/D;
- teamlidmaatschappen;
- wedstrijden;
- beschikbare Ledendiensten.

De importlaag vertaalt bronkolommen naar canonieke DVK-objecten. De functionele regels mogen geen kennis hebben van CSV-bestandsnamen of Sportlink-specifieke kolomnamen.

### Stap 1 – Taakplicht bepalen

Op dit moment bepaalt een lid van de Vrijwilligerscommissie handmatig welke leden taakplichtig zijn, op basis van onder andere spelend lidmaatschap, functies, erelidmaatschap en broederdienst. Het resultaat wordt in Sportlink impliciet vastgelegd door verplichte taakuren in te vullen.

Taakplichtigheid is echter een **afgeleide kwalificatie** uit bronfeiten en CKC-beleid. DVK moet daarom zelfstandig kunnen bepalen of een lid taakplichtig is en waarom het lid taakplichtig of vrijgesteld is.

De omvang van de verplichting — momenteel **10 uur per seizoen** — is een **CKC-beleidskeuze**. Het getal 10 is dus geen bronfeit en geen intrinsieke eigenschap van taakplichtigheid.

De in Sportlink ingevulde verplichte uren zijn de huidige **administratieve vastlegging van de uit taakplicht en beleid volgende urenverplichting**. DVK kan deze registratie vergelijken met de eigen reproduceerbare afleiding. Bij verschil ontstaat een signalering voor menselijke beoordeling.

### Stap 2 – Urenpositie bepalen

Sportlink hanteert:

- **A – Verplicht**
- **B – Correctie**
- **C – Voldaan**
- **D – Nog ingedeeld**
- **E – Niet ingedeeld**

met:

**E = A − B − C − D**

DVK onderscheidt norm/verplichte uren, correcties, daadwerkelijk uitgevoerde uren, reeds geplande uren en nog niet afgedekte uren. Reeds ingedeelde uren tellen mee bij kandidaatselectie, maar zijn nog niet voldaan.

### Stap 3 – Openstaande Ledendienst bepalen

Voor een concrete dienst zijn minimaal nodig: identificatie, diensttype, datum, begin- en eindtijd, duur, locatie, benodigde bezetting en eventuele expliciete geschiktheidseisen.

V0.3 onderscheidt minimaal bardienst en gastheer/gastvrouw CommissieKamer.

### Stap 4 – Kandidaatpopulatie bepalen

DVK selecteert leden die taakplichtig zijn, nog niet alle uren hebben afgedekt en volgens de regels kandidaat voor de dienst kunnen zijn.

Het taakplichtige lid blijft altijd het administratieve subject. Voor minderjarige taakplichtige leden gebruikt v0.3 bij de kandidaatselectie de uitvoerdercategorie `parent_guardian`. Vanaf 18 jaar gebruikt v0.3 `member`.

Een ouder/verzorger krijgt door het uitvoeren van een dienst namens een minderjarig lid geen afzonderlijke taakplicht.

### Stap 5 – Geschiktheid bepalen

Voor Prototype v0.3 wordt geschiktheid bewust eenvoudig gehouden. De kandidaatselectie werkt primair met het taakplichtige lid als administratief subject en de uitvoerdercategorie die uit de leeftijd volgt.

Voor CommissieKamer geldt geen aanvullende harde geschiktheidsbeperking.

Leeftijds- en dienstspecifieke mogelijkheden voor het minderjarige lid om een dienst eventueel zelf uit te voeren — waaronder de beleidscommunicatie dat onder 16 jaar geen bardienst wordt uitgevoerd — worden niet als afzonderlijke kandidaatselectieregel in de kernengine gemodelleerd.

DVK verzint geen ontbrekende geschiktheidsgegevens. Als een werkelijk noodzakelijke geschiktheid niet betrouwbaar kan worden vastgesteld, ontstaat een signalering of onzekerheidsstatus.

### Stap 6 – Wedstrijdcontext meenemen

Kandidaten uit thuisspelende teams hebben de voorkeur.

Bij jeugdleden wordt bij voorkeur een dienst voorgesteld die geheel of gedeeltelijk overlapt met de thuiswedstrijd, zodat ouder/verzorger de dienst kan uitvoeren terwijl het kind speelt.

Bij senioren wordt bij voorkeur een dienst vóór of na de eigen thuiswedstrijd voorgesteld.

Kandidaten uit uitspelende teams komen pas in beeld als onvoldoende geschikte kandidaten uit thuisspelende teams beschikbaar zijn en alleen wanneer dienst en wedstrijd niet overlappen.

### Stap 7 – Kandidaten prioriteren

De actuele urenpositie is leidend:

> **Hoe groter E, het aantal nog niet ingedeelde taakuren, hoe hoger de prioriteit voor indeling.**

Iemand die de norm door voldane en geplande uren volledig heeft afgedekt, wordt niet opnieuw bovenaan geplaatst.

Tot **1 december** wordt daarnaast de relevante achterstand uit het voorgaande seizoen meegewogen. Hiermee vervalt de eerdere vereenvoudigde formulering dat uitsluitend leden met minder dan vijf gerealiseerde uren in het vorige seizoen als afzonderlijke groep worden behandeld.

De prioritering combineert actuele achterstand, relevante achterstand vorig seizoen en praktische wedstrijdcontext. De rangorde moet verklaarbaar zijn.

### Stap 8 – Indelingsvoorstel genereren

Een voorstel bevat minimaal: openstaande dienst, taakplichtig lid, uitvoerdercategorie, A/B/C/D/E, relevante positie vorig seizoen, team, thuis/uit, relatie wedstrijdtijd-diensttijd, geschiktheid, toegepaste prioriteitsregels en eventuele onzekerheden.

Het voorstel is expliciet een **DVK-voorstel**, geen indeling.

### Stap 9 – Menselijke beoordeling

De Vrijwilligerscommissie beoordeelt het voorstel.

**Goedgekeurd:** pas dan ontstaat een daadwerkelijke indeling. De geplande uren D veranderen; voldane uren C veranderen pas nadat de dienst daadwerkelijk is uitgevoerd en als voldaan is geregistreerd.

**Afgewezen:** het voorstel wordt niet uitgevoerd en een reden is verplicht. Minimale categorieën zijn persoonlijke omstandigheid, ongeschikt voor dienst, planning, brondata onjuist en anders.

Een afwijzing doet taakplicht, geschiktheid of resterende uren niet automatisch vervallen. De dienst blijft open en DVK kan een volgend voorstel doen.

### Stap 10 – Operationeel dashboard

Zodra taakplicht, urenpositie, wedstrijdcontext en kandidaatselectie beschikbaar zijn, moet een eenvoudig dashboard deze resultaten zichtbaar en hanteerbaar maken voor de Vrijwilligerscommissie.

Het eerste dashboard toont minimaal:

1. **Taakplichtigen en urenpositie** — lid, team, taakplicht/vrijstelling, A/B/C/D/E en eventuele afwijking tussen DVK-afleiding en Sportlink-registratie;
2. **Openstaande diensten** — datum, diensttype, tijden, benodigde bezetting en resterende bezetting;
3. **Kandidaatselectie per dienst** — gerangschikte kandidaten met team, E, wedstrijdcontext, uitvoerdercategorie, prioriteit, uitsluitingsredenen en verklaring.

Het dashboard is een gebruikerslaag bovenop de DVK-engine. Selectie-, prioriterings- en beleidsregels worden niet in het dashboard geïmplementeerd.

In een latere stap binnen v0.3 kan het dashboard worden uitgebreid met goedkeuren en afwijzen van voorstellen, inclusief verplichte reden bij afwijzing.

## 5. CKC-beleidsregels

Voor v0.3 gelden:

1. Een spelend lid heeft in beginsel een Ledendienstverplichting.
2. Recreatieve spelers zijn vooralsnog vrijgesteld.
3. Een erkende actieve functie kan tot vrijstelling leiden.
4. Ereleden zijn vrijgesteld.
5. Voor een gezin ontstaat niet voor ieder minderjarig kind afzonderlijk een volledige verplichting; de familielogica uit v0.2 blijft gelden.
6. De huidige norm is **10 taakuren per seizoen**. Dit aantal is een CKC-beleidskeuze.
7. Het taakplichtige jeugdlid blijft administratief subject, ook wanneer ouder/verzorger uitvoert.
8. Voor kandidaatselectie en planning geldt: **jonger dan 18 jaar → uitvoerdercategorie ouder/verzorger; vanaf 18 jaar → uitvoerdercategorie lid zelf**.
9. De mogelijkheid dat een minderjarig lid in de praktijk zelf een toegestane dienst uitvoert, wordt niet als afzonderlijke kandidaatselectieregel in v0.3 gemodelleerd.
10. Hoe groter E, hoe hoger de prioriteit.
11. Tot 1 december wordt relevante achterstand uit het vorige seizoen meegewogen.
12. Kandidaten uit thuisspelende teams hebben praktisch de voorkeur.
13. Bij jeugd wordt bij voorkeur een met de thuiswedstrijd overlappende dienst gebruikt.
14. Bij senioren wordt bij voorkeur vóór of na de eigen thuiswedstrijd gepland.
15. Uitspelende teams worden alleen aanvullend gebruikt en niet bij tijdsoverlap.
16. Een DVK-indelingsvoorstel vereist menselijke goedkeuring.
17. Een afwijzing vereist een reden.
18. De C-cases en W-cases vormen permanente functionele regressietests en blijven ook bij operationele doorontwikkeling automatisch meelopen.

## 6. Bronfeiten, kwalificaties en beleidsgevolgen

### Bronfeiten

Voor zover betrouwbaar beschikbaar: persoon, geboortedatum, lidmaatschapsstatus, spelend/niet spelend, recreatief, erelidstatus, actieve functies, ouder-kindrelaties, gezinsrelaties, teamindeling, seizoen, geregistreerde A/B/C/D-waarden, beschikbare diensten, wedstrijdinformatie, datum/tijd en thuis/uit.

Bronfeiten mogen in Prototype v0.3 via Sportlink-achtige downloadbestanden worden aangeleverd. De bestandsvorm is geen onderdeel van de beleidslogica.

### Afgeleide kwalificaties

DVK leidt onder andere af: taakplichtig/niet taakplichtig, vrijstellingsgrond, administratief subject, uitvoerdercategorie, geschikt/ongeschikt/onzeker, tijdsconflict, thuis-/uitvoorkeur, prioriteit en kandidaatstatus.

### Beleidsgevolgen

Uit kwalificaties plus CKC-beleid volgen onder andere: het aantal verplichte uren A (momenteel 10), familievrijstelling, uitvoerdercategorie op basis van meerderjarigheid en prioriteringsregels.

Een afgeleid gegeven of beleidsgevolg moet herleidbaar zijn naar gebruikte bronfeiten en beleidsregels.

## 7. Taakplicht als expliciete DVK-afleiding

Huidige werkwijze:

**mens beoordeelt feiten → mens bepaalt taakplicht → mens past beleidsnorm toe → mens vult verplichte uren in Sportlink**

Doelbeeld v0.3:

**bronfeiten → DVK importeert/normaliseert → DVK bepaalt taakplicht → DVK past CKC-beleidsnorm toe → DVK vergelijkt met Sportlink → mens behandelt afwijkingen**

Dit levert twee resultaten:

1. DVK kan zelfstandig een reproduceerbare lijst van taakplichtige leden en de daaruit volgende urenverplichting produceren.
2. DVK kan signaleren wanneer de administratieve positie in Sportlink niet overeenkomt met feiten en beleid.

V0.3 hoeft nog niet zelfstandig wijzigingen in Sportlink weg te schrijven.

## 8. Menselijk beslismoment

**DVK-voorstel ≠ CKC-besluit.**

Een voorstel kan `proposed`, `approved` of `rejected` zijn. Alleen goedkeuring mag leiden tot een daadwerkelijke geplande Ledendienst.

Auditketen:

**bronfeiten → import/normalisatie → afleidingen → beleidsregels → kandidaatselectie → DVK-voorstel → menselijke beslissing → indeling**

## 9. Verklaarbaarheid

Voor ieder voorstel moet DVK minimaal kunnen verklaren:

1. waarom het lid taakplichtig is;
2. welke bronfeiten en beleidsregels dat bepalen;
3. hoe de verplichte urennorm uit beleid volgt;
4. wat de actuele A/B/C/D/E-positie is;
5. welke uitvoerdercategorie geldt;
6. waarom de dienst praktisch past;
7. waarom deze kandidaat hoger staat dan andere kandidaten;
8. welke rol het vorige seizoen speelt;
9. welke gegevens ontbreken of onzeker zijn;
10. welke menselijke beslissing uiteindelijk is genomen.

Een voorstel zonder reproduceerbare verklaring voldoet niet aan dit FO.

## 10. Uitzonderingen die DVK niet autonoom oplost

DVK stopt of signaleert wanneer noodzakelijke brongegevens of relaties ontbreken, brongegevens elkaar tegenspreken, Sportlink-administratie niet overeenkomt met de afgeleide taakplicht/urenverplichting, geschiktheid niet betrouwbaar kan worden vastgesteld, beleidsregels conflicteren, een persoonlijke uitzondering niet in beleid staat, geen geschikte kandidaat beschikbaar is, een voorstel wordt afgewezen of nieuwe beleidsvorming nodig is.

DVK maakt van een uitzondering geen nieuwe beleidsregel.

## 11. Minimale uitbreiding logisch model v0.2

V0.2 blijft het fundament. Voor v0.3 zijn minimaal nodig:

### DutyPosition
Urenpositie per taakplichtig lid en seizoen: verplicht A, correctie B, voldaan C, ingedeeld D en niet ingedeeld E. `E = A - B - C - D`.

### DutyService
Concrete beschikbare dienst: ID, type, datum/tijd, duur, locatie, benodigde bezetting en eisen.

### TeamMembership
Relatie tussen lid en team gedurende een periode.

### Match
Wedstrijdcontext: team, datum/tijd en thuis/uit.

### CandidateAssessment
Beoordeling van kandidaat voor concrete dienst: taakplicht, urenpositie, uitvoerdercategorie, geschiktheid, wedstrijdrelatie, prioriteit, uitsluitingsreden en verklaring.

### AssignmentProposal
DVK-advies met dienst, kandidaat, rang, gebruikte regels, verklaring en status.

### HumanDecision
Menselijke beoordeling met voorstel, goedgekeurd/afgewezen, beslisser, moment en reden bij afwijzing.

### DutyAssignment
Goedgekeurde feitelijke indeling. Ontstaat pas na menselijke goedkeuring.

### ImportAdapter
Functionele grens die Sportlink-achtige bronbestanden omzet naar canonieke DVK-objecten. De adapter bevat bronmapping, maar geen beleids- of selectielogica.

### DashboardViewModel
Afgeleide presentatiestructuur voor het dashboard. Bevat uitsluitend gegevens en verklaringen uit de DVK-engine en geen zelfstandige beleidsregels.

## 12. Permanente regressiestrategie

De geaccepteerde C-cases uit Prototype v0.2 en de W-cases uit Prototype v0.3 vormen samen een blijvend functioneel contract van DVK.

Daarom gelden de volgende uitgangspunten:

1. C01–C22 blijven als vaste regressieset bestaan.
2. W01–W13 worden na acceptatie eveneens als vaste regressieset gehandhaafd.
3. Nieuwe werkstromen kunnen eigen vaste regressiesets toevoegen.
4. Alle relevante regressiesets draaien automatisch in batch mode bij wijzigingen.
5. Operationele interfaces, imports en dashboards mogen de onderliggende geaccepteerde functionele uitkomsten niet stilzwijgend wijzigen.
6. Een bewuste beleidswijziging mag een bestaande regressie alleen wijzigen wanneer die functionele wijziging expliciet is vastgesteld en in ontwerp en testcase is vastgelegd.

## 13. Acceptatiecases v0.3

### W01 – Taakplicht automatisch afgeleid
Spelend seniorlid, geen vrijstellende functie of andere vrijstellingsgrond. **Verwacht:** DVK leidt taakplicht af en past de beleidsnorm van 10 uur toe zonder handmatig taakplichtveld.

### W02 – Afwijkende Sportlink-administratie
Lid is volgens feiten en beleid 10 uur taakplichtig, maar Sportlink bevat geen verplichte taakuren. **Verwacht:** DVK signaleert het verschil en verzint geen correctie.

### W03 – Volwassen senior en thuiswedstrijd
Taakplichtige senior heeft E > 0 en speelt thuis. **Verwacht:** passende dienst vóór of na wedstrijd krijgt voorkeur; uitvoerdercategorie is het lid zelf.

### W04 – Minderjarig jeugdlid en thuiswedstrijd
Taakplichtig jeugdlid jonger dan 18 jaar speelt thuis. **Verwacht:** overlappende dienst kan worden voorgesteld; uitvoerdercategorie is ouder/verzorger; administratie blijft op het kind.

### W05 – Vijftienjarig jeugdlid
Taakplichtig lid van 15 jaar. **Verwacht:** administratief subject blijft het jeugdlid; uitvoerdercategorie voor kandidaatselectie en planning is ouder/verzorger.

### W06 – Zeventienjarig jeugdlid
Taakplichtig lid van 17 jaar. **Verwacht:** ook vlak vóór meerderjarigheid blijft het jeugdlid administratief subject en is de uitvoerdercategorie voor kandidaatselectie en planning ouder/verzorger. Vanaf 18 jaar wordt de uitvoerdercategorie het lid zelf.

### W07 – Urenpositie
A=10, B=0, C=4, D=3. **Verwacht:** E=3; DVK behandelt het lid niet alsof nog zes uur moet worden ingepland.

### W08 – Prioritering
Twee geschikte kandidaten hebben E=7 en E=3. **Verwacht:** kandidaat met E=7 krijgt, overige omstandigheden gelijk, hogere prioriteit.

### W09 – Achterstand vorig seizoen
Twee vergelijkbare kandidaten worden vóór 1 december beoordeeld; één heeft relevante achterstand vorig seizoen. **Verwacht:** deze achterstand beïnvloedt de prioritering verklaarbaar.

### W10 – Uitspelend team
Onvoldoende geschikte kandidaten uit thuisspelende teams. **Verwacht:** uitspelende kandidaat kan worden voorgesteld, maar alleen zonder tijdsoverlap.

### W11 – Goedkeuring
Vrijwilligerscommissie keurt voorstel goed. **Verwacht:** DutyAssignment ontstaat; D/E veranderen; C blijft gelijk tot uitvoering.

### W12 – Afwijzing
Vrijwilligerscommissie wijst voorstel af met reden. **Verwacht:** geen DutyAssignment; urenpositie verandert niet; dienst blijft open; volgende kandidaat kan worden beoordeeld.

### W13 – Familieverplichting
Meerdere minderjarige spelende kinderen waarvoor volgens familielogica slechts één verplichting geldt. **Verwacht:** geen dubbele gezinsverplichting of kunstmatig verdubbelde kandidaatdruk.

## 14. Acceptatie van bronimport en dashboard

Naast W01–W13 gelden voor v0.3 twee operationele acceptatie-eisen.

### I01 – Sportlink-achtige bronimport
Een representatieve set leden, taakuren, teams, wedstrijden en diensten wordt via downloadbestanden ingelezen. **Verwacht:** de importlaag levert canonieke DVK-objecten op waarop dezelfde regels reproduceerbaar werken als bij directe testfixtures.

### I02 – Dashboard gebruikt uitsluitend engine-uitkomsten
Een gebruiker selecteert een openstaande dienst in het dashboard. **Verwacht:** het dashboard toont taakplichtigen, urenpositie, kandidaatvolgorde, uitvoerdercategorie, uitsluitingsredenen en verklaringen zoals door de DVK-engine bepaald; het dashboard bevat geen afwijkende eigen selectie- of beleidslogica.

Deze twee eisen vervangen de W-regressies niet. Zij voegen een operationele acceptatielaag toe bovenop dezelfde functionele kern.

## 15. Implementatievolgorde v0.3

De voorkeursvolgorde is:

1. domeinfundament, taakplichtafleiding en `DutyPosition`; C01–C22 blijven groen; W01, W02 en W07 worden toegevoegd;
2. Sportlink-achtige CSV-importlaag en representatieve bronbestanden;
3. minderjarigen- en familielogica volgens de vereenvoudigde uitvoerdersregel; W04, W05, W06 en W13;
4. wedstrijdcontext en kandidaatselectie; W03 en W10;
5. prioritering; W08 en W09;
6. eerste operationele dashboard voor urenposities, diensten en kandidaatselectie;
7. `AssignmentProposal` en menselijke goedkeuring/afwijzing;
8. `DutyAssignment`; W11 en W12;
9. uitbreiding dashboard met goedkeuren/afwijzen;
10. geïntegreerde regressie- en operationele acceptatie over C-, W- en import/dashboardtests.

Het doel is bewust om vroeg met realistisch aangeleverde brondata en een zichtbaar selectieproces te werken, zonder de scheiding tussen bronimport, domeinlogica en gebruikersinterface op te geven.

## 16. Acceptatiecriterium

V0.3 is functioneel geslaagd wanneer reproduceerbaar wordt aangetoond dat taakplicht uit feiten en regels wordt afgeleid; de beleidsnorm afzonderlijk wordt toegepast; afwijkingen met Sportlink worden gesignaleerd; urenposities correct worden bepaald; Sportlink-achtige bronbestanden via een expliciete importlaag kunnen worden verwerkt; geschikte kandidaten worden gevonden en volgens expliciete regels geprioriteerd; ieder voorstel verklaarbaar is; de resultaten via een dashboard operationeel inzichtelijk zijn zonder businesslogica in het dashboard te dupliceren; ontbrekende feiten of regels niet worden verzonnen; goedkeuring en afwijzing menselijke beslissingen blijven; alleen goedkeuring tot indeling leidt; en de geaccepteerde v0.2-logica behouden blijft behalve waar v0.3 deze expliciet verfijnt.

## 17. Ontwerpconclusie

V0.3 verschuift DVK van regelbeoordelaar naar eerste operationele procesondersteuner. De belangrijke nieuwe stap is dat taakplicht zelf uit feiten wordt afgeleid en de omvang van de daaruit volgende urenverplichting uit CKC-beleid volgt.

Tegelijk wordt de stap gezet van uitsluitend interne testdata naar een realistische operationele keten:

**Sportlink-achtige brondata → DVK-import → canonieke objecten → regels → kandidaatselectie → dashboard → menselijke beslissing**

De huidige werkwijze:

**handmatig bepalen → handmatig zoeken → handmatig afwegen → handmatig indelen**

wordt:

**DVK importeert → DVK bepaalt → DVK controleert → DVK zoekt → DVK prioriteert → DVK verklaart → mens beslist**

De Vrijwilligerscommissie houdt regie en eindverantwoordelijkheid, terwijl reproduceerbaar en arbeidsintensief administratief werk naar DVK kan verschuiven.

De C- en W-regressies blijven daarbij het uitvoerbare functionele contract waarop ook latere operationele doorontwikkeling wordt bewaakt.
