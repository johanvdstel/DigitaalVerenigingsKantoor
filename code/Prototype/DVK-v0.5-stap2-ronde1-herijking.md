# Stap 2 ronde 1 — herijking op actuele integratiebaseline

## Context, grondslag en scope

- Baseline: `prototype-v0.5` @ `cba876a440ffc2600007e0a08eab5f8a5e0505c6`, opgehaald en gecontroleerd op GitHub; nieuwe branch `codex/v05-step2-ronde1-herijking` begint exact op deze commit.
- Bronimplementatie: PR #19, head `b7854abb05e227a476ba2c2158e2ee721db30a2f`. PR #19 blijft open en ongewijzigd.
- Gelezen: actuele AGENTS.md, ronde-1-rapport en PR-beschrijving van PR #19, herijkte functionele baseline Ledendiensten en FUNCTIONEEL-CONTRACT-v0.5-vervolg.md. v0.4 blijft de functioneel geaccepteerde technische baseline; v0.5 is integratie/ontwikkeling. De actuele opdracht accepteert de bestaande ronde-1-classificatie als bron voor deze gecontroleerde overname.
- Geaccepteerde eis: uitsluitend de bestaande functie-/commissieclassificatie opnieuw aanbrengen; bronfeiten, configuratie en afleiding gescheiden houden. Sportlink blijft bronhouder. CKC-classificatie en goedgekeurde mapping komen uit ronde 1; geen nieuwe beleidsinterpretatie.
- Vastgesteld feit: de actuele baseline bevat het no-showherstel uit PR #22, maar nog geen functieclassificatie. De oude PR is niet mergeable. Een volledige vervanging van overlappende bestanden zou de nieuwere Sportlink-naamkoppeling verwijderen. Daarom is uitsluitend de gecontroleerde classificatiediff overgenomen, zonder merge of cherry-pick.
- Proportionaliteit: geen extra architectuur, refactor, migratie of reconstructie. Geen operationele gegevens gewijzigd; bestaande geaccepteerde regressiefixtures blijven behouden. De vijf nieuwe ronde-1-bestanden zijn exact uit PR #19 overgenomen.
- Buiten scope: ronde 2, huishoudens, ouderrelaties, peildatumrechtentoepassing en aansluiting op de ledendienstbeslissing. De al bestaande ronde-1-adres/oudernaamvelden blijven uitsluitend optionele bronmodelvoorbereiding en krijgen geen nieuwe importmapping of beleid.

## Vergelijking van alle acht PR-bestanden

Paden hieronder zijn relatief aan `code/Prototype`.

| Bestand | Actuele baseline en gecontroleerde overname |
| --- | --- |
| `dvk/model.py` | Baseline voegt `Person.sportlink_name` toe. Dit veld blijft op zijn bestaande positie, zodat bestaande positionele constructie behouden blijft. Ronde-1-adres/oudernaamvelden worden daarna toegevoegd; RoleAssignment krijgt dezelfde optionele oorspronkelijke titel en provenance als PR #19. Alleen deze veldvolgorde verschilt technisch van PR #19. |
| `dvk/real_data_import.py` | Naamopbouw, `Rel. code`, leden-CSV-route en `read_rows_text` uit PR #22 blijven intact. Alleen de afzonderlijke classificatie-uitkomst en ronde-1-functie/commissieprovenance en datums worden toegevoegd; de inhoudelijke classificatiediff is gelijk aan PR #19. |
| `pyproject.toml` | Niet gewijzigd sinds de oude startbaseline; package-data-instelling overgenomen. Eindbestand byte-identiek aan PR #19. |
| `dvk/function_classification.py` | Ontbreekt op actuele baseline; byte-identiek overgenomen. |
| `dvk/configuration/function_classification.csv` | Ontbreekt; byte-identiek overgenomen, inclusief alle 27/62 sleutels en twee beleidsingangen. |
| `testdata/v05_function_classification/approved_keys.json` | Ontbreekt; onafhankelijke sleutelfixture byte-identiek overgenomen. |
| `tests/test_function_classification_v05.py` | Ontbreekt; alle 104 tests byte-identiek overgenomen, zonder technische of inhoudelijke testaanpassing. |
| `DVK-v0.5-stap2-ronde1-functieclassificatie.md` | Ontbreekt; byte-identiek behouden als historisch ronde-1-rapport. De daar genoemde oude baseline en testaantallen beschrijven de oorspronkelijke uitvoering; dit herijkingsrapport geeft de actuele uitvoering. |

Dit herijkingsrapport is het negende gewijzigde/toegevoegde bestand. Alle overige bestaande baselinebestanden zijn ongewijzigd, waaronder Vrijwilligers-adapter/client, datum/tijdparser, no-showmodel/services/opslag, tijdelijke planning, UI en Streamlit-1.65-testcorrectie. De huidige Sportlink-regressies verifiëren de werking met het gecombineerde model/importbestand.

## Tests en acceptatiecriteria

Verwacht totaal: **312 + 104 = 416**. Werkelijk totaal: **416**. Geen tests verwijderd, gedupliceerd of versoepeld.

- Exacte startbaseline vóór wijziging: **312 geslaagd**.
- Alle actuele baselinetests na overname, classificatiebestand uitgesloten: **312 geslaagd**.
- Ongewijzigde PR #19-classificatietests afzonderlijk: **104 geslaagd**.
- Gerichte combinatie van classificatie, real-data-import, Sportlink/no-show, Vrijwilligers-adapter en intrekkings-UI: **175 geslaagd**.
- Volledige suite: **416 geslaagd** met project-Streamlit 1.64.0.
- Volledige suite: **416 geslaagd** met geïsoleerde Streamlit 1.65.0.
- `git diff --check`: schoon.
- Bytevergelijking met PR #19: classifier, mapping, onafhankelijke sleutelfixture, 104-testbestand, historisch rapport en pyproject identiek.

Een eerste modelpatch plaatste `source_role`/`provenance` per ongeluk bij PersonRelationship in plaats van RoleAssignment. Die tussenstand faalde met 38 classificatietests en 63 volledige-suitetests (353 geslaagd). De modelpatch is gecorrigeerd; geen testverwachting is gewijzigd. Alle bovenstaande eindverificaties zijn daarna uitgevoerd. Dit is een gecorrigeerde uitvoeringsfout, geen gewijzigde functionele afspraak.

CI wordt na push op de nieuwe PR gecontroleerd; uitslag en commit worden in PR/eindrapportage vermeld. Groene CI is geen functionele acceptatie. PR #19 blijft intact en er wordt niet zelfstandig gemerged.

## Resterende aandachtspunten

Geen nieuwe functionele of architectuurbesluiten nodig voor deze overname. De oorspronkelijke ronde-1-beperkingen blijven: exacte adres/ouderheaders en bronvolledigheid, huishoud-/ouderregels, peildatumgeldigheid en daadwerkelijke toepassing van classificatierechten horen bij ronde 2. Het vrije legacy-adres wordt niet geconverteerd en namen leveren geen fictieve relaties. Live Sportlink is niet opnieuw aangeroepen; de bestaande synthetische regressies blijven de technische verificatiebasis.
