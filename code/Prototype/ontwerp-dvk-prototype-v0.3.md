# Functioneel Ontwerp DVK Prototype v0.3
## Werkstroom Ledendiensten – Fase 1: Signaleren en voorstellen

**Versie:** v0.3  
**Status:** kandidaat-definitief functioneel ontwerp vóór implementatie

## 1. Doel en scope

Prototype v0.3 bouwt voort op de in Prototype v0.2 bewezen logica voor Ledendienstverplichtingen.

Waar v0.2 vooral antwoord gaf op de vraag wie volgens de CKC-regels een Ledendienstverplichting heeft en waarom, moet v0.3 aantonen dat DVK deze kennis kan inzetten in een operationele werkstroom:

> Kan DVK vanuit betrouwbare bronfeiten en expliciete CKC-beleidsregels de Ledendienstverplichtingen bepalen en bewaken en verklaarbare voorstellen voor indeling maken, terwijl de Vrijwilligerscommissie de regie en beslissingsbevoegdheid behoudt?

De functionele keten is:

**bronfeiten → taakplicht afleiden → urenpositie bepalen → openstaande dienst → geschikte kandidaten → prioritering → verklaarbaar DVK-voorstel → menselijke beoordeling → goedkeuring of afwijzing**

Buiten scope blijven automatische communicatie, reminders, no-show-opvolging, escalatie na niet verschijnen, volledig autonome inroostering en autonome beleidsvorming.

## 2. Hoofdprincipe

DVK bepaalt en verklaart wat uit feiten en vastgesteld CKC-beleid kan worden afgeleid, doet een voorstel waar een keuze nodig is, maar de Vrijwilligerscommissie neemt het operationele indelingsbesluit.

Steeds worden onderscheiden:

1. **bronfeit** — gegeven uit een gezaghebbende bron;
2. **afgeleide kwalificatie** — reproduceerbare conclusie uit bronfeiten;
3. **CKC-beleidsregel** — expliciet door CKC vastgesteld;
4. **DVK-besluit** — deterministische toepassing van feiten en regels;
5. **signalering** — constatering die menselijke aandacht vraagt;
6. **voorstel** — door DVK berekende voorkeursoptie;
7. **menselijke beslissing** — goedkeuring of afwijzing door de Vrijwilligerscommissie;
8. **vervolgactie** — handeling die uit die beslissing volgt.

DVK mag ontbrekende feiten of ontbrekend beleid nooit zelf invullen.

## 3. Actoren en verantwoordelijkheden

### 3.1 Vrijwilligerscommissie

De Vrijwilligerscommissie is operationeel proceseigenaar. Zij beoordeelt DVK-indelingsvoorstellen, keurt deze goed of af, motiveert een afwijzing, behandelt uitzonderingen en blijft eindverantwoordelijk voor de feitelijke indeling.

### 3.2 DVK

DVK leest en combineert bronfeiten, leidt taakplicht af, controleert de administratieve vastlegging in Sportlink, bepaalt de urenpositie, zoekt beschikbare diensten, bepaalt geschikte kandidaten, prioriteert kandidaten, maakt verklaarbare voorstellen en legt gebruikte feiten, regels en afleidingen vast. DVK stelt geen nieuw beleid vast.

### 3.3 Lid / jeugdlid / ouder of verzorger

Het taakplichtige lid is het administratieve subject van de Ledendienstverplichting. De feitelijke uitvoerder kan daarvan verschillen. Bij minderjarigen kan de dienst, afhankelijk van leeftijd en diensttype, worden uitgevoerd door een ouder/verzorger of door het lid zelf. De dienst blijft administratief gekoppeld aan het lidmaatschap van het jeugdlid.

### 3.4 Bronsystemen

Sportlink is een belangrijke bron voor lidmaatschap, voetbaldeelname, functies, teamindeling, taakuren, reeds ingedeelde en voldane uren, beschikbare Ledendiensten en relevante wedstrijdcontext voor zover beschikbaar.

Een bronsysteem levert feiten of administratieve registraties. DVK bepaalt daaruit, met expliciete CKC-regels, kwalificaties, beleidsgevolgen, signaleringen en voorstellen.

## 4. Functioneel proces

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

Bij jeugdleden blijft het jeugdlid administratief subject. Een ouder/verzorger kan feitelijk uitvoeren zonder dat daarvoor een afzonderlijke taakplicht ontstaat.

### Stap 5 – Geschiktheid bepalen

Voor CommissieKamer geldt voor v0.3 geen aanvullende harde geschiktheidsbeperking.

Voor bardienst geldt dat een uitvoerder jonger dan 16 jaar niet wordt voorgesteld.

DVK verzint geen ontbrekende geschiktheidsgegevens. Als geschiktheid niet betrouwbaar kan worden vastgesteld, ontstaat een signalering of onzekerheidsstatus.

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

Een voorstel bevat minimaal: openstaande dienst, taakplichtig lid, eventuele uitvoerderscategorie, A/B/C/D/E, relevante positie vorig seizoen, team, thuis/uit, relatie wedstrijdtijd-diensttijd, geschiktheid, toegepaste prioriteitsregels en eventuele onzekerheden.

Het voorstel is expliciet een **DVK-voorstel**, geen indeling.

### Stap 9 – Menselijke beoordeling

De Vrijwilligerscommissie beoordeelt het voorstel.

**Goedgekeurd:** pas dan ontstaat een daadwerkelijke indeling. De geplande uren D veranderen; voldane uren C veranderen pas nadat de dienst daadwerkelijk is uitgevoerd en als voldaan is geregistreerd.

**Afgewezen:** het voorstel wordt niet uitgevoerd en een reden is verplicht. Minimale categorieën zijn persoonlijke omstandigheid, ongeschikt voor dienst, planning, brondata onjuist en anders.

Een afwijzing doet taakplicht, geschiktheid of resterende uren niet automatisch vervallen. De dienst blijft open en DVK kan een volgend voorstel doen.

## 5. CKC-beleidsregels

Voor v0.3 gelden:

1. Een spelend lid heeft in beginsel een Ledendienstverplichting.
2. Recreatieve spelers zijn vooralsnog vrijgesteld.
3. Een erkende actieve functie kan tot vrijstelling leiden.
4. Ereleden zijn vrijgesteld.
5. Voor een gezin ontstaat niet voor ieder minderjarig kind afzonderlijk een volledige verplichting; de familielogica uit v0.2 blijft gelden.
6. De huidige norm is **10 taakuren per seizoen**. Dit aantal is een CKC-beleidskeuze.
7. Het taakplichtige jeugdlid blijft administratief subject, ook wanneer ouder/verzorger uitvoert.
8. Tot en met 14 jaar wordt de Ledendienst door ouder/verzorger uitgevoerd.
9. Van 15 tot en met 17 jaar kan ouder/verzorger of het jeugdlid zelf uitvoeren.
10. Een uitvoerder jonger dan 16 jaar wordt niet voorgesteld voor bardienst.
11. Hoe groter E, hoe hoger de prioriteit.
12. Tot 1 december wordt relevante achterstand uit het vorige seizoen meegewogen.
13. Kandidaten uit thuisspelende teams hebben praktisch de voorkeur.
14. Bij jeugd wordt bij voorkeur een met de thuiswedstrijd overlappende dienst gebruikt.
15. Bij senioren wordt bij voorkeur vóór of na de eigen thuiswedstrijd gepland.
16. Uitspelende teams worden alleen aanvullend gebruikt en niet bij tijdsoverlap.
17. Een DVK-indelingsvoorstel vereist menselijke goedkeuring.
18. Een afwijzing vereist een reden.

## 6. Bronfeiten, kwalificaties en beleidsgevolgen

### Bronfeiten

Voor zover betrouwbaar beschikbaar: persoon, geboortedatum, lidmaatschapsstatus, spelend/niet spelend, recreatief, erelidstatus, actieve functies, ouder-kindrelaties, gezinsrelaties, teamindeling, seizoen, geregistreerde A/B/C/D-waarden, beschikbare diensten, wedstrijdinformatie, datum/tijd en thuis/uit.

### Afgeleide kwalificaties

DVK leidt onder andere af: taakplichtig/niet taakplichtig, vrijstellingsgrond, administratief subject, mogelijke uitvoerderscategorie, geschikt/ongeschikt/onzeker, tijdsconflict, thuis-/uitvoorkeur, prioriteit en kandidaatstatus.

### Beleidsgevolgen

Uit kwalificaties plus CKC-beleid volgen onder andere: het aantal verplichte uren A (momenteel 10), familievrijstelling, leeftijdsregels voor uitvoering en prioriteringsregels.

Een afgeleid gegeven of beleidsgevolg moet herleidbaar zijn naar gebruikte bronfeiten en beleidsregels.

## 7. Taakplicht als expliciete DVK-afleiding

Huidige werkwijze:

**mens beoordeelt feiten → mens bepaalt taakplicht → mens past beleidsnorm toe → mens vult verplichte uren in Sportlink**

Doelbeeld v0.3:

**bronfeiten → DVK bepaalt taakplicht → DVK past CKC-beleidsnorm toe → DVK vergelijkt met Sportlink → mens behandelt afwijkingen**

Dit levert twee resultaten:

1. DVK kan zelfstandig een reproduceerbare lijst van taakplichtige leden en de daaruit volgende urenverplichting produceren.
2. DVK kan signaleren wanneer de administratieve positie in Sportlink niet overeenkomt met feiten en beleid.

V0.3 hoeft nog niet zelfstandig wijzigingen in Sportlink weg te schrijven.

## 8. Menselijk beslismoment

**DVK-voorstel ≠ CKC-besluit.**

Een voorstel kan `proposed`, `approved` of `rejected` zijn. Alleen goedkeuring mag leiden tot een daadwerkelijke geplande Ledendienst.

Auditketen:

**bronfeiten → afleidingen → beleidsregels → kandidaatselectie → DVK-voorstel → menselijke beslissing → indeling**

## 9. Verklaarbaarheid

Voor ieder voorstel moet DVK minimaal kunnen verklaren:

1. waarom het lid taakplichtig is;
2. welke bronfeiten en beleidsregels dat bepalen;
3. hoe de verplichte urennorm uit beleid volgt;
4. wat de actuele A/B/C/D/E-positie is;
5. waarom uitvoerder/categorie geschikt is;
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
Beoordeling van kandidaat voor concrete dienst: taakplicht, urenpositie, mogelijke uitvoerder, geschiktheid, wedstrijdrelatie, prioriteit, uitsluitingsreden en verklaring.

### AssignmentProposal
DVK-advies met dienst, kandidaat, rang, gebruikte regels, verklaring en status.

### HumanDecision
Menselijke beoordeling met voorstel, goedgekeurd/afgewezen, beslisser, moment en reden bij afwijzing.

### DutyAssignment
Goedgekeurde feitelijke indeling. Ontstaat pas na menselijke goedkeuring.

## 12. Acceptatiecases v0.3

### W01 – Taakplicht automatisch afgeleid
Spelend seniorlid, geen vrijstellende functie of andere vrijstellingsgrond. **Verwacht:** DVK leidt taakplicht af en past de beleidsnorm van 10 uur toe zonder handmatig taakplichtveld.

### W02 – Afwijkende Sportlink-administratie
Lid is volgens feiten en beleid 10 uur taakplichtig, maar Sportlink bevat geen verplichte taakuren. **Verwacht:** DVK signaleert het verschil en verzint geen correctie.

### W03 – Volwassen senior en thuiswedstrijd
Taakplichtige senior heeft E > 0 en speelt thuis. **Verwacht:** passende dienst vóór of na wedstrijd krijgt voorkeur.

### W04 – Jeugdlid tot en met 14 jaar
Taakplichtig jeugdlid speelt thuis. **Verwacht:** overlappende dienst kan worden voorgesteld; uitvoerdercategorie ouder/verzorger; administratie blijft op kind.

### W05 – Vijftienjarig jeugdlid en bardienst
Taakplichtig lid van 15 jaar. **Verwacht:** lid zelf niet als bardienstuitvoerder; ouder/verzorger kan wel uitvoeren.

### W06 – Zestien- of zeventienjarig lid
**Verwacht:** zowel lid zelf als ouder/verzorger kan mogelijke uitvoerder zijn; lid zelf kan voor bardienst worden voorgesteld.

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

## 13. Acceptatiecriterium

V0.3 is functioneel geslaagd wanneer reproduceerbaar wordt aangetoond dat taakplicht uit feiten en regels wordt afgeleid; de beleidsnorm afzonderlijk wordt toegepast; afwijkingen met Sportlink worden gesignaleerd; urenposities correct worden bepaald; geschikte kandidaten worden gevonden en volgens expliciete regels geprioriteerd; ieder voorstel verklaarbaar is; ontbrekende feiten of regels niet worden verzonnen; goedkeuring en afwijzing menselijke beslissingen blijven; alleen goedkeuring tot indeling leidt; en de geaccepteerde v0.2-logica behouden blijft behalve waar v0.3 deze expliciet verfijnt.

## 14. Ontwerpconclusie

V0.3 verschuift DVK van regelbeoordelaar naar eerste operationele procesondersteuner. De belangrijke nieuwe stap is dat taakplicht zelf uit feiten wordt afgeleid en de omvang van de daaruit volgende urenverplichting uit CKC-beleid volgt.

De huidige werkwijze:

**handmatig bepalen → handmatig zoeken → handmatig afwegen → handmatig indelen**

wordt:

**DVK bepaalt → DVK controleert → DVK zoekt → DVK prioriteert → DVK verklaart → mens beslist**

De Vrijwilligerscommissie houdt regie en eindverantwoordelijkheid, terwijl reproduceerbaar en arbeidsintensief administratief werk naar DVK kan verschuiven.