# DVK ontwikkelworkflow met Codex

**Status:** werkafspraak voor gecontroleerde ontwikkeling vanaf Prototype v0.5  
**Doel:** vastleggen hoe Johan/CKC, ChatGPT, Codex, GitHub en CI samenwerken zonder functionele of architecturale besluitvorming impliciet aan code of tests over te laten.

## 1. Rollen

- **Johan / CKC** is functioneel eigenaar en bepaalt functionele werkelijkheid, beleid, prioriteit, scope en functionele acceptatie.
- **ChatGPT** bewaakt functionele afspraken, architectuur, iteratiescope en acceptatiecriteria; verifieert GitHub vóór een opdracht; formuleert de afgebakende Codex-iteratie en beoordeelt daarna diff, tests en CI.
- **Codex** voert de afgesproken technische opdracht uit binnen `AGENTS.md` en de iteratiespecifieke opdracht.
- **GitHub** is de gezaghebbende projectadministratie voor code, branches, commits, baselines, tests en projectdocumentatie.
- **CI** levert technisch regressiebewijs. Groen is noodzakelijk maar is geen functionele acceptatie.

## 2. Vaste ontwikkelketen

```text
Johan / CKC
    ↓ functionele keuze en scope
ChatGPT
    ↓ GitHub-verificatie + afgebakende iteratieopdracht
Codex
    ↓ werkbranch + analyse/wijziging + lokale tests
GitHub pull request
    ↓
CI
    ↓
ChatGPT review
    ↓
Johan / CKC acceptatie
    ↓
merge naar integratiebranch
```

Voor v0.5 is `main` de functioneel geaccepteerde v0.4-baseline en `prototype-v0.5` de integratiebranch. PR #5 van `prototype-v0.5` naar `main` blijft draft totdat v0.5 integraal functioneel is geaccepteerd.

## 3. Branch- en PR-procedure

Iedere Codex-iteratie krijgt een kortlevende branch met één doel:

```text
codex/<iteratie>-<kort-doel>
```

Voorbeelden: `codex/c6-simplification`, `codex/g10-b-replacement-noshow`.

De iteratieopdracht noemt altijd:
- startbranch;
- exacte startcommit;
- werkbranch;
- doelbranch voor de PR.

Codex controleert startbranch en startcommit vóór uitvoering. Bij afwijking stopt de iteratie.

Codex mag, wanneer de opdracht dat toestaat, de werkbranch maken, committen, pushen en een PR naar `prototype-v0.5` openen. Codex merge't niet zelfstandig. Een merge volgt pas na review en expliciete menselijke acceptatie.

## 4. Testprocedure

### Voor wijziging

Voer de relevante bestaande tests uit om de uitgangssituatie vast te stellen. Een reeds falende test wordt niet automatisch onderdeel van de iteratiescope.

### Na wijziging

Voer achtereenvolgens uit:
1. gerichte regressietests voor de iteratie;
2. de volledige regressiesuite;
3. eventuele aanvullende opdrachtgebonden controles.

Voor het prototype is de volledige pytest-regressie minimaal:

```bash
cd code/Prototype
pytest -q
```

Na de PR herhaalt GitHub Actions de repositorychecks onafhankelijk.

## 5. Functionele regressie en testdata

De richting is:

```text
CKC-afspraak
→ functionele regressiecase
→ testdata
→ geautomatiseerde test(s)
```

Niet andersom.

Geaccepteerde C-, W-, I- en R-cases zijn functionele regressiebasis. v0.5-cases die nog niet functioneel zijn geaccepteerd blijven herkenbaar als ontwikkeling.

Codex mag een regressiecase of geaccepteerde verwachting niet aanpassen om gewijzigde code passend te maken. Wanneer code, test en functionele afspraak elkaar tegenspreken, wordt de inconsistentie gerapporteerd en volgt menselijke besluitvorming.

Testdata blijft naar functie onderscheiden:
- basisfixture;
- brondataset;
- lokale scenariodata;
- integrale demodataset.

Historische regressiefixtures worden niet aangepast voor demo- of UI-gemak. Kleine lokale fixtures hoeven niet te worden gecentraliseerd uitsluitend om duplicatie te verminderen.

## 6. Standaardformat Codex-iteratie

Iedere opdracht gebruikt minimaal onderstaande structuur.

```text
DVK CODEX-ITERATIE

1. Identiteit
Iteratie:
Doel:
Type: analyse | documentatie | implementatie | bugfix | refactor

2. Baseline
Repository:
Startbranch:
Startcommit:
Werkbranch:
Doelbranch voor PR:

3. Functioneel contract
Relevante functionele afspraken:
Relevante regressiecases:
Relevante testdata/fixtures:
Relevante geaccepteerde baseline:

4. Probleem / opdracht
Concrete beginsituatie:
Gewenste uitkomst:
Waarom deze iteratie nodig is:

5. Scope
Binnen scope:
-
Expliciet buiten scope:
-

6. Architectuurgrenzen
Relevante architectuurregels uit AGENTS.md:
-
Aanvullende iteratiespecifieke beperkingen:
-

7. Verwachte wijzigingsscope
Primair te onderzoeken/wijzigen bestanden:
-

8. Verificatie
Baseline-tests:
Gerichte tests:
Volledige regressie:
Aanvullende controles:

9. Stopcondities
Iteratiespecifieke stopcondities:
-

10. Oplevering
Rapporteer baseline, werkbranch, analyse, gewijzigde bestanden,
tests, regressieresultaat, CI-status, risico's, beslispunten en commits.
Niet zelfstandig mergen.
```

Codex mag de repository breed lezen om afhankelijkheden te begrijpen. De wijzigingsscope blijft beperkt. Als een extra wijziging een functionele of architecturale uitbreiding inhoudt, stopt Codex en rapporteert het beslispunt.

## 7. Betekenis van 'klaar'

- **Codex klaar:** opdracht uitgevoerd, gerichte tests groen, volledige lokale regressie groen, commit en eventueel PR gereed.
- **CI groen:** GitHub heeft technische regressie onafhankelijk bevestigd.
- **ChatGPT-review akkoord:** wijziging past bij opdracht, architectuur en functioneel contract.
- **Johan / CKC akkoord:** iteratie mag in de v0.5-integratiebaseline worden opgenomen.
- **v0.5 geaccepteerd:** pas na alle vereiste gates, regressies en integrale functionele acceptatie kan PR #5 naar `main`.

Een merge van één Codex-iteratie naar `prototype-v0.5` betekent dus niet automatisch dat een volledige gate of v0.5 functioneel is geaccepteerd.

## 8. Eerste gecontroleerde Codex-iteratie

Consolidatie-iteratie 6 is de eerste proef van deze workflow. Het type is **analyse/documentatie**.

Doel: de functionele kaart, testdatakaart en technische modulekaart uit Consolidatie 1–5 over elkaar leggen en relevante onderdelen classificeren als:

- **Behouden**;
- **Documenteren**;
- **Vereenvoudigen**.

Voor iedere voorgestelde vereenvoudiging moeten minimaal worden benoemd:
- het concrete onderhoudsprobleem;
- de functionele regressies die beschermd moeten blijven;
- de kleinste mogelijke wijziging;
- het risico.

Consolidatie 6 voert nog geen productiecode-refactor uit.


## 9. Baseline- en wijzigingsdiscipline

Vanaf deze werkafspraak wordt DVK nadrukkelijk baseline-gedreven ontwikkeld.

### 9.1 Een geaccepteerde baseline is het contract

Een releasebaseline bestaat niet alleen uit werkende code. De baseline omvat de bij die release geaccepteerde combinatie van:

- code en databasemigraties;
- functioneel ontwerp en functioneel contract;
- bron- en integratiecontracten;
- relevante configuratie en beleidsparameters;
- geaccepteerde regressiecases en tests.

GitHub is de gezaghebbende opslag. Een chat, samenvatting of Codex-opdracht kan naar de baseline verwijzen, maar vervangt haar niet.

Een nieuwe ontwikkelchat of Codex-iteratie start daarom vanaf een expliciet genoemde baselinebranch en -commit en benoemt de gezaghebbende documenten. Reeds geaccepteerde afspraken worden niet opnieuw ontworpen alleen omdat zij in de actuele chat niet volledig zichtbaar zijn.

### 9.2 Nieuwe bevindingen wijzigen de baseline niet impliciet

Tijdens analyse of implementatie wordt iedere relevante nieuwe bevinding eerst geclassificeerd:

| Bevinding | Behandeling |
| --- | --- |
| Implementatiefout ten opzichte van de baseline | Code corrigeren; functionele baseline blijft gelijk. |
| Onduidelijkheid of inconsistentie in de baseline | Stoppen met het betreffende onderdeel; baseline eerst verduidelijken. |
| Nieuwe requirement | Als change request/backlog vastleggen; niet stil aan de lopende iteratie toevoegen. |
| Eerdere functionele afspraak blijkt onjuist of onvolledig | Eerst expliciete baselinewijziging ontwerpen, documenteren en accepteren; daarna pas implementeren. |

Een plausibele nieuwe redenering, chatbesluit of technische implementatie is dus nooit op zichzelf voldoende om geaccepteerd gedrag te wijzigen.

### 9.3 Volgorde bij een baselinewijziging

Wanneer een functionele afspraak, bronmapping of architectuurregel moet veranderen, geldt:

    bevinding
    → vergelijking met actuele baseline
    → expliciet wijzigingsvoorstel
    → functionele/architecturale acceptatie
    → baseline-documentatie aanpassen
    → regressiecriteria aanpassen/toevoegen
    → implementatie op afgebakende werkbranch
    → tests + CI
    → functionele acceptatie
    → merge

Code loopt niet vooruit op een nog niet geaccepteerde functionele baselinewijziging.

### 9.4 Releasebaseline afronden

Bij functionele acceptatie van een release wordt expliciet vastgelegd welke commit en welke documenten samen de nieuwe baseline vormen. Openstaande requirements, bekende afwijkingen en latere verbeteringen worden apart gehouden en maken niet stilzwijgend deel uit van de baseline.

## 10. Chatdiscipline en overdracht

Chats zijn werkruimten, geen projectadministratie. Om verlies en herinterpretatie van besluiten door lange ontwikkelgesprekken te voorkomen, krijgt iedere ontwikkelchat voortaan één afgebakend doel en een expliciete eindconditie.

Een volledige release hoeft niet in één chat te worden uitgevoerd. Baseline-herijking, implementatie, functionele acceptatie en integratie kunnen bewust afzonderlijke chats zijn.

### 10.1 Start van een nieuwe chat

Een nieuwe ontwikkelchat vermeldt minimaal:

- release/iteratie en doel;
- gezaghebbende baselinebranch en -commit;
- te lezen baseline-documenten;
- expliciete scope en buiten-scope;
- eindconditie van de chat.

De chat reconstrueert geen beleid uit herinnering wanneer dit in GitHub hoort te staan. Als noodzakelijke informatie niet eenduidig uit de genoemde baseline kan worden vastgesteld, wordt dat als baselineprobleem behandeld.

### 10.2 Wanneer een chat wordt beëindigd

Een chat wordt bewust afgesloten zodra de afgesproken eindconditie is bereikt, of eerder wanneer blijkt dat eerst een andere baselinewijziging of besluitvorming nodig is. Een nieuwe inhoudelijke werkstroom start vervolgens in een nieuwe chat.

Bij afsluiting wordt een compacte overdracht gemaakt met:

- bereikte toestand;
- relevante branch/commit/PR;
- geaccepteerde besluiten;
- nog openstaande punten;
- concrete opdracht voor de volgende chat;
- verwijzingen naar de gezaghebbende GitHub-documenten.

De overdracht is een navigatiehulpmiddel en geen vervanging van de GitHub-baseline.

## 11. Stopregel voor scope creep

Wanneer tijdens een lopende iteratie een nieuwe requirement, fout in een eerder ontwerp of ontbrekende bronafspraak wordt ontdekt die de geaccepteerde baseline raakt, wordt de lopende implementatie op dat onderdeel gepauzeerd. De bevinding wordt niet terloops opgelost.

Eerst wordt vastgesteld of sprake is van een bug, onduidelijkheid, nieuwe requirement of baselinewijziging volgens §9.2. Alleen nadat de vereiste documentatie en besluitvorming zijn afgerond, wordt de technische iteratie hervat of opnieuw geformuleerd.

Dit geldt ook wanneer de voorgestelde wijziging klein of technisch eenvoudig lijkt.
