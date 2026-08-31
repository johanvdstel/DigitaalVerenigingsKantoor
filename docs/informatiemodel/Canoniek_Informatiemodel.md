# Canoniek CKC-informatiemodel

**Versie:** 0.5  
**Status:** Concept – canoniek logisch model  
**Datum:** 31 augustus 2026  

---

## 1. Doel van dit document

Dit document beschrijft het **canonieke informatiemodel van CKC**.

Het model legt vast welke begrippen CKC gebruikt om de werkelijkheid van de vereniging te beschrijven, welke relaties tussen die begrippen bestaan en welke informatie als bronfeit, afleiding of beleidsgevolg moet worden beschouwd.

Het model is:

- onafhankelijk van de inrichting van Sportlink, Sponsit, TapKey of andere bronsystemen;
- onafhankelijk van schermen, formulieren en technische databasevelden;
- leidend voor de ontwikkeling van het Digitaal Verenigingskantoor (DVK);
- het gemeenschappelijke begrippenkader voor processen, regels, gegevens en integraties binnen CKC.

Het canonieke model beschrijft daarmee **de werkelijkheid zoals CKC die wil begrijpen**, niet de toevallige manier waarop die werkelijkheid vandaag in afzonderlijke systemen is vastgelegd.

---

## 2. Ontwerpprincipes

### 2.1 De werkelijkheid staat centraal

Een begrip wordt opgenomen omdat het voor CKC betekenis heeft, niet omdat een bestaand systeem er toevallig een veld voor heeft.

Sportlink, Sponsit, TapKey, documenten en andere administraties zijn bronnen voor het model, maar bepalen het model niet.

### 2.2 Persoon en Organisatie zijn actoren

Een natuurlijke persoon wordt één keer als `Persoon` beschouwd.

Die persoon kan tegelijkertijd meerdere relaties en rollen binnen CKC hebben, bijvoorbeeld:

- lid;
- speler;
- trainer;
- commissielid;
- ouder/verzorger;
- vrijwilliger;
- erelid;
- lid van verdienste.

Deze rollen zijn geen afzonderlijke personen en mogen daarom niet als afzonderlijke persoonsidentiteiten worden gemodelleerd.

Niet iedere actor is een persoon. Daarom kent het model naast `Persoon` ook `Organisatie`.

Voorbeelden zijn:

- KNVB;
- gemeente;
- Sportbedrijf;
- leverancier;
- sponsor;
- externe instantie.

### 2.3 Feit, afleiding en beleid worden gescheiden

Het model maakt expliciet onderscheid tussen:

1. **bronfeiten** – wat feitelijk is geregistreerd of vastgesteld;
2. **afgeleide kwalificaties** – wat uit feiten kan worden geconcludeerd;
3. **beleidsgevolgen** – wat CKC op basis van feiten en regels verlangt, toestaat of veroorzaakt.

Voorbeeld:

> Een persoon is statutair lid en neemt deel aan een recreatief team.

Dat zijn feiten.

Daaruit kan worden afgeleid:

> Deze persoon is een recreatief voetballend lid.

Op basis van CKC-beleid kan vervolgens gelden:

> Voor deze persoon geldt contributiecategorie X.

Die drie informatielagen worden niet met elkaar vermengd.

### 2.4 Rollen worden afgeleid uit relaties

Begrippen als `Trainer`, `Speler`, `Commissielid` en `Vrijwilliger` zijn in beginsel geen zelfstandige persoonstypen.

Het zijn rollen of kwalificaties die ontstaan doordat een persoon een bepaalde relatie met CKC, een team, commissie, activiteit of functie heeft.

### 2.5 Historie is onderdeel van de werkelijkheid

Relaties en kwalificaties kunnen in de tijd veranderen.

Waar relevant kent een relatie daarom een geldigheidsperiode.

Het canonieke model moet bijvoorbeeld meerdere opeenvolgende lidmaatschapsperioden kunnen representeren, ook wanneer een bronsysteem slechts één begin- of einddatum bewaart.

### 2.6 Eén feit kan uit verschillende bronnen afkomstig zijn

Het canonieke model bepaalt **wat een gegeven betekent**.

Een afzonderlijke bronnenmapping bepaalt:

- waar het gegeven vandaag wordt geregistreerd;
- welk systeem voor dat gegeven leidend is;
- welke gegevens ontbreken;
- welke gegevens door het DVK zelf moeten worden beheerd.

---

## 3. Kernstructuur

Op het hoogste niveau onderscheidt het canonieke model de volgende domeinen:

```text
CKC
│
├── Actor
│   ├── Persoon
│   └── Organisatie
│
├── Relatie
│   ├── Lidmaatschap
│   ├── Ouder-/verzorgerrelatie
│   └── Organisatierelatie
│
├── Voetbal
│   ├── Team
│   ├── Spelersdeelname
│   └── Teamfunctie
│
├── Verenigingsorganisatie
│   ├── Functie
│   ├── Commissie
│   └── Commissierelatie
│
├── Vrijwilligerswerk
│   ├── Taak
│   ├── Taakvervulling
│   └── Taakuren
│
├── Waardering
│   ├── Erelidmaatschap
│   └── Lid van verdienste
│
├── Bestuur, bevoegdheid & mandaat
│   ├── Bestuursorgaan
│   ├── Bestuursfunctie
│   ├── Verantwoordelijkheid
│   ├── Bevoegdheid
│   ├── Mandaat / delegatie
│   └── Bevoegdheidstoekenning
│
├── Autorisatie & toegang
│   ├── Beschermd object
│   ├── Recht / permissie
│   ├── Autorisatiegroep
│   └── Autorisatietoekenning
│
└── Commerciële relatie
```

Deze structuur is conceptueel. Zij schrijft nog geen fysieke database-indeling voor.

Begrippen zoals `Bardienst` worden bewust niet in dit hoofdoverzicht opgenomen. Een bardienst is een concreet taaktype binnen het domein Vrijwilligerswerk en geen zelfstandig hoofddomein.

Ook `Ledendienst` staat niet als zelfstandig hoofddomein in deze structuur. Ledendienst is primair een beleidsregime dat op basis van feiten en CKC-beleidsregels leidt tot verplichtingen, vrijstellingen en andere beleidsuitkomsten.

---

## 4. Persoon

### 4.1 Definitie

Een `Persoon` is een natuurlijke persoon die voor CKC relevant is of is geweest.

Een persoon hoeft geen lid te zijn.

Voorbeelden:

- huidig lid;
- oud-lid;
- ouder/verzorger;
- vrijwilliger;
- contactpersoon van een sponsor;
- vertegenwoordiger van een leverancier of andere organisatie.

### 4.2 Persoonsgegevens

Bij een persoon kunnen onder meer behoren:

- officiële naam;
- roepnaam/voornaam;
- tussenvoegsel;
- achternaam;
- geboortedatum;
- geslacht, voor zover functioneel noodzakelijk;
- contactgegevens;
- adresgegevens;
- betaalgegevens.

Welke gegevens verplicht zijn, is geen eigenschap van het begrip `Persoon` zelf, maar wordt bepaald door het proces en de toepasselijke beleids- of bronregels.

---

## 5. Organisatie

Een `Organisatie` is een niet-natuurlijke actor waarmee CKC een relevante relatie heeft.

Voorbeelden:

- KNVB;
- gemeente;
- Sportbedrijf;
- sponsorbedrijf;
- leverancier;
- maatschappelijke organisatie;
- externe commissie of instantie.

Een organisatie kan één of meer contactpersonen hebben. Die contactpersonen zijn afzonderlijke `Personen`.

Hierdoor hoeft het model geen kunstmatige personen te creëren voor organisaties.

---

## 6. Lidmaatschap

### 6.1 Definitie

`Lidmaatschap` beschrijft de formele relatie waarbij een persoon statutair lid van CKC is.

Een lidmaatschap heeft een geldigheidsperiode.

Een persoon kan daardoor historisch meerdere lidmaatschapsperioden hebben.

```text
Persoon
   │
   └── heeft 0..n
          │
          ▼
     Lidmaatschap
```

### 6.2 Lidmaatschap en Sportlink-lidsoort

De Sportlink-classificaties zoals:

- Bondslid;
- Verenigingslid;
- Relatie;

zijn **geen canonieke CKC-definities van lidmaatschap**.

Zij worden beschouwd als classificaties binnen het bronsysteem Sportlink.

Of iemand statutair lid van CKC is, wordt canoniek als afzonderlijk feit beschouwd.

### 6.3 Oud-lid

`Oud-lid` is geen zelfstandig persoonstype.

Het is een afgeleide kwalificatie:

> een persoon die in het verleden minimaal één lidmaatschapsperiode heeft gehad en momenteel geen actief lidmaatschap heeft.

---

## 7. Waardering en bijzondere lidstatus

CKC kan bijzondere waarderingen toekennen.

Vooralsnog worden onderscheiden:

- `Erelidmaatschap`;
- `Lid van verdienste`.

Deze worden afzonderlijk gemodelleerd van het gewone lidmaatschap.

```text
Persoon
   │
   ├── Lidmaatschap
   │
   └── Waardering
          ├── Erelidmaatschap
          └── Lid van verdienste
```

Hierdoor kan een bijzondere waardering worden vastgelegd zonder deze te vermengen met voetbaldeelname, functies of contributieregels.

---

## 8. Ouder-/verzorgerrelatie

Een `Ouder-/verzorgerrelatie` verbindt twee personen.

```text
Persoon A
   │
   └── ouder/verzorger van
              │
              ▼
          Persoon B
```

De relatie is expliciet en mag niet uitsluitend worden afgeleid uit bijvoorbeeld:

- hetzelfde adres;
- hetzelfde e-mailadres;
- dezelfde bankrekening;
- dezelfde achternaam.

Een minderjarig lid kan één of meerdere geregistreerde ouders/verzorgers hebben.

De ouder/verzorger hoeft zelf geen lid van CKC te zijn.

Deze relatie is onder andere relevant voor:

- communicatie;
- toestemming;
- financiële processen;
- vrijwilligers- en Ledendienstbeleid.

---

## 9. Voetbaldeelname

### 9.1 Definitie

`Voetbaldeelname` beschrijft feitelijke deelname aan voetbalactiviteiten binnen CKC.

Dit begrip wordt bewust afzonderlijk van lidmaatschap gemodelleerd.

Een persoon kan statutair lid zijn zonder te voetballen en een voetbalgerelateerde rol kan aanvullende eigenschappen hebben die niet uit het lidmaatschap zelf volgen.

### 9.2 Spelersdeelname

Een `Spelersdeelname` verbindt een persoon aan een team gedurende een bepaalde periode.

```text
Persoon
   │
   └── Spelersdeelname
              │
              ▼
             Team
```

Daarmee kan onder andere onderscheid worden gemaakt tussen:

- competitievoetbal;
- recreatief voetbal;
- verschillende teams;
- historische teamdeelname.

### 9.3 Recreatief voetbal

`Recreant`, `Oldstars`, `Vroege Vogels` en `Harry's Voetbalschool` zijn niet automatisch verschillende lidmaatschapstypen.

Canoniek geldt:

> recreatief voetbal is een vorm van voetbaldeelname.

Benamingen zoals `Oldstars`, `Vroege Vogels` en `Harry's Voetbalschool` kunnen namen van teams, groepen of activiteiten zijn.

Een eventueel afwijkend contributiebeleid voor zo'n groep is een beleidsgevolg en verandert de canonieke aard van het lidmaatschap niet.

---

## 10. Teamfunctie

Een persoon kan naast of zonder spelersdeelname een functie binnen een team vervullen.

Voorbeelden:

- trainer;
- teamleider;
- assistent-trainer;
- verzorger;
- andere teamfunctie.

Binnen de huidige CKC-beleidscontext geldt:

> een trainer van CKC is lid van CKC.

Het canonieke model hoeft daarom geen actuele CKC-situatie te ondersteunen waarin een trainer géén lid is.

De begrippen blijven logisch gescheiden:

```text
Persoon
   ├── Lidmaatschap
   └── Teamfunctie
          │
          ▼
         Team
```

Daarmee wordt voorkomen dat `Trainer` ten onrechte een soort lidmaatschap wordt.

Een spelend trainer heeft eenvoudig zowel:

- een spelersdeelname;
- een teamfunctie.

---

## 11. Functie

Een `Functie` beschrijft een structurele rol die een persoon voor CKC vervult.

Voorbeelden kunnen zijn:

- bestuursfunctie;
- ledenadministrateur;
- trainer;
- teamleider;
- commissiefunctie;
- toegangsbeheerder;
- andere structurele verenigingsfunctie.

Een functie heeft in beginsel:

- een persoon;
- een functietype;
- een beginmoment;
- eventueel een eindmoment;
- eventueel een organisatorische context.

Functies kunnen relevant zijn voor:

- bevoegdheden;
- verantwoordelijkheden;
- communicatie;
- vrijwilligerswerk;
- Ledendienstvrijstellingen;
- digitale of fysieke autorisaties.

---

## 12. Commissie

Een `Commissie` is een organisatorisch onderdeel van CKC.

Voorbeelden:

- vrijwilligerscommissie;
- kantinebeheercommissie;
- kledingcommissie;
- technische commissie;
- jeugdcommissie.

Een persoon kan gedurende een bepaalde periode lid zijn van een commissie.

```text
Persoon
   │
   └── Commissierelatie
              │
              ▼
          Commissie
```

### 12.1 Commissie en vrijwilligerswerk

Binnen CKC geldt:

> lidmaatschap van een commissie is vrijwilligerswerk.

Een commissierelatie is daarmee een feitelijke grond voor de kwalificatie dat de betreffende persoon vrijwilligerswerk voor CKC verricht.

Er hoeft geen kunstmatig onderscheid te worden gemaakt tussen een commissierol enerzijds en vrijwilligerswerk anderzijds.

De commissierelatie blijft wel afzonderlijk vastgelegd, omdat zij aanvullende betekenis heeft, bijvoorbeeld voor:

- organisatorische positie;
- communicatie;
- bevoegdheden;
- verantwoordelijkheden;
- toegangsrechten;
- eventuele Ledendienstvrijstelling.

---

## 13. Vrijwilligerswerk

### 13.1 Definitie

`Vrijwilligerswerk` is werk dat een persoon voor CKC verricht en dat door CKC wordt geaccepteerd of georganiseerd.

Binnen de huidige CKC-context wordt ervan uitgegaan dat geaccepteerd vrijwilligerswerk onder het Ledendienstbeleid kan worden erkend.

Vrijwilligerswerk kan onder andere voortkomen uit:

- een functie;
- commissielidmaatschap;
- een geplande taak;
- bardienst;
- een andere door CKC geaccepteerde activiteit.

### 13.2 Vrijwilliger als kwalificatie

`Vrijwilliger` is geen zelfstandig persoonstype en evenmin noodzakelijkerwijs een formele lidmaatschapscategorie.

Het is een kwalificatie die volgt uit het verrichten van vrijwilligerswerk.

Daarmee wordt voorkomen dat bijvoorbeeld het vrije Sportlink-veld `Status lidmaatschap = vrijwilliger` canoniek wordt geïnterpreteerd als een lidmaatschapstype.

---

## 14. Taak, taakvervulling en taakuren

### 14.1 Taak

Een `Taak` beschrijft een concrete soort of geplande eenheid van vrijwilligerswerk die voor CKC kan worden uitgevoerd.

Voorbeelden:

- bardienst;
- wedstrijdorganisatie;
- onderhoud;
- ondersteuning van een evenement;
- andere geaccepteerde verenigingswerkzaamheden.

Een `Bardienst` is daarmee geen zelfstandig hoofddomein, maar een specifiek taaktype.

### 14.2 Taakvervulling

`Taakvervulling` registreert dat een persoon een taak daadwerkelijk heeft uitgevoerd.

Daarbij kan onder andere worden vastgelegd:

- uitvoerende persoon;
- taak;
- datum/periode;
- aantal erkende taakuren;
- eventueel het lid namens wie de taak is verricht;
- status van de registratie.

Dit laatste is met name relevant wanneer een ouder een taak namens een minderjarig kind uitvoert.

Conceptueel:

```text
Taak
  │
  └── bijvoorbeeld: Bardienst
                      │
                      ▼
                 Taakvervulling
                      │
                      └── uitgevoerd door Persoon
```

### 14.3 Taakuren

`Taakuren` zijn de voor het Ledendienstbeleid erkende uren die voortkomen uit taakvervulling.

De uren zijn dus geen los persoonskenmerk.

```text
Persoon
   │
   └── voert uit
          │
          ▼
     Taakvervulling
          │
          ├── betreft → Taak
          └── levert → erkende taakuren
```

De vrijwilligerscommissie registreert en bewaakt deze uren momenteel in de vrijwilligersmodule van Sportlink.

In de toekomstige situatie kan het DVK deze registratie en/of bewaking geheel of gedeeltelijk ondersteunen.

### 14.4 Bardienst als toepassing

Bardienst is een specifieke toepassing van het generieke taakmodel.

De planning en registratie van bardiensten vindt bij CKC in Sportlink plaats.

De Voetbal.nl-app fungeert daarbij als gebruikerskanaal voor registratie en communicatie.

Eventuele eigen CKC-software voor bardiensten heeft uitsluitend een aanvullende communicatiefunctie en is **niet de primaire bron voor de bardienstplanning**.

Een persoon die een bardienst uitvoert hoeft niet noodzakelijkerwijs zelf lid te zijn.

Een ouder kan bijvoorbeeld bardienst verrichten namens een minderjarig lid.

---

## 15. Ledendienst als beleidsregime

### 15.1 Begrip

`Ledendienst` is het CKC-beleidskader waarin van bepaalde leden een bijdrage in werkzaamheden voor de vereniging wordt verlangd.

Ledendienst is daarom geen zelfstandig domeinfeit of persoonskenmerk, maar een **beleidsregime dat uit feiten en beleidsregels verplichtingen en vrijstellingen afleidt**.

Conceptueel:

```text
Bronfeiten
   │
   ├── Lidmaatschap
   ├── Leeftijd
   ├── Spelersdeelname
   ├── Functie
   ├── Commissierelatie
   ├── Ouder-/verzorgerrelatie
   └── Reeds verrichte werkzaamheden
            │
            ▼
       Beleidsregels
            │
            ▼
   Ledendienstpositie
```

### 15.2 Recht op vrijwilligerswerk

Uitgangspunt van het CKC-beleid is dat ieder lid het recht heeft om vrijwilligerswerk voor CKC te verrichten.

Vrijwilligerswerk dat door CKC wordt geaccepteerd of georganiseerd kan binnen het Ledendienstbeleid als taakvervulling worden erkend.

### 15.3 Verplichte Ledendienst

Voor daarvoor aangewezen spelende leden geldt volgens het huidige beleid een jaarlijkse Ledendienstverplichting van:

**10 taakuren.**

Of de verplichting daadwerkelijk geldt, wordt afgeleid uit de toepasselijke beleidsregels.

Het getal `10` is daarmee geen onveranderlijk kenmerk van het begrip `Lid`, maar een versieerbare beleidsparameter.

### 15.4 Minderjarige leden

Bij een minderjarig lid wordt de Ledendienst feitelijk namens het kind door een ouder/verzorger uitgevoerd.

De verplichting blijft beleidsmatig gekoppeld aan het betreffende lid.

```text
Minderjarig spelend lid
        │
        └── Ledendienstverplichting
                    │
                    ▼
             ouder/verzorger
                    │
                    ▼
               taakvervulling
```

### 15.5 Meerdere minderjarige kinderen

De ouderlijke Ledendienstverplichting geldt binnen een gezin slechts voor het eerste daarvoor in aanmerking komende minderjarige kind.

Voor jongere minderjarige broers of zussen ontstaat daardoor geen aanvullende ouderlijke taakverplichting.

Binnen de huidige Sportlink-inrichting wordt dit onder andere verwerkt via een vrijstellingsgrond die als `broederdienst` wordt aangeduid.

Canoniek wordt `broederdienst` niet als fundamenteel persoonskenmerk beschouwd, maar als:

> een beleidsmatig bepaalde vrijstellingsgrond die volgt uit de gezins-/ouderrelaties en de Ledendienstpositie van een ander minderjarig kind.

Wanneer het oudste betreffende kind niet langer minderjarig is, kan de ouderlijke verplichting volgens de beleidsregels doorschuiven naar het volgende minderjarige kind.

### 15.6 Vrijstelling

Een lid kan zijn vrijgesteld van de normale taakurenverplichting.

Een vrijstelling heeft altijd een grond.

Voorbeelden:

- vervullen van een daarvoor kwalificerende functie;
- relevante commissie- of vrijwilligersrol;
- broederdienst;
- andere door CKC vastgestelde vrijstellingsgrond.

De vrijstelling is een beleidsgevolg en geen intrinsieke eigenschap van de persoon.

---


## 16. Bestuur, bevoegdheid & mandaat

### 16.1 Bestuursorgaan

Een `Bestuursorgaan` is een formeel organisatorisch orgaan waaraan binnen CKC bestuurlijke verantwoordelijkheid en bevoegdheid zijn toegekend.

Voor de hier beschreven autorisatieketen is het `Dagelijks Bestuur (DB)` van bijzonder belang. Het DB bestaat momenteel uit:

- voorzitter;
- penningmeester;
- secretaris;
- twee vicevoorzitters.

Het canonieke model legt vast waar bestuurlijke verantwoordelijkheid en bevoegdheid zijn belegd. Eventuele persoonlijke of wettelijke aansprakelijkheid van individuele bestuurders is een juridische kwalificatie en wordt niet als zelfstandig canoniek gegeven afgeleid zonder daarvoor geldende juridische grondslag.

### 16.2 Bestuursfunctie en verantwoordelijkheid

Een `Bestuursfunctie` is een functie binnen een bestuursorgaan.

`Verantwoordelijkheid` beschrijft het domein waarvoor een bestuursorgaan of functie bestuurlijk verantwoordelijk is.

Voorbeelden zijn:

- ledenadministratie en persoonsgegevens;
- fysieke toegang;
- cameratoegang en cameragegevens;
- veldverlichting;
- kassasysteem en tarieven;
- financiële gegevens;
- uitvoering van kantine-inkoopbeleid.

Bestuurlijke verantwoordelijkheid en operationele uitvoering zijn niet hetzelfde.

### 16.3 Bevoegdheid

Een `Bevoegdheid` beschrijft wat een bestuursorgaan of functionaris namens CKC mag beslissen, beheren, uitvoeren, goedkeuren of toekennen.

Voorbeelden van handelingen zijn:

- bekijken;
- wijzigen;
- beheren;
- bedienen;
- goedkeuren;
- inkopen;
- rechten toekennen;
- rechten intrekken.

### 16.4 Mandaat / delegatie

Een `Mandaat` of `Delegatie` legt vast dat een bevoegdheid voor een bepaald domein door een bevoegde actor of bestuursorgaan aan een functie of functionaris wordt toevertrouwd.

Conceptueel:

```text
CKC
  │
  ▼
Dagelijks Bestuur
  │
  ├── bestuurlijke verantwoordelijkheid
  │
  └── mandaat / delegatie
              │
              ▼
           Functie
              │
              ▼
     operationele bevoegdheid
```

Een mandaat kan waar relevant worden begrensd door:

- domein;
- toegestane handelingen;
- geldigheidsperiode;
- voorwaarden;
- mogelijkheid tot verdere delegatie;
- verantwoordings- of auditvereisten.

### 16.5 Bevoegdheidstoekenning

Een `Bevoegdheidstoekenning` verbindt een bevoegdheid aan een functie of functionaris en maakt de herkomst van die bevoegdheid herleidbaar.

Het model moet daarmee uiteindelijk vragen kunnen beantwoorden zoals:

> Waarom mag deze persoon deze handeling uitvoeren?

Conceptueel:

```text
Persoon
  → vervult Functie
  → Functie heeft bevoegdheid
  → bevoegdheid volgt uit mandaat
  → mandaat is verleend door bevoegd bestuursorgaan
```

### 16.6 Voorbeelden binnen CKC

Voorbeelden van deze keten zijn:

- de ledenadministrateur krijgt bevoegdheden voor de ledenadministratie, inclusief toegang tot privacygevoelige persoonsgegevens;
- de TapKey-toegangsbeheerder krijgt bevoegdheden voor beheer van fysieke toegangsrechten;
- de beheerder van het camerasysteem krijgt bevoegdheden voor toegang tot en beheer van privacygevoelige camerafunctionaliteit en/of cameragegevens;
- de beheerder van de digitaal gestuurde veldverlichting krijgt bevoegdheden voor bediening en beheer van een voorziening met materiële aanschaf- en gebruikskosten;
- de voorzitter van de kantinebeheercommissie krijgt in de huidige praktijk bevoegdheden voor het digitale kassasysteem, waaronder relevante tarieven en financiële/bankgerelateerde gegevens, en geeft uitvoering aan het kantine-inkoopbeleid.

Deze voorbeelden zijn toepassingen van hetzelfde generieke canonieke patroon en worden daarom niet als afzonderlijke hoofddomeinen gemodelleerd.

---

## 17. Autorisatie & toegang

### 17.1 Doel

`Autorisatie & toegang` beschrijft de operationele rechten waarmee personen toegang krijgen tot fysieke locaties, digitale systemen, gegevens, functionaliteiten of andere beschermde middelen.

Dit domein is een uitwerking van bestuurlijke bevoegdheid en mandaat, maar valt daar niet mee samen.

Het onderscheid is:

```text
Bestuurlijke verantwoordelijkheid
        │
        ▼
Mandaat / bevoegdheid
        │
        ▼
Gewenste operationele rechten
        │
        ▼
Feitelijke autorisatietoekenning
```

### 17.2 Beschermd object

Een `Beschermd object` is iets waarop CKC toegang of gebruik afzonderlijk wil kunnen autoriseren.

Een beschermd object kan onder andere zijn:

- een fysieke locatie;
- een digitaal systeem;
- een gegevensverzameling;
- een systeemfunctie;
- een financieel middel;
- een technische installatie.

Voorbeelden:

- complexpoort;
- kleedkamers;
- materiaalhok;
- kantine;
- kledinghok;
- ledenadministratie;
- persoonsgegevens;
- camerasysteem;
- camerabeelden;
- veldverlichting;
- kassasysteem;
- tarieven;
- relevante bank- of financiële gegevens;
- TapKey-beheeromgeving.

### 17.3 Recht / permissie

Een `Recht` of `Permissie` beschrijft welke handeling op een beschermd object is toegestaan.

Voorbeelden:

- bekijken;
- wijzigen;
- beheren;
- bedienen;
- openen;
- autoriseren;
- rechten toekennen of intrekken.

Het gewenste recht volgt in beginsel uit een combinatie van:

- functie of andere rol;
- bevoegdheid of mandaat;
- CKC-beleid;
- beschermd object.

### 17.4 Autorisatiegroep

Een `Autorisatiegroep` bundelt personen en/of rechten om operationeel beheer efficiënt uit te voeren.

Voorbeelden kunnen zijn:

- bestuur;
- leden kledingcommissie;
- leden kantinebeheercommissie;
- trainers van een bepaald team.

Een autorisatiegroep is een beheermiddel. De canonieke betekenis blijft dat individuele personen op grond van hun functie, rol of mandaat bepaalde rechten behoren te hebben.

### 17.5 Autorisatietoekenning

Een `Autorisatietoekenning` legt vast welke rechten een persoon feitelijk heeft gekregen, rechtstreeks of via een autorisatiegroep.

Daarmee kan het DVK onderscheid maken tussen:

- **gewenste autorisatie**: wat iemand op grond van functie, mandaat en beleid behoort te hebben;
- **feitelijke autorisatie**: wat in het operationele systeem daadwerkelijk is toegekend.

Dat maakt controles mogelijk, bijvoorbeeld:

- een trainer is gestopt maar heeft nog toegang tot het materiaalhok;
- een nieuw commissielid behoort toegang te hebben maar heeft die nog niet;
- een voormalig beheerder heeft nog beheerrechten in een digitaal systeem;
- een functionaris beschikt over meer rechten dan uit het geldende mandaat volgt.

### 17.6 Fysieke toegang via TapKey

CKC gebruikt momenteel TapKey voor centrale digitale toegangsverlening tot het complex en onderdelen daarvan.

De technische TapKey-licentie is niet hetzelfde als een canoniek toegangsrecht.

CKC beschikt over een beperkt aantal betaalde licenties, die via logisch ingerichte groepen functioneel worden gedeeld, bijvoorbeeld door:

- leden van een commissie;
- leden van het bestuur;
- trainers van een team.

De primaire operationele registratie van deze fysieke toegang vindt plaats in TapKey.

Daarnaast bestaat een afgeleide registratie in een Excel-bestand dat in Dropbox wordt opgeslagen.

### 17.7 Andere operationele autorisaties

Hetzelfde canonieke autorisatiemodel geldt voor andere CKC-systemen en voorzieningen, waaronder:

- het camerasysteem;
- de digitaal gestuurde veldverlichting;
- het digitale kassasysteem;
- de ledenadministratie;
- andere systemen waarin gevoelige gegevens, financiële waarden of bestuurlijk relevante functies worden beheerd.

De specifieke applicatie bepaalt niet het canonieke model. Applicaties zijn uitvoerings- en bronsystemen waarin feitelijke autorisaties worden gerealiseerd.

---

## 18. Commerciële relaties

CKC onderhoudt commerciële relaties met organisaties en personen.

Voor sponsorgerelateerde informatie wordt Sponsit gebruikt als CRM.

Relevante begrippen zijn onder andere:

- sponsor;
- organisatie;
- contactpersoon;
- contract;
- factuur;
- afspraak;
- taak.

Conceptueel:

```text
Organisatie
   │
   └── Sponsorrelatie
            │
            ├── Contract
            ├── Factuur
            ├── Afspraak
            └── Taak

Persoon
   │
   └── Contactpersoon van Organisatie
```

De commerciële relatie staat los van het lidmaatschap.

Een sponsorcontact kan tegelijkertijd lid, ouder, vrijwilliger of helemaal geen andere CKC-relatie hebben.

---

## 19. Organisatierelaties

CKC kan relaties onderhouden met externe organisaties zonder dat sprake is van sponsoring.

Voorbeelden:

- KNVB;
- gemeente;
- Sportbedrijf;
- leverancier;
- maatschappelijke partner;
- tuchtinstantie.

Daarvoor wordt het generieke begrip `Organisatierelatie` gebruikt.

Een specifieke toepassing kan aanvullende eigenschappen en processen kennen.

---

## 20. Bronfeiten

Onder bronfeiten vallen gegevens die rechtstreeks zijn geregistreerd of formeel vastgesteld.

Voorbeelden:

- persoon bestaat;
- geboortedatum;
- adres;
- ouder/verzorger van;
- lidmaatschap gestart;
- lidmaatschap beëindigd;
- deelname aan team;
- functie vervuld;
- commissielidmaatschap;
- taak uitgevoerd;
- aantal geregistreerde taakuren;
- erelidmaatschap toegekend;
- sponsorcontract gesloten;
- feitelijke toegang of systeemautorisatie toegekend;
- mandaat of bevoegdheid formeel toegekend.

Bronfeiten moeten zoveel mogelijk voorzien zijn van:

- bron;
- geldigheidsperiode;
- registratiemoment;
- eventueel verantwoordelijke actor.

---

## 21. Afgeleide kwalificaties

Afgeleide kwalificaties worden berekend of geconcludeerd uit bronfeiten.

Voorbeelden:

- huidig lid;
- oud-lid;
- minderjarig lid;
- spelend lid;
- recreatief voetballend lid;
- trainer;
- spelend trainer;
- commissielid;
- vrijwilliger;
- ouder van een minderjarig spelend lid.

Een afgeleide kwalificatie wordt bij voorkeur niet als onafhankelijk bronfeit onderhouden wanneer zij betrouwbaar uit andere gegevens kan worden bepaald.

---

## 22. Beleidsgevolgen

Beleidsgevolgen ontstaan door beleidsregels toe te passen op bronfeiten en eventueel afgeleide kwalificaties.

Voorbeelden:

- contributiecategorie;
- contributiebedrag;
- Ledendienstplicht;
- aantal verplichte taakuren;
- Ledendienstvrijstelling;
- broederdienst;
- bevoegdheid;
- gewenst autorisatie- of toegangsrecht;
- operationele bevoegdheid op grond van mandaat;
- communicatieverplichting;
- vereiste goedkeuring.

Conceptueel:

```text
Bronfeiten
     │
     ▼
Afgeleide kwalificaties
     │
     +───────────────+
     │               │
     ▼               ▼
Beleidsregels ──► Beleidsgevolgen
```

Hiermee wordt voorkomen dat tijdelijke beleidskeuzes onderdeel worden van de fundamentele definitie van een persoon of lid.

---

## 23. Tijd en historie

Voor relevante relaties wordt historie expliciet ondersteund.

Dat geldt ten minste voor:

- lidmaatschap;
- teamdeelname;
- functies;
- commissierelaties;
- waarderingen waar relevant;
- ouder-/verzorgerrelaties waar relevant;
- commerciële relaties;
- Ledendienstposities en vrijstellingen;
- mandaten en bevoegdheidstoekenningen;
- autorisaties en toegangstoekenningen waar relevant.

Een beëindigde relatie wordt in beginsel niet overschreven of verwijderd, maar historisch bewaard.

Hiermee kan het DVK vragen beantwoorden zoals:

- Wanneer was iemand lid?
- Is iemand meerdere keren lid geweest?
- In welk team speelde iemand in een bepaald seizoen?
- Wanneer was iemand trainer?
- Wanneer maakte iemand deel uit van een commissie?
- Op welke grond was iemand in een bepaald seizoen vrijgesteld van Ledendienst?
- Welke toegang behoorde iemand op grond van zijn functie te hebben?
- Welke toegang was feitelijk toegekend?

---

## 24. Bronhouderschap

Het canonieke model is nadrukkelijk geen aanwijzing dat alle gegevens in één nieuw systeem moeten worden ingevoerd.

Per gegeven moet worden bepaald welk systeem bronhouder is.

De belangrijkste huidige bronnen zijn:

| Informatiedomein | Belangrijke huidige bron |
|---|---|
| Personen en leden | Sportlink |
| Voetbaldeelname | Sportlink |
| Teams en teamfuncties | Sportlink |
| Commissies/functies | Sportlink en CKC-registraties |
| Ouder-/verzorgerrelaties | Sportlink, voor zover geregistreerd |
| Ledendienstplicht/vrijstelling | Sportlink vrijwilligersmodule |
| Taakuren | Sportlink vrijwilligersmodule |
| Bardienstplanning | Sportlink |
| Bardienst gebruikersinteractie | Voetbal.nl |
| Sponsor-CRM | Sponsit |
| Fysieke digitale toegang | TapKey |
| Afgeleide registratie fysieke toegang | Excel in Dropbox |
| Camerabeheer en feitelijke camera-autorisaties | huidig camerasysteem / beheeromgeving |
| Veldverlichting en feitelijke bedieningsautorisaties | huidig digitaal veldverlichtingssysteem |
| Kassa, tarieven en feitelijke kassa-autorisaties | huidig digitaal kassasysteem |
| Bestuurlijke mandaten en bevoegdheden | CKC-besluiten, beleid en toekomstig DVK-register |
| Historische ledeninformatie | bestaande CKC-administraties, waaronder Access |
| CKC-specifieke afleidingen en beleidsuitkomsten | toekomstig DVK-register |

De precieze bron per gegeven wordt vastgelegd in het afzonderlijke **Logisch Gegevenswoordenboek & Bronnenmapping**.

---

## 25. Het DVK-register

Uit de gap-analyse volgt dat CKC behoefte heeft aan een eigen logische datalaag binnen het Digitaal Verenigingskantoor.

Dit `DVK-register` is niet bedoeld als vervanging van Sportlink, Sponsit, TapKey, camera-, veldverlichtings-, kassa- of andere gespecialiseerde bronsystemen.

Het heeft primair vier functies.

### 24.1 Canonieke samenvoeging

Gegevens uit verschillende bronnen worden samengebracht rond dezelfde canonieke begrippen.

### 24.2 Aanvulling

CKC-specifieke gegevens waarvoor geen geschikte bron bestaat, kunnen in het DVK-register worden vastgelegd.

### 24.3 Afleiding

Het DVK kan kwalificaties bepalen uit bronfeiten.

Bijvoorbeeld:

```text
geboortedatum
+ actief lidmaatschap
+ spelersdeelname
        ↓
minderjarig spelend lid
```

### 24.4 Beleidsuitvoering en controle

Het DVK kan versieerbare CKC-beleidsregels toepassen en de uitkomsten vergelijken met de operationele werkelijkheid.

Bijvoorbeeld voor Ledendienst:

```text
minderjarig spelend lid
+ ouderrelatie
+ positie broer/zus
+ functie/vrijstelling
+ Ledendienstbeleid seizoen X
        ↓
Ledendienstpositie
```

Of voor toegangsbeheer:

```text
functie / commissierelatie
+ mandaat / bevoegdheid
+ autorisatiebeleid
        ↓
gewenste rechten
        │
        ▼
vergelijking met
feitelijke systeemautorisaties
```

---

## 26. Canonieke gegevensstroom

De beoogde architectuur is conceptueel:

```text
┌──────────────────────┐
│      Sportlink       │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│       Sponsit        │
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Systemen / CKC-bronnen│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────┐
│      Canonieke DVK-laag      │
│                              │
│  • identiteit                │
│  • relaties                  │
│  • historie                  │
│  • bronherkomst              │
│  • afleidingen               │
│  • CKC-specifieke gegevens   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Beleidsregels DVK      │
│                              │
│  • contributie               │
│  • Ledendienst               │
│  • mandaat/bevoegdheid       │
│  • toegang/autorisatie       │
│  • procesregels              │
│  • bevoegdheden              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ Processen / AI / gebruikers  │
└──────────────────────────────┘
```

---

## 27. Voorbeeld: één persoon, meerdere relaties

Een persoon kan bijvoorbeeld tegelijkertijd:

- statutair lid zijn;
- in een recreatief team spelen;
- trainer van een ander team zijn;
- lid zijn van de technische commissie;
- ouder zijn van twee jeugdleden;
- vrijwilligerswerk uitvoeren;
- op grond van een functie zijn vrijgesteld van de normale Ledendiensturen;
- op grond van functies, mandaten of commissierelaties bepaalde bevoegdheden en autorisaties hebben.

Canoniek wordt dit niet vastgelegd als één complexe `lidsoort`.

Het wordt opgebouwd uit afzonderlijke feiten en relaties:

```text
Persoon
│
├── Lidmaatschap
├── Spelersdeelname ──► Recreatief team
├── Teamfunctie ──────► Trainer team X
├── Commissierelatie ─► Technische Commissie
├── Ouderrelatie ─────► Kind A
├── Ouderrelatie ─────► Kind B
├── Taakvervulling
├── Bevoegdheidstoekenning
└── Autorisatietoekenning
```

Daaruit kunnen vervolgens kwalificaties en beleidsgevolgen worden afgeleid.

Dit is een fundamenteel uitgangspunt van het canonieke model.

---

## 28. Wat bewust niet canoniek wordt gemaakt

De volgende zaken worden niet zonder meer als canoniek CKC-begrip overgenomen:

- vrije tekstvelden uit Sportlink;
- `Status lidmaatschap` als semantisch leidend veld;
- Sportlink-lidsoort als definitie van statutair lidmaatschap;
- `Oldstar` als afzonderlijk lidtype;
- `Recreant` als afzonderlijk persoonstype;
- `Vrijwilliger` als afzonderlijk lidtype;
- `Bardienst` als zelfstandig hoofddomein;
- `Broederdienst` als persoonskenmerk;
- een contributiecategorie als eigenschap van de persoon;
- een Ledendienstvrijstelling als permanente eigenschap van het lid;
- een TapKey-licentie als synoniem voor een toegangsrecht;
- applicatiebeheerder als zelfstandig persoonstype in plaats van een functie;
- feitelijke systeemrechten als synoniem voor bestuurlijke bevoegdheid.

Deze kunnen wel als bronwaarde, toepassing, afleiding, technisch middel of beleidsuitkomst relevant zijn.

---

## 29. Relatie met de andere informatiemodeldocumenten

Dit document vormt de canonieke bovenlaag van het CKC-informatiemodel.

Het moet in samenhang worden gelezen met:

1. **Personenmodel**  
   Verdiept de modellering van personen, relaties, rollen en kwalificaties.

2. **Logisch informatiemodel**  
   Werkt de logische entiteiten en onderlinge relaties verder uit.

3. **Logisch Gegevenswoordenboek & Bronnenmapping**  
   Legt per gegeven de betekenis, bron en bronhouderschap vast.

4. **Gap-analyse**  
   Vergelijkt het gewenste canonieke model met de mogelijkheden en feitelijke inrichting van de huidige bronsystemen.

De richting is steeds:

```text
Werkelijkheid CKC
      ↓
Canoniek informatiemodel
      ↓
Logisch gegevensmodel
      ↓
Gegevenswoordenboek
      ↓
Bronnenmapping
      ↓
Gap-analyse
      ↓
DVK-ontwerp
      ↓
Technische implementatie
```

---

## 30. Wijzigingen in versie 0.5

Versie 0.5 bouwt voort op versie 0.4.1 en voegt een generieke bestuurlijke autorisatieketen toe.

Belangrijkste wijzigingen:

- het hoofddomein `Bestuur, bevoegdheid & mandaat` is toegevoegd;
- het Dagelijks Bestuur is gepositioneerd als relevant bestuursorgaan voor de uiteindelijke bestuurlijke verantwoordelijkheid en bevoegdheidsverlening binnen de beschreven domeinen;
- onderscheid is aangebracht tussen bestuurlijke verantwoordelijkheid, operationele bevoegdheid en feitelijke systeemautorisatie;
- `Mandaat / delegatie` en `Bevoegdheidstoekenning` zijn als canonieke begrippen toegevoegd;
- functies kunnen bevoegdheden ontvangen die herleidbaar zijn tot een bevoegd bestuursorgaan;
- het eerdere domein `Toegang & autorisatie` is verbreed naar `Autorisatie & toegang`;
- `Beschermd object` vervangt het te smalle begrip `Toegangsobject` en omvat fysieke locaties, systemen, gegevens, functionaliteiten, financiële middelen en technische installaties;
- rechten/permissies kunnen verschillende handelingen omvatten, zoals bekijken, wijzigen, beheren, bedienen, goedkeuren en rechten toekennen;
- TapKey, camerasysteem, veldverlichting, kassasysteem en ledenadministratie zijn toepassingen van hetzelfde generieke autorisatiemodel;
- de ledenadministrateur, TapKey-beheerder, camerabeheerder, veldverlichtingsbeheerder en voorzitter van de kantinebeheercommissie zijn als voorbeelden van functiegebonden bevoegdheden opgenomen;
- het DVK kan in de toekomst gewenste rechten op grond van functie, mandaat en beleid vergelijken met feitelijk toegekende systeemrechten;
- juridische persoonlijke aansprakelijkheid van bestuurders wordt bewust niet als automatisch canoniek gevolg van bestuurslidmaatschap gemodelleerd.

---

## 31. Vervolg

Versie 0.5 is voldoende stabiel om als uitgangspunt te dienen voor de volgende ontwerpfase.

De eerstvolgende stap is niet het toevoegen van steeds meer begrippen aan het canonieke model, maar het systematisch vertalen ervan naar een **technisch realiseerbaar DVK-gegevensmodel**.

Daarbij moeten per canoniek begrip worden bepaald:

1. welke gegevens rechtstreeks uit Sportlink komen;
2. welke gegevens uit Sponsit, TapKey of andere bronnen komen;
3. welke gegevens uitsluitend in het DVK-register worden opgeslagen;
4. welke kwalificaties dynamisch worden afgeleid;
5. welke beleidsuitkomsten door de regelengine worden bepaald;
6. welke historie het DVK zelf moet bewaren;
7. welke bron- en auditinformatie noodzakelijk is;
8. waar gewenste beleidsuitkomsten met de feitelijke situatie moeten worden vergeleken.

Daarmee ontstaat de brug van het canonieke CKC-informatiemodel naar de daadwerkelijke architectuur van het Digitaal Verenigingskantoor.

---

**Einde Canoniek CKC-informatiemodel v0.5**
