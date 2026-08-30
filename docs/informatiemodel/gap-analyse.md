# CKC Gap-analyse v0.1

**Project:** Digitaal Verenigingskantoor  
**Domein:** Ledenadministratie / Informatiemodel  
**Status:** Werkdocument  
**Versie:** 0.1  
**Datum:** 30 augustus 2026

## 1. Doel

Deze gap-analyse toetst of de tot nu toe ontworpen lagen van het Digitaal Verenigingskantoor onderling consistent zijn:

**CKC-begrippen → logisch informatiemodel → proces → functies → gegevens → bronnen**

Centrale toetsvraag:

> Kan ieder relevant feit over een persoon en diens relatie met CKC eenduidig worden verklaard vanuit het informatiemodel, ontstaan of veranderen via een herkenbaar proces, worden ondersteund door een functie en worden herleid tot een gezaghebbende bron?

De analyse kijkt vanuit het gewenste CKC-model. Sportlink, Access, Dropbox, Excel en andere systemen zijn bronnen en implementaties; hun huidige inrichting bepaalt niet wat een CKC-begrip betekent.

## 2. Uitgangspunten en correcties

Naar aanleiding van de review op de eerste gap-analyse gelden de volgende aangescherpte uitgangspunten:

1. **Een trainer bij CKC is altijd lid van CKC.** Het model hoeft dus geen operationele CKC-situatie te ondersteunen waarin een trainer geen lid is. Wel blijven `lidmaatschap` en `functievervulling` afzonderlijke begrippen: het lidmaatschap is de relatie met de vereniging; trainer is een functie die een lid gedurende een bepaalde periode kan vervullen.
2. **Lidmaatschap van een CKC-commissie is vrijwilligerswerk.** Een commissierelatie is een specifieke vorm van vrijwilligerswerk. Niet ieder vrijwilligerswerk is echter commissiewerk, bijvoorbeeld een bardienst.
3. **Bardiensten:** Sportlink is het leidende systeem voor registratie en planning. De Voetbal.nl-app is het kanaal voor registratie/interactie en communicatie richting gebruikers. De eigen CKC-roostergenerator wordt uitsluitend voor aanvullende communicatie gebruikt.
4. **Eigen CKC-datalaag:** het Digitaal Verenigingskantoor krijgt een eigen CKC-register/datalaag. Dit register kan voor gegevens die bestaande bronsystemen niet volledig of duurzaam beheren zelf de gezaghebbende CKC-registratie worden.

## 3. Samenvatting

De fundamentele structuur van het personenmodel en logisch informatiemodel houdt stand. De belangrijkste gaps liggen in tijd/historie, formele kwalificaties, brongezag, beleidsregels en procesdekking.

| ID | Bevinding | Classificatie | Prioriteit |
|---|---|---|---|
| G01 | Historie van relaties is niet uniform beschikbaar | GAP | Hoog |
| G02 | Functievervulling mist structurele historie in Sportlink | GAP | Hoog |
| G03 | Erelid en lid van verdienste zijn semantisch onzuiver geïmplementeerd | CONFLICT | Hoog |
| G04 | `Status lidmaatschap` vermengt verschillende soorten informatie | CONFLICT | Hoog |
| G05 | Brongezag is nog niet per gegeven formeel vastgesteld | AMBIGU | Hoog |
| G06 | Beleidsbesluiten zijn nog geen uitvoerbare beleidsregels | GAP | Hoog |
| G07 | Ouder-/verzorgerrelatie is in Sportlink contextgebonden | ONBEDEKT | Midden |
| G08 | Teamhistorie is afhankelijk van lidcategorie | CONFLICT | Midden |
| G09 | Commissies worden in Sportlink ook als technisch classificatiemechanisme gebruikt | CONFLICT | Midden |
| G10 | Contractuele relaties buiten sponsoring zijn nog niet functioneel uitgewerkt | ONBEDEKT | Midden |
| G11 | Leveranciersinformatie is verdeeld over Dropbox en Excel | GAP | Midden |
| G12 | Vrijwilligerswerk en bardienst vragen om heldere semantische relaties | AMBIGU | Midden |
| G13 | Bronfeit, afgeleide kwalificatie en beleidsgevolg zijn operationeel nog niet overal gescheiden | GAP | Hoog |
| G14 | Procesdekking is sterk voor instroom, maar nog beperkt voor mutatie en uitstroom | ONBEDEKT | Hoog |

## 4. Bevindingen

### G01 — Historie als ontwerpprincipe

Sportlink bewaart historische teamdeelname alleen voor bondsleden en geen historie van functievervulling. Access bevat historische informatie over clublidmaatschap en functies.

**Gap:** CKC-historie is afhankelijk van beperkingen van het bronsysteem.

**Ontwerprichting:** relaties die in de tijd veranderen moeten in het canonieke CKC-model tijdgebonden kunnen worden vastgelegd, minimaal met begin- en eindmoment waar dat betekenisvol is. De eigen CKC-datalaag moet duurzame historie kunnen bewaren.

### G02 — Historische functievervulling

Sportlink registreert actuele functies, maar bewaart de historie daarvan niet. Access bevat een deel van de historische functies.

**Gap:** er bestaat geen complete duurzame bron voor historische functievervulling.

**Ontwerprichting:** het CKC-register wordt kandidaat voor de gezaghebbende registratie van functievervulling door de tijd. Voor trainers geldt daarbij de CKC-regel dat een trainer tevens lid moet zijn; `trainer` blijft desondanks een afzonderlijke functievervulling en wordt niet onderdeel van het begrip lidmaatschap.

### G03 — Erelid en lid van verdienste

Erelid wordt vastgelegd in het vrije veld `Status lidmaatschap`. Lid van verdienste wordt vastgelegd via een speciaal daarvoor gecreëerde commissie.

**Gap:** twee inhoudelijk vergelijkbare CKC-kwalificaties worden technisch als verschillende soorten objecten gerepresenteerd.

**Ontwerprichting:** beide worden in het canonieke model als formele CKC-kwalificatie/onderscheiding gemodelleerd, eventueel met datum en besluitgrondslag. De Sportlink-weergave wordt een mapping, niet de semantische definitie.

### G04 — Semantische vervuiling van `Status lidmaatschap`

Het vrije veld bevat waarden die betrekking hebben op verschillende dimensies, zoals recreatief, vrijwilliger, Old Star, reservespeler, erelid en overleden.

**Gap:** één technisch veld vermengt persoonsfeiten, deelname, vrijwilligerswerk, kwalificaties en andere statussen.

**Ontwerprichting:** `Status lidmaatschap` wordt geen canoniek CKC-begrip. Bestaande waarden worden bij integratie gemapt naar de juiste begrippen.

### G05 — Gezaghebbende bron

De huidige informatie is verdeeld over meerdere systemen:

| Informatie | Huidige registratie |
|---|---|
| Contributie | Sportlink |
| Actuele ledengegevens | hoofdzakelijk Sportlink |
| Historisch lidmaatschap | deels Access |
| Historische functies | Access |
| Leveranciers/contractdocumentatie | Dropbox |
| Leveranciersadministratie financieel | Excel |
| Vrijwilligers/bardiensten | Sportlink |
| Bardienstinteractie/communicatie | Voetbal.nl |
| Aanvullende bardienstcommunicatie | eigen CKC-roostergenerator |
| Bestuurs-/ALV-besluiten | Dropbox |

**Gap:** aanwezigheid van gegevens in een systeem is nog niet hetzelfde als formeel brongezag.

**Ontwerprichting:** per canoniek gegeven wordt vastgesteld welk systeem/register de gezaghebbende bron is. De eigen CKC-datalaag kan daarbij zelf System of Record zijn.

### G06 — Beleidsbesluit versus uitvoerbare beleidsregel

CKC-beleid is gebaseerd op statuten en besluiten van bestuur en ledenvergadering, met notulen/documenten in Dropbox.

**Gap:** een formeel besluit is nog geen expliciete machine-uitvoerbare regel.

**Ontwerprichting:** onderscheid maken tussen bronbesluit, geïnterpreteerde beleidsregel, machine-uitvoerbare representatie en toegepast beleidsgevolg. De oorspronkelijke besluitvorming blijft de grondslag.

### G07 — Ouder-/verzorgerrelatie

Sportlink verplicht voor spelende leden onder 16 jaar minimaal één ouder/verzorger met naam, e-mail en telefoon.

**Gap:** de registratieverplichting van Sportlink is contextgebonden en mag niet de definitie van de relatie bepalen.

**Ontwerprichting:** ouder/verzorger blijft een zelfstandige persoonsrelatie in het CKC-model. Leeftijd en voetbaldeelname kunnen bepalen wanneer registratie verplicht is.

### G08 — Historische teamdeelname

Sportlink bewaart teamhistorie alleen voor bondsleden.

**Gap:** historische CKC-teamdeelname wordt technisch verschillend behandeld naar gelang de lidcategorie.

**Ontwerprichting:** CKC bepaalt zelf welke teamhistorie relevant is. Het CKC-register moet relevante historische teamdeelname kunnen bewaren, ook wanneer Sportlink dat niet doet.

### G09 — Commissie als technisch classificatiemechanisme

Sportlink bevat echte CKC-commissies, maar ook een kunstmatige commissie voor `Lid van verdienste`.

**Gap:** uit een Sportlink-commissielidmaatschap kan niet zonder mapping worden afgeleid dat daadwerkelijk sprake is van commissiewerk.

**Ontwerprichting:** onderscheid tussen echte organisatorische commissies en technische Sportlink-constructies. Een echte commissierelatie is in CKC een specifieke vorm van vrijwilligerswerk.

### G10 — Contractuele relaties

CKC heeft vele overeenkomsten buiten sponsoring, waaronder leverancierscontracten en overeenkomsten met trainers. Deze worden in Dropbox bewaard.

**Gap:** contractuele relaties zijn nog niet functioneel uitgewerkt binnen de huidige ledenadministratiescope.

**Ontwerprichting:** nog niet volledig uitwerken, maar het canonieke informatiemodel mag toekomstige contract- en leveranciersprocessen niet blokkeren. Voor trainers moet tevens rekening worden gehouden met de CKC-regel dat zij lid zijn.

### G11 — Leveranciers

Leveranciersinformatie/documentatie staat in Dropbox; de financiële leveranciersadministratie wordt in Excel bijgehouden.

**Gap:** gegevens over dezelfde externe relatie zijn verdeeld over verschillende bronnen zonder nog vastgelegd canoniek brongezag.

**Ontwerprichting:** opnemen in de bronnenmapping en later bepalen welke kerngegevens in het CKC-register thuishoren.

### G12 — Vrijwilligerswerk, commissies en bardiensten

Een echte commissierelatie is per definitie vrijwilligerswerk. Vrijwilligerswerk is echter breder: iemand kan bijvoorbeeld een bardienst uitvoeren zonder commissielid te zijn.

Voor bardiensten geldt:
- Sportlink: registratie en planning;
- Voetbal.nl: gebruikersinteractie/registratie en communicatie;
- CKC-roostergenerator: uitsluitend aanvullende communicatie.

**Gap:** de begrippen vrijwilligerswerk, vrijwilligersrol, commissierelatie en bardienst moeten hiërarchisch en functioneel scherp worden verbonden.

**Ontwerprichting:** `vrijwilligerswerk` als overkoepelend concept, met specifieke vormen zoals commissiewerk en bardienst waar relevant. Niet iedere eenmalige vrijwilligersactiviteit hoeft een duurzame functievervulling te zijn.

### G13 — Bronfeit → kwalificatie → beleidsgevolg

Het personenmodel onderscheidt bronfeiten, afgeleide kwalificaties en beleidsgevolgen. De huidige Sportlink-inrichting vermengt deze lagen regelmatig.

**Gap:** de conceptuele scheiding is nog niet overal operationeel afdwingbaar.

**Ontwerprichting:** het CKC-register en de toekomstige regellaag moeten de redeneerketen reproduceerbaar maken: bronfeiten → regel → kwalificatie → beleidsgevolg.

### G14 — Procesdekking

Het proces- en functioneel ontwerp is vooral gedetailleerd voor `nieuw-lid-aanmelden`. Het informatiemodel kent veel meer veranderingen gedurende de levenscyclus.

Voorbeelden zijn functiewijziging, teamwisseling, commissie toetreden/verlaten, onderscheiding, opzegging, herintreding en overlijden.

**Gap:** mutatie- en uitstroomprocessen zijn nog onvoldoende systematisch tegen het informatiemodel getoetst.

**Ontwerprichting:** vóór het fysieke gegevensmodel de belangrijkste toestandsovergangen expliciet toetsen.

## 5. Bevestigde ontwerpprincipes

De gap-analyse bevestigt de volgende principes:

- Persoon en lid zijn verschillende begrippen.
- Lidmaatschap en voetbaldeelname zijn verschillende begrippen.
- Voetbaldeelname verdient een zelfstandige modellering.
- Functievervulling en lidmaatschap zijn verschillende begrippen, ook wanneer CKC-beleid vereist dat een functie uitsluitend door leden wordt vervuld.
- Een commissierelatie is een specifieke vorm van vrijwilligerswerk; vrijwilligerswerk is breder dan commissiewerk.
- Bronfeit, afgeleide kwalificatie en beleidsgevolg moeten gescheiden blijven.
- Sportlink is een belangrijk bronsysteem, maar niet het CKC-informatiemodel.
- Het Digitaal Verenigingskantoor krijgt een eigen CKC-datalaag/register.

## 6. Architectuurconclusie

Het Digitaal Verenigingskantoor wordt niet uitsluitend een intelligente laag die bestaande systemen uitleest. Het krijgt een eigen CKC-datalaag/register.

De rol van dit register verschilt per gegeven:
- voor sommige gegevens is Sportlink de gezaghebbende bron en bevat het CKC-register een gesynchroniseerde representatie;
- voor andere gegevens kan het CKC-register zelf de gezaghebbende bron worden, bijvoorbeeld wanneer bestaande systemen noodzakelijke historie of semantiek niet duurzaam ondersteunen;
- afgeleide kwalificaties en beleidsgevolgen moeten herleidbaar blijven tot bronfeiten en regels.

De precieze bronverantwoordelijkheid wordt in het vervolgontwerp per gegeven vastgesteld.

## 7. Vervolgstap

De volgende ontwerpstap is:

**Stap 5 — Canoniek CKC-informatiemodel v0.3**

Daarin wordt voor de kernbegrippen expliciet vastgelegd:

1. betekenis en definitie;
2. onderlinge relaties;
3. onderscheid tussen bronfeit, kwalificatie en beleidsgevolg;
4. tijdgebondenheid en historie;
5. mutatie/verantwoordelijkheid;
6. gezaghebbende bron;
7. rol van het CKC-register;
8. relevante CKC-beleidsregels en constraints.

Pas na deze stap wordt het fysieke/technische gegevensmodel ontworpen.

---

## 8. Openstaande ontwerpvragen voor v0.3

De gap-analyse reduceert de onzekerheden, maar laat een beperkt aantal ontwerpvragen bewust open:

- Voor welke gegevens wordt het CKC-register zelf System of Record?
- Welke historische relaties wil CKC duurzaam bewaren en met welke granulariteit?
- Hoe modelleren we formele onderscheidingen en hun besluitgrondslag?
- Welke typen vrijwilligerswerk verdienen een duurzame relatie/functievervulling en welke slechts een activiteitregistratie?
- Welke beleidsregels worden als expliciete, machine-uitvoerbare regels opgenomen?
- Welke mutatie- en uitstroomprocessen moeten vóór het technische model minimaal zijn uitgewerkt?

Deze vragen vormen directe input voor Canoniek CKC-informatiemodel v0.3.
