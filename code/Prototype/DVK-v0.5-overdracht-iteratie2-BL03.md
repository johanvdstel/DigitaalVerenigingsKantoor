# DVK v0.5 — Overdracht Iteratie 2: BL-03

**Actueel (29 oktober 2026):** BL-03 functioneel geaccepteerd op implementatiecommit `e3b17fc83e88d9640bc011afc69a666b8b8dbe1a` van PR #55; merge staat nog open.

Deze overdracht vervangt de eerdere Excel-, bronseizoenverificatie- en 1-decemberaannames volgens de expliciete opdracht van Johan. De rolverdeling in AGENTS.md blijft gelden; geen gedeelde chatcontext of automatische toestemming veronderstellen.

## Baseline

prototype-v0.5 op 881d807138f951a69d651e8ee37b68042fe319a4 (PR #53, Iteratie 1 geaccepteerd). Bij uitvoeringsstart identiek aan GitHub. main blijft geaccepteerde v0.4; integrale v0.5-acceptatie blijft open. Werkbranch codex/iteratie-2-historische-achterstand, werkmap /private/tmp/dvk-iteratie-2. Oorspronkelijke werkmap en twee lokale wijzigingen blijven ongemoeid.

## Definitieve afspraken

Historische bron: `~/Documents/DVK-Sportlink-exports/Overzicht per periode vorig seizoen.csv`, dezelfde CSV-kolomstructuur als de actuele urenexport. De planner levert het onmiddellijk voorafgaande seizoen; DVK leidt of verifieert dat bronseizoen niet zelfstandig. Koppeling uitsluitend op `Relatiecode`; `Niet ingedeeld` is de bronwaarde, getoetst aan A−B−C−D. Positieve achterstand telt als tweede criterium na actuele E voor diensten in **juli tot en met december** (`7 <= on_date.month <= 12`); januari t/m juni niet. Nul betekent geen achterstand; negatieve waarden blijven als bronfeit behouden en geven geen krediet. Actuele A/B/C/D/E blijven ongewijzigd.

Bij ontbrekend, onleesbaar of structureel ongeldig historisch bestand blijft planning bruikbaar met een zichtbare waarschuwing. Ontbrekende ledenregels, dubbele relatiecodes, ongeldige getallen en formuleverschillen leveren voor de betrokken kandidaat onbekende/onbetrouwbare historische achterstand op; geen uitsluiting of stilzwijgende nul. Voor rangschikking neutraal, in toelichting onderscheiden van bekende nul, ontbrekende bron en maanden buiten toepassing. Andere geldige historische records blijven bruikbaar. Taakplichtcontrole blijft onafhankelijk van deze optionele bron.

Geen aanvullende seizoensmetadata, database, migratie of alternatieve persoonsmatching. De historische export is geen algemene verplichte bron. De W09-verwachting op 1 december is na expliciet aanvullend akkoord aangepast, met behoud van testgegevens. Huidige maandenregel en regressies omvatten ook juni/juli en december/januari over meerdere kalenderjaren.

## Controle en acceptatie

Zie [Iteratie-2-verslag](DVK-v0.5-iteratie2-historische-achterstand.md) voor code-/testherleiding, resultaten en synthetische browserproef. Controleer de exacte opgeleverde commit en CI; de lokale synthetische acceptatie is op 29 oktober 2026 geslaagd (prioriteit 8/4/0 bij actuele E=10; bronwaarschuwing zonder historische CSV; bevestiging en undo). Zie het bijgewerkte Iteratie-2-verslag. Geen merge zonder afzonderlijke toestemming. Geen andere backlogitems uitvoeren.
