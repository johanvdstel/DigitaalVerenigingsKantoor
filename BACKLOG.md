# DVK — Functionele backlog

**Status:** bijgewerkt naar aanleiding van backlogbespreking 9 oktober 2026  
**Scope:** prototype v0.5 en later; geen implementatieplanning of productiearchitectuur.  
**Verwijzingen:** [Prototypeplanning](DVK-PROTOTYPE-PLANNING.md) · [Productieroadmap](PRODUCTIE-ROADMAP.md)

De backlog bevat openstaande functionaliteit, beleidsbesluiten en bronafhankelijkheden. De volgorde, afzonderlijke ontwikkelstappen en integrale acceptatiemijlpaal staan in de prototypeplanning. Statussen beschrijven wat is afgesproken; ze bewijzen niet dat code al bestaat.

## Afgerond

| ID | Onderwerp | Status / bewijs |
| --- | --- | --- |
| BL-01 | Adresgebaseerde huishoud- en minderjarigenregels B-05/B-06/B-07 | **Afgerond en functioneel geaccepteerd** in Stap 2 ronde 4; uitsluitend volledig geregistreerd adres als automatische huishoudsleutel; relevante leden op peildatum; geen ouder-/achternaamheuristiek. |
| BL-02 | Read-only taakplichtcontroledashboard | **Afgerond en functioneel geaccepteerd.** Lokale CKC-acceptatie: 650 relevante leden, 563 overeenkomsten, 87 afwijkingen, 0 niet betrouwbaar beoordeelbaar. Bron- en controlediagnose behouden. [PR #28](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/pull/28) gemerged naar `prototype-v0.5`. |

## Open / geprioriteerd

| ID | Onderwerp | Afspraak en eerstvolgende stap | Afhankelijkheid |
| --- | --- | --- | --- |
| BL-03 | Achterstallige uren vorig seizoen | **Hoge prioriteit, v0.5.** Planner bevestigt beschikbaar Excel-overzicht; bestand/kolommen nog te ontvangen en lokaal te verifiëren. Koppeling bij voorkeur op Sportlink-lidnummer, met seizoen, openstaande uren en controle op duplicaten/ontbrekende matches. Achterstand beïnvloedt kandidaatprioritering **tot en met 31 december**; vanaf 1 januari niet meer. Niet optellen bij Sportlink A van het nieuwe seizoen. **Wijziging B-13** t.o.v. eerdere grens 1 december: functionele baseline, configuratie en regressietests expliciet bijwerken vóór implementatie. | Excel van planner; bronsemantiek en seizoensidentificatie |
| BL-04 | DVK-frontend, hoofdmenu, licht portaal | **Eerstvolgende ontwikkelstap.** DVK-welkomstpagina met moduleoverzicht; Ledendienst Planning toegankelijk, taakplichtcontrole als functie daarbinnen. Rooster Generator tonen als operationeel buiten DVK, overige modules eerlijk als toekomstig. Lichte Streamlit-navigatie; geen nieuw portaalframework, geen beleidslogica in UI. | F-01–F-08; actuele UI verifiëren |
| BL-05 | Duurzame plannerbeslissingen bij taakplichtafwijkingen | **v0.5, na terugkoppeling planner.** Leg besluit, reden, actor, tijdstip, geldigheid en herbeoordeling na bronvernieuwing vast; onderscheid DVK-afleiding van menselijke administratieve beslissing. Ontwerp mede op basis van beoordeling van de 87 afwijkingen. | Terugkoppeling CKC-planner; B-09/B-14 |
| BL-06 | Urenoverdracht bij 18 jaar | **v0.5.** Signaleer overdrachtsmogelijkheid; uitsluitend menselijke goedkeuring en twee tegengestelde handmatige Sportlink-B-correcties; na nieuwe import beide verifiëren. Geen automatische Sportlink-mutatie. | B-08; verificatie Sportlink B |
| BL-07 | Sportlink-urenbron en seizoensgegevens | **Gedeeltelijk gevalideerd.** Sportlink A is voor read-only taakplichtcontrole met echte CKC-exports getoetst. Nog open: werkelijke B/C/D/E-betekenis, beschikbare velden, seizoensafbakening en controle van correcties na import. | Brononderzoek Sportlink |
| BL-08 | Functieclassificatie `Verzorger` | **Wacht op CKC-broncorrectie.** Onderscheid betaalde en onbetaalde functie in Sportlink nog niet betrouwbaar; huidige tijdelijke classificatie niet persoonsgebonden hardcoden. Na correctie lokaal opnieuw controleren. Blokkeert ander v0.5-werk niet. | CKC/Sportlink |
| BL-09 | Bronactualiteit functies en commissies | **Bewaken binnen v0.5.** Bestaande bron- en controlediagnose behouden; verouderde of onvolledige bronfeiten signaleren, geen ontbrekende functiedatums verzinnen. Geen aparte ontwikkelronde tenzij controle een concrete tekortkoming aantoont. | Nieuwe bronexports |
| BL-10 | Tijdelijke planning en Sportlink-synchronisatie | **v0.5, integrale verificatie.** Bestaande implementatie eerst inspecteren; controleer directe bezettings- en beschikbaarheidseffecten, undo, handmatige Sportlink-verwerking, succesvolle sync als grens en behoud werkvoorraad bij mislukte sync. Alleen aantoonbare gaps herstellen. | API Vrijwilligers; FR-02–FR-08 |
| BL-11 | No-shows en handmatige Sportlink-correctiewerkvoorraad | **v0.5, integrale verificatie.** Controleer koppeling aan feitelijke Sportlink-inroostering, duurzame no-show, intrekking, sanctieafleiding en status openstaand/afgehandeld van handmatige correctie. Hergebruik geaccepteerde functionaliteit. | API Vrijwilligers; FR-09–FR-12 |

## Gegevensintegraties als afzonderlijke ontwikkelstappen

De **Vrijwilligers API** en **Programma API** zijn noodzakelijke bouwstenen voor Stap 3 Planning. Ze staan als aparte acceptatiestappen in [DVK-PROTOTYPE-PLANNING.md](DVK-PROTOTYPE-PLANNING.md), niet als verondersteld geheel nieuwe backlogfunctionaliteit. Eerst de actuele adapters, broncontracten en werkelijke integratiestatus verifiëren; geen duplicatie.

## Niet in de backlog

Voormalig **BL-12 — Integrale acceptatie prototype v0.5** is een **implementatie-/acceptatiemijlpaal**, geen functionele backlogwens. Deze staat daarom in de [prototypeplanning](DVK-PROTOTYPE-PLANNING.md).

## Werkafspraken

1. Besluiten uit deze bespreking vormen geen stilzwijgende codewijziging. Functionele baseline, technische implementatie en tests worden traceerbaar bijgewerkt.
2. Echte CKC-bestanden (Sportlink CSV's, planner-Excel), persoonsgegevens en lokale databases blijven op de eigen computer; niet uploaden naar GitHub, Codex of ChatGPT. Alleen synthetische voorbeelden en niet-herleidbare aggregaten in repository.
3. Elke ontwikkelstap krijgt een afgebakende branch/PR, regressie en expliciete functionele acceptatie; geen merge zonder akkoord.
4. Productievereisten worden apart beheerd in [PRODUCTIE-ROADMAP.md](PRODUCTIE-ROADMAP.md).
5. De historische backlog is een gereconstrueerde werklijst; controleer bij uitvoering de actuele code en GitHub Issues voordat iets als ontbrekend wordt aangemerkt.

## Functionele bronnen

- [Herijkte functionele baseline Ledendiensten](code/Prototype/DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md)
- [Functioneel contract v0.5 vervolg](code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md)
- [Technische impactanalyse v0.5 vervolg](code/Prototype/TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md)
- [GitHub Issue #12](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/12) en [#14](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/14)
