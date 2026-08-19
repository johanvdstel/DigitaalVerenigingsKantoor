# Ledenadministratie

**Werkstroom:** LA  
**Sprint:** 0.5 – Procesontwerp  
**Status:** Concept  
**Versie:** 0.1  
**Datum:** 2026-08-19  

---

## Inhoud

1. [Doel van de werkstroom](#1-doel-van-de-werkstroom)
2. [Positionering van Sportlink](#2-positionering-van-sportlink)
3. [Afbakening van Ledenadministratie](#3-afbakening-van-ledenadministratie)
4. [Centrale procesobjecten](#4-centrale-procesobjecten)
5. [Rollen en verantwoordelijkheden](#5-rollen-en-verantwoordelijkheden)
6. [Universeel statusmodel](#6-universeel-statusmodel)
7. [Hoofdproces LA-01 – Nieuw lid aanmelden](#7-hoofdproces-la-01--nieuw-lid-aanmelden)
8. [Procesfasen Nieuw lid](#8-procesfasen-nieuw-lid)
9. [Beslismomenten Nieuw lid](#9-beslismomenten-nieuw-lid)
10. [Uitzonderingen](#10-uitzonderingen)
11. [Termijnen en herinneringen](#11-termijnen-en-herinneringen)
12. [Menselijke controlemomenten](#12-menselijke-controlemomenten)
13. [Audittrail](#13-audittrail)
14. [Communicatieprincipes](#14-communicatieprincipes)
15. [Eerste functionele procesregels](#15-eerste-functionele-procesregels)
16. [Voorlopig toestandsmodel Nieuw lid](#16-voorlopig-toestandsmodel-nieuw-lid)
17. [Werkvoorraad voor de ledenadministrateur](#17-werkvoorraad-voor-de-ledenadministrateur)
18. [Prestatie- en kwaliteitsmetingen](#18-prestatie--en-kwaliteitsmetingen)
19. [Ontwerpbesluiten voor Sprint 0.5](#19-ontwerpbesluiten-voor-sprint-05)
20. [Definitie van gereed voor proces LA-01](#20-definitie-van-gereed-voor-proces-la-01)

---

# 1. Doel van de werkstroom

De werkstroom **Ledenadministratie** ondersteunt de volledige levenscyclus van een persoon binnen CKC:

> **Van eerste aanmelding tot en met beëindiging en archivering van het lidmaatschap.**

Het Digitaal Verenigingskantoor:

- verzamelt informatie uit formulieren, e-mail, documenten en Sportlink;
- controleert gegevens op volledigheid, geldigheid en onderlinge samenhang;
- stelt handelingen en besluiten voor;
- voert toegestane administratieve handelingen uit;
- legt iedere stap vast in een audittrail;
- vraagt menselijke beoordeling wanneer een regel, uitzondering of risico dat vereist.

**De ledenadministrateur blijft eindverantwoordelijk.**

---

# 2. Positionering van Sportlink

## 2.1 Uitgangspunt

Sportlink is het officiële registratiesysteem voor:

- verenigingsleden;
- bondsleden;
- persoonsgegevens;
- lidmaatschappen;
- overschrijvingen;
- team- en functiegegevens voor zover deze daar worden beheerd;
- KNVB-gerelateerde statussen en registraties.

Het Digitaal Verenigingskantoor wordt niet onmiddellijk een vervanger van Sportlink.

Het fungeert als:

1. **procesregisseur**;
2. **controlelaag**;
3. **werkvoorraad voor medewerkers**;
4. **regel- en beslismachine**;
5. **audit- en communicatielaag**;
6. **integratiepunt** tussen website, e-mail, documenten, betalingen en Sportlink.

## 2.2 Bronverantwoordelijkheid

Per gegeven wordt vastgelegd welk systeem leidend is.

| Gegeven | Voorlopige bron |
| --- | --- |
| Officiële lidstatus | Sportlink |
| KNVB-relatie- of bondsgegevens | Sportlink |
| Naam en geboortedatum | Sportlink, na verificatie |
| Adres en contactgegevens | Sportlink |
| Aanmeldingsformulier | Digitaal Verenigingskantoor |
| Ingeleverde documenten | Digitaal Verenigingskantoor |
| Processtatus | Digitaal Verenigingskantoor |
| Interne notities en beslissingen | Digitaal Verenigingskantoor |
| Communicatiehistorie | Digitaal Verenigingskantoor |
| Contributiestatus | Financieel systeem, nader te bepalen |
| Vrijwilligersverplichtingen | Vrijwilligersadministratie, nader te koppelen |

> **Principe:** bij tegenstrijdige gegevens maakt het systeem niet zelfstandig een willekeurige keuze. Het opent een controleactie.

---

# 3. Afbakening van Ledenadministratie

De werkstroom bestaat uit acht hoofdprocessen.

## LA-01 – Nieuw lid aanmelden

Van ontvangen aanmelding tot een volledig en actief geregistreerd lid.

## LA-02 – Bestaand lid wijzigen

Wijzigingen in bijvoorbeeld:

- adres;
- telefoonnummer;
- e-mailadres;
- naam;
- betaalgegevens;
- contactpersoon;
- lidmaatschapstype;
- team- of functiegegevens.

## LA-03 – Lidmaatschap beëindigen

Van opzegging of voorgenomen uitschrijving tot definitieve beëindiging en archivering.

## LA-04 – Overschrijving naar CKC

Een speler komt van een andere vereniging naar CKC.

## LA-05 – Overschrijving van CKC

Een speler vertrekt naar een andere vereniging.

## LA-06 – Jaarlijkse gegevenscontrole

Periodieke controle of persoonsgegevens, contactgegevens en lidmaatschapsgegevens nog juist zijn.

## LA-07 – Signalering en herstel van afwijkingen

Bijvoorbeeld:

- ontbrekende gegevens;
- dubbele personen;
- ongeldige adressen;
- onbestelbare e-mail;
- inconsistente lidstatus;
- verlopen documenten;
- verschil tussen Sportlink en andere systemen.

## LA-08 – Bijzondere lidmaatschapsbesluiten

Bijvoorbeeld:

- tijdelijke opschorting;
- royement;
- overlijden;
- dispensatie;
- ereleden;
- niet-spelende leden;
- bijzondere contributieregelingen.

> Deze processen gebruiken allemaal hetzelfde centrale lid-dossier en dezelfde basisprincipes.

---

# 4. Centrale procesobjecten

## 4.1 Persoon

De natuurlijke persoon waarop gegevens betrekking hebben.

Een persoon kan bestaan voordat er sprake is van een lidmaatschap, bijvoorbeeld als:

- kandidaat-lid;
- ouder of verzorger;
- vrijwilliger;
- contactpersoon;
- oud-lid.

## 4.2 Lidmaatschap

De formele relatie tussen een persoon en CKC.

Een persoon kan in de tijd meerdere lidmaatschappen hebben, maar ieder lidmaatschap heeft een eigen:

- begindatum;
- einddatum;
- categorie;
- status;
- reden van wijziging of beëindiging.

## 4.3 Procesdossier

Een dossier voor één concrete administratieve zaak, bijvoorbeeld:

- nieuwe aanmelding;
- adreswijziging;
- opzegging;
- jaarlijkse controle.

Eén persoon kan meerdere procesdossiers hebben.

## 4.4 Taak

Een concrete handeling die door het systeem of een medewerker moet worden uitgevoerd.

Voorbeelden:

- controleer identiteitsgegevens;
- vraag ontbrekend telefoonnummer op;
- beoordeel mogelijke dubbele registratie;
- verwerk lid in Sportlink;
- bevestig inschrijving.

## 4.5 Besluit

Een expliciete keuze met:

- beslisser;
- datum en tijd;
- gebruikte gegevens;
- toepasselijke regel;
- uitkomst;
- eventuele motivering.

## 4.6 Gebeurtenis

Een onveranderbare registratie van iets dat heeft plaatsgevonden.

Voorbeelden:

- formulier ontvangen;
- e-mail verzonden;
- geboortedatum gewijzigd;
- controle mislukt;
- lid geactiveerd;
- medewerker heeft uitzondering goedgekeurd.

---

# 5. Rollen en verantwoordelijkheden

## Kandidaat-lid of lid

Levert gegevens aan en bevestigt waar nodig de juistheid daarvan.

## Ouder of verzorger

Handelt voor een minderjarig lid en geeft vereiste toestemmingen.

## Ledenadministrateur

Is proceseigenaar en eindverantwoordelijk voor administratieve juistheid.

## Technische commissie of jeugdcommissie

Beoordeelt waar nodig:

- plaatsingsmogelijkheden;
- leeftijdscategorie;
- teamindeling;
- wachtlijst;
- voetbaltechnische toelating.

Deze commissie bepaalt niet zelfstandig de officiële lidstatus.

## Penningmeester of financiële administratie

Beoordeelt financiële uitzonderingen en verwerkt financiële gegevens.

## Bestuur

Beslist over bijzondere gevallen zoals:

- royement;
- uitzonderingen op beleid;
- bijzondere lidmaatschappen;
- conflicten of bezwaar.

## Digitaal Verenigingskantoor

Voert geautomatiseerde controles en toegestane acties uit, maar neemt alleen besluiten waarvoor expliciet een regel en bevoegdheid zijn vastgelegd.

## Sportlink

Is een extern kernsysteem, geen menselijke actor. Handelingen in Sportlink worden wel als afzonderlijke processtappen geregistreerd.

---

# 6. Universeel statusmodel

Iedere zaak binnen de ledenadministratie gebruikt zoveel mogelijk dezelfde hoofdstatussen.

| Status | Betekenis |
| --- | --- |
| **Ontvangen** | Een verzoek, formulier, signaal of wijziging is binnengekomen. |
| **In controle** | Het systeem controleert volledigheid, formaat, plausibiliteit, duplicaten en regels. |
| **Wacht op aanvrager** | Er ontbreken gegevens of documenten die de aanvrager moet leveren. |
| **Wacht op interne beoordeling** | Een commissie, administrateur, penningmeester of bestuurder moet een oordeel geven. |
| **Gereed voor verwerking** | Alle vereiste gegevens, controles en besluiten zijn aanwezig. |
| **In verwerking** | De wijziging wordt in Sportlink of een ander bronsysteem uitgevoerd. |
| **Controle na verwerking** | Het systeem controleert of de verwerking correct en volledig is doorgevoerd. |
| **Afgerond** | De zaak is correct verwerkt en de betrokkenen zijn geïnformeerd. |
| **Afgewezen** | Het verzoek wordt niet uitgevoerd. De reden en beslisser zijn vastgelegd. |
| **Geannuleerd** | De aanvrager of vereniging heeft het proces ingetrokken voordat het was afgerond. |
| **Geblokkeerd** | Het proces kan niet verder door een technisch probleem, conflicterende registratie of afhankelijkheid. |

> Niet iedere overgang tussen deze statussen is toegestaan. De toegestane overgangen worden later in de procesmachine vastgelegd.

---

# 7. Hoofdproces LA-01 – Nieuw lid aanmelden

## 7.1 Startmoment

Het proces begint wanneer CKC een aanmelding ontvangt via een toegestaan kanaal.

**Voorkeurskanaal:**

- digitaal aanmeldingsformulier op de website.

**Mogelijke alternatieve kanalen:**

- e-mail;
- papieren formulier;
- mondeling verzoek dat door een medewerker wordt ingevoerd;
- import uit een extern formulier.

Iedere aanmelding wordt omgezet in één procesdossier.

## 7.2 Gewenst eindresultaat

Het proces is geslaagd wanneer:

- de persoon uniek is geïdentificeerd;
- alle verplichte gegevens zijn gecontroleerd;
- eventuele toestemmingen zijn vastgelegd;
- interne toelating of plaatsing is beoordeeld;
- de juiste registratie in Sportlink is uitgevoerd;
- de registratie na verwerking is gecontroleerd;
- het lid of de verzorger een bevestiging heeft ontvangen;
- vervolgacties zijn gestart;
- de volledige audittrail beschikbaar is.

---

# 8. Procesfasen Nieuw lid

## Fase A – Aanmelding ontvangen

### Systeemhandelingen

1. Maak een uniek procesnummer aan.
2. Sla het oorspronkelijke formulier onveranderd op.
3. Registreer:
   - ontvangstdatum;
   - ontvangstkanaal;
   - indiener;
   - technische bron;
   - versie van het gebruikte formulier.
4. Stuur een ontvangstbevestiging.
5. Zet de status op **Ontvangen**.

### Controles

- Is de inzending technisch leesbaar?
- Is toestemming voor verwerking vastgelegd?
- Is bij een minderjarige een ouder of verzorger bekend?
- Is er voldoende informatie om de persoon te identificeren?

Een technisch onleesbare of evident lege inzending wordt niet als normale aanmelding verwerkt, maar als uitzondering geregistreerd.

---

## Fase B – Volledigheidscontrole

Het systeem controleert of alle verplichte gegevens aanwezig zijn.

### Voorlopig verplichte gegevens

- voornaam of voornamen;
- achternaam;
- geboortedatum;
- geslacht of relevante registratiecategorie, voor zover vereist;
- adres;
- postcode;
- woonplaats;
- e-mailadres;
- telefoonnummer;
- gewenste lidmaatschapsvorm;
- gewenste ingangsdatum;
- akkoord met toepasselijke voorwaarden;
- benodigde privacyverklaringen;
- gegevens ouder of verzorger bij minderjarigheid.

Welke velden juridisch, sporttechnisch of beleidsmatig verplicht zijn, wordt later in de gegevenscatalogus vastgelegd.

### Uitkomsten

**Volledig:** verder naar identificatie en duplicaatcontrole.

**Onvolledig maar herstelbaar:** status wordt **Wacht op aanvrager**.

**Onvoldoende om contact op te nemen:** taak voor de ledenadministrateur.

### Automatische communicatie

De aanvrager ontvangt geen algemene melding als *formulier incompleet*, maar een concrete lijst:

- wat ontbreekt;
- waarom dit nodig is;
- hoe het kan worden aangevuld;
- vóór welke datum reactie gewenst is.

---

## Fase C – Identiteits- en duplicaatcontrole

Het systeem zoekt of de persoon al bekend is.

### Zoekcriteria

Een combinatie van:

- volledige naam;
- geboortedatum;
- postcode en huisnummer;
- e-mailadres;
- telefoonnummer;
- Sportlink-relatiegegevens;
- eerdere lidmaatschappen;
- ouder- of verzorgerrelaties.

### Mogelijke uitkomsten

#### Geen overeenkomst gevonden

De persoon wordt behandeld als nieuwe relatie.

#### Exacte overeenkomst gevonden

Het systeem maakt geen nieuw persoonrecord aan. De aanmelding wordt gekoppeld aan de bestaande persoon.

#### Mogelijke overeenkomst gevonden

Bijvoorbeeld dezelfde naam en geboortedatum, maar een ander adres.

De zaak gaat naar **Wacht op interne beoordeling**.

#### Meerdere mogelijke overeenkomsten

De zaak wordt geblokkeerd voor automatische verwerking.

> **Belangrijk principe:** het systeem mag bij twijfel nooit automatisch twee personen samenvoegen en evenmin zonder controle een tweede persoon aanmaken.

---

## Fase D – Inhoudelijke toelatingscontrole

Afhankelijk van het type lidmaatschap worden aanvullende controles uitgevoerd.

### Voor een spelend lid

Mogelijke controles:

- leeftijdscategorie;
- beschikbaar passend team;
- wachtlijst;
- overschrijvingssituatie;
- bestaande KNVB-registratie;
- vereiste toestemming;
- eventuele verenigingsregels;
- gewenste speeldag of teamcategorie.

### Voor een niet-spelend lid

Mogelijke controles:

- juiste lidcategorie;
- contributiecategorie;
- eventuele functie of rol;
- benodigde interne goedkeuring.

### Voor een vrijwilliger zonder regulier lidmaatschap

Er moet worden bepaald of deze persoon:

- als lid;
- als verenigingsfunctionaris;
- of uitsluitend in een intern relatiesysteem

wordt geregistreerd.

### Uitkomsten

- automatisch toelaatbaar;
- interne goedkeuring vereist;
- wachtlijst;
- aanvullende informatie vereist;
- afwijzing voorgesteld.

> Het systeem mag alleen automatisch toelaten wanneer alle toepasselijke beleidsregels eenduidig zijn.

---

## Fase E – Besluitvorming

Alle vereiste beslissingen worden verzameld.

Een besluit bevat minimaal:

- de vraag waarover is besloten;
- de uitkomst;
- de beslisser;
- de datum en tijd;
- de gebruikte regel of bevoegdheid;
- eventuele toelichting.

### Voorbeelden

- Technische commissie: plaatsing mogelijk.
- Ledenadministrateur: identiteit voldoende vastgesteld.
- Penningmeester: bijzondere contributieregeling akkoord.
- Bestuur: uitzondering op standaardbeleid goedgekeurd.

Wanneer alle verplichte besluiten positief zijn, wordt de zaak **Gereed voor verwerking**.

---

## Fase F – Voorbereiding Sportlink-verwerking

Het Digitaal Verenigingskantoor stelt een verwerkingspakket samen.

Dit pakket bevat:

- definitieve persoonsgegevens;
- lidmaatschapstype;
- gewenste ingangsdatum;
- bonds- of verenigingsstatus;
- relevante toestemmingen;
- verwijzing naar het procesdossier;
- overzicht van uitgevoerde controles;
- openstaande waarschuwingen.

### Vier mogelijke verwerkingsvormen

1. **Volledig automatisch via een toegestane koppeling.**
2. **Automatisch voorbereid, handmatig bevestigd.**
3. **Begeleide handmatige invoer in Sportlink.**
4. **Volledig handmatige verwerking met controle achteraf.**

Welke vorm mogelijk is, hangt af van de technische mogelijkheden en gebruiksvoorwaarden van Sportlink.

---

## Fase G – Verwerking in Sportlink

De status wordt **In verwerking**.

Het systeem registreert:

- wie de verwerking uitvoert;
- wanneer deze begint;
- welke gegevens worden aangeboden;
- welke Sportlink-actie wordt uitgevoerd;
- de technische of handmatige uitkomst;
- eventuele foutmeldingen.

### Veiligheidsregel

Een mislukte verwerking mag niet automatisch onbeperkt worden herhaald.

Na een vooraf bepaald aantal mislukte pogingen wordt de zaak **Geblokkeerd** en ontstaat een technische taak.

---

## Fase H – Controle na verwerking

Het systeem leest of controleert de nieuwe Sportlink-registratie.

### Te controleren punten

- bestaat de persoon;
- is het juiste lidmaatschap aangemaakt;
- klopt de ingangsdatum;
- klopt de lidcategorie;
- zijn de persoonsgegevens juist;
- is er geen duplicaat ontstaan;
- is een bonds- of relatienummer ontvangen;
- zijn eventuele signaleringen afgehandeld.

### Uitkomsten

**Alles correct:** verder naar afronding.

**Kleine herstelbare afwijking:** herstelactie aanmaken.

**Materiële afwijking:** zaak blokkeren en ledenadministrateur waarschuwen.

> Het proces is pas afgerond nadat deze nacontrole succesvol is.

---

## Fase I – Afronding en vervolgacties

Na succesvolle verwerking:

1. Zet de status op **Afgerond**.
2. Verstuur een bevestiging aan het lid of de verzorger.
3. Informeer relevante interne rollen.
4. Start gekoppelde vervolgprocessen.
5. Sluit tijdelijke taken.
6. Bewaar het volledige procesdossier volgens de bewaartermijnen.

### Mogelijke vervolgprocessen

- contributie-inning;
- teamindeling;
- spelerspas of speelgerechtigdheid;
- vrijwilligersverplichtingen;
- kleding of materialen;
- toegang tot app of ledenomgeving;
- nieuwsbrief;
- introductie-informatie;
- uitnodiging voor trainingen;
- website- of communicatierechten;
- registratie van ouder of verzorger.

> Deze vervolgprocessen zijn afzonderlijke werkstromen. Het proces Nieuw lid geeft alleen het startsein.

---

# 9. Beslismomenten Nieuw lid

| ID | Beslissing | Mogelijke uitkomsten |
| --- | --- | --- |
| **D1** | Is de aanmelding voldoende identificeerbaar? | Ja / herstelbaar / handmatige beoordeling |
| **D2** | Zijn alle verplichte gegevens aanwezig? | Ja / aanvulverzoek |
| **D3** | Bestaat de persoon al? | Nee / ja / misschien |
| **D4** | Is sprake van een bestaand of oud lidmaatschap? | Nee / herinschrijving of wijziging |
| **D5** | Is een overschrijving van toepassing? | Nee / start overschrijvingswerkstroom |
| **D6** | Is plaatsing mogelijk? | Ja / wachtlijst / afwijzing |
| **D7** | Zijn bijzondere goedkeuringen vereist? | Nee / taak naar bevoegde rol |
| **D8** | Mag deze zaak automatisch worden verwerkt? | Ja / na bevestiging / nee |
| **D9** | Is de Sportlink-verwerking correct uitgevoerd? | Ja / herstelbaar / blokkeren |

---

# 10. Uitzonderingen

Voor ieder proces worden uitzonderingen expliciet ontworpen. Ze mogen niet als losse improvisaties in de code terechtkomen.

Voor **Nieuw lid** voorzien we minimaal:

- minderjarig lid zonder geldige verzorger;
- mogelijk dubbel persoonrecord;
- oud-lid meldt zich opnieuw aan;
- kandidaat is al bij een andere vereniging geregistreerd;
- wachtlijst voor leeftijdscategorie;
- onvolledig of buitenlands adres;
- geen e-mailadres;
- afwijkende naam of roepnaam;
- toekomstige ingangsdatum;
- aanmelding met terugwerkende kracht;
- meerdere kinderen binnen één gezin;
- gescheiden ouders of meerdere contactpersonen;
- bijzondere privacybeperking;
- financiële uitzondering;
- ongeldige of tegenstrijdige geboortedatum;
- technische storing in Sportlink;
- handmatige Sportlink-mutatie buiten het proces om;
- aanvrager trekt de inschrijving in;
- kandidaat reageert niet op aanvulverzoeken;
- vereniging wijst de aanmelding af.

Iedere uitzondering krijgt later:

- een herkenningsregel;
- een eigenaar;
- een toegestane vervolgactie;
- een reactietermijn;
- een escalatiepad.

---

# 11. Termijnen en herinneringen

Voor elke wachtstatus wordt een termijn ingesteld.

### Voorbeeld: ontbrekende informatie

| Moment | Actie |
| --- | --- |
| Dag 0 | Verzoek om aanvulling |
| Dag 7 | Eerste herinnering |
| Dag 14 | Tweede herinnering |
| Dag 21 | Taak voor ledenadministrateur |
| Dag 30 | Voorstel om dossier te annuleren |

> **Let op:** dit zijn nog geen definitieve CKC-beleidsregels. Ze moeten door de proceseigenaar worden vastgesteld.

Het systeem sluit een dossier niet definitief zonder dat de toegepaste regel en reden worden vastgelegd.

---

# 12. Menselijke controlemomenten

Menselijke beoordeling is minimaal verplicht bij:

- mogelijke dubbele personen;
- tegenstrijdige identiteitsgegevens;
- beleidsuitzonderingen;
- afwijzing van een aanmelding;
- bijzondere financiële afspraken;
- privacygevoelige uitzonderingen;
- technisch onzekere Sportlink-verwerking;
- materiële verschillen na verwerking;
- handmatige correctie van automatisch verzamelde gegevens.

Voor standaardgevallen kan het systeem na bewezen betrouwbaarheid meer handelingen automatisch uitvoeren.

De autonomie wordt stapsgewijs opgebouwd:

1. **Signaleren**
2. **Voorstellen**
3. **Voorbereiden**
4. **Uitvoeren na goedkeuring**
5. **Zelfstandig uitvoeren met controle achteraf**

---

# 13. Audittrail

Iedere relevante gebeurtenis wordt onveranderbaar vastgelegd.

### Minimale auditgegevens

- datum en tijd;
- procesnummer;
- persoon of lid;
- actor: mens, systeem of koppeling;
- uitgevoerde actie;
- oude waarde;
- nieuwe waarde;
- bron van de informatie;
- toegepaste regel;
- resultaat;
- eventuele foutmelding;
- besluit of goedkeuring;
- communicatie die is verzonden.

> Correcties overschrijven de historie niet. Ze voegen een nieuwe gebeurtenis toe.

---

# 14. Communicatieprincipes

Communicatie wordt onderdeel van het procesmodel en niet verspreid door de code gebouwd.

Iedere boodschap heeft:

- een communicatietype;
- ontvanger;
- aanleiding;
- sjabloonversie;
- verzendmoment;
- verzendstatus;
- eventuele bijlage;
- relatie met een processtap.

### Voorbeelden

- ontvangstbevestiging;
- verzoek om aanvullende gegevens;
- herinnering;
- melding wachtlijst;
- bevestiging inschrijving;
- afwijzing;
- melding technische vertraging;
- bevestiging intrekking.

Voor gevoelige of negatieve beslissingen kan menselijke goedkeuring vóór verzending verplicht worden gemaakt.

---

# 15. Eerste functionele procesregels

De volgende regels vormen een eerste aanzet. Ze zijn nog niet definitief.

```yaml
regels:
  - id: LA01-R001
    naam: Minderjarige vereist verzorger
    wanneer:
      leeftijd_op_ingangsdatum: "< 18"
    dan:
      verplicht:
        - verzorger_naam
        - verzorger_contact
        - vereiste_toestemming

  - id: LA01-R002
    naam: Mogelijk dubbel lid vereist controle
    wanneer:
      duplicaatscore: ">= grenswaarde"
    dan:
      automatische_verwerking: false
      taak: controleer_mogelijk_dubbel_lid

  - id: LA01-R003
    naam: Onvolledig dossier niet naar Sportlink
    wanneer:
      verplichte_velden_compleet: false
    dan:
      sportlink_verwerking: geblokkeerd
      status: wacht_op_aanvrager

  - id: LA01-R004
    naam: Verwerking vereist positieve besluiten
    wanneer:
      verplichte_besluiten_compleet: false
    dan:
      status: wacht_op_interne_beoordeling

  - id: LA01-R005
    naam: Nacontrole verplicht
    wanneer:
      sportlink_verwerking: geslaagd
    dan:
      status: controle_na_verwerking

  - id: LA01-R006
    naam: Geen automatische samenvoeging
    wanneer:
      mogelijke_bestaande_personen: "> 0"
    dan:
      persoon_aanmaken: false
      menselijke_controle: verplicht
```

Deze YAML-regels beschrijven later het beleid. De procesmachine bepaalt welke statusovergangen mogelijk zijn.

---

# 16. Voorlopig toestandsmodel Nieuw lid

```text
ONTVANGEN
   ↓
IN_CONTROLE
   ├── ontbrekende gegevens ──→ WACHT_OP_AANVRAGER
   │                                ↓
   │                           IN_CONTROLE
   │
   ├── beoordeling nodig ─────→ WACHT_OP_INTERNE_BEOORDELING
   │                                ↓
   │                           IN_CONTROLE
   │
   ├── niet toelaatbaar ──────→ AFGEWEZEN
   │
   ├── ingetrokken ───────────→ GEANNULEERD
   │
   └── akkoord ───────────────→ GEREED_VOOR_VERWERKING
                                      ↓
                                IN_VERWERKING
                                  ├── fout ──→ GEBLOKKEERD
                                  └── gelukt
                                        ↓
                              CONTROLE_NA_VERWERKING
                                  ├── afwijking ──→ GEBLOKKEERD
                                  └── correct ────→ AFGEROND
```

Terugovergangen zijn alleen toegestaan wanneer daar een expliciete reden voor bestaat.

---

# 17. Werkvoorraad voor de ledenadministrateur

De ledenadministrateur ziet niet primair een lijst met alle leden, maar een **geprioriteerde werkvoorraad**.

Voorbeelden:

- drie nieuwe aanmeldingen gereed voor goedkeuring;
- één mogelijk dubbel lid;
- twee dossiers wachten langer dan veertien dagen;
- één Sportlink-verwerking mislukt;
- vijf leden hebben onbestelbare e-mailadressen;
- één aanmelding dreigt de gewenste ingangsdatum te missen;
- vier verwerkingen zijn gereed voor nacontrole.

Iedere taak toont:

- wat er moet gebeuren;
- waarom;
- vóór wanneer;
- benodigde gegevens;
- systeemvoorstel;
- risico;
- mogelijke acties.

---

# 18. Prestatie- en kwaliteitsmetingen

Voor deze werkstroom kunnen later onder andere worden gemeten:

- gemiddelde doorlooptijd;
- tijd tot eerste reactie;
- percentage volledig ingediende formulieren;
- aantal handmatige correcties;
- aantal mogelijke duplicaten;
- percentage verwerking zonder herstelactie;
- aantal zaken buiten de termijn;
- aantal Sportlink-fouten;
- aantal wijzigingen buiten het proces om;
- percentage automatisch afgehandelde standaardzaken;
- tevredenheid van nieuwe leden;
- hoeveelheid werk per ledenadministrateur.

> De metingen zijn bedoeld om het proces te verbeteren, niet om vrijwilligers persoonlijk af te rekenen.

---

# 19. Ontwerpbesluiten voor Sprint 0.5

Voordat het proces definitief kan worden vastgesteld, moeten we voor CKC bepalen:

1. Welke lidcategorieën bestaan er precies?
2. Welke gegevens zijn per categorie verplicht?
3. Wanneer is iemand officieel toegelaten?
4. Wie beslist over teamruimte en wachtlijsten?
5. Welke situaties vereisen bestuursgoedkeuring?
6. Wanneer geldt een aanmelding als overschrijving?
7. Welke Sportlink-handelingen kunnen technisch worden gekoppeld?
8. Welke handelingen moeten voorlopig handmatig blijven?
9. Welk financieel systeem is leidend?
10. Welke termijnen gelden voor reacties en herinneringen?
11. Welke communicatie mag automatisch worden verzonden?
12. Welke gegevens en documenten mogen worden bewaard en hoe lang?
13. Hoe behandelen we bestaande, dubbele en historische Sportlink-records?
14. Welke interne systemen moeten na inschrijving worden bijgewerkt?
15. Wat gebeurt er wanneer iemand buiten het proces om rechtstreeks in Sportlink wordt gewijzigd?

---

# 20. Definitie van gereed voor proces LA-01

Het procesontwerp **Nieuw lid** is pas definitief wanneer:

- [ ] alle stappen en beslispunten door CKC zijn gevalideerd;
- [ ] rollen en bevoegdheden zijn toegewezen;
- [ ] verplichte gegevens zijn vastgesteld;
- [ ] uitzonderingen zijn beschreven;
- [ ] termijnen zijn vastgesteld;
- [ ] Sportlink-interacties zijn geïnventariseerd;
- [ ] communicatie-uitingen zijn bepaald;
- [ ] privacy- en bewaartermijnen zijn beoordeeld;
- [ ] statusovergangen zijn goedgekeurd;
- [ ] testscenario's voor normale en afwijkende gevallen zijn opgesteld.

Pas daarna vertalen we het ontwerp naar:

1. **statemachine**;
2. **YAML-regels**;
3. **gegevensmodel**;
4. **schermen**;
5. **integraties**;
6. **programmacode**.

---

## Versiehistorie

| Versie | Datum | Status | Wijziging |
| --- | --- | --- | --- |
| 0.1 | 2026-08-19 | Concept | Eerste volledige procesbeschrijving Ledenadministratie |

---

*Dit document is de canonieke procesbeschrijving voor de werkstroom Ledenadministratie binnen het Digitaal Verenigingskantoor.*
