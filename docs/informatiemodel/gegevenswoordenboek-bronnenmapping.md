# CKC Logisch Gegevenswoordenboek & Bronnenmapping v0.2

**Status:** concept  
**Versie:** 0.2  
**Datum:** 1 september 2026  
**Project:** Digitaal Verenigingskantoor (DVK) – CKC  
**Gebaseerd op:** Canoniek CKC-informatiemodel v0.5.1

---

## Inhoudsopgave

1. [Doel en positie van dit document](#1-doel-en-positie-van-dit-document)
2. [Uitgangspunten](#2-uitgangspunten)
3. [Legenda bronnenmapping](#3-legenda-bronnenmapping)
4. [Kernbegrippen personen en organisaties](#4-kernbegrippen-personen-en-organisaties)
5. [Lidmaatschap en voetbaldeelname](#5-lidmaatschap-en-voetbaldeelname)
6. [Functies en functievervulling](#6-functies-en-functievervulling)
7. [Vrijwilligerswerk en Ledendienst](#7-vrijwilligerswerk-en-ledendienst)
8. [Governance en bestuurlijke verantwoordelijkheid](#8-governance-en-bestuurlijke-verantwoordelijkheid)
9. [Delegatie en bevoegdheid](#9-delegatie-en-bevoegdheid)
10. [Resources en handelingen](#10-resources-en-handelingen)
11. [Autorisatie en feitelijke toegang](#11-autorisatie-en-feitelijke-toegang)
12. [Temporaliteit](#12-temporaliteit)
13. [Beleidsregels, afleidingen en signaleringen](#13-beleidsregels-afleidingen-en-signaleringen)
14. [Bronnenmatrix](#14-bronnenmatrix)
15. [Logische relaties](#15-logische-relaties)
16. [Eigenaarschap en bronautoriteit](#16-eigenaarschap-en-bronautoriteit)
17. [Nieuwe DVK-registers](#17-nieuwe-dvk-registers)
18. [Belangrijkste gaps ten opzichte van het canonieke model](#18-belangrijkste-gaps-ten-opzichte-van-het-canonieke-model)
19. [Ontwerpregels](#19-ontwerpregels)
20. [Vervolg](#20-vervolg)

---

## 1. Doel en positie van dit document

Dit document vertaalt het **Canoniek CKC-informatiemodel v0.5.1** naar een logisch gegevenswoordenboek en een mapping naar de bekende CKC-bronsystemen.

Het document beschrijft:

- welke logische gegevensobjecten CKC nodig heeft;
- welke betekenis deze objecten hebben;
- hoe zij onderling samenhangen;
- welk systeem vandaag bronhouder is of kan zijn;
- waar gegevens slechts indirect of onvolledig beschikbaar zijn;
- welke gegevens in de toekomst in een eigen CKC/DVK-datalaag moeten worden vastgelegd.

Dit is **geen fysiek databaseontwerp**. Tabellen, kolomnamen, API-contracten en technische datatypes worden in een latere stap ontworpen.

---

## 2. Uitgangspunten

### 2.1 Canoniek vóór bronsysteem

Sportlink, Sponsit, TapKey, kassasystemen en andere applicaties bepalen niet welke begrippen CKC nodig heeft.

Het canonieke CKC-model bepaalt de gewenste betekenis. Daarna wordt vastgesteld waar de benodigde feiten beschikbaar zijn.

### 2.2 Bronfeit, afleiding en beleidsgevolg

Het logisch gegevensmodel houdt onderscheid tussen:

1. **bronfeit** – expliciet geregistreerd feit;
2. **afgeleide kwalificatie** – logisch afgeleid uit één of meer feiten;
3. **beleidsgevolg** – resultaat van een CKC-beleidsregel.

Voorbeeld:

```text
Functievervulling: lid kantinecommissie     = bronfeit
Vrijwilliger                                  = afgeleide kwalificatie
Vrijstelling Ledendienst                      = beleidsgevolg
```

### 2.3 Meerdere bronnen

Eén logisch object kan gegevens uit meerdere bronnen combineren.

Daarbij moet steeds duidelijk blijven:

- welk systeem bronhouder is;
- welke waarde leidend is;
- wanneer een waarde is verkregen;
- of een waarde rechtstreeks of afgeleid is.

### 2.4 Historie

Het DVK moet waar relevant zowel actuele als historische situaties kunnen reconstrueren.

### 2.5 Eigen CKC-datalaag

Niet ieder canoniek begrip bestaat in de huidige bronsystemen. Voor ontbrekende CKC-specifieke feiten is een eigen DVK-register legitiem en noodzakelijk.

---

## 3. Legenda bronnenmapping

In de tabellen worden de volgende aanduidingen gebruikt.

| Aanduiding | Betekenis |
|---|---|
| **Bron** | systeem waarin het feit primair wordt vastgelegd |
| **Afgeleid** | door DVK berekend uit andere feiten |
| **DVK-register** | eigen CKC-registratie noodzakelijk of gewenst |
| **Extern** | bron buiten directe CKC-beheersing |
| **Nog vast te stellen** | bron of technische ontsluiting moet nog worden onderzocht |

De genoemde systemen zijn logisch benoemd. Exacte productnamen, modules en interfaces worden waar nodig later technisch uitgewerkt.

---

# 4. Kernbegrippen personen en organisaties

## 4.1 Persoon

**Definitie:** natuurlijk persoon die een actuele of historische relatie met CKC heeft.

Voorbeelden:

- lid;
- oud-lid;
- ouder/verzorger;
- vrijwilliger;
- bestuurder;
- leveranciercontact;
- sponsorcontact;
- vertegenwoordiger van een externe organisatie.

| Aspect | Mapping |
|---|---|
| Primaire bronnen | Sportlink, Sponsit, overige CKC-registers |
| Canonieke identificatie | DVK |
| Persoonsgegevens leden | primair Sportlink |
| Sponsorcontacten | primair Sponsit |
| Niet-leden buiten deze bronnen | DVK-register indien nodig |
| Historische samenvoeging | DVK |

**Ontwerpbesluit:** het DVK heeft een eigen canonieke persoonsidentiteit nodig waarmee records uit verschillende bronnen naar dezelfde persoon kunnen verwijzen.

---

## 4.2 Organisatie

**Definitie:** rechtspersoon, organisatie-eenheid of externe partij met een relevante relatie tot CKC.

Voorbeelden:

- CKC;
- KNVB;
- gemeente;
- Sportbedrijf;
- leverancier;
- sponsor;
- externe commissie of instantie.

| Aspect | Mapping |
|---|---|
| Sponsororganisaties | Sponsit |
| Voetbalorganisaties | Sportlink/KNVB waar aanwezig |
| Leveranciers | huidige financiële/administratieve bron + DVK |
| Overige organisaties | DVK-register |
| Canonieke organisatie-identiteit | DVK |

---

## 4.3 Persoon-organisatierelatie

**Definitie:** relatie tussen een persoon en een organisatie, anders dan de specifieke CKC-relaties die afzonderlijk worden gemodelleerd.

Voorbeelden:

- contactpersoon leverancier;
- vertegenwoordiger sponsor;
- medewerker Sportbedrijf;
- gemeentelijk contactpersoon.

**Bron:** Sponsit waar sponsorgerelateerd; anders DVK-register of relevante externe bron.

---

# 5. Lidmaatschap en voetbaldeelname

## 5.1 Lidmaatschap

**Definitie:** formele lidmaatschapsrelatie tussen een persoon en CKC.

| Aspect | Mapping |
|---|---|
| Actueel lidmaatschap | Sportlink |
| KNVB/bondsrelatie | Sportlink/KNVB |
| CKC-lidcategorie | Sportlink, geïnterpreteerd volgens CKC-model |
| Historische lidmaatschapsperioden | Sportlink deels; historische Access-data waar beschikbaar; uiteindelijk DVK |
| Canonieke interpretatie | DVK |

Sportlink-velden zoals lidsoort en het vrije veld *Status lidmaatschap* worden niet zonder meer gelijkgesteld aan canonieke CKC-begrippen.

---

## 5.2 Voetbaldeelname

**Definitie:** deelname van een persoon aan voetbalactiviteiten bij CKC.

| Aspect | Mapping |
|---|---|
| Competitieteam | Sportlink |
| Teamfunctie/deelname | Sportlink |
| Recreatief/lokaal team | Sportlink voor zover geregistreerd |
| Lokale groepsnaam | Sportlink en/of DVK |
| Historie | Sportlink waar beschikbaar; DVK voor aanvullende historie |

**Ontwerpbesluit:** voetbaldeelname blijft een afzonderlijk bronfeit en wordt niet afgeleid uit lidmaatschap.

---

# 6. Functies en functievervulling

## 6.1 Functie

**Definitie:** herkenbare organisatorische verantwoordelijkheid of positie binnen CKC.

Voorbeelden:

- voorzitter;
- penningmeester;
- secretaris;
- vicevoorzitter;
- trainer;
- teamleider;
- ledenadministrateur;
- commissielid;
- TapKey-beheerder;
- camerabeheerder;
- beheerder veldverlichting;
- kassabeheerder.

| Aspect | Mapping |
|---|---|
| KNVB-/teamfuncties | Sportlink |
| Commissiefuncties | Sportlink voor zover geregistreerd |
| Bestuursfuncties | Sportlink en/of CKC-register |
| Applicatie-/toegangsbeheerfuncties | veelal niet centraal geregistreerd |
| Canonieke functiecatalogus | **DVK-register** |

**Nieuw in v0.2:** het DVK heeft een eigen **Functiecatalogus** nodig. Bronsysteemfuncties worden daarop gemapt.

---

## 6.2 Functievervulling

**Definitie:** tijdgebonden relatie tussen een persoon en een functie.

```text
Persoon ── vervult ──> Functie
```

| Aspect | Mapping |
|---|---|
| Teamfuncties | Sportlink |
| Commissierelaties | Sportlink waar geregistreerd |
| Bestuursfuncties | Sportlink/CKC |
| Beheerfuncties digitale systemen | afzonderlijke systemen of handmatig |
| Canonieke consolidatie | DVK |
| Geldigheidsperiode | DVK moet deze kunnen bewaren |

Een functievervulling mag niet worden gelijkgesteld aan de bevoegdheden of technische toegangsrechten die uit de functie kunnen volgen.

---

# 7. Vrijwilligerswerk en Ledendienst

## 7.1 Vrijwilligerswerk

**Definitie:** werkzaamheden die een persoon vrijwillig voor CKC verricht en die door CKC als zodanig worden erkend.

Vrijwilligerswerk kan voortvloeien uit functievervulling.

```text
Functievervulling
      │
      └── kwalificeert volgens CKC-beleid als
                         │
                         ▼
                  Vrijwilligerswerk
```

| Aspect | Mapping |
|---|---|
| Functie/commissie | Sportlink |
| Vrijwilligersmodule | Sportlink |
| Taakuren | Sportlink vrijwilligersmodule |
| Canonieke kwalificatie | DVK-afleiding |
| Beleidsregel | DVK-beleidsregister |

---

## 7.2 Ledendienstverplichting

**Definitie:** verplichting die volgens CKC-beleid rust op een daarvoor kwalificerend lid.

| Aspect | Mapping |
|---|---|
| Spelende leden / basisgegevens | Sportlink |
| Vastlegging verplicht/vrijgesteld | Sportlink vrijwilligersmodule |
| Beleidsmatige bepaling | DVK |
| Historische regelversie | DVK-beleidsregister |

---

## 7.3 Ledendienstuitvoering

**Definitie:** feitelijk uitgevoerde werkzaamheden waarmee een Ledendienstverplichting geheel of gedeeltelijk wordt vervuld.

| Aspect | Mapping |
|---|---|
| Taakplanning | Sportlink |
| Bardiensten | Sportlink |
| Communicatie bardienst | voetbal.nl / CKC-communicatie |
| Geregistreerde uren | Sportlink vrijwilligersmodule |
| Canonieke koppeling uitvoering-verplichting | DVK |

De CKC-eigen bardienstgenerator is geen bron van de planning, maar een communicatievoorziening.

---

## 7.4 Ouder-/verzorgerrelatie

**Definitie:** relatie waarbij een persoon ouder of verzorger is van een andere persoon.

Deze relatie is nodig om Ledendienst door ouders/verzorgers namens minderjarige leden correct te kunnen interpreteren.

**Bron:** Sportlink voor zover vastgelegd; aanvullende of canonieke relatie in DVK indien noodzakelijk.

---

## 7.5 Vrijstelling Ledendienst

**Definitie:** beleidsgevolg waardoor een Ledendienstverplichting niet of niet volledig van toepassing is.

Mogelijke gronden zijn onder meer:

- kwalificerende functie;
- reeds vervulde gezinsverplichting;
- zogenoemde broederdienst;
- andere door CKC vastgestelde vrijstellingsgrond.

**Bron:** vastgelegde status in Sportlink waar aanwezig.  
**Herkomst/redenering:** DVK-beleidsregister en DVK-afleiding.

---

# 8. Governance en bestuurlijke verantwoordelijkheid

## 8.1 Bestuursorgaan

**Definitie:** formeel CKC-orgaan waaraan bestuurlijke verantwoordelijkheid of beslissingsbevoegdheid is toegekend.

Voorbeelden:

- bestuur;
- dagelijks bestuur (DB).

**Bron:** CKC-statuten, bestuursbesluiten en DVK-register.

---

## 8.2 Bestuurlijke verantwoordelijkheid

**Definitie:** formele verantwoordelijkheid van een bestuursorgaan voor een domein, proces, resource of activiteit.

Voorbeelden:

- verantwoordelijkheid voor ledenadministratie;
- verantwoordelijkheid voor financiële administratie;
- verantwoordelijkheid voor privacygevoelige camerabeelden;
- verantwoordelijkheid voor toegangsbeheer.

**Bron:** statuten, reglementen, bestuursbesluiten en beleid.  
**Canonieke registratie:** **DVK Governance-register**.

**Nieuw in v0.2:** bestuurlijke verantwoordelijkheid wordt niet afgeleid uit technische systeemrechten.

---

# 9. Delegatie en bevoegdheid

## 9.1 Delegatie

**Definitie:** vastlegging dat een bevoegde actor een bevoegdheid toekent aan een andere actor, bij voorkeur aan een functie.

```text
Bestuursorgaan
      │
      └── delegeert
             │
             ▼
        Bevoegdheid
             │
             └── aan
                  ▼
               Functie
```

| Gegeven | Beoogde bron |
|---|---|
| Delegerende actor | DVK Governance-register |
| Bevoegdheid | DVK Governance-register |
| Ontvangende functie/actor | DVK Governance-register |
| Grondslag/besluit | bestuursbesluit/document + DVK-verwijzing |
| Geldig vanaf/tot | DVK Governance-register |

---

## 9.2 Bevoegdheid

**Definitie:** wat een actor bestuurlijk of organisatorisch namens CKC mag doen.

Een bevoegdheid wordt logisch beschreven door ten minste:

```text
Actor/Functie
+ Handeling
+ Resource of domein
+ Scope
+ Geldigheidsperiode
+ Grondslag
```

Voorbeeld:

> De functie Ledenadministrateur mag persoonsgegevens van leden beheren binnen de CKC-ledenadministratie.

**Primaire bron:** **DVK Governance-register**.

Dit is een nieuw CKC-register; huidige operationele systemen bevatten vooral technische rechten, niet de bestuurlijke grondslag daarvan.

---

## 9.3 Bevoegdheidsgrondslag

**Definitie:** formele reden waarom een bevoegdheid bestaat.

Mogelijke grondslagen:

- statuten;
- reglement;
- bestuursbesluit;
- vastgesteld beleid;
- expliciete delegatie.

**Bron:** CKC-documentatie.  
**Indexering en canonieke verwijzing:** DVK.

---

# 10. Resources en handelingen

## 10.1 Resource

**Definitie:** door of namens CKC beheerd object waarop gecontroleerde handelingen kunnen worden uitgevoerd.

### Logische resourcecategorieën

| Categorie | Voorbeelden |
|---|---|
| Informatiesysteem | Sportlink, Sponsit, kassasysteem, TapKey |
| Gegevensverzameling | ledengegevens, camerabeelden, financiële gegevens |
| Fysiek object | clubgebouw, bestuurskamer, materiaalruimte |
| Installatie | camera-installatie, veldverlichting, toegangsinstallatie |

**Canonieke catalogus:** **DVK Resource-register**.

Operationele systemen blijven bron voor hun eigen technische objecten en toestand.

---

## 10.2 Handeling

**Definitie:** gecontroleerde activiteit die op of met een Resource kan worden uitgevoerd.

Voorbeelden:

- bekijken;
- wijzigen;
- toevoegen;
- verwijderen;
- exporteren;
- configureren;
- gebruikers beheren;
- toegangsrechten beheren;
- verkoop registreren;
- rapportage bekijken;
- installatie in-/uitschakelen.

**Canonieke catalogus:** DVK.

---

## 10.3 Resource-handeling

**Definitie:** geldige combinatie van Resource en Handeling waarop bevoegdheden en autorisaties kunnen worden gebaseerd.

Voorbeelden:

```text
Ledenadministratie + bekijken
Ledenadministratie + wijzigen
Camerabeelden + terugkijken
Camerabeelden + exporteren
Kassasysteem + tarieven wijzigen
TapKey + toegangsrechten beheren
Veldverlichting + configureren
```

**Bron:** DVK Resource-register, mede gevoed door mogelijkheden van de operationele systemen.

---

## 10.4 Beschermingsgrond

**Definitie:** reden waarom toegang tot of gebruik van een Resource gecontroleerd moet worden.

Mogelijke classificaties:

- privacy;
- financieel;
- veiligheid;
- operationele continuïteit;
- vertrouwelijkheid;
- bestuurlijke gevoeligheid.

Eén Resource kan meerdere beschermingsgronden hebben.

**Bron:** DVK Resource-register / CKC-beleid.

---

# 11. Autorisatie en feitelijke toegang

## 11.1 Autorisatie

**Definitie:** toegekend technisch of fysiek recht waarmee een actor een bepaalde handeling op een Resource mag uitvoeren.

```text
Bevoegdheid
     │
     └── rechtvaardigt gewenste
                    │
                    ▼
                Autorisatie
```

Voorbeelden:

- Sportlink-account met ledenadministratierechten;
- TapKey-beheerrecht;
- toegang tot camerabeelden;
- beheerrecht kassasysteem.

### Bronnen

De bron is in beginsel het systeem dat de autorisatie technisch beheert:

| Resource | Mogelijke autorisatiebron |
|---|---|
| Sportlink | Sportlink |
| Sponsit | Sponsit |
| TapKey | TapKey |
| Camerasysteem | camerasysteem |
| Kassasysteem | kassasysteem |
| Veldverlichting | besturingssysteem veldverlichting |
| Overige resources | relevant systeem / DVK-register |

**Belangrijk:** de aanwezigheid van een autorisatie bewijst niet dat een geldige CKC-bevoegdheid bestaat.

---

## 11.2 Gewenste autorisatie

**Definitie:** autorisatie die op grond van een geldige functie en bevoegdheid aanwezig zou moeten zijn.

**Bron:** DVK-afleiding uit:

```text
Functievervulling
+ Bevoegdheid
+ Resource
+ Handeling
+ Geldigheid
```

---

## 11.3 Feitelijke toegang

**Definitie:** toegang of handelingsmogelijkheid die technisch of fysiek daadwerkelijk bestaat.

De bron kan zijn:

- actuele gebruikers- en rechtenconfiguratie;
- slot-/toegangssysteem;
- systeem-API;
- periodieke export;
- audit/loggegevens;
- handmatige verificatie indien technische ontsluiting ontbreekt.

**Bron:** operationeel systeem.  
**Consolidatie:** DVK.

---

## 11.4 Autorisatie-afwijking

**Definitie:** geconstateerd verschil tussen geldige bevoegdheid, gewenste autorisatie, aanwezige autorisatie en/of feitelijke toegang.

Voorbeelden:

### Onterechte toegang

```text
Geldige bevoegdheid:      NEE
Aanwezige autorisatie:     JA
Feitelijke toegang:        JA
```

### Ontbrekende toegang

```text
Geldige bevoegdheid:       JA
Gewenste autorisatie:      JA
Aanwezige autorisatie:     NEE
```

**Bron:** DVK-afleiding.  
**Opvolging:** DVK-workflow/audittrail.

---

# 12. Temporaliteit

## 12.1 Geldigheidsperiode

**Definitie:** periode waarin een relatie, toekenning, regel of kwalificatie geldig is.

Conceptueel:

```text
geldig vanaf
geldig tot
```

Dit principe geldt onder meer voor:

- lidmaatschap;
- voetbaldeelname;
- teamrelaties;
- functievervulling;
- delegatie;
- bevoegdheid;
- autorisatie;
- vrijstelling;
- contract;
- beleidsregel.

**Ontwerpbesluit:** historie wordt niet overschreven wanneer reconstructie van de oude situatie relevant is.

---

## 12.2 Registratie- versus geldigheidstijd

Waar nodig moet later technisch onderscheid kunnen worden gemaakt tussen:

- **geldigheidstijd:** wanneer was het feit in de werkelijkheid geldig?
- **registratietijd:** wanneer wist of registreerde CKC/DVK dit?

Dit onderscheid wordt nog niet als verplicht fysiek veld uitgewerkt, maar het logisch model sluit het expliciet niet uit.

---

# 13. Beleidsregels, afleidingen en signaleringen

## 13.1 Beleidsregel

**Definitie:** door CKC vastgestelde regel waarmee uit bronfeiten een kwalificatie, verplichting, bevoegdheid of ander beleidsgevolg volgt.

Voorbeelden:

- trainer moet CKC-lid zijn;
- kwalificerende functie geeft Ledendienstvrijstelling;
- ouder/verzorger voert Ledendienst uit voor het eerste minderjarige kind;
- bepaalde functie vereist bepaalde autorisaties.

**Bron:** CKC-beleid.  
**Machineleesbare representatie:** DVK-beleidsregister.

---

## 13.2 Afgeleid feit

**Definitie:** gegeven dat reproduceerbaar uit bronfeiten en/of beleidsregels kan worden berekend.

Voorbeelden:

- persoon kwalificeert als vrijwilliger;
- persoon heeft Ledendienstplicht;
- persoon heeft een afgeleide bevoegdheid via een functie;
- autorisatie behoort aanwezig te zijn.

Een afgeleid feit moet herleidbaar zijn naar gebruikte bronfeiten en regelversie.

---

## 13.3 Signalering

**Definitie:** door het DVK vastgestelde situatie die menselijke aandacht of actie vraagt.

Voorbeelden:

- autorisatie zonder geldige bevoegdheid;
- nieuwe functionaris zonder benodigde autorisatie;
- verlopen functievervulling met nog actieve systeemrechten;
- ontbrekende brongegevens;
- conflicterende brongegevens.

Een signalering is geen bronfeit over de werkelijkheid, maar een DVK-resultaat.

---

# 14. Bronnenmatrix

| Logisch object | Primaire bron vandaag | DVK-rol | Gap / aandachtspunt |
|---|---|---|---|
| Persoon – lid | Sportlink | consolideren/identificeren | cross-source identiteit |
| Persoon – sponsorcontact | Sponsit | consolideren | koppeling met dezelfde persoon elders |
| Organisatie – sponsor | Sponsit | consolideren | canonieke organisatie-ID |
| Overige organisatie | divers | registreren | geen uniforme bron |
| Lidmaatschap | Sportlink | interpreteren/historiseren | historie deels elders |
| Voetbaldeelname | Sportlink | consolideren | recreatieve lokale indeling |
| Team | Sportlink | consolideren | lokale teams correct mappen |
| Functie | Sportlink + CKC | canonieke catalogus | niet alle functies in Sportlink |
| Functievervulling | Sportlink + CKC | consolideren/historiseren | beheerfuncties ontbreken centraal |
| Vrijwilligerswerk | Sportlink + afleiding | afleiden | betekenis niet gelijk aan één Sportlink-status |
| Ledendienstverplichting | Sportlink + beleid | afleiden/controleren | regelgrondslag expliciteren |
| Ledendienstuitvoering | Sportlink | koppelen | koppeling uitvoerder-verplichting |
| Bardienstplanning | Sportlink | lezen | voetbal.nl is communicatiekanaal |
| Taakuren | Sportlink vrijwilligersmodule | lezen/controleren | historie/kwaliteit |
| Ouder-/verzorgerrelatie | Sportlink waar aanwezig | consolideren | volledigheid onderzoeken |
| Vrijstelling | Sportlink + beleid | verklaren | reden en regelversie bewaren |
| Bestuursorgaan | CKC-documentatie | registreren | eigen register nodig |
| Bestuurlijke verantwoordelijkheid | CKC-documentatie | registreren | eigen register nodig |
| Delegatie | bestuursbesluiten/beleid | registreren | **nieuwe DVK-bron nodig** |
| Bevoegdheid | beleid/delegatie | registreren/afleiden | **nieuwe DVK-bron nodig** |
| Bevoegdheidsgrondslag | CKC-documenten | verwijzen/indexeren | documenten koppelen |
| Resource | diverse systemen | catalogiseren | **nieuw Resource-register** |
| Handeling | diverse systemen/beleid | catalogiseren | canonieke normalisatie |
| Beschermingsgrond | CKC-beleid | registreren | nieuwe classificatie |
| Autorisatie | operationeel systeem | verzamelen | API/exportmogelijkheden verschillen |
| Gewenste autorisatie | DVK | afleiden | regels per functie/resource nodig |
| Feitelijke toegang | operationeel systeem | verzamelen/controleren | technische ontsluiting onderzoeken |
| Autorisatie-afwijking | DVK | signaleren | workflow/audittrail nodig |
| Beleidsregel | CKC-beleid | versieerbaar registreren | machineleesbare representatie |
| Signalering | DVK | genereren | opvolging en status nodig |
| Sponsorgegevens | Sponsit | integreren | buiten ledenmodel houden waar passend |
| Contract sponsor | Sponsit | integreren | relatie met organisatie/persoon |
| Historische ledengegevens | Access + Sportlink | migreren/consolideren | bronkwaliteit en overlap |

---

# 15. Logische relaties

De belangrijkste relaties in v0.2 zijn:

```text
Persoon ── heeft ──> Lidmaatschap

Persoon ── neemt deel via ──> Voetbaldeelname
Voetbaldeelname ── betreft ──> Team/Groep

Persoon ── vervult ──> Functie
Functievervulling ── heeft ──> Geldigheidsperiode

Persoon ── is ouder/verzorger van ──> Persoon

Persoon/Lid ── heeft ──> Ledendienstverplichting
Persoon ── verricht ──> Ledendienstuitvoering
Ledendienstuitvoering ── vervult ──> Ledendienstverplichting

Bestuursorgaan ── draagt ──> Bestuurlijke verantwoordelijkheid
Bestuursorgaan ── verleent/delegeert ──> Bevoegdheid
Bevoegdheid ── wordt toegekend aan ──> Functie
Persoon ── verkrijgt via functievervulling ──> Bevoegdheid

Bevoegdheid ── betreft ──> Handeling
Handeling ── wordt uitgevoerd op ──> Resource
Resource ── heeft ──> Beschermingsgrond

Bevoegdheid ── rechtvaardigt ──> Gewenste autorisatie
Operationeel systeem ── registreert ──> Autorisatie
Operationeel systeem ── bepaalt/toont ──> Feitelijke toegang

DVK ── vergelijkt ──> Bevoegdheid
DVK ── vergelijkt ──> Gewenste autorisatie
DVK ── vergelijkt ──> Aanwezige autorisatie
DVK ── vergelijkt ──> Feitelijke toegang
DVK ── genereert ──> Signalering
```

---

# 16. Eigenaarschap en bronautoriteit

## 16.1 Bestuurlijke bronautoriteit

De aanwezigheid van data in een operationeel systeem maakt dat systeem niet automatisch bestuurlijk autoritatief.

Voorbeeld:

```text
Sportlink zegt: account heeft beheerdersrecht
```

betekent uitsluitend:

```text
technische autorisatie bestaat
```

en niet automatisch:

```text
bestuur heeft deze persoon geldig bevoegd verklaard
```

---

## 16.2 Domeinbron versus canonieke bron

Het DVK wordt niet noodzakelijk de operationele bron van alle gegevens.

Het fungeert als:

- canonieke integratielaag;
- register voor CKC-specifieke feiten die elders ontbreken;
- regel- en afleidingslaag;
- controlelaag;
- audit- en signaleringslaag.

---

## 16.3 Voorgestelde bronhiërarchie

Bij conflicten wordt niet één universele bronvolgorde gebruikt. Bronautoriteit wordt per gegevenstype vastgesteld.

Voorbeelden:

| Gegeven | Leidende bron |
|---|---|
| Actueel formeel lidmaatschap | Sportlink |
| Actuele KNVB-relatie | Sportlink/KNVB |
| Sponsorcontract | Sponsit |
| CKC-bevoegdheidsdelegatie | DVK Governance-register op basis van CKC-besluit |
| Sportlink-autorisatie | Sportlink |
| TapKey-autorisatie | TapKey |
| Canonieke persoonskoppeling | DVK |
| DVK-signalering | DVK |

---

# 17. Nieuwe DVK-registers

De uitbreiding van het canonieke model maakt duidelijk dat het DVK een aantal eigen registers nodig heeft.

## 17.1 Canoniek Identiteitsregister

Doel:

- personen uit meerdere bronnen herkennen en koppelen;
- canonieke persoons-ID uitgeven;
- bronidentificaties bewaren;
- organisaties op vergelijkbare wijze identificeren.

---

## 17.2 Functiecatalogus

Doel:

- canonieke CKC-functies definiëren;
- bronsysteemfuncties daarop mappen;
- onderscheid maken tussen functie en functievervulling.

---

## 17.3 Governance-register

Doel:

- bestuursorganen;
- verantwoordelijkheidsdomeinen;
- delegaties;
- bevoegdheden;
- grondslagen;
- geldigheidsperioden

expliciet vastleggen.

---

## 17.4 Resource-register

Doel:

- systemen;
- gegevensverzamelingen;
- fysieke objecten;
- installaties;
- toegestane handelingen;
- beschermingsgronden

canoniek beschrijven.

---

## 17.5 Autorisatie-mapping

Doel:

de relatie vastleggen tussen:

```text
Functie
→ Bevoegdheid
→ Resource
→ Handeling
→ benodigde technische autorisatie
```

Hierdoor kan het DVK bepalen welke autorisaties bij een functievervulling behoren.

---

## 17.6 Beleidsregister

Doel:

- CKC-beleidsregels versieerbaar vastleggen;
- afleidingen reproduceerbaar maken;
- geldigheidsperioden van regels bewaren;
- de grondslag van beleidsgevolgen verklaren.

---

## 17.7 Audit- en signaleringsregister

Doel:

- gevonden afwijkingen vastleggen;
- datum/tijd van constatering bewaren;
- gebruikte bronfeiten registreren;
- opvolging en verantwoordelijke vastleggen;
- afsluiting en reden documenteren.

---

# 18. Belangrijkste gaps ten opzichte van het canonieke model

## 18.1 Governance is niet centraal als data beschikbaar

De huidige operationele systemen registreren vooral hun eigen gebruikers en rechten. Er is nog geen centrale, machineleesbare registratie van:

```text
wie
op grond waarvan
welke bevoegdheid
aan welke functie
voor welke resource en handeling
heeft verleend
```

**Oplossingsrichting:** DVK Governance-register.

---

## 18.2 Functies zijn verspreid en semantisch niet uniform

Functies bestaan in Sportlink en andere systemen, maar vormen nog geen uniforme CKC-functiecatalogus.

**Oplossingsrichting:** canonieke Functiecatalogus met bronmapping.

---

## 18.3 Autorisaties zijn per systeem geïsoleerd

Sportlink, TapKey, camera, kassa en verlichting kennen ieder hun eigen toegangsmodel.

**Oplossingsrichting:** geen centrale technische autorisatie-engine bouwen als eerste stap, maar een canonieke **autorisatie-mapping** waarmee rechten uit verschillende systemen vergelijkbaar worden.

---

## 18.4 Feitelijke toegang is nog niet structureel uitleesbaar

Voor diverse systemen moet nog worden onderzocht of actuele gebruikers en rechten via API, export of andere betrouwbare interface beschikbaar zijn.

**Oplossingsrichting:** per Resource een connector-/bronnenonderzoek.

---

## 18.5 Historische geldigheid is onvolledig

Sportlink bewaart niet voor ieder relevant CKC-feit de volledige gewenste historie. Voor lidmaatschap bestaat aanvullende historische informatie in de bestaande Access-database.

**Oplossingsrichting:** historie consolideren in DVK zonder bronherkomst te verliezen.

---

## 18.6 Beleidsregels zijn nog onvoldoende machineleesbaar

CKC-beleid bestaat inhoudelijk, maar is nog niet systematisch vertaald naar versieerbare regels waarmee DVK afleidingen kan reproduceren.

**Oplossingsrichting:** Beleidsregister en later technische regelrepresentatie.

---

# 19. Ontwerpregels

Voor het logisch gegevensmodel gelden vanaf v0.2 de volgende regels:

1. **Persoon en rol/functie worden gescheiden.**
2. **Functie en functievervulling worden gescheiden.**
3. **Lidmaatschap en voetbaldeelname worden gescheiden.**
4. **Bronfeit, afgeleide kwalificatie en beleidsgevolg worden gescheiden.**
5. **Vrijwilligerswerk wordt niet gelijkgesteld aan één Sportlink-status.**
6. **Ledendienstverplichting en Ledendienstuitvoering worden gescheiden.**
7. **Bestuurlijke verantwoordelijkheid en dagelijkse uitvoering worden gescheiden.**
8. **Delegatie en bevoegdheid worden expliciet geregistreerd.**
9. **Bevoegdheid en autorisatie zijn verschillende gegevensobjecten.**
10. **Autorisatie en feitelijke toegang zijn verschillende gegevensobjecten.**
11. **Een bevoegdheid wordt waar mogelijk aan een functie toegekend.**
12. **Een bevoegdheid wordt gekoppeld aan Resource, Handeling, Scope en geldigheid.**
13. **Resources zijn breder dan digitale systemen.**
14. **Bronautoriteit wordt per gegevenstype vastgesteld.**
15. **Een operationeel systeem is niet automatisch de bron van de bestuurlijke waarheid.**
16. **Historische geldigheid wordt bewaard waar reconstructie relevant is.**
17. **Afgeleide gegevens moeten herleidbaar zijn naar bronfeiten en regelversies.**
18. **Het DVK mag eigen CKC-registers bevatten voor canonieke feiten die in bronsystemen ontbreken.**
19. **Bronidentificaties blijven naast canonieke DVK-identificaties bewaard.**
20. **Afwijkingen tussen bevoegdheid, autorisatie en toegang moeten detecteerbaar en auditeerbaar zijn.**

---

# 20. Vervolg

Met v0.2 is de aanscherping uit het Canoniek CKC-informatiemodel v0.5.1 verwerkt in het logisch gegevenswoordenboek en de bronnenmapping.

De logisch volgende uitwerking is nu niet opnieuw een brede modeldiscussie, maar een concretere specificatie van de nieuwe DVK-registers.

Een zinvolle volgorde is:

```text
1. Functiecatalogus
        ↓
2. Governance-register
        ↓
3. Resource- en handelingencatalogus
        ↓
4. Autorisatie-mapping
        ↓
5. Connectoren naar operationele systemen
        ↓
6. Afwijkings- en signaleringslogica
```

Daarmee ontstaat tevens een geschikte basis voor een eerste zichtbaar DVK-prototype:

```text
Persoon
  ├── relaties
  ├── functies
  ├── bevoegdheden
  ├── gewenste autorisaties
  ├── aanwezige autorisaties/toegang
  └── signaleringen
```

Dit prototype kan vervolgens worden gebruikt om het canonieke model, het logisch gegevensmodel én de bronnenmapping aan de werkelijkheid te toetsen voordat een definitief fysiek datamodel wordt ontworpen.
