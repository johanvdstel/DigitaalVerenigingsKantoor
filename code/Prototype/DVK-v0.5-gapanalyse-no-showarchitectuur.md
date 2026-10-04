# DVK v0.5 — gerichte architectuur- en contractcontrole no-shows

**Status:** technische gapanalyse ter beoordeling; geen functionele beleidswijziging of implementatieacceptatie.  
**Referentie:** `prototype-v0.5`, `code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` FR-01–FR-12 en de herijkte functionele baseline Ledendiensten.  
**Afzonderlijk traject:** PR #19 (functieclassificatie) blijft ongewijzigd en ongemerged; ronde 2 wordt niet gestart zolang de blokkade niet is afgehandeld.

## 1. Functioneel contract

- Sportlink is de enige bronhouder van feitelijke ledendienstinroosteringen. DVK schrijft in v0.5 geen indelingen naar Sportlink.
- DVK maakt voorstellen en bewaart tijdelijke planningsposities uitsluitend als werkvoorraad. De planner verwerkt de gewenste indeling handmatig in Sportlink. Na succesvolle nieuwe import geldt de nieuwe Sportlink-positie als actuele werkelijkheid; tijdelijke DVK-posities worden vervangen.
- Een no-show kan uitsluitend worden geregistreerd op een concrete, feitelijke Sportlink-inroostering, ongeacht hoe die inroostering oorspronkelijk tot stand kwam. Een tijdelijk DVK-voorstel is onvoldoende.
- DVK bewaart een no-show als zelfstandig, onveranderlijk en duurzaam feit, met voldoende dienstcontext en Sportlink-bronherkomst om het feit ook na een latere bronwijziging te begrijpen.
- Een intrekking van een no-show blijft een afzonderlijk duurzaam feit met verplichte toelichting, actor en tijdstip. Actuele teller en sanctiestatus worden afgeleid zonder ingetrokken no-shows.
- Een eventuele Sportlink-urencorrectie blijft een afzonderlijke handmatige werkvoorraad; DVK muteert Sportlink niet.

**Geen herziening:** DVK blijft eigenaar van nieuwe no-showregistraties en de historie van bijbehorende intrekkingen. Bestaande prototype-no-shows uit de achterhaalde functionaliteit zijn wegwerpbare testgegevens: geen migratie of behoud vereist.

## 2. Geconstateerde technische verschillen

| Onderdeel | Huidige implementatie | Contractverschil / actie |
|---|---|---|
| Tijdelijke planning | `PlanningApplicationService` gebruikt `temporary_planning`; terugdraaien is mogelijk. | In lijn met tijdelijke werkvoorraad; behoud regressies. |
| Herkomst no-show | `NoShowApplicationService.register()` accepteert een `assignment_id` uit `uow.assignments` (`duty_assignments`). | Bestaan in de DVK-repository bewijst niet dat de indeling feitelijk in Sportlink staat. Verplicht aantoonbare Sportlink-bronherkomst. |
| Beschikbare UI-indelingen | `NoShowApplicationService.assignment_contexts()` leest `uow.assignments.recent()`; de Streamlit-no-showselectie gebruikt deze lijst. | Vervang selectiebron door concrete feitelijke Sportlink-inroosteringen. |
| Duurzame no-showcontext | `NoShowEvent` bevat een verwijzing naar een `assignment_id`; `revocable_no_shows()` verwacht dat die DVK-indeling later nog bestaat. | Bepaal sleutel, provenance en immutable snapshot zodat een no-show ook na nieuwe Sportlink-import zelfstandig raadpleegbaar blijft. |
| No-showintrekking | `NoShowRevocation` en de opslag bewaren apart actor, tijdstip en toelichting; de teller sluit intrekkingen uit. | Functioneel behouden; technische afhankelijkheid van legacy indeling onderzoeken. |
| UI-regressietest | `test_gate10ade_ui_v05.py` zet synthetische DVK-indelingen in de repository om intrekking te testen. | Gebruik synthetische feitelijke Sportlink-inroosteringen; voeg negatieve test voor uitsluitend tijdelijke DVK-planning toe. |
| CI-fout PR #19 | Bestaande intrekkings-UI-test mist exact verwachte succesmelding in GitHub Actions, terwijl lokale suite groen is. | Oorzaak afzonderlijk vaststellen; architectuurverschil bewijst geen verband met deze CI-fout. |

De docstring van `DutyAssignment` beschrijft `duty_assignments` expliciet als legacy no-showverwijzingen. De aparte `temporary_planning`-repository toont dat de scheiding gedeeltelijk al is aangebracht; de no-showketen is nog niet volledig meegegaan.

## 3. Controle volgens AGENTS.md §4a

**Projectfase en status.** v0.5 is een prototype, `prototype-v0.5` de integratiebranch en `main` de geaccepteerde v0.4-baseline. PR #19 betreft afzonderlijk functieclassificatie en wordt hier niet aangepast. Er is geen operationele DVK-no-showdatabase die gemigreerd moet worden.

**Vastgestelde codefeiten.** `dvk/real_data_import.py` bevat een read-only Sportlink-adapter voor personen, lidmaatschappen, functies en vrijwilligersuren, maar geen aangetoonde import van individuele feitelijke dienstindelingen. `dvk/import_management.py`, `dvk/persistence/sqlite.py` en `dvk/persistence/migrations.py` bevatten reeds generieke importbatches, bronsnapshots, records en provenance. `NoShowApplicationService` leest daarentegen uit de legacy `duty_assignments`-repository. `NoShowEvent` bewaart alleen een `assignment_id`, en `revocable_no_shows()` is afhankelijk van de beschikbaarheid van die legacy indeling. De UI-test maakt zulke indelingen rechtstreeks aan.

**Geaccepteerde eisen.** FR-01–FR-12 onderscheiden Sportlink als feitelijke bron, DVK als tijdelijke planningswerkvoorraad en no-shows/intrekkingen als duurzame DVK-feiten. Bestaande achterhaalde prototype-no-shows en hun intrekkingen mogen worden weggegooid. Geaccepteerde functionele regressiegevallen worden inhoudelijk behouden en waar nodig opnieuw opgebouwd met passende synthetische brondata.

**Nog onbewezen.** Het daadwerkelijke exportformaat voor individuele Sportlink-dienstindelingen, de beschikbare bronidentificator en de precieze technische oorzaak van de rode CI-test zijn niet vastgesteld. Er mag daarom nog geen definitieve Sportlink-sleutel of importkolommapping als feit worden voorgeschreven.

**Proportionaliteit.** Een gerichte uitbreiding op de bestaande bronimport is noodzakelijk omdat FR-09 zonder feitelijke Sportlink-indelingen niet afdwingbaar is. Een generieke nieuwe importlaag, migratie van wegwerpdata, historische reconstructie en andere refactors zijn niet nodig en blijven buiten scope.

## 4. Afgebakende vervolgopdracht (nog niet uitvoeren)

1. Stel eerst vast welke feitelijke Sportlink-export/API-gegevens voor individuele dienstindelingen beschikbaar zijn (inclusief bronidentificatie, peildatum en vervanging bij volgende import). Leg ontbrekende gegevens als technische blokkade voor; verzin geen kolommen of sleutel. Hergebruik de bestaande generieke importvoorziening.
2. Bepaal pas op basis van vastgestelde bronvelden een canonieke, uit Sportlink afkomstige inroostering en voldoende duurzame no-showcontext. Borg dat latere bronsynchronisatie bestaande nieuwe no-shows en intrekkingen niet aantast.
3. Herijk applicatieservice, opslag en UI zonder tijdelijke DVK-planning duurzaam tot feitelijke indeling te promoveren. Verwijder bestaande legacy prototype-no-shows en bijbehorende intrekkingen uit de testomgeving; bouw geen datamigratie.
4. Vervang legacy testfixtures; test positieve registratie, weigering van tijdelijke DVK-planning, één oorspronkelijke no-show per feitelijke inroostering, duurzame raadpleegbaarheid na bronwijziging, intrekking en actuele teller.
5. Onderzoek los daarvan de rode GitHub Actions-test: controleer op baseline en werkbranch de werkelijke database-uitkomst en getoonde meldingen, en reproduceer waar mogelijk met Streamlit 1.64.0 en 1.65.0. Niet op voorhand testverwachtingen versoepelen of dependencies vastpinnen.
6. Voer gerichte tests en volledige regressiesuite uit. Geen wijzigingen in PR #19, geen merge zonder expliciete acceptatie, geen opportunistische refactors.

## 5. Open technische punten

- Welk Sportlink-exportformaat levert de feitelijke inroosteringen en welke sleutel is daarin voldoende stabiel?
- Welke gegevens zijn minimaal nodig in de immutable no-showsnapshot, inclusief datum, dienst, persoon en bron/provenance?
- **Besloten:** bestaande legacy no-shows en eventuele intrekkingen zijn uitsluitend achterhaalde prototype-/testgegevens en worden weggegooid. Geen inventarisatie, herkomstonderzoek of migratie nodig. Nieuwe no-shows en intrekkingen blijven voortaan duurzaam DVK-eigendom.
- Is de rode CI-test een Streamlit-versieverschil, testharnasprobleem of werkelijk functioneel probleem? Dit is nog niet vastgesteld.

**Beslisgrens:** deze analyse is een documentatievoorstel. De technische vervolgopdracht bevat een bronverificatiepoort: als de feitelijke Sportlink-indelingen of sleutel niet vaststaan, eerst het broncontract vastleggen en géén geïmproviseerd datamodel implementeren. Implementatie en testwijzigingen volgen pas na acceptatie en afzonderlijke opdracht. Migratie van legacy no-showgegevens is expliciet buiten scope.
