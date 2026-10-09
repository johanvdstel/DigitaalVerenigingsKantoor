# AGENTS.md — Digitaal Verenigingskantoor (DVK)

## 1. Doel en gezag

Deze repository bevat het Digitaal Verenigingskantoor (DVK) van CKC.

Werk uitsluitend binnen de expliciete opdracht van de actuele iteratie. Breid scope niet zelfstandig uit en verander geen functioneel CKC-beleid op eigen initiatief.

GitHub is de gezaghebbende projectadministratie voor code, branches, tests, baselines en projectdocumentatie.

De hoogste aanwezige prototypeversie is niet automatisch de functioneel geaccepteerde baseline. Controleer vóór iedere wijziging de actuele baseline- en branchdocumentatie.

Bij twijfel of tegenstrijdigheid tussen opdracht, functionele afspraak, testcase, documentatie en implementatie: niet gokken. Leg de tegenstrijdigheid expliciet voor en stop met het betreffende onderdeel.

## 2. Verantwoordelijkheden

- Johan / CKC bepaalt functionele werkelijkheid, beleid, scope en functionele acceptatie.
- ChatGPT bewaakt functionele afspraken, architectuur, iteratiescope en acceptatiecriteria en formuleert de gecontroleerde technische opdracht.
- Codex voert de afgesproken technische opdracht uit en rapporteert het resultaat.
- CI bewijst technische regressievrijheid; groene CI is geen functionele acceptatie.

Codex introduceert geen nieuwe beleidsregel, functionele interpretatie of architectuurkeuze zonder expliciete opdracht.

## 3. Architectuurregels

Respecteer de bestaande richting:

```text
sources
→ adapters
→ normalization / canonical DVK objects
→ domain / engine
→ proposal
→ human decision
→ scheduling
```

Harde regels:

- bronfeiten, configuratie en DVK-afleidingen blijven onderscheiden;
- provenance blijft behouden;
- business- en beleidslogica hoort niet in Streamlit, repositories of SQL;
- de UI bevat geen eigen beleidsregels;
- UI gebruikt publieke applicatieservices en geen private interne state;
- een DVK-voorstel is geen CKC-besluit;
- scheduling ontstaat alleen na expliciete menselijke bevestiging;
- ontbrekende of ambigue brondata worden niet gegokt of stilzwijgend gerepareerd;
- familierelaties worden niet uit naam of achternaam afgeleid;
- negatieve open uren zijn toegestaan;
- Sportlink-integraties blijven read-only zolang de functionele scope dat voorschrijft;
- Streamlit is een vervangbare UI-laag;
- technische identifiers horen niet in normale gebruikersweergave wanneer een menselijke identificatie beschikbaar is.

## 4. Wijzigingsdiscipline

Werk met de kleinste wijziging die het afgesproken probleem correct oplost.

Voor iedere wijziging:

1. controleer eerst de actuele code en relevante tests;
2. beschrijf het concrete probleem;
3. identificeer de relevante functionele afspraak/invariant;
4. bepaal de minimale wijziging;
5. voeg gerichte regressiebescherming toe of pas die alleen aan wanneer de functionele afspraak dat vereist;
6. voer daarna de volledige regressiesuite uit.

Niet toegestaan zonder expliciete opdracht:

- opportunistische refactors;
- bestanden samenvoegen of verplaatsen alleen om de structuur mooier te maken;
- geaccepteerde historische cases aanpassen voor nieuwe demo- of UI-behoeften;
- tests versoepelen zodat gewijzigde code alsnog slaagt;
- bestaande functionele afwijkingen stilzwijgend meenemen in een andere wijziging;
- technische schuld buiten de iteratiescope "even oplossen".

Als een noodzakelijke oplossing buiten de afgesproken scope valt: rapporteer dit en stop daar.

## 4a. Verplichte context- en proportionaliteitscontrole

Deze controle geldt vóór iedere technische gapanalyse, ontwerpaanbeveling en Codex-opdracht; ook wanneer de wijziging klein lijkt.

1. **Projectcontext eerst.** Benoem de geldende functionele baseline, ontwikkelfase, iteratiescope, bronhouders en relevante geaccepteerde besluiten. Verifieer ze in de actuele repositorydocumentatie. Ga niet uit van algemene productieaannames bij een prototype.
2. **Scheid bewijs en interpretatie.** Label relevante uitspraken als vastgesteld feit (met code-/documentreferentie), geaccepteerde eis, nog onbewezen aanname of aanbeveling. Presenteer aannames nooit als vaststaande projectvereisten.
3. **Toets proportionaliteit.** Motiveer iedere extra technische maatregel met (a) het concrete probleem, (b) bewijs dat dit probleem in de huidige ontwikkelfase bestaat en (c) de gevolgen als de maatregel achterwege blijft. Zonder aantoonbare noodzaak: niet opnemen in de uitvoeringsscope; hoogstens expliciet als onbewezen vraag rapporteren.
4. **Toets gegevensstatus.** Maak onderscheid tussen wegwerpbare prototype-/testgegevens, geaccepteerde regressiefixtures en werkelijk te behouden operationele gegevens. Stel geen migratie of historische reconstructie voor zonder vastgestelde behoudsplicht of expliciete opdracht. Verwijderen van geaccepteerde regressiefixtures vereist wel een afzonderlijk functioneel besluit.
5. **Codex-acceptatiepoort.** Neem uitsluitend werkzaamheden op die herleidbaar zijn tot een geaccepteerde eis, aantoonbare technische afwijking of expliciet goedgekeurde technische verbetering. Leg de herleiding en bijbehorende acceptatiecriteria in de opdracht vast. Onbewezen aannames zijn geen implementatieopdracht.
6. **Stop bij onzekerheid.** Als het bewijs voor een ingrijpende maatregel ontbreekt, benoem de onzekerheid en vraag zo nodig een gericht besluit. Breid de scope niet uit om hypothetische problemen op te lossen.

Voorbeeld v0.5: oude no-showregistraties uit achterhaalde prototypefunctionaliteit zijn wegwerpbare testgegevens; er is geen migratieopdracht. Nieuwe no-shows en hun intrekkingen zijn daarentegen duurzame DVK-feiten en moeten voldoen aan het actuele functionele contract.

## 5. Regressies en testdata

De functionele afspraak leidt de regressie:

```text
functionele afspraak
→ regressiecase
→ testdata
→ geautomatiseerde test(s)
```

Niet andersom.

Bestaande geaccepteerde casefamilies, waaronder C-, W-, I- en R-cases, zijn regressiebasis en mogen niet zonder expliciet functioneel besluit worden gewijzigd.

v0.5-cases die nog niet functioneel zijn geaccepteerd blijven herkenbaar als ontwikkeling en mogen niet als geaccepteerde baseline worden gepresenteerd.

Historische regressiedata en integrale demo/UI-data blijven gescheiden.

Gebruik bestaande fixtures wanneer die functioneel passend zijn. Centraliseer of dupliceer testdata niet uitsluitend voor technische elegantie.

Wanneer tests en functionele documentatie elkaar tegenspreken, kies niet zelfstandig één van beide als waarheid. Rapporteer de inconsistentie.

## 6. Branches, commits en CI

Werk nooit rechtstreeks op `main`.

Werk voor een gecontroleerde iteratie op de daarvoor aangewezen werkbranch vanaf de expliciet opgegeven baselinecommit.

Voor v0.5 geldt, totdat anders besloten:

- `main` = functioneel geaccepteerde v0.4-baseline;
- `prototype-v0.5` = integratiebranch voor v0.5;
- PR #5 naar `main` blijft draft tot integrale functionele acceptatie van v0.5;
- Codex-iteraties gebruiken een afzonderlijke werkbranch en worden via een kleine PR naar `prototype-v0.5` aangeboden.

Codex mag een werkbranch maken, committen, pushen en een PR openen wanneer de iteratieopdracht dat toestaat. Codex merge't niet zelfstandig naar `prototype-v0.5` of `main`.

Een groene CI-run is noodzakelijk maar niet voldoende voor acceptatie.

## 7. Vereiste rapportage

Rapporteer na iedere iteratie minimaal:

- gebruikte baselinebranch en baselinecommit;
- gemaakte werkbranch;
- gewijzigde bestanden;
- reden per wijziging;
- toegevoegde of aangepaste tests;
- gerichte testresultaten;
- resultaat volledige regressiesuite;
- CI-status indien beschikbaar;
- bekende resterende afwijkingen of risico's;
- punten waarvoor functionele of architectuurbesluitvorming nodig is;
- commit(s).

Verberg geen mislukte test, onzekerheid of afwijking achter een algemene melding dat de wijziging "werkt".

## 8. Stopcondities

Stop en vraag om besluitvorming wanneer:

- de opdracht een ontbrekende functionele regel vereist;
- twee gezaghebbende afspraken elkaar tegenspreken;
- een historische geaccepteerde case zou moeten veranderen;
- de minimale oplossing een nieuwe architectuurkeuze vereist;
- de gevraagde wijziging buiten de afgesproken iteratiescope blijkt te vallen;
- een test alleen groen kan worden door verwacht gedrag zonder functionele grondslag te wijzigen.

Bij twijfel: expliciet maken, niet invullen.
