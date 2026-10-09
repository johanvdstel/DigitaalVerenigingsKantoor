# DVK — Backlog

**Status:** voorlopige, herleidbare werklijst · **Bijgewerkt:** 9 oktober 2026  
**Scope:** Digitaal Verenigingskantoor, in het bijzonder prototype v0.5.  
**Doel:** openstaande werkzaamheden en besluiten bewaren voor latere opvolging. Dit document is geen functionele baseline en geen bewijs dat een onderdeel nog geheel ontbreekt.

> De eerdere backlog uit een verwijderde chat is niet beschikbaar. Onderstaande punten zijn gereconstrueerd uit de actuele v0.5-documenten in GitHub en de nadien expliciet gemaakte afspraken. Bij vervolgwerk eerst de actuele code, branches en eventuele GitHub Issues controleren. Niet automatisch als nieuwe implementatieopdrachten beschouwen.

## Actieve werkzaamheden

| ID | Onderwerp | Status / eerstvolgende stap | Bron |
| --- | --- | --- | --- |
| BL-01 | Taakplichtcontrole: adresgebaseerde broederdienst B-06/B-07 | **Actief.** Functionele baseline, code en synthetische regressies aanpassen en daarna lokaal met CKC-exports hertesten. Zelfde volledige adres is het enige automatische gezinscriterium; ouders, achternaam en `Contact via ouders` zijn geen beslisgegevens. | Herijkingsbesluit 9 oktober 2026; `DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md` B-05–B-07 |
| BL-02 | Read-only taakplichtcontroledashboard | **In uitvoering / functionele hertest open.** Vergelijk DVK-afleiding met Sportlink A, inclusief afwijkingen, onzekerheden en bron- en controlediagnose. | `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` E-06; baseline B-09/B-10 |

## Uitgesteld of nog uit te werken

| ID | Onderwerp | Status / eerstvolgende stap | Bron |
| --- | --- | --- | --- |
| BL-03 | Achterstallige uren uit vorig seizoen | **Uitgesteld — bron ontbreekt.** Bepaal betrouwbare bron, seizoensidentificatie, peildatum, verwerking en voorkomen van dubbeltelling. Volgens B-13 kunnen openstaande uren **vóór 1 december** meewegen bij kandidaatprioritering; niet automatisch optellen bij nieuwe Sportlink A. Geen blokkade voor BL-01. | Herijkte baseline B-13; besluit 9 oktober 2026 |
| BL-04 | DVK-frontend / hoofdmenu / licht portaal | **Gepland; actuele implementatiestatus verifiëren.** Eén herkenbare DVK-ingang met modulenavigatie. Ledendienst Planning is één module; toon toekomstige modules eerlijk als niet beschikbaar. Rooster Generator mag als operationeel maar nog niet geïntegreerd zichtbaar zijn. Geen generiek portaalframework nodig voor v0.5. | `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` F-01–F-07; `TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md` sectie F |
| BL-05 | Duurzame plannerbeslissingen en afwijkingen | **Status verifiëren / resterende functionaliteit afbakenen.** Reden, verantwoordelijke, geldigheid, bevestiging na nieuwe import en herbeoordeling van geaccepteerde afwijkingen. | Herijkte baseline B-09/B-14; V-05 |
| BL-06 | Urenoverdracht bij 18 jaar | **Status verifiëren.** Alleen na menselijke goedkeuring via twee tegengestelde Sportlink-B-correcties; samen controleren na nieuwe import. Geen automatische overdracht. | Herijkte baseline B-08; V-05 |
| BL-07 | Sportlink-urenbron en seizoensgegevens | **Bronverificatie open.** Werkelijke velden/semantiek A/B/C/D/E, seizoensidentificatie en verificatie van B-correcties. | Herijkte baseline §7 |
| BL-08 | Functieclassificatie `Verzorger` | **Wachten op broncorrectie CKC.** Eén onbetaalde `Verzorger` is tijdelijk als betaald geclassificeerd; na onderscheidende Sportlink-titel opnieuw classificeren. Geen persoonsgebonden hardcode. | Herijkte baseline B-04 |
| BL-09 | Bronactualiteit en geldigheid functies/commissies | **Bewaken / nader verifiëren bij bronwijziging.** Huidige exports hebben beperkte datumvelden; signalering van verouderde bronnen behouden. | Herijkte baseline B-11/B-12 |
| BL-10 | Tijdelijke planning en Sportlink-synchronisatie | **Integrale status/acceptatie verifiëren.** Bestaande implementaties en tests controleren; read-only, gezamenlijke syncgrens en behoud tijdelijke werkvoorraad bij fouten. | `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` FR-02–FR-08; GitHub Issues #12 en #14 |
| BL-11 | No-shows en handmatige correctiewerkvoorraad | **Integrale status/acceptatie verifiëren.** No-showfeiten, sancties en handmatige Sportlink-correcties in samenhang toetsen. | Herijkte baseline §5; `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` FR-09–FR-12 |
| BL-12 | Integrale acceptatie prototype v0.5 | **Nog open.** Samenhangende functionele acceptatie en regressie van broncontracten, taakplicht, planning, synchronisatie, no-shows en portaal. | Herijkte baseline §§6–8; root `README.md` |

## Afspraken voor opvolging

1. **Geen dubbele backlog:** controleer bij vervolg eerst of een punt al als GitHub Issue of implementatiecontract bestaat.
2. **Prioriteit:** rond BL-01/BL-02 af vóór nieuwe uitgestelde functionaliteit; verdere prioritering later expliciet afspreken.
3. **Privacy:** echte CKC-bronbestanden blijven op de computer van de opdrachtgever; geen persoonsgegevens in GitHub.
4. **Wijzigingsbeheer:** backlogitems wijzigen de geaccepteerde baseline niet automatisch. Functionele keuzes, code en regressies worden afzonderlijk gecontroleerd.
5. **Onbekende historische items:** deze inventaris is niet noodzakelijk volledig; vul aan wanneer oudere afspraken alsnog worden teruggevonden.

## Brondocumenten

- [Herijkte functionele baseline](code/Prototype/DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md)
- [Functioneel contract v0.5 vervolg](code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md)
- [Technische impactanalyse v0.5 vervolg](code/Prototype/TECHNISCHE-IMPACTANALYSE-v0.5-vervolg.md)
- [GitHub Issue #12](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/12)
- [GitHub Issue #14](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/issues/14)
