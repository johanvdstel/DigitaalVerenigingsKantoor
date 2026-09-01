# CKC Informatiemodel

Deze map bevat de samenhangende ontwerpdocumenten voor het informatiemodel van het **Digitaal Verenigingskantoor (DVK)** van CKC.

De documenten zijn iteratief ontstaan. Daardoor vertegenwoordigen zij **niet allemaal exact hetzelfde moment in het voortschrijdend inzicht**. Dat is bewust geen probleem: oudere deelmodellen en analyses blijven waardevol als onderbouwing en ontwerpgeschiedenis.

Voor de actuele richting geldt het **Canoniek Informatiemodel v0.5.1** als leidend. Waar oudere documenten daarvan afwijken, prevaleert het Canoniek Informatiemodel, tenzij expliciet anders vermeld.

---

## Inhoudsopgave

1. [Documenten in deze map](#1-documenten-in-deze-map)
2. [Onderlinge samenhang](#2-onderlinge-samenhang)
3. [Welke documenten zijn leidend?](#3-welke-documenten-zijn-leidend)
4. [Voortschrijdend inzicht](#4-voortschrijdend-inzicht)
5. [Belangrijkste ontwerpprincipes](#5-belangrijkste-ontwerpprincipes)
6. [Bronnen en DVK-datalaag](#6-bronnen-en-dvk-datalaag)
7. [Huidige stand](#7-huidige-stand)
8. [Vervolg](#8-vervolg)
9. [Versiebeheer](#9-versiebeheer)

---

## 1. Documenten in deze map

| Bestand | Versie | Rol | Status ten opzichte van actuele model |
|---|---:|---|---|
| [`Canoniek_Informatiemodel.md`](./Canoniek_Informatiemodel.md) | v0.5.1 | Overkoepelend canoniek begrippen- en relatiemodel | **Leidend** |
| [`gegevenswoordenboek-bronnenmapping.md`](./gegevenswoordenboek-bronnenmapping.md) | v0.2 | Logische begrippen, gegevensbetekenis en mapping naar bronnen | **Actuele uitwerking van v0.5.1** |
| [`gap-analyse.md`](./gap-analyse.md) | v0.1 | Analyse van verschillen tussen gewenste situatie en huidige bronnen/registraties | Onderbouwend; deels ingehaald door latere keuzes |
| [`logisch-informatiemodel.md`](./logisch-informatiemodel.md) | v0.2 | Eerdere logische structurering van entiteiten en relaties | Onderbouwend; nog niet volledig bijgewerkt naar v0.5.1 |
| [`personenmodel.md`](./personenmodel.md) | v0.2.1 | Verdieping van persoon, relaties, rollen en CKC-context | Onderbouwend; belangrijke basis voor het canonieke model |
| [`README.md`](./README.md) | huidig | Wegwijzer, samenhang en status van de documentset | **Leidend voor navigatie** |

---

## 2. Onderlinge samenhang

De ontwikkeling van het informatiemodel kan globaal als volgt worden gelezen:

```text
Personenmodel
     │
     │ onderzoekt personen, relaties en rollen
     ▼
Logisch Informatiemodel
     │
     │ structureert begrippen en relaties breder
     ▼
Gap-analyse
     │
     │ vergelijkt gewenste werkelijkheid met
     │ huidige CKC-registraties en bronsystemen
     ▼
Canoniek Informatiemodel
     │
     │ consolideert het voortschrijdend inzicht
     │ en bepaalt de actuele semantische richting
     ▼
Gegevenswoordenboek & Bronnenmapping
     │
     │ vertaalt het canonieke model naar
     │ logische gegevensobjecten en bronnen
     ▼
DVK-ontwerp en prototypes
```

Deze volgorde betekent niet dat ieder document simpelweg een nieuwe versie van het vorige is. De documenten hebben verschillende functies.

Het **Personenmodel**, **Logisch Informatiemodel** en de **Gap-analyse** vormen vooral de analyse- en ontwerpgeschiedenis. Het **Canoniek Informatiemodel** consolideert de huidige begrippen en ontwerpregels. Het **Gegevenswoordenboek & Bronnenmapping** vertaalt die vervolgens richting gegevensvoorziening en implementatie.

---

## 3. Welke documenten zijn leidend?

Bij interpretatie of eventuele tegenstrijdigheid geldt voorlopig de volgende prioriteitsvolgorde:

```text
1. Canoniek_Informatiemodel.md
          ↓
2. gegevenswoordenboek-bronnenmapping.md
          ↓
3. logisch-informatiemodel.md
          ↓
4. personenmodel.md
          ↓
5. gap-analyse.md
```

Deze volgorde zegt niets over de kwaliteit of historische waarde van een document. Zij geeft alleen aan welk document bij verschillen de **meest actuele ontwerpbeslissing** bevat.

Het Canoniek Informatiemodel beschrijft de actuele CKC-begrippen en hun betekenis onafhankelijk van de beperkingen van bestaande systemen. Het Gegevenswoordenboek & Bronnenmapping operationaliseert dit model richting gegevensobjecten, bronnen, gaps en eigen DVK-registers.

De overige documenten blijven belangrijke onderbouwing en ontwerpgeschiedenis. Zij worden niet automatisch herschreven wanneer het canonieke model verandert.

---

## 4. Voortschrijdend inzicht

Het informatiemodel wordt bewust iteratief ontwikkeld.

In plaats van alle documenten bij iedere nieuwe ontdekking direct volledig te synchroniseren, hanteren we voorlopig het volgende principe:

> **Het Canoniek Informatiemodel bevat de actuele semantische waarheid; oudere documenten mogen de redeneer- en ontwerpgeschiedenis blijven tonen.**

Een verschil tussen documenten is daarom niet automatisch een fout.

Wel geldt:

> Een verschil dat tot ambiguïteit bij ontwerp of implementatie kan leiden, moet expliciet worden opgelost voordat daarop software wordt gebouwd.

Wanneer een ouder document inhoudelijk sterk achterloopt of verwarrend wordt, kan een nieuwe versie daarvan worden gemaakt.

---

## 5. Belangrijkste ontwerpprincipes

De huidige documentset heeft geleid tot de volgende centrale principes:

1. **Persoon is niet hetzelfde als rol of functie.** Een persoon kan gelijktijdig meerdere relaties met CKC hebben en meerdere functies vervullen.
2. **Lidmaatschap en voetbaldeelname zijn afzonderlijke feiten.**
3. **Functie en functievervulling zijn afzonderlijke begrippen.**
4. **Bronfeit, afgeleide kwalificatie en beleidsgevolg blijven gescheiden.**
5. **Ledendienstverplichting en Ledendienstuitvoering zijn niet hetzelfde.**
6. **Bestuurlijke verantwoordelijkheid en gedelegeerde uitvoering worden onderscheiden.**
7. **Bevoegdheid, autorisatie en feitelijke toegang zijn verschillende begrippen.**
8. **Resources zijn breder dan informatiesystemen:** ook gegevens, fysieke objecten en installaties kunnen resources zijn.
9. **Tijd is onderdeel van de betekenis:** veranderlijke relaties moeten waar relevant een geldigheidsperiode hebben.

De actuele governance-keten is conceptueel:

```text
Bestuurlijke verantwoordelijkheid
        ↓
Delegatie
        ↓
Bevoegdheid
        ↓
Functie
        ↓
Functievervulling
        ↓
Persoon
        ↓
Gewenste autorisatie
        ↓
Aanwezige autorisatie
        ↓
Feitelijke toegang
```

Het DVK moet afwijkingen tussen deze niveaus uiteindelijk kunnen signaleren.

---

## 6. Bronnen en DVK-datalaag

Het model wordt niet ontworpen als afspiegeling van één bestaand systeem.

Bekende bronnen zijn onder meer:

```text
Sportlink
├── leden
├── voetbaldeelname
├── teams en functies
├── vrijwilligersmodule
├── bardiensten
└── taakuren

Sponsit
├── sponsors
├── sponsorcontacten
├── contracten
├── facturen
├── taken
└── afspraken

Overige operationele systemen
├── TapKey
├── camerasysteem
├── kassasysteem
└── veldverlichting

Historische / aanvullende bronnen
└── bestaande CKC Access-database
```

Niet alle canonieke CKC-feiten bestaan in deze systemen. Daarom voorziet het ontwerp in een eigen **DVK-datalaag**, met onder meer:

- canonieke persoons- en organisatie-identificatie;
- functiecatalogus;
- governance-register;
- resource- en handelingencatalogus;
- autorisatie-mapping;
- beleidsregister;
- audit- en signaleringsregister.

Het DVK vervangt daarmee niet automatisch de operationele bronsystemen. Het voegt gegevens samen, geeft er canonieke betekenis aan en registreert CKC-specifieke feiten waarvoor elders geen geschikte bron bestaat.

---

## 7. Huidige stand

### Relatief volwassen

- personen en organisaties;
- lidmaatschap;
- voetbaldeelname;
- functies en functievervulling;
- vrijwilligerswerk;
- Ledendienst;
- onderscheid bronfeit / afleiding / beleidsgevolg.

### Recent toegevoegd en nog verder te toetsen

- bestuurlijke verantwoordelijkheid;
- delegatie;
- bevoegdheid;
- resources en handelingen;
- autorisatie;
- feitelijke toegang;
- generieke temporaliteit;
- automatische signalering van afwijkingen.

Deze nieuwe governance- en autorisatielaag is opgenomen in:

- `Canoniek_Informatiemodel.md` v0.5.1;
- `gegevenswoordenboek-bronnenmapping.md` v0.2.

De oudere documenten zijn hier nog niet volledig op aangepast.

---

## 8. Vervolg

De documentset is inmiddels voldoende volwassen om naast verdere modellering ook een eerste kleine softwarematige toets uit te voeren.

De beoogde vervolgrichting is een **DVK Prototype v0.1 – Persoon & Bevoegdheden**.

Een eerste prototype kan voor een testpersoon zichtbaar maken:

```text
Persoon
  ├── relaties
  ├── functies
  ├── bevoegdheden
  ├── gewenste autorisaties
  ├── aanwezige autorisaties / toegang
  └── signaleringen
```

Het prototype gebruikt in eerste instantie een kleine testdataset en hoeft nog niet live met Sportlink, TapKey of andere operationele systemen te integreren.

Doel is eerst vast te stellen of het canonieke en logische model zich daadwerkelijk goed laat vertalen naar begrijpelijke software. De uitkomsten van die praktijktest kunnen vervolgens terugvloeien naar het informatiemodel.

---

## 9. Versiebeheer

De bestanden in deze map behouden bij voorkeur een **stabiele bestandsnaam**. Het versienummer wordt in het document zelf bijgehouden.

Bijvoorbeeld:

```text
Canoniek_Informatiemodel.md
```

kan achtereenvolgens v0.5, v0.5.1, v0.6 enzovoort bevatten.

Git bewaart via de commitgeschiedenis de eerdere versies. Daardoor blijven interne Markdown-links stabiel en hoeft andere documentatie niet bij iedere versie te worden aangepast.

Bij iedere relevante modelwijziging wordt in de commit message kort aangegeven welk voortschrijdend inzicht of welke ontwerpbeslissing is verwerkt.
