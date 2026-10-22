# DVK v0.5 — Functioneel ontwerp Planningssessies

**Status:** Functioneel ontwerp geaccepteerd door CKC op 22 oktober 2026; implementatie en functionele acceptatie van de werking staan nog open.  
**Scope:** Ledendienst Planning, Sportlink Vrijwilligers, tijdelijke DVK-indelingen en No-Shows.

## 1. Doel en uitgangspunt

Een planningssessie is een samenhangende werkvoorraad voor één gekozen periode. De planner bepaalt expliciet wanneer een sessie begint, wordt hervat, wordt afgesloten of wordt vervangen. Browserafsluiting, schermwisseling of herstart van Streamlit, applicatie of computer beëindigen de sessie niet. Er is maximaal één actieve planningssessie.

## 2. Inhoud en grenzen

De actieve planningssessie omvat de geselecteerde periode, de voor die periode gevalideerde Sportlink-vrijwilligersgegevens (inclusief oorspronkelijke inroosteringen, bronstatus en ophaaltijdstip) en de tijdelijke DVK-indelingen met bijbehorende planningsstatus. Deze werkvoorraad wordt duurzaam lokaal bewaard tot expliciete afsluiting of vervanging.

De CKC-dienstencatalogus is onafhankelijke configuratie en blijft altijd beschikbaar. Duurzame No-Show-registraties en intrekkingen staan buiten de levenscyclus van de planningssessie.

## 3. Openen via navigatie ‘Ledendienst Planning’

**A — Geen bestaande sessie:** DVK opent de start van een nieuwe planning. De planner kiest eerst de periode en haalt daarna handmatig de Sportlink-vrijwilligersgegevens op. Zonder gevalideerde bron blijven ingeroosterde namen, bezetting en resterende capaciteit onbekend.

**B — Wel een bewaarde sessie, nieuwe browser- of applicatiesessie:** DVK toont de bewaarde periode en vraagt **Bestaande planning hervatten** of **Nieuwe planning starten**. Hervatten brengt de volledige werkvoorraad terug.

**C — Terugkeer tijdens dezelfde actieve gebruikerssessie:** DVK toont direct de bestaande planning, zonder nieuwe hervatvraag. Gewone navigatie verandert de sessie niet.

## 4. Nieuwe planning starten

1. De planner kiest **Start nieuwe planning**.
2. De planner selecteert de planningsperiode.
3. De planner haalt handmatig de Sportlink-vrijwilligersgegevens voor die periode op via de API.
4. DVK valideert de volledige bronophaalactie.
5. Pas na succes worden namen, bezetting en capaciteit beschikbaar.
6. De planner voert de tijdelijke planning uit en verwerkt goedgekeurde indelingen zelf in Sportlink.

Zonder gevalideerde bron worden geen eerdere inroosteringen als actuele planning gepresenteerd.

## 5. Bewaren, afsluiten en vervangen

Een sessie blijft behouden bij schermwisseling, browserafsluiting en herstart van Streamlit, applicatie of computer.

Een expliciet bevestigde handeling kan de sessie afsluiten of vervangen:
- **Start nieuwe planning:** sluit de bestaande werkvoorraad af en begint opnieuw met periodekeuze.
- **Wijziging van periode:** na bevestiging vervalt de eerdere werkvoorraad; voor de nieuwe periode moet opnieuw worden opgehaald.
- **Nieuwe Sportlink-synchronisatie:** na expliciete bevestiging en volledige succesvolle validatie vervangen nieuwe brongegevens de oude bronuitgangssituatie en vervallen eerdere tijdelijke DVK-indelingen.

DVK waarschuwt vooraf dat tijdelijke indelingen zullen vervallen. De planner bevestigt dat deze niet langer nodig zijn en dat noodzakelijke handmatige verwerking in Sportlink is afgehandeld. Dit is een verklaring van de planner, geen technische verificatie door DVK.

Annuleren behoudt de sessie volledig. Een mislukte of onvolledige synchronisatie laat bestaande brongegevens, tijdelijke indelingen en sessiestatus intact. Het afsluiten of vervangen voert zelf geen Sportlink-mutaties uit.

## 6. No-Shows

Een nieuwe No-Show mag uitsluitend worden geregistreerd op basis van een betrouwbaar aan een lid gekoppelde inroostering uit de actieve, gevalideerde Sportlink-bron voor de gekozen periode. De keuzelijst toont geen boekingen uit afgesloten, eerdere of niet-gevalideerde bronnen. Bij bevestiging wordt de geldigheid opnieuw gecontroleerd; een uitsluitend visuele filter is onvoldoende.

Geregistreerde No-Shows en intrekkingen blijven duurzaam bewaard, ook na afsluiting of vervanging van een planningssessie. Bestaande afspraken over sancties, intrekking en menselijke verantwoordelijkheid blijven gelden.

## 7. Functionele invarianten

1. Maximaal één actieve planningssessie.
2. Alle operationele plannings- en No-Show-schermen gebruiken dezelfde actieve bron en periode.
3. Een technische herstart beëindigt of wist de sessie niet.
4. Tijdelijke indelingen vervallen niet zonder expliciete bevestiging.
5. Een mislukte bronverversing tast bestaande werkgegevens niet aan.
6. No-Shows en intrekkingen worden niet door sessieafsluiting verwijderd.
7. Bronfeiten, tijdelijke DVK-indelingen en duurzame administratieve feiten blijven gescheiden.
8. Sportlink blijft bronhouder; geen automatische writeback in v0.5.

## 8. Functionele acceptatiecriteria

- Alle drie navigatiesituaties werken zoals beschreven.
- Een nieuwe planning begint zonder actieve Sportlink-bron, met eerst periodekeuze en daarna handmatige synchronisatie.
- Een gevalideerde bron levert juiste namen, bezetting en capaciteit.
- Een bewaarde sessie is na browser-, proces- en computerherstart volledig hervatbaar.
- Nieuwe planning, periodewisseling en vervangende synchronisatie volgen de bevestigingsregels.
- Annuleren of mislukte synchronisatie behoudt de volledige bestaande sessie.
- No-Show-selectie en registratie zijn gebonden aan de actieve gevalideerde bron.
- Duurzame No-Shows en intrekkingen blijven na sessieafsluiting beschikbaar.

## 9. Relatie tot eerdere afspraken en implementatiestatus

Dit ontwerp **vervangt de functionele afspraak uit PR #35 dat tijdelijke planning bij een procesherstart vervalt**. De eerdere technische acceptatie van PR #35 blijft historisch correct, maar deze specifieke gedragsregel is achterhaald.

De huidige implementatie voldoet nog niet aan dit ontwerp; in het bijzonder kan de No-Show-keuzelijst eerdere opgeslagen Sportlink-boekingen aanbieden buiten de gevalideerde actieve periode. Dit is een te herstellen functionele fout, geen bewijs van een fout in databasemigraties.

Dit document is uitsluitend een geaccepteerde **ontwerpbaseline**. Technische implementatie, regressietests en lokale functionele acceptatie volgen afzonderlijk. Geen bestaande SQLite-data wissen of migreren als onderdeel van deze documentatiestap.
