# Ontwerp DVK Prototype v0.2

## 1. Doel van v0.2

DVK Prototype v0.2 is de tweede functionele versie van het prototype van het Digitaal Verenigingskantoor.

Het doel is niet om al een productieplatform, gebruikersinterface, database of koppeling met externe systemen te bouwen. Het doel is om te bewijzen dat de 22 vastgestelde mastercases C01–C22 met één klein en samenhangend logisch model reproduceerbaar kunnen worden afgehandeld.

De centrale keten blijft:

**bronfeit → canoniek object → afgeleide kwalificatie → beleidsgevolg → besluit/signalering → eventuele vervolgactie → geautomatiseerde test**

`code/Prototype/22 cases.md` is voor v0.2 de gezaghebbende functionele masterset.

### Definitie van gereed

Prototype v0.2 is functioneel gereed wanneer:

- C01–C22 als afzonderlijke testcases zijn gemodelleerd;
- iedere case de in `22 cases.md` beschreven uitkomst oplevert;
- afgeleide feiten daadwerkelijk worden afgeleid en niet als handmatig resultaat in de testcase worden voorgekookt;
- signaleringen reproduceerbaar worden gegenereerd;
- afgesproken vervolgacties reproduceerbaar worden gegenereerd;
- alle 22 cases geautomatiseerd worden getest;
- de bestaande correcte werking van C01–C08 behouden blijft;
- C09 wordt gecorrigeerd;
- C10–C22 volledig worden ondersteund.

---

# 2. Ontwerpprincipes

## 2.1 Bronfeiten en afleidingen blijven gescheiden

Het prototype moet onderscheid blijven maken tussen:

1. **bronfeiten**  
   Bijvoorbeeld geboortedatum, lidmaatschap, ouder-kindrelatie, functie, feitelijke toegang of uitgegeven kleding;

2. **afgeleide kwalificaties**  
   Bijvoorbeeld minderjarig, ledendienstplichtig, vrijgesteld, bevoegd voor een resource of ontbrekende ouderrelatie;

3. **beleidsgevolgen**  
   Bijvoorbeeld 10 uur ledendienst, geen tweede gezinsverplichting of vereist toegangsrecht;

4. **besluiten en signaleringen**  
   Bijvoorbeeld `6 uur open`, `ongewenste autorisatie` of `mobiel nummer ongeldig`;

5. **vervolgacties**  
   Bijvoorbeeld e-mail sturen, toegang laten intrekken of gegevens laten corrigeren.

Een testcase mag een afgeleide kwalificatie alleen rechtstreeks bevatten wanneer dat kwalificatiefeit zelf expliciet het bronfeit van de case is.

## 2.2 Geen kennis verzinnen

Ontbrekende informatie mag niet door het prototype worden ingevuld met een aannemelijke veronderstelling.

Voorbeelden:

- geen ouder/verzorger bekend → signaleren, niet zelf een ouder kiezen;
- toegang zonder bekende functie → onverklaard signaleren, niet zelf een bevoegdheidsgrond bedenken;
- verschillende woonadressen → niet concluderen dat een ouder-kindrelatie fout is.

## 2.3 Persoon, functie en lidmaatschap zijn verschillende begrippen

Eén persoon kan:

- lid zijn;
- geen lid zijn;
- meerdere functies tegelijkertijd vervullen;
- een functie beëindigen;
- op grond van verschillende functies verschillende bevoegdheden hebben.

Een functie mag daarom niet als attribuut van het lidmaatschap worden behandeld.

## 2.4 Autorisatie volgt uit bevoegdheid, niet andersom

Dat iemand feitelijke toegang heeft, bewijst niet dat die persoon bevoegd is.

De redeneerlijn is:

**functie/delegatie → bevoegdheid → gewenste autorisatie**

en vervolgens:

**gewenste autorisatie ↔ feitelijke autorisatie → overeenkomst of afwijking**

## 2.5 Signalering en actie zijn niet hetzelfde

Een signalering constateert een toestand.

Een actie beschrijft wat daarop moet gebeuren.

Voorbeeld C10:

- signalering: kleding niet ingeleverd;
- beleidsgevolg: geen vrijgave voor overschrijving;
- actie: e-mail sturen en blokkade handhaven.

---

# 3. Minimaal logisch gegevensmodel v0.2

Het gegevensmodel wordt alleen uitgebreid voor begrippen die aantoonbaar nodig zijn voor C01–C22.

## 3.1 Person

Representeert een natuurlijke persoon.

Minimaal nodig:

- identiteit;
- naam;
- geboortedatum;
- mobiel telefoonnummer;
- woonadres.

Afleidbaar:

- leeftijd;
- minderjarig/meerderjarig;
- geldigheid mobiel telefoonnummer.

Wordt gebruikt in vrijwel alle cases en expliciet in C03, C04, C20, C21 en C22.

## 3.2 Membership

Representeert een CKC-lidmaatschap van een persoon.

Minimaal nodig:

- persoon;
- status: actief / beëindigd / geen lidmaatschap;
- soort/categorie waar relevant;
- startdatum indien relevant;
- einddatum indien relevant;
- competitieve voetbaldeelname;
- recreatieve deelname;
- erelidstatus.

Afleidbaar:

- actief CKC-lid;
- statutair lid;
- voormalig lid;
- recreatieve speler;
- erelid.

## 3.3 PersonRelationship

Nieuw in v0.2.

Representeert een expliciete relatie tussen twee personen.

Minimaal benodigde relatietypen:

- ouder/verzorger → kind.

Broer-/zusrelaties hoeven voor het prototype niet noodzakelijk als afzonderlijk bronfeit te worden opgeslagen. Zij mogen worden afgeleid doordat twee kinderen een ouder/verzorger gemeenschappelijk hebben.

Minimaal nodig:

- persoon A;
- persoon B;
- relatietype;
- actief/geldig.

Hiermee ondersteunen we:

- C03: ouder als feitelijke uitvoerder;
- C04: één gezinsverplichting;
- C20: minderjarige zonder ouder/verzorger;
- C22: ouder met kinderen op verschillende adressen.

Belangrijk ontwerpprincipe:

**woonadres bepaalt de ouder-kindrelatie niet.**

## 3.4 RoleAssignment

Representeert het vervullen van een CKC-functie door een persoon.

Minimaal nodig:

- persoon;
- functie;
- startdatum;
- einddatum of actief-status.

Voorbeelden:

- trainer;
- commissielid;
- bestuurslid;
- ledenadministrateur;
- beheerder CKC Kleding Beheer Tool;
- barteamlid.

Meerdere RoleAssignments per persoon zijn toegestaan.

Dit ondersteunt onder andere C05, C06 en C11–C19.

## 3.5 Delegation / AuthorityGrant

Nieuw in v0.2.

Representeert een expliciete bestuurlijke of organisatorische bevoegdheidsgrond.

Minimaal nodig:

- bevoegde persoon of functie;
- resource of domein waarop de bevoegdheid betrekking heeft;
- toegestane handelingen;
- delegatiegever;
- geldig vanaf;
- geldig tot / actief.

Voor het prototype hoeft nog geen volledig CKC-governancemodel te worden gebouwd.

We moeten alleen kunnen bewijzen dat bijvoorbeeld:

- het DB bevoegdheid kan delegeren;
- een beheerder daardoor bepaalde rechten behoort te hebben;
- een niet-beheerder zonder geldige grond `manage_access` niet behoort te hebben.

## 3.6 Resource

Nieuw als generiek begrip in v0.2.

Representeert iets waarop autorisatie van toepassing is.

Voorbeelden:

- CKC Kleding Beheer Tool;
- ledenadministratie;
- digitaal kassasysteem.

Het resourcebegrip voorkomt dat autorisatieregels uitsluitend voor de kledingtool worden geprogrammeerd.

## 3.7 RequiredAuthorization

Conceptueel nieuw in v0.2.

Representeert de **gewenste** toegang die uit functie en bevoegdheid wordt afgeleid.

Minimaal benodigde handelingen:

- read;
- use waar relevant;
- update;
- manage_access.

RequiredAuthorization is in beginsel een **afgeleid gegeven**, geen bronfeit.

Voorbeeld:

`beheerder kledingtool + geldige DB-delegatie`

leidt tot:

`read + update + manage_access`

## 3.8 AccessGrant

Blijft het bronfeit voor **feitelijke toegang**.

Minimaal nodig:

- persoon;
- resource;
- toegekende rechten;
- eventueel bron/beheerder van de toekenning.

Belangrijk:

AccessGrant zegt uitsluitend **wat iemand feitelijk kan**.

Het zegt niet automatisch **wat iemand mag**.

## 3.9 DutyRegistration

Representeert de administratieve ledendienstverplichting en geregistreerde uren.

Minimaal nodig:

- persoon/lid waarop de verplichting rust;
- geregistreerde gerealiseerde uren.

De verplichte omvang van 10 uur hoort bij voorkeur niet meer als bronfeit per testcase te worden ingevoerd wanneer deze uit CKC-beleid volgt.

Afleidbaar:

- verplicht aantal uren;
- gerealiseerde uren;
- resterende uren;
- vrijstelling;
- feitelijke uitvoerder.

## 3.10 ClothingIssue

Representeert uitgegeven CKC-kleding.

Minimaal nodig:

- persoon/lid;
- kledingartikel;
- maat;
- ingeleverd ja/nee;
- financieel afgehandeld ja/nee of equivalente afhandelstatus.

Voor C10 moet kunnen worden vastgesteld of een openstaande kledingkwestie inmiddels is opgelost door:

- fysieke inlevering; of
- financiële afhandeling.

## 3.11 ComplianceFact

Nieuw, maar bewust minimaal.

Voor v0.2 is slechts één concrete toepassing noodzakelijk:

- VOG aangeleverd/geldig.

We hoeven nog geen generiek complianceplatform te bouwen.

Het object moet alleen voldoende zijn om C18 logisch te modelleren zonder een speciaal veld `trainer_has_vog` op de testcase te zetten.

## 3.12 PrototypeCase

Een testcase is niet langer noodzakelijkerwijs één persoon plus wat attributen.

Een case moet een kleine relevante werkelijkheid kunnen bevatten:

- één of meer personen;
- memberships;
- relaties;
- functies;
- delegaties;
- feitelijke autorisaties;
- ledendienstregistraties;
- kledingregistraties;
- compliancefeiten;
- relevante contextdatum.

Dit is met name noodzakelijk voor C04 en C22.

---

# 4. Afgeleide begrippen

Naast de bronobjecten introduceert v0.2 expliciet afgeleide kwalificaties.

Belangrijke voorbeelden:

- is_active_member;
- is_minor;
- is_recreational_player;
- is_honorary_member;
- has_exempting_role;
- duty_subject;
- duty_executor;
- family_duty_subject;
- duty_required_hours;
- duty_remaining_hours;
- has_registered_parent_or_guardian;
- valid_authority;
- required_authorizations;
- actual_authorizations;
- excess_authorizations;
- missing_authorizations;
- unexplained_authorizations;
- vog_required;
- vog_valid;
- mobile_number_valid;
- outstanding_clothing;
- transfer_release_blocked.

Deze begrippen hoeven niet noodzakelijk allemaal als permanente objecten te worden opgeslagen. Het mogen resultaten van pure regels zijn.

---

# 5. Rule-categorieën v0.2

De huidige afzonderlijke regels worden uitgebreid tot zeven functionele categorieën.

## 5.1 Membership rules

Doel:

vaststellen van lidmaatschapskwalificaties.

Ondersteunt:

C01–C10 en waar nodig latere cases.

Voorbeelden:

- actief versus beëindigd;
- erelid blijft actief lid;
- recreatieve speler is statutair lid;
- incidenteel vrijwilligerswerk maakt iemand niet automatisch lid.

## 5.2 Relationship & family rules

Nieuw.

Doel:

afleidingen maken uit expliciete persoonsrelaties.

Ondersteunt:

C03, C04, C20 en C22.

Regels:

- bepaal geregistreerde ouder/verzorger(s);
- stel vast of een minderjarige geen ouder/verzorger heeft;
- bepaal relevante gezinsgroep op grond van ouder-kindrelaties;
- bepaal op welk minderjarig kind de gezins-ledendienstplicht rust;
- leg geen tweede verplichting op;
- gebruik woonadres niet als bewijs voor of tegen familieverband.

## 5.3 Ledendienst rules

Uitbreiding bestaande regels.

Ondersteunt:

C01–C09.

Logische volgorde:

1. is er actief lidmaatschap?
2. valt het lid onder een beleidsvrijstelling?
3. is sprake van een erkende vrijwilligersfunctie?
4. is sprake van recreatieve deelname?
5. is sprake van één gezinsverplichting?
6. wie is administratief verplicht?
7. wie voert de dienst feitelijk uit?
8. hoeveel uren zijn gerealiseerd?
9. hoeveel uren staan nog open?

Belangrijke wijziging:

`broederdienst_exempt` verdwijnt als rechtstreeks contextfeit.

C09 wordt gecorrigeerd:

**recreatieve speler → vrijgesteld.**

## 5.4 Clothing & termination rules

Uitbreiding bestaande kledingregel.

Ondersteunt:

C10.

Regels:

- detecteer openstaande kleding;
- stel vast of lidmaatschap is beëindigd;
- bepaal of de kledingkwestie is afgehandeld;
- leid zolang nodig `transfer_release_blocked = true` af;
- genereer bij openstaande kwestie de benodigde vervolgacties.

## 5.5 Governance & authorization rules

Grootste nieuwe rule-categorie.

Ondersteunt:

C11–C17 en C19.

De kernberekening is:

**actuele functies + actuele delegaties → geldige bevoegdheden → gewenste autorisaties**

Daartegenover:

**AccessGrant → feitelijke autorisaties**

Vervolgens bepaalt het DVK:

- correct;
- ontbrekende toegang;
- te ruime toegang;
- onverklaarde toegang.

Regels moeten meerdere functies tegelijk kunnen combineren.

Daarmee wordt C17 automatisch een normale consequentie van het model in plaats van een aparte uitzonderingssituatie.

## 5.6 Compliance rules

Nieuw.

Ondersteunt:

C18.

Voor v0.2:

- trainer → VOG vereist;
- geldige VOG aanwezig → correct;
- geen geldige VOG → beleidsafwijking + opvolgactie.

De trainerfunctie zelf blijft geldig als bronfeit; het DVK constateert alleen de beleidsafwijking.

## 5.7 Data-quality rules

Nieuw.

Ondersteunt:

C20–C22.

Voor v0.2:

- minderjarig lid zonder ouder/verzorger → fout/signalering;
- mobiel nummer met 9 cijfers → ongeldig;
- ouder met kinderen op verschillende adressen → géén fout;
- opvallende maar mogelijke gegevenssituaties mogen als aandachtspunt worden weergegeven zonder automatisch gegevens te wijzigen.

---

# 6. Gewenste outputstructuur

De huidige `Decision` wordt conceptueel uitgebreid.

Iedere rule-uitkomst moet waar relevant vijf soorten informatie kunnen bevatten.

## 6.1 Decision

De inhoudelijke conclusie.

Voorbeelden:

- actief CKC-lid;
- vrijgesteld van ledendienst;
- toegang correct;
- mobiele nummer ongeldig.

## 6.2 Facts / derived facts

De feiten waarop de conclusie berust of die eruit zijn afgeleid.

Voorbeelden:

- required_hours = 10;
- completed_hours = 4;
- remaining_hours = 6;
- executor = ouder P23;
- required_access = read + update;
- actual_access = read.

Dit maakt besluiten uitlegbaar en testbaar.

## 6.3 Severity / status

Voorgestelde minimale statussen:

- `ok`;
- `attention`;
- `error`;
- `blocked`;
- `not_applicable`.

Niet iedere afwijking is even ernstig.

Voorbeeld:

- C22: eventueel `attention`;
- C12: `blocked` of kritieke afwijking.

## 6.4 Signal

Een expliciete signalering voor menselijke aandacht.

Voorbeelden:

- nog 6 uur ledendienst open;
- ouder/verzorger ontbreekt;
- VOG ontbreekt;
- feitelijke toegang heeft geen bekende bevoegdheidsgrond.

Een `ok`-besluit hoeft niet noodzakelijk een signalering op te leveren.

## 6.5 Action

Nieuw first-class outputbegrip.

Een Action beschrijft een noodzakelijke of voorgestelde vervolgactie.

Minimaal nodig:

- actietype;
- onderwerp/persoon;
- verantwoordelijke rol waar bekend;
- reden;
- status of blokkade-effect waar relevant.

Voorbeelden:

- `send_email`;
- `revoke_access`;
- `grant_access`;
- `request_data_correction`;
- `start_vog_followup`;
- `block_transfer_release`;
- `review_anomaly`.

Belangrijk:

v0.2 **voert deze acties nog niet daadwerkelijk uit in externe systemen**.

Het prototype bewijst alleen dat het DVK op reproduceerbare wijze kan bepalen **welke actie moet plaatsvinden**.

Dat is voldoende voor deze prototypefase.

---

# 7. Caseclusters en implementatievolgorde

Niet numeriek C01 → C22 programmeren, maar per logisch cluster.

## Cluster 1 — Stabiliseren bestaande kern

Cases:

**C01, C02, C05, C06, C07, C08, C09**

Doel:

- bestaande correcte logica behouden;
- C09 corrigeren;
- basis-outputstructuur invoeren zonder functionele regressie.

Waarom eerst:

Dit levert snel een stabiele basis op waarop de nieuwe modellen kunnen voortbouwen.

## Cluster 2 — Personen en gezinsrelaties

Cases:

**C03, C04, C20, C22**

Doel:

- PersonRelationship introduceren;
- echte ouder/verzorger kunnen identificeren;
- broederdienstcontext verwijderen;
- gezinsverplichting afleiden;
- ontbrekende ouderrelatie herkennen;
- verschillende adressen correct behandelen.

Waarom als tweede:

C04 en C22 zijn goede stresstests voor de vraag of het prototype werkelijk redeneert vanuit relaties in plaats van uit losse labels.

## Cluster 3 — Ledendienstmodel afronden

Cases:

**C01–C09 opnieuw integraal**

Doel:

na invoering van relaties de volledige ledendienstlogica opnieuw als één samenhangende set testen:

- volwassenen;
- minderjarigen;
- gezin;
- vrijwilligersfuncties;
- erelid;
- recreanten.

Resultaat:

C01–C09 vormen daarna één stabiel functioneel domein.

## Cluster 4 — Generiek autorisatiemodel

Cases:

**C11, C12, C13, C14, C15, C16, C17, C19**

Doel:

introduceren van:

- Resource;
- Delegation/Authority;
- gewenste autorisatie;
- feitelijke autorisatie;
- vergelijking tussen beide;
- samengestelde bevoegdheden vanuit meerdere functies.

Voorgestelde bouwvolgorde binnen dit cluster:

1. C11 — positieve beheerdercase;
2. C12 — te ruime toegang;
3. C13 — normale positieve toegang;
4. C15 — ontbrekende toegang;
5. C16 — onverklaarde toegang;
6. C14 — verlopen functie;
7. C17 — twee functies combineren;
8. C19 — bewijs dat hetzelfde model ook buiten de kledingtool werkt.

C19 is daarmee bewust de stresstest die bewijst dat het autorisatiemodel daadwerkelijk generiek is.

## Cluster 5 — Vervolgacties en blokkades

Case:

**C10**, aangevuld met actie-uitkomsten uit autorisatiecases.

Doel:

Action als expliciet resultaat introduceren.

Voor C10 minimaal:

- e-mailactie;
- melding inleveren of restwaarde betalen;
- blokkade vrijgave overschrijving;
- blokkade vervalt na geregistreerde afhandeling.

Daarna kunnen dezelfde action-mechanismen worden gebruikt voor:

- access intrekken;
- access toekennen;
- gegevens laten corrigeren.

## Cluster 6 — Compliance en datakwaliteit

Cases:

**C18, C20, C21, C22**

C20 en C22 bestaan dan inhoudelijk al vanuit cluster 2, maar worden hier onderdeel van één bredere kwaliteitslaag.

Doel:

bewijzen dat DVK niet alleen beleidsbesluiten neemt, maar ook tekortkomingen en opvallende brongegevens kan herkennen zonder zelf informatie te verzinnen.

## Cluster 7 — Integrale regressietest C01–C22

Als laatste:

- alle 22 cases samen uitvoeren;
- per case Decision controleren;
- relevante derived facts controleren;
- signaleringen controleren;
- acties controleren;
- controleren dat geen onverwachte signaleringen of acties ontstaan.

Pas dan noemen we het:

**DVK Prototype v0.2.**

---

# 8. Wat bewust buiten v0.2 blijft

Om scopegroei te voorkomen bevat v0.2 nog niet:

- Streamlit-interface;
- PostgreSQL/Supabase;
- Sportlink-koppeling;
- Google Forms-koppeling;
- kassasysteemkoppeling;
- daadwerkelijk verzenden van e-mail;
- daadwerkelijk wijzigen van autorisaties;
- daadwerkelijk blokkeren van een overschrijving;
- VOG-aanvraagproces;
- workflow-engine;
- YAML-regelbeheer;
- AI/LLM-besluitvorming;
- volledige historische administratie;
- productierijpe audittrail.

De output van v0.2 mag wel al voldoende gestructureerd zijn om zulke voorzieningen later aan te sluiten.

---

# 9. Beoogde architectuur v0.2

Conceptueel:

**Case / bronfeiten**

↓

**Canonieke prototype-objecten**

- Person
- Membership
- PersonRelationship
- RoleAssignment
- Delegation/Authority
- Resource
- AccessGrant
- DutyRegistration
- ClothingIssue
- ComplianceFact

↓

**Rule engine**

- membership
- relationships
- ledendienst
- clothing
- authorization
- compliance
- data quality

↓

**Resultaat**

- Decision
- Derived facts
- Signal
- Action

↓

**Automated tests C01–C22**

De rule engine blijft daarbij deterministisch.

Hetzelfde feitenbeeld moet steeds dezelfde uitkomst geven.

---

# 10. Belangrijkste wijziging ten opzichte van v0.1

Prototype v0.1 bewijst voornamelijk:

> Kan een kleine set feiten met Python-regels tot een reproduceerbaar besluit leiden?

Prototype v0.2 moet bewijzen:

> Kan het DVK een kleine maar realistische werkelijkheid van personen, relaties, functies, bevoegdheden en registraties samenhangend interpreteren, daaruit beleid afleiden, afwijkingen herkennen en de juiste vervolgactie bepalen?

Dat is een wezenlijke stap vooruit.

Het prototype gaat daarmee van enkele afzonderlijke regels naar een eerste echte **digitale verenigingslogica**.

---

# 11. Acceptatiecriteria v0.2

v0.2 wordt pas geaccepteerd wanneer:

1. C01–C22 allemaal bestaan als expliciete cases.
2. C09 geen ledendienstplicht meer oplegt aan recreatieve spelers.
3. C04 geen handmatig `broederdienst_exempt`-feit meer nodig heeft.
4. C03 een werkelijke ouder/verzorgerrelatie kan gebruiken.
5. C10 zowel signalering, blokkade als vervolgacties oplevert.
6. C11–C19 hetzelfde generieke autorisatiemodel gebruiken.
7. C17 twee gelijktijdige functies correct combineert.
8. C18 trainer zonder geldige VOG signaleert.
9. C20 ontbrekende ouder/verzorger signaleert.
10. C21 het 9-cijferige mobiele nummer afkeurt.
11. C22 verschillende adressen niet ten onrechte als fout behandelt.
12. Alle relevante vervolgacties expliciet testbaar zijn.
13. Alle 22 tests slagen.
14. Geen case afhankelijk is van een vooraf ingevulde afgeleide conclusie die uit bronfeiten had moeten worden berekend.

---

# 12. Eerstvolgende implementatiestap na goedkeuring

Na inhoudelijke goedkeuring van dit ontwerp is de eerstvolgende stap:

**Implementatie DVK Prototype v0.2 — stap 1: canoniek prototype-model uitbreiden.**

Daarbij wordt eerst uitsluitend het gegevensmodel aangepast.

Nog géén nieuwe rules.

Nog géén 22 cases ineens programmeren.

De volgorde wordt:

**model → regels per cluster → cases → tests → integrale regressietest**

Zo blijft bij iedere wijziging zichtbaar welk nieuw begrip wordt toegevoegd, welke cases dat begrip nodig hebben en welk gedrag daardoor ontstaat.
