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
