# Digitaal Verenigingskantoor

Deze repository bevat de functionele modellen, ontwerpen, documentatie en uitvoerbare prototypes voor het **Digitaal Verenigingskantoor (DVK)** van CKC.

## Huidige mijlpaal

**DVK Prototype v0.3 — Werkstroom Ledendiensten & Vrijwilligersbeleid, Fase 1 — is functioneel geaccepteerd op 8 september 2026.**

De geaccepteerde implementatie staat onder [`code/Prototype/`](code/Prototype/). Daar zijn ook de formele [`BASELINE-v0.3.md`](code/Prototype/BASELINE-v0.3.md), het v0.3-ontwerp, de regressietests en de uitvoerbare acceptatierunners opgenomen.

De baseline omvat:

- de bestaande geaccepteerde C01–C22-functionaliteit;
- Sportlink-achtige bronimport;
- automatische taakplicht en urenpositie;
- kandidaatselectie en uitlegbare prioritering;
- adviesplanning en dashboard;
- menselijke goedkeuring/afwijzing;
- feitelijke `DutyAssignment` na goedkeuring;
- geïntegreerde end-to-endacceptatie.

De afsluitende acceptatierun rapporteerde **59 geslaagde tests** en een reproduceerbare functionele v0.3-keten.

## Repositorystructuur

- `code/Prototype/` — uitvoerbare DVK-prototypes, ontwerpen, testcases en baseline;
- `docs/informatiemodel/` — canoniek en logisch informatiemodel, gegevenswoordenboek en bronnenmapping;
- `docs/DVK – Werkstroom Ledendiensten & Vrijwilligersbeleid/` — functionele werkelijkheid en werkstroomdocumentatie;
- `docs/functioneel-ontwerp/` — functionele ontwerpen per domein;
- `docs/procesontwerp/` — procesontwerpen.

## Baselineprincipe

Prototype v0.3 is vanaf de acceptatiedatum de functionele regressiebasis. Nieuwe ontwikkeling wordt hier bovenop uitgevoerd en moet de geaccepteerde werking behouden, tenzij CKC expliciet een functionele wijziging besluit.

Zie voor technische details en uitvoerinstructies de [`README` van het prototype](code/Prototype/README.md).
