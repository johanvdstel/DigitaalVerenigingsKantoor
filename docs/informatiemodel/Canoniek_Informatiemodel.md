# Canoniek CKC-informatiemodel v0.5.1

**Status:** concept na stresstest v0.5  
**Versie:** 0.5.1  
**Datum:** 1 september 2026  
**Project:** Digitaal Verenigingskantoor (DVK) – CKC

---

## Inhoudsopgave

1. [Doel van deze versie](#1-doel-van-deze-versie)
2. [Bestaande uitgangspunten blijven gelden](#2-bestaande-uitgangspunten-blijven-gelden)
3. [Kernbegrippen](#3-kernbegrippen)
4. [Vrijwilligerswerk en Ledendienst](#4-vrijwilligerswerk-en-ledendienst)
5. [Governance](#5-governance)
6. [Bevoegdheid](#6-bevoegdheid)
7. [Resource](#7-resource)
8. [Handeling](#8-handeling)
9. [Autorisatie](#9-autorisatie)
10. [Feitelijke toegang](#10-feitelijke-toegang)
11. [Gewenste samenhang](#11-gewenste-samenhang)
12. [Afwijkingen en signalering](#12-afwijkingen-en-signalering)
13. [Privacy, financiële waarde en operationele waarde](#13-privacy-financiële-waarde-en-operationele-waarde)
14. [Temporaliteit](#14-temporaliteit)
15. [Bronfeit, afleiding en beleidsgevolg bij governance](#15-bronfeit-afleiding-en-beleidsgevolg-bij-governance)
16. [Samengevat conceptueel model](#16-samengevat-conceptueel-model)
17. [Ontwerpregels v0.5.1](#17-ontwerpregels-v051)
18. [Resultaat van de stresstest](#18-resultaat-van-de-stresstest)
19. [Vervolg](#19-vervolg)

---

## 1. Doel van deze versie

Versie 0.5.1 is een aanscherping van het Canoniek CKC-informatiemodel v0.5 naar aanleiding van de stresstest.

De bestaande kern van v0.5 blijft intact. De belangrijkste uitbreiding is het expliciet modelleren van governance, delegatie, bevoegdheid, autorisatie, feitelijke toegang en de resources waarop die betrekking hebben.

De centrale ontwerpregel is:

> **Verantwoordelijkheid, bevoegdheid, autorisatie en feitelijke toegang zijn verschillende begrippen.**

Deze scheiding maakt het mogelijk om later niet alleen vast te leggen wie welke functie heeft, maar ook te controleren of technische toegangsrechten daadwerkelijk overeenkomen met de bestuurlijk verleende bevoegdheden.

---

## 2. Bestaande uitgangspunten blijven gelden

Het canonieke model blijft uitgaan van de eerder vastgelegde principes:

1. Een **Persoon** wordt niet gereduceerd tot één rol of categorie.
2. Een persoon kan gelijktijdig meerdere **Relaties**, **Functies** en **Deelnames** hebben.
3. **Lidmaatschap**, **Voetbaldeelname**, **Functievervulling** en andere relaties worden afzonderlijk gemodelleerd.
4. Het model maakt expliciet onderscheid tussen:
   - **bronfeiten**;
   - **afgeleide kwalificaties**;
   - **beleidsgevolgen**.
5. CKC-specifieke beleidsregels worden niet onnodig als fundamentele eigenschappen van personen gemodelleerd.
6. Relaties die in de tijd kunnen veranderen moeten een geldigheidsperiode kunnen hebben.

---

## 3. Kernbegrippen

### 3.1 Persoon

Een natuurlijk persoon die een relatie met CKC heeft of heeft gehad.

Een persoon kan bijvoorbeeld tegelijk zijn:

- lid;
- speler;
- trainer;
- ouder/verzorger;
- commissielid;
- bestuurslid;
- vrijwilliger;
- functionaris met een gedelegeerde bevoegdheid.

Deze kwalificaties worden waar mogelijk afgeleid uit afzonderlijke bronfeiten en relaties.

---

### 3.2 Organisatie

Een rechtspersoon, organisatie-eenheid of externe partij waarmee CKC een relevante relatie onderhoudt.

Voorbeelden zijn:

- CKC zelf;
- KNVB;
- gemeente;
- leverancier;
- sponsor;
- Sportbedrijf;
- externe commissie of instantie.

---

### 3.3 Lidmaatschap

De formele lidmaatschapsrelatie tussen een persoon en CKC.

Lidmaatschap staat los van bijvoorbeeld voetbaldeelname of functievervulling.

---

### 3.4 Voetbaldeelname

De deelname van een persoon aan voetbalactiviteiten binnen CKC.

Voorbeelden:

- competitiespeler;
- recreatieve speler;
- deelname aan een lokaal/recreatief team of groep.

Benamingen zoals *Oldstars*, *Vroege Vogels* of *Harry's Voetbalschool* zijn geen afzonderlijke fundamentele lidmaatschapssoorten, maar kunnen namen of classificaties van recreatieve voetbalactiviteiten of groepen zijn.

---

### 3.5 Functie

Een herkenbare organisatorische verantwoordelijkheid of positie binnen CKC.

Voorbeelden:

- voorzitter;
- penningmeester;
- secretaris;
- vicevoorzitter;
- ledenadministrateur;
- trainer;
- commissielid;
- TapKey-beheerder;
- camerabeheerder;
- kassabeheerder.

Een functie bestaat onafhankelijk van de persoon die deze op een bepaald moment vervult.

---

### 3.6 Functievervulling

De tijdgebonden relatie tussen een **Persoon** en een **Functie**.

Conceptueel:

```text
Persoon
   │
   └── vervult
          │
          ▼
       Functie
```

Een functievervulling heeft in beginsel een geldigheidsperiode.

---

## 4. Vrijwilligerswerk en Ledendienst

### 4.1 Vrijwilligerswerk

Vrijwilligerswerk is een kwalificatie van werkzaamheden die iemand voor CKC verricht.

Een organisatorische relatie, zoals commissielidmaatschap, kan betekenen dat de verrichte werkzaamheden als vrijwilligerswerk kwalificeren.

Daarom geldt niet:

```text
Commissielid = Vrijwilliger
```

maar bijvoorbeeld:

```text
Persoon
   │
   └── Functievervulling: commissielid
                  │
                  └── kwalificeert als vrijwilligerswerk
```

---

### 4.2 Ledendienst

Een **Ledendienstverplichting** en de **uitvoering van Ledendienst** zijn afzonderlijke begrippen.

Bij een minderjarig lid kan bijvoorbeeld:

- de verplichting gekoppeld zijn aan het lid;
- de feitelijke uitvoering plaatsvinden door een ouder/verzorger.

Conceptueel:

```text
Minderjarig lid
      │
      └── heeft Ledendienstverplichting

Ouder/verzorger
      │
      └── voert Ledendienst uit
                │
                └── ten behoeve van verplichting van lid
```

Een aanduiding zoals *broederdienst* is geen fundamenteel persoonskenmerk, maar een mogelijke vrijstellingsgrond die volgt uit beleidsregels en gezins-/ouderrelaties.

---

## 5. Governance

### 5.1 Bestuurlijke verantwoordelijkheid

De uiteindelijke bestuurlijke verantwoordelijkheid en autoriteit binnen CKC berust bij het bevoegde bestuur en, waar van toepassing, het dagelijks bestuur (DB).

Bestuurlijke verantwoordelijkheid moet worden onderscheiden van de dagelijkse uitvoering van werkzaamheden.

Een bestuursorgaan kan bevoegdheden delegeren zonder daarmee zijn bestuurlijke eindverantwoordelijkheid noodzakelijkerwijs over te dragen.

---

### 5.2 Bestuursorgaan

Een formeel orgaan binnen CKC waaraan bestuurlijke verantwoordelijkheid of beslissingsbevoegdheid is toegekend.

Voorbeelden:

- bestuur;
- dagelijks bestuur;
- eventueel andere statutair of beleidsmatig bevoegde organen.

---

### 5.3 Delegatie

**Delegatie** legt vast dat een bevoegde actor een bepaalde bevoegdheid toekent aan een andere actor.

Waar mogelijk wordt een bevoegdheid gedelegeerd aan een **Functie** in plaats van rechtstreeks aan een individuele persoon.

Voorkeursmodel:

```text
Bestuursorgaan
      │
      └── verleent/delegeert
                 │
                 ▼
            Bevoegdheid
                 │
                 └── toegekend aan
                            │
                            ▼
                         Functie
                            │
                            └── vervuld door
                                       │
                                       ▼
                                    Persoon
```

Hierdoor hoeft bij een personele wisseling de governance-definitie niet te worden gewijzigd.

---

## 6. Bevoegdheid

Een **Bevoegdheid** beschrijft wat een actor bestuurlijk of organisatorisch namens CKC mag doen.

Een bevoegdheid:

- heeft een grondslag;
- wordt verleend door een bevoegde actor;
- heeft een bepaalde scope;
- kan betrekking hebben op één of meer resources en handelingen;
- heeft een geldigheidsperiode;
- kan rechtstreeks of via een functie aan een persoon toekomen.

Voorbeeld:

> De functie Ledenadministrateur is bevoegd om de CKC-ledenadministratie te beheren.

De persoon die deze functie op een bepaald moment geldig vervult, verkrijgt daarmee de bijbehorende bevoegdheid.

---

## 7. Resource

### 7.1 Definitie

Een **Resource** is een door of namens CKC beheerd object waarop gecontroleerde handelingen kunnen worden uitgevoerd.

Het begrip Resource is bewust breder dan alleen een digitaal systeem.

### 7.2 Typen resources

```text
Resource
├── Informatiesysteem
│   ├── Sportlink
│   ├── Kassasysteem
│   └── TapKey
│
├── Gegevensverzameling
│   ├── Ledenadministratie
│   ├── Camerabeelden
│   └── Financiële gegevens
│
├── Fysiek object
│   ├── Clubgebouw
│   ├── Bestuurskamer
│   └── Materiaalruimte
│
└── Installatie
    ├── Veldverlichting
    ├── Camera-installatie
    └── Toegangsinstallatie
```

Deze classificatie is uitbreidbaar.

---

## 8. Handeling

Een **Handeling** beschrijft wat met of op een Resource mag worden gedaan.

Voorbeelden:

| Resource | Mogelijke handeling |
|---|---|
| Ledenadministratie | bekijken |
| Ledenadministratie | wijzigen |
| Sportlink | gebruikers beheren |
| Camerabeelden | live bekijken |
| Camerabeelden | terugkijken |
| Camerabeelden | exporteren |
| Camera-installatie | configureren |
| Kassasysteem | verkoop registreren |
| Kassasysteem | assortiment/tarieven wijzigen |
| Kassasysteem | financiële rapportage bekijken |
| TapKey | toegangsrechten beheren |
| Veldverlichting | inschakelen/configureren |

Hiermee wordt voorkomen dat een generieke aanduiding als *beheerder* automatisch onbeperkte rechten impliceert.

---

## 9. Autorisatie

Een **Autorisatie** is de vertaling van een geldige bevoegdheid naar toegestane toegang of handelingen binnen een specifieke Resource.

Daarmee geldt:

```text
Bevoegdheid ≠ Autorisatie
```

Voorbeeld:

- **Bevoegdheid:** Kees is als ledenadministrateur bevoegd ledengegevens te beheren.
- **Autorisatie:** Kees heeft in Sportlink een account met de daarvoor benodigde rechten.

Een autorisatie moet herleidbaar zijn tot een geldige bevoegdheid.

---

## 10. Feitelijke toegang

**Feitelijke toegang** beschrijft wat een persoon technisch of fysiek daadwerkelijk kan benaderen of uitvoeren.

Daarmee geldt ook:

```text
Autorisatie ≠ Feitelijke toegang
```

Een systeem kan bijvoorbeeld nog toegang toestaan nadat de formele bevoegdheid is geëindigd.

Het canonieke model moet daarom drie situaties afzonderlijk kunnen vaststellen:

1. wat iemand **mag** op basis van bevoegdheid;
2. waarvoor iemand **geautoriseerd behoort te zijn**;
3. waartoe iemand **feitelijk toegang heeft**.

---

## 11. Gewenste samenhang

De kernketen wordt:

```text
CKC
 │
 ├── bestuurlijke verantwoordelijkheid
 │
 ▼
Bestuursorgaan
 │
 ├── verleent / delegeert
 ▼
Bevoegdheid
 │
 ├── toegekend aan
 ▼
Functie / Rol
 │
 ├── vervuld door
 ▼
Persoon
 │
 ├── leidt tot gewenste
 ▼
Autorisatie
 │
 ├── op
 ▼
Resource
 │
 └── voor
 ▼
Handeling
```

Daarnaast geldt als controleprincipe:

```text
Werkelijke toegang
        │
        ▼
moet overeenkomen met
        │
        ▼
Geldige autorisatie
        │
        ▼
Geldige bevoegdheid
```

---

## 12. Afwijkingen en signalering

Doordat bevoegdheid, autorisatie en feitelijke toegang afzonderlijk worden gemodelleerd, kan het DVK afwijkingen signaleren.

### Voorbeeld 1 – achtergebleven autorisatie

Een persoon is sinds 1 augustus geen lid meer van de kantinecommissie, maar heeft nog beheerrechten in het kassasysteem.

```text
Geldige bevoegdheid: NEE
Autorisatie:          JA
Feitelijke toegang:   JA
```

Resultaat:

> **Signalering:** technische toegang bestaat zonder geldige bevoegdheid.

### Voorbeeld 2 – ontbrekende autorisatie

Een persoon is vanaf vandaag ledenadministrateur, maar heeft nog geen overeenkomstige Sportlink-autorisatie.

```text
Geldige bevoegdheid: JA
Benodigde autorisatie: JA
Aanwezige autorisatie: NEE
```

Resultaat:

> **Signalering:** geldige functie en bevoegdheid zijn nog niet vertaald naar benodigde technische toegang.

Deze controles vormen een belangrijke toekomstige toepassing van het Digitaal Verenigingskantoor.

---

## 13. Privacy, financiële waarde en operationele waarde

Het autorisatiemodel is niet uitsluitend bedoeld voor privacygevoelige persoonsgegevens.

Resources kunnen verschillende beschermingsgronden hebben, bijvoorbeeld:

- privacygevoeligheid;
- financiële waarde;
- financiële impact van gebruik;
- veiligheidsbelang;
- operationele continuïteit;
- vertrouwelijkheid;
- bestuurlijke gevoeligheid.

Voorbeelden:

- ledenadministratie: privacygevoelig;
- camerabeelden: privacy- en veiligheidsgevoelig;
- kassasysteem: financieel en privacygevoelig;
- veldverlichting: financiële en operationele waarde;
- digitale toegangsinstallatie: veiligheids- en operationele waarde.

De beschermingsgrond bepaalt mede welke governance, autorisatie en controles passend zijn, maar verandert het generieke model niet.

---

## 14. Temporaliteit

### 14.1 Generiek principe

Relaties en toekenningen die in de tijd kunnen veranderen, moeten een geldigheidsperiode kunnen hebben.

Conceptueel:

```text
geldig vanaf
geldig tot
```

### 14.2 Toepassing

Dit geldt onder meer voor:

- lidmaatschap;
- voetbaldeelname;
- teamrelaties;
- functievervulling;
- ouder-/verzorgerrelaties waar relevant;
- delegaties;
- bevoegdheden;
- autorisaties;
- vrijstellingen;
- contracten;
- beleidsregels waar relevant.

Hiermee kan het DVK niet alleen de huidige situatie vaststellen, maar ook historische vragen beantwoorden, zoals:

> Welke functie, bevoegdheden en autorisaties had deze persoon op 14 maart 2024?

---

## 15. Bronfeit, afleiding en beleidsgevolg bij governance

Ook voor governance blijft de driedeling gelden.

### Bronfeiten

Voorbeelden:

- persoon X vervult functie Y;
- bevoegdheid Z is aan functie Y gedelegeerd;
- autorisatie A bestaat in systeem B;
- technische toegang C is vastgesteld.

### Afgeleide kwalificaties

Voorbeelden:

- persoon X is bevoegd voor handeling H;
- persoon X behoort toegang tot resource R te hebben;
- een commissiefunctie kwalificeert als vrijwilligerswerk.

### Beleidsgevolgen en controles

Voorbeelden:

- toegang moet worden ingetrokken;
- autorisatie moet worden verstrekt;
- functiescheiding is vereist;
- een afwijking moet aan een verantwoordelijke functionaris worden gemeld.

Hiermee blijft ook het governance-deel van het model zuiver ten opzichte van veranderbaar CKC-beleid.

---

## 16. Samengevat conceptueel model

De voor v0.5.1 relevante kernbegrippen zijn:

```text
Persoon
Organisatie
Lidmaatschap
Voetbaldeelname
Functie
Functievervulling
Vrijwilligerswerk
Ledendienstverplichting
Ledendienstuitvoering
Bestuursorgaan
Bestuurlijke verantwoordelijkheid
Delegatie
Bevoegdheid
Autorisatie
Feitelijke toegang
Resource
Handeling
Geldigheidsperiode
Beleidsregel
```

De belangrijkste nieuwe relaties zijn:

```text
Bestuursorgaan ── verleent/delegeert ──> Bevoegdheid
Bevoegdheid ── wordt toegekend aan ──> Functie
Persoon ── vervult ──> Functie
Bevoegdheid ── betreft ──> Handeling
Handeling ── wordt uitgevoerd op ──> Resource
Bevoegdheid ── rechtvaardigt ──> Autorisatie
Autorisatie ── behoort overeen te komen met ──> Feitelijke toegang
```

---

## 17. Ontwerpregels v0.5.1

1. **Een functie is geen persoon.**
2. **Een functie is geen bevoegdheid.**
3. **Een bevoegdheid is geen technische autorisatie.**
4. **Een autorisatie is geen bewijs van bestuurlijke bevoegdheid.**
5. **Feitelijke toegang is geen bewijs dat toegang toegestaan is.**
6. **Bevoegdheden worden waar mogelijk aan functies gedelegeerd, niet aan individuele personen.**
7. **Een bevoegdheid wordt uitgedrukt in termen van handelingen en resources.**
8. **Resources omvatten zowel digitale systemen en gegevens als fysieke objecten en installaties.**
9. **Tijdsafhankelijkheid is een generiek kenmerk van veranderlijke relaties.**
10. **Bronfeiten, afgeleide kwalificaties en beleidsgevolgen blijven gescheiden.**
11. **Afwijkingen tussen bevoegdheid, autorisatie en feitelijke toegang moeten detecteerbaar zijn.**
12. **Bestuurlijke eindverantwoordelijkheid en gedelegeerde uitvoering worden afzonderlijk gemodelleerd.**

---

## 18. Resultaat van de stresstest

De stresstest van v0.5 heeft geen fundamentele tekortkoming in de bestaande kern van het Canoniek CKC-informatiemodel aangetoond.

De belangrijkste gevonden aanscherping betreft de governance- en autorisatielaag.

Met v0.5.1 kan het model nu conceptueel onderscheid maken tussen:

```text
Wie iemand is
        ↓
Welke relatie iemand met CKC heeft
        ↓
Welke functie iemand vervult
        ↓
Welke bevoegdheid daaruit volgt
        ↓
Welke autorisatie daarbij hoort
        ↓
Welke toegang feitelijk bestaat
        ↓
Op welke resource
        ↓
Voor welke handeling
```

Daarmee ontstaat tevens de basis voor geautomatiseerde controles door het DVK.

---

## 19. Vervolg

Na vaststelling van v0.5.1 zijn twee vervolgstappen logisch:

1. de nieuwe begrippen en relaties verwerken in het logisch gegevenswoordenboek en de bronnenmapping;
2. een eerste klein DVK-prototype ontwerpen waarin voor een persoon zichtbaar wordt:
   - identiteit en relaties;
   - actuele functies;
   - daaruit voortvloeiende bevoegdheden;
   - gewenste autorisaties;
   - aanwezige autorisaties/toegang;
   - eventuele afwijkingen.

Daarmee kan het Canoniek Informatiemodel voor het eerst direct worden vertaald naar een zichtbare, bruikbare toepassing.
