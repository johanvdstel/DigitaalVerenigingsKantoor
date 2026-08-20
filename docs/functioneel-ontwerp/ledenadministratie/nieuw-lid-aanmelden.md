# Functioneel ontwerp – Nieuw lid aanmelden

## 1. Doel

Dit document beschrijft het functionele proces voor het scenario **Nieuw lid aanmelden** binnen Sprint 1 van het Digitaal Verenigingskantoor.

Het doel van Sprint 1 is om een ledenmutatie als zaak end-to-end te kunnen begeleiden: gegevens verzamelen en controleren, de voortgang bewaken, menselijke beslissingen ondersteunen, administratieve verwerking volgen en achteraf reconstrueren wat er is gebeurd.

Dit document vormt het functionele contract voor de latere technische implementatie van onder andere:

* het statusmodel;
* de proceslogica;
* de gegevensstructuur;
* de gebruikersinterface;
* de business rules;
* de audittrail.

Het bestaande procesontwerp van de ledenadministratie blijft leidend voor de inhoudelijke verenigingsregels.

---

## 2. Uitgangspunten

### 2.1 Zaak als centraal object

Iedere nieuwe aanmelding wordt binnen het Digitaal Verenigingskantoor behandeld als een **zaak**.

Een zaak bevat minimaal:

* een uniek zaaknummer;
* het zaaktype;
* de gegevens van de aanmelding;
* de actuele processtatus;
* openstaande taken;
* genomen beslissingen;
* uitgevoerde acties;
* een audittrail.

### 2.2 Status en actie zijn gescheiden

Een **status** beschrijft waar een zaak zich in het proces bevindt.

Een **actie** beschrijft wat een gebruiker of het systeem vanuit die status kan of moet doen.

Niet iedere gebeurtenis of handeling krijgt daarom een eigen status.

### 2.3 Processtatus en taakstatus zijn gescheiden

Binnen één processtatus kunnen meerdere taken bestaan.

Bijvoorbeeld:

```text
TE_VERWERKEN

✓ Sportlink
✓ Access
✓ Welkomstmail
○ Teamadministratie
```

De zaak blijft `TE_VERWERKEN` totdat alle voor die specifieke zaak verplichte verwerkingstaken zijn afgerond.

Een fout in één taak leidt niet automatisch tot een aparte processtatus.

### 2.4 Menselijke verantwoordelijkheid

Het systeem mag:

* gegevens controleren;
* ontbrekende informatie signaleren;
* processtappen voorstellen;
* regels toepassen;
* taken genereren;
* communicatie voorbereiden.

Beslissingen waarvoor volgens het proces menselijke bevoegdheid nodig is, blijven bij de bevoegde functionaris.

### 2.5 Audittrail

Iedere relevante gebeurtenis wordt geregistreerd.

Minimaal wordt vastgelegd:

* gebeurtenis of actie;
* datum en tijd;
* actor;
* eventuele oude en nieuwe status;
* eventuele toelichting;
* bron van de actie.

Hierdoor moet achteraf altijd kunnen worden vastgesteld wat er met een zaak is gebeurd, door wie en wanneer.

---

## 3. Happy flow

De normale route voor een nieuwe aanmelding is:

```text
Aanmelding ontvangen
        ↓
Gegevens controleren
        ↓
Gegevens compleet
        ↓
Ter beoordeling
        ↓
Toegelaten
        ↓
Administratief verwerken
        ↓
Verwerking compleet
        ↓
Afgerond
```

Functioneel wordt deze flow als volgt uitgewerkt.

| Stap | Status                    | Voorwaarde                           | Actie                       | Actor                        | Volgende status           |
| ---- | ------------------------- | ------------------------------------ | --------------------------- | ---------------------------- | ------------------------- |
| 1    | `NIEUW`                   | Aanmelding ontvangen                 | Aanmelding registreren      | Systeem                      | `GEGEVENS_CONTROLEREN`    |
| 2    | `GEGEVENS_CONTROLEREN`    | Vereiste gegevens aanwezig en geldig | Gegevens compleet verklaren | Ledenadministratie           | `GEREED_VOOR_BEOORDELING` |
| 3    | `GEREED_VOOR_BEOORDELING` | Gegevens compleet                    | Ter beoordeling aanbieden   | Systeem                      | `WACHT_OP_BESLUIT`        |
| 4    | `WACHT_OP_BESLUIT`        | Beoordeling mogelijk                 | Toelaten                    | Bevoegde functionaris        | `TE_VERWERKEN`            |
| 5    | `TE_VERWERKEN`            | Toelating heeft plaatsgevonden       | Verwerkingstaken uitvoeren  | Ledenadministratie / systeem | `TE_VERWERKEN`            |
| 6    | `TE_VERWERKEN`            | Alle verplichte taken gereed         | Verwerking afronden         | Systeem / ledenadministratie | `VERWERKT`                |
| 7    | `VERWERKT`                | Administratieve verwerking compleet  | Zaak afronden               | Systeem                      | `AFGEROND`                |

---

## 4. Uitzonderingen

### 4.1 Ontbrekende gegevens

Wanneer tijdens `GEGEVENS_CONTROLEREN` verplichte gegevens ontbreken:

```text
GEGEVENS_CONTROLEREN
        ↓
WACHT_OP_AANVULLING
        ↓
GEGEVENS_CONTROLEREN
```

Het systeem registreert welke gegevens ontbreken.

De ledenadministratie kan aanvullende informatie opvragen.

Na ontvangst van de aanvullende gegevens gaat de zaak terug naar `GEGEVENS_CONTROLEREN`, zodat opnieuw kan worden vastgesteld of de gegevens compleet en geldig zijn.

---

### 4.2 Gegevens aanwezig maar controle vereist

Een gegeven kan aanwezig zijn zonder dat het direct geaccepteerd kan worden.

Voorbeelden:

* onwaarschijnlijke geboortedatum;
* ongeldig e-mailadres;
* lidcategorie past mogelijk niet bij leeftijd;
* mogelijke dubbele aanmelding;
* mogelijk bestaand of voormalig lid.

De zaak blijft in `GEGEVENS_CONTROLEREN` totdat de kwestie is opgelost.

Het systeem maakt daarbij onderscheid tussen:

* **ontbrekend gegeven**;
* **waarschuwing / controle vereist**;
* **blokkerende fout**.

Welke controles in welke categorie vallen, wordt vastgelegd in de business rules.

---

### 4.3 Herintreder of voormalig lid

Wanneer de aanmelder mogelijk al eerder lid is geweest, moet worden voorkomen dat zonder controle een tweede persoon wordt aangemaakt.

De flow is conceptueel:

```text
Nieuwe aanmelding
        ↓
Mogelijk bestaand persoon
        ↓
Identiteit controleren
        ↓
Bestaand persoon koppelen
        ↓
Normale aanmeldflow vervolgen
```

De actie **Bestaand persoon koppelen** wordt beschikbaar vanuit `GEGEVENS_CONTROLEREN`.

Wanneer het inderdaad een voormalig lid betreft, wordt een nieuwe lidmaatschapsperiode gekoppeld aan de bestaande persoon en historie.

Voor Sprint 1 mag de detectie en koppeling nog handmatig plaatsvinden.

---

### 4.4 Aanmelding wordt afgewezen

Vanuit `WACHT_OP_BESLUIT` kan de bevoegde functionaris besluiten de aanmelding af te wijzen.

```text
WACHT_OP_BESLUIT
        ↓
AFGEWEZEN
```

Minimaal worden vastgelegd:

* het besluit;
* wie het besluit heeft genomen;
* datum en tijd;
* reden of toelichting.

Eventuele verplichte communicatie over het besluit moet zijn afgehandeld voordat de zaak administratief wordt afgesloten.

---

### 4.5 Aanvullende beoordeling nodig

Een beoordelaar kan aanvullende informatie nodig hebben voordat een besluit kan worden genomen.

Bijvoorbeeld informatie over:

* teamindeling;
* spelactiviteit;
* verenigingsvoorwaarden;
* een bijzondere situatie.

De flow wordt dan:

```text
WACHT_OP_BESLUIT
        ↓
WACHT_OP_AANVULLING
        ↓
WACHT_OP_BESLUIT
```

Bij `WACHT_OP_AANVULLING` wordt vastgelegd:

* welke informatie nodig is;
* van wie deze informatie wordt gevraagd;
* wanneer de vraag is uitgezet.

Na ontvangst keert de zaak terug naar de processtap waar de aanvulling nodig was.

---

### 4.6 Verwerkingstaak mislukt

Na toelating kunnen één of meer administratieve verwerkingstaken mislukken.

Bijvoorbeeld:

```text
Sportlink
Status: fout
Reden: relatiecode reeds aanwezig
```

De processtatus blijft `TE_VERWERKEN`.

De betreffende taak krijgt een eigen taakstatus.

Mogelijke acties zijn bijvoorbeeld:

* opnieuw proberen;
* gegevens corrigeren;
* handmatig oplossen.

Pas wanneer alle verplichte taken gereed zijn, kan de zaak naar `VERWERKT`.

---

### 4.7 Correctie na toelatingsbesluit

Wanneer na het toelatingsbesluit een fout in de gegevens wordt ontdekt, hoeft de zaak niet automatisch terug naar het begin van het proces.

De actie **Gegevens corrigeren** registreert minimaal:

* gewijzigd gegeven;
* oude waarde;
* nieuwe waarde;
* actor;
* datum en tijd;
* reden voor de correctie.

Wanneer de wijziging gevolgen kan hebben voor het eerdere toelatingsbesluit, moet het systeem signaleren dat een nieuwe beoordeling noodzakelijk is.

De zaak gaat dan terug naar `WACHT_OP_BESLUIT`.

---

### 4.8 Aanmelding wordt ingetrokken

Een aanmelding kan vóór de totstandkoming van het lidmaatschap worden ingetrokken.

De zaak krijgt dan de eindstatus:

`INGETROKKEN`

Na de totstandkoming van het lidmaatschap is geen sprake meer van intrekking van de aanmelding.

Een verzoek om daarna te stoppen wordt behandeld als een nieuw proces: **Lidmaatschap beëindigen**.

---

## 5. Statusmodel

Voor Sprint 1 wordt voorlopig het volgende statusmodel gehanteerd:

```text
NIEUW
GEGEVENS_CONTROLEREN
WACHT_OP_AANVULLING
GEREED_VOOR_BEOORDELING
WACHT_OP_BESLUIT
TE_VERWERKEN
VERWERKT
AFGEROND
```

Daarnaast bestaan de eindstatussen:

```text
AFGEWEZEN
INGETROKKEN
```

Statussen zoals `SPORTLINK_FOUT`, `TEAM_NODIG` of `ON_HOLD` worden niet als afzonderlijke processtatus gemodelleerd wanneer ze feitelijk betrekking hebben op een taak of blokkade binnen de zaak.

---

## 6. Toelating als gebeurtenis

`TOEGELATEN` wordt voorlopig **niet als afzonderlijke workflowstatus** opgenomen.

De actie:

```text
toelaten
```

zorgt voor de overgang:

```text
WACHT_OP_BESLUIT
        ↓
TE_VERWERKEN
```

Het toelatingsbesluit wordt wel als zelfstandig bedrijfsfeit geregistreerd.

Bijvoorbeeld:

```text
20-08-2026 18:21
Lid toegelaten
Besloten door: [functionaris]
```

Ook wordt het toelatingsbesluit als gegeven bij de zaak bewaard.

Uitgangspunt hierbij is:

> Niet ieder betekenisvol bedrijfsfeit hoeft een workflowstatus te zijn. Een afzonderlijke status is vooral nodig wanneer een zaak in die toestand kan wachten of wanneer vanuit die toestand specifieke acties moeten kunnen plaatsvinden.

---

## 7. Functionele acties

| Actie                         | Beschikbaar vanuit                         | Effect                                                   |
| ----------------------------- | ------------------------------------------ | -------------------------------------------------------- |
| Aanmelding registreren        | `NIEUW`                                    | Start gegevenscontrole                                   |
| Gegevens wijzigen             | Meerdere statussen                         | Gegevens aanpassen en wijziging registreren              |
| Aanvulling opvragen           | `GEGEVENS_CONTROLEREN`, `WACHT_OP_BESLUIT` | Naar `WACHT_OP_AANVULLING`                               |
| Aanvulling registreren        | `WACHT_OP_AANVULLING`                      | Terug naar voorafgaande controle- of beoordelingsstap    |
| Bestaand persoon koppelen     | `GEGEVENS_CONTROLEREN`                     | Aanmelding koppelen aan bestaande persoon/historie       |
| Gegevens compleet verklaren   | `GEGEVENS_CONTROLEREN`                     | Naar `GEREED_VOOR_BEOORDELING`                           |
| Ter beoordeling aanbieden     | `GEREED_VOOR_BEOORDELING`                  | Naar `WACHT_OP_BESLUIT`                                  |
| Toelaten                      | `WACHT_OP_BESLUIT`                         | Besluit registreren en naar `TE_VERWERKEN`               |
| Afwijzen                      | `WACHT_OP_BESLUIT`                         | Naar `AFGEWEZEN`                                         |
| Aanmelding intrekken          | Voor toelating                             | Naar `INGETROKKEN`                                       |
| Verwerkingstaak gereed melden | `TE_VERWERKEN`                             | Taak afsluiten                                           |
| Verwerkingsfout registreren   | `TE_VERWERKEN`                             | Taak openhouden met foutstatus                           |
| Verwerking afronden           | `TE_VERWERKEN`                             | Naar `VERWERKT` indien alle verplichte taken gereed zijn |
| Zaak afronden                 | `VERWERKT`                                 | Naar `AFGEROND`                                          |

---

## 8. Scope Sprint 1

In Sprint 1 mogen externe onderdelen nog mocked of handmatig worden uitgevoerd.

### Sportlink

De daadwerkelijke verwerking in Sportlink gebeurt handmatig.

Het Digitaal Verenigingskantoor registreert de benodigde taak en de ledenadministrateur bevestigt na uitvoering dat deze is afgerond.

### Access

Ook verwerking of raadpleging van de bestaande Access-database mag handmatig plaatsvinden.

De historische gegevens in Access worden in Sprint 1 niet gemigreerd.

### Communicatie

E-mailberichten mogen in Sprint 1 worden gegenereerd of gesimuleerd zonder dat automatische verzending noodzakelijk is.

### AI

AI mag ondersteunen bij bijvoorbeeld:

* signaleren van ontbrekende informatie;
* interpreteren van een zaak;
* formuleren van communicatie;
* presenteren van de volgende logische actie.

Expliciete business rules bepalen echter of een procesvoorwaarde is vervuld. AI neemt geen menselijke toelatingsbeslissing over.

---

## 9. Acceptatiecriterium

Het scenario **Nieuw lid aanmelden** is functioneel geslaagd wanneer het Digitaal Verenigingskantoor voor iedere testzaak betrouwbaar antwoord kan geven op drie vragen:

1. **Waar staat deze zaak?**
2. **Waarom staat de zaak daar en wat moet er nu gebeuren?**
3. **Wat is er tot nu toe gebeurd, door wie en wanneer?**

Na afronding moet het volledige proces aan de hand van de audittrail reconstrueerbaar zijn.

---

## 10. Nog uit te werken

De volgende stap in het functioneel ontwerp is per processtap vastleggen:

* welke gegevens noodzakelijk zijn;
* welke gegevens per lidcategorie verplicht zijn;
* welke business rules gelden;
* welke controles blokkerend zijn;
* welke controles alleen een waarschuwing geven;
* welke actor bevoegd is voor welke actie;
* welke verwerkingstaken per type aanmelding verplicht zijn;
* welke gebeurtenissen in de audittrail moeten worden opgenomen.

Deze uitwerking vormt de basis voor de technische implementatie van Sprint 1.
