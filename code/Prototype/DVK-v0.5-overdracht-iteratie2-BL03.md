# DVK v0.5 — Overdracht Iteratie 2: BL-03 achterstallige uren

## Rol en startopdracht

Deze overdracht is voor de functionele ontwerpchat. Begin met repository- en code-inventarisatie; niet direct bouwen. Johan bepaalt de functionele werkelijkheid, ChatGPT verzorgt functioneel ontwerp/architectuur en gecontroleerde opdracht, Codex technisch ontwerp/bouw/tests, daarna afzonderlijke controle en Johans acceptatie. Vraag akkoord op de concrete implementatieaanpak voordat uitvoering begint.

## Uitgangssituatie

Iteratie 1 (BL-17/20/21) is op 29 oktober 2026 functioneel geaccepteerd; PR #53 is met expliciete toestemming aangeboden voor merge naar prototype-v0.5. Verifieer bij start de definitieve merge en actuele branch-head op GitHub; leg de gekozen baselinecommit vast vóór wijzigingen. De geaccepteerde codecommit van Iteratie 1 is 9016c8a17f631bf015308ce43ba50169c7c1aa21; zie het iteratieverslag voor acceptatie en herstelrondes. Eén weekendrichting en noodkandidaten zijn uitsluitend synthetisch gedekt. Integrale v0.5-acceptatie blijft open; main blijft geaccepteerde v0.4-baseline en PR #5 blijft draft.

Sportlink bepaalt de kandidatenbasis, niet de DVK-beleidsvrijstelling. Teams-veld Speeldag stuurt weekendselectie; vrijdagteams zijn geldig zonder eigen weekendbeperking. Noodkandidaten van de andere weekenddag zijn uitsluitend beschikbaar bij onvoldoende overige geschikte kandidaten voor het actuele minimum. Kandidaattoelichting verschijnt direct per aangevinkte kandidaat; selectie is geen bevestiging. Behoud dit gedrag.

## BL-03 — Bevestigde scope

Het planner-Excel met achterstallige uren uit het vorige seizoen is reeds beschikbaar. Er is geen externe aanleverblokkade. Verifieer kolommen, betekenis, seizoen en persoonskoppeling uitsluitend lokaal. Koppeling bij voorkeur op Sportlink-lidnummer; ontbrekende matches, duplicaten en onduidelijke seizoenen niet gokken. Geen persoonsgegevens, bronregels of echte bestanden in chats, GitHub, logs of tests.

Achterstallige uren beïnvloeden kandidaatprioritering tot en met 31 december; vanaf 1 januari tellen zij niet mee. Niet optellen bij Sportlink A van het nieuwe seizoen. Dit is de vastgelegde wijziging van B-13 ten opzichte van de historische grens 1 december. Werk functionele baseline, relevante configuratie en regressies traceerbaar bij; verander historische geaccepteerde cases niet zonder afzonderlijk besluit.

## Verplichte inventarisatie

Lees AGENTS.md, README.md, BACKLOG.md (BL-03), DVK-PROTOTYPE-PLANNING.md, PRODUCTIE-ROADMAP.md en relevante uren-/prioriteitscontracten, plus het Iteratie-1-verslag. Onderzoek onder meer dvk/prioritization.py, kandidaatcontext, bronimport, kandidaatpresentatie en bestaande tests. De operationele planning schakelde vorigeseizoensprioritering uit via apply_previous_season=False; historische code kent de oude decembergrens. Verifieer de actuele toestand in plaats van deze aanwijzingen als actuele feiten over te nemen.

Rapporteer compact wat al bestaat, aantoonbare gaps, bronverificatiepunten, risico's en minimale aanpak. Onderscheid feiten, geaccepteerde eisen en onbewezen aannames. Leg alleen echt ontbrekende functionele keuzes voor. Ontwerp geen productie-infrastructuur, migratie of bewaarplicht zonder grondslag.

## Uitvoering na akkoord

Afzonderlijke werkbranch vanaf expliciete actuele prototype-v0.5-baseline, gerichte synthetische regressies (inclusief 31 december en 1 januari), volledige suite, CI en PR naar prototype-v0.5. Geen merge zonder expliciet akkoord. Geen uitvoering van BL-14, BL-19, BL-22/23/24 of writeback. Behoud oorspronkelijke lokale wijzigingen; hergebruik of verplaats geen echte databases.
