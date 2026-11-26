# CKC-beleidsregelindex Ledendiensten — prototype v0.5

## Leeswijzer en gezag

Deze index beschrijft bestaand beleid en uitvoerbare synthetische voorbeelden.
Hij stelt geen nieuw beleid vast en is geen integrale functionele acceptatie van
v0.5. Onderzoeksbasis: `prototype-v0.5` op
`4699e036147e051b2958fe0e71496ae104b0d864`; BL-22 verandert alleen de organisatie
van de uitvoering. De normatieve bronnen zijn:

- [Herijkte baseline B-01–B-14](../code/Prototype/DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md).
- [Taakplichtcontract E-01–E-08](../code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md).
- [Actuele backlogbesluiten](../BACKLOG.md), met name BL-03, BL-08, BL-09, BL-17 en BL-20.
- [Broncontracten](../DVK-BRONCONTRACTEN-v0.5.md): deels reconstructieconcept;
  alleen afzonderlijk goedgekeurde aanvullingen zijn vastgestelde aanvullingen.
- Acceptaties [Iteratie 1](../code/Prototype/DVK-v0.5-iteratie1-kandidaten-versiebeheer.md),
  [2](../code/Prototype/DVK-v0.5-iteratie2-historische-achterstand.md),
  [3](../code/Prototype/DVK-v0.5-iteratie3-bronstatus-rubrieken.md),
  [4](../code/Prototype/DVK-v0.5-iteratie4-BL14.md) en
  [5](../code/Prototype/DVK-v0.5-iteratie5-BL19.md).

Sportlink is bronhouder van leden, teamregistraties, functies, feitelijke
inroosteringen en geregistreerde uren. CKC bepaalt het beleid. DVK berekent
kwalificaties, verwachtingen en voorstellen; de mens beslist.

**Verwachte taakplicht en kandidatenbasis verschillen:** Taakplichtcontrole
berekent welke A CKC verwacht. Ledendienst Planning gebruikt de geregistreerde
Sportlink-A als leidende taakplicht, ook als de controle een vrijstelling of
onzekerheid meldt. Overige bron-, leeftijds-, uren- en geschiktheidscontroles
blijven gelden. Een voorstel wordt pas een tijdelijke indeling na bevestiging.

De vaste rubrieken per regelgroep zijn ook bruikbaar als inhoudsbasis voor een
latere read-only functie 'Beleidsregels bekijken'. Er is nu geen nieuw scherm,
opslag of beleidsbeheer gebouwd. Regelnummer, brongegevens, uitkomst, toelichting
en tests zijn herbruikbare organisatieprincipes; dit document definieert geen
beleid voor Ledenadministratie of Wedstrijdsecretariaat.

## B-01/B-03 — Actueel lidmaatschap

**Soort:** broninterpretatie en afgeleide kwalificatie.

**Betekenis:** lidmaatschap en voetbaldeelname zijn afzonderlijke begrippen.
De afmelddatum is de eerste dag zonder geldig lidmaatschap.

**Brongegevens:** Leden-export: relatiecode, Lidstatus en Afmelddatum; peildatum.

**Voorwaarden en uitzonderingen:** Definitief zonder afmelddatum is actueel.
Met een afmelddatum wordt de peildatum ermee vergeleken. Ontbrekende,
ongeldige of conflicterende gegevens worden niet stilzwijgend gerepareerd.
De dashboardpopulatie en operationele kandidatenbasis hebben eigen aanvullende
statusvoorwaarden; de kandidatenbasis vereist Definitief.

**Uitkomst en toelichting:** actueel, niet actueel of onzeker. In de taakplicht
kan 'Geen actueel lidmaatschap op de peildatum' de grond zijn.

**Demonstratie D-01:** oudste minderjarige heeft afmelddatum 6 oktober 2026.
Op 5 oktober valt het jongere kwalificerende kind nog onder de gezinsregel;
op 6 oktober verschuift de verplichting naar dat jongere kind.

**Implementatie en test:** `SportlinkRealDataAdapter.current_membership` in
[`real_data_import.py`](../code/Prototype/dvk/real_data_import.py),
`_membership_grounds` in [`member_duty.py`](../code/Prototype/dvk/member_duty.py);
[`test_member_duty_v05.py`](../code/Prototype/tests/test_member_duty_v05.py),
`test_membership_end_moves_family_duty_on_exact_date`;
[`test_candidate_person_issues_v05.py`](../code/Prototype/tests/test_candidate_person_issues_v05.py),
`test_only_definitief_may_proceed_regardless_of_other_status_end_date`.

## B-02 — Bondsteamdeelname

**Soort:** afgeleide kwalificatie op één teamregistratie.

**Betekenis:** een registratie kwalificeert alleen als die tegelijk Bond,
Teamspeler en Spelend lid=Ja aangeeft. Een extra trainersrol maakt een
kwalificerende spelersregistratie niet ongedaan.

**Brongegevens:** Teams-export, gekoppeld op relatiecode; teamsoort, teamrol en
geparseerde speelstatus. Een ledenveld met voetbalactiviteiten is geen vervanging.

**Voorwaarden en uitzonderingen:** voorwaarden mogen niet over verschillende
registraties worden gecombineerd. Parsing en bronvalidatie blijven afzonderlijk;
de domeinfunctie voegt geen datums, tekstopschoning of nieuwe bronnotaties toe.

**Uitkomst en toelichting:** per regel wel/geen kwalificerend bewijs. Import
vat minstens één kwalificerende regel samen in voetbaldeelname per persoon.
Weekendplanning bewaart juist de afzonderlijke kwalificerende teamdagen.
Niet kwalificeren is op zichzelf geen verklaring dat de bron volledig is;
bronmeldingen blijven apart zichtbaar.

**Demonstraties:**

| ID | Synthetische invoer | Verwachte uitkomst |
| --- | --- | --- |
| D-02 | Eén regel: Bond, Teamspeler, Ja | Beide importvelden voor voetbaldeelname zijn waar |
| D-03 | Regel A: Bond, Trainer, Ja; regel B: Vereniging, Teamspeler, Ja | Beide velden onwaar; geen kwalificerende weekendspeler |
| D-04 | Zaterdagspeler plus zondagtrainer | Wel bondsteamdeelname; trainerregistratie geeft geen zondagspelersrecht |

**Implementatie en tests:** `is_bond_team_player` in
[`football_participation.py`](../code/Prototype/dvk/football_participation.py);
`load_exports` in [`real_data_import.py`](../code/Prototype/dvk/real_data_import.py)
en `other_weekend_persons` in
[`team_matchday.py`](../code/Prototype/dvk/team_matchday.py).
[`test_bl22_b02_v05.py`](../code/Prototype/tests/test_bl22_b02_v05.py):
`test_b02_truth_table`, `test_import_booleans_signals_and_weekend_outcome`,
`test_distributed_conditions_do_not_qualify_in_either_application`,
`test_saturday_player_plus_sunday_trainer_does_not_gain_sunday_player_rights`.

## B-04/B-11, E-03 — Persoonlijke functie- en titelvrijstelling

**Soort:** CKC-configuratie, classificatie en beleidsgevolg.

**Betekenis:** erkende functies en eretitels geven persoonlijke vrijstelling.
Alleen erkende onbetaalde vrijwilligersfuncties geven ook huishoudvrijstelling.

**Brongegevens:** oorspronkelijke Functies-titel of combinatie Commissie/Functie;
eventuele begin/einddatum, peildatum en de vaste CKC-classificatietabel.

**Voorwaarden en uitzonderingen:** `Hoofdtrainer Sen.` en `Verzorger` zijn volgens
de CKC-afspraak betaald; `Erelid` en `Lid van verdienste` zijn eretitels. Deze vier
geven alleen persoonlijke vrijstelling. Onbekende titels worden niet gegokt.
Functies zonder brondata gelden als actuele exportregistraties; aanwezige
geldigheidsdatums worden toegepast, met begin- en einddag inclusief. Overlap
geeft geen dubbele urenvrijstelling; ondersteunende registraties blijven behouden.

**Uitkomst en toelichting:** verwachte A=0 bij bewezen persoonlijke vrijstelling;
'Persoonlijke vrijstelling wegens functie', met de betreffende titel(s).

**Demonstratie D-05:** twee volwassen spelers wonen op hetzelfde volledige adres.
Bij Assistenttrainer op lid A worden A en B vrijgesteld. Bij Hoofdtrainer Sen.
op A is alleen A vrijgesteld; B heeft bij verder complete feiten verwachte A=10.

**Implementatie en tests:** bestaande, ongewijzigde
[`function_classification.csv`](../code/Prototype/dvk/configuration/function_classification.csv)
en [`function_classification.py`](../code/Prototype/dvk/function_classification.py);
`_personal_function_grounds` in `member_duty.py`.
[`test_bl22_policy_v05.py`](../code/Prototype/tests/test_bl22_policy_v05.py),
`test_paid_and_unpaid_functions_demonstrate_different_household_effect`;
[`test_function_classification_v05.py`](../code/Prototype/tests/test_function_classification_v05.py)
toetst de volledige goedgekeurde mapping en oorspronkelijke bronregistraties.

## B-05 — Huishoudvrijstelling

**Soort:** CKC-beleid op afgeleide adres- en functiekwalificaties.

**Betekenis:** een erkende onbetaalde functie van een actueel huishoudlid kan
de andere relevante leden op hetzelfde volledige woonadres vrijstellen.

**Brongegevens:** postcode, huisnummer, eventuele toevoeging, actueel
lidmaatschap en geclassificeerde functies van de betrokken personen.

**Voorwaarden en uitzonderingen:** een lege toevoeging is geldig; verschillende
toevoegingen blijven verschillende adressen. Achternaam, ouders en contact-via-ouders
zijn geen besliscriteria. Ontbrekend of conflicterend adres bewijst geen huishouden
en kan een adresgebonden vrijstelling ook niet betrouwbaar uitsluiten.

**Uitkomst en toelichting:** 'Huishoudvrijstelling wegens functie van …', met
ondersteunende registratie, of expliciete onzekerheid over adres/functie/lidmaatschap.

**Demonstratie D-06:** volwassen speler zonder bruikbaar adres: verwachte A onbekend.
Heeft die persoon zelf Hoofdtrainer Sen., dan blijft de bewezen persoonlijke
vrijstelling gelden: A=0; de adresonzekerheid blijft als grond zichtbaar.
Dit geldt ook bij tegenstrijdige adresgegevens.

**Implementatie en tests:** `canonical_address`, `_household_function_grounds`
in `member_duty.py`; `test_bl22_policy_v05.py`,
`test_proven_personal_exemption_precedes_address_uncertainty`;
`test_member_duty_v05.py`, `test_household_function_has_separate_supporting_ground`.

## B-06/B-07/B-08 — Minderjarigen en oudste-kindregel

**Soort:** CKC-beleid op huishouden, leeftijd en deelname.

**Betekenis:** van kwalificerende minderjarigen in hetzelfde geregistreerde
huishouden draagt in beginsel de oudste de gezinsgebonden verplichting.

**Brongegevens:** volledige adressen, geboortedatums, lidmaatschap, deelname,
functies en peildatum. Oudergegevens zijn geen automatische huishoudsleutel.

**Voorwaarden en uitzonderingen:** gelijke geboortedatums of ontbrekende relevante
feiten kunnen onzekerheid geven. Een onbetaalde functie van het oudste kind kan
het huishouden vrijstellen; een persoonlijke vrijstelling alleen is geen nieuwe
regel om de verplichting door te schuiven. Op de 18e verjaardag kan het oudste
kind zelfstandig taakplichtig worden én de gezinsverplichting naar het jongere
kind verschuiven. Reeds gewerkte uren blijven bij het oorspronkelijke lid.
Bezwaren over de feitelijke gezinssituatie blijven menselijke besluitvorming;
registratie van uitzonderingsbesluiten valt buiten deze werking.

**Uitkomst en toelichting:** onder meer 'oudste kwalificerende minderjarige',
'jonger kind; oudste kwalificerende kind is …', of onzekerheid zonder gekozen kind.

**Demonstratie D-07:** oudste geboren 7 oktober 2008, jongere geboren 1 januari 2012,
zelfde adres, beiden kwalificerend. Op 6 oktober 2026 is verwachte A respectievelijk
10 en 0. Op 7 oktober: 10 en 10. Vier gewerkte uren van het oudste lid blijven
bij dat lid. Met Sportlink-A=10 voor beiden verandert de controle voor het jongere
van afwijking naar overeenkomst; DVK wijzigt geen urenregistratie.

**Implementatie en tests:** `_minor_grounds` en `_resolve_duty` in `member_duty.py`;
`test_bl22_policy_v05.py`,
`test_eighteenth_birthday_keeps_child_evidence_and_does_not_transfer_hours`;
`test_member_duty_v05.py`,
`test_equal_birth_dates_use_b10_uncertainty_without_selecting_a_child` en
`test_oldest_function_exempts_household_instead_of_shifting_duty`.

## B-10, E-02/E-04/E-07 — Samenloop en begrijpelijke afleiding

**Soort:** combinatievolgorde van beleidsuitkomsten en onzekerheden.

**Betekenis:** bewezen vrijstellingen houden voorrang. Zonder bewezen
vrijstelling maar met onzekerheid blijft de verwachte A onbekend. Als beide
ontbreken, geldt de ingestelde norm, momenteel 10 uur.

**Brongegevens:** alle voorgaande kwalificaties, gronden en ondersteunend bewijs.

**Voorwaarden en uitzonderingen:** vrijstelling, onzekerheid en toelichting
worden niet met elkaar vereenzelvigd. Alle gronden blijven bewaard; de weergave
kan gelijke tekst samenvoegen. Recreatieve deelname en erelidmaatschap blijven
afzonderlijke bestaande vrijstellingsgronden.

**Uitkomst en toelichting:** vrijgesteld/0, niet betrouwbaar beoordeelbaar/onbekend,
of taakplichtig/norm. Bewezen vrijstelling onderdrukt niet het bronbewijs van
andere gronden of onzekerheden.

**Demonstratie D-08:** A heeft Assistenttrainer én Hoofdtrainer Sen.; huisgenoot B
heeft Assistenttrainer én een onbekende titel. A blijft vrijgesteld met twee
persoonlijke functiegronden, een huishoudgrond en de onbekende huishoudfunctie
als onzekerheid. Alle ondersteunende registraties blijven behouden.

**Implementatie en tests:** `derive_member_duties`, `_resolve_duty`;
`test_bl22_policy_v05.py`,
`test_multiple_exemptions_keep_order_evidence_and_explanation` toetst ook de
exacte menselijke toelichting en volgorde van bronbewijs.

## B-09/B-14, E-01/E-05/E-08 — Vergelijking met Sportlink

**Soort:** read-only controle en menselijke vervolgbeslissing.

**Betekenis:** verwachte A is CKC-afleiding; geregistreerde A is Sportlink-bronfeit.
Een verschil is een signaal voor beoordeling, geen correctie of uitzonderingsbesluit.

**Brongegevens:** verwachte A met gronden; betrouwbaar gekoppelde Sportlink-A.

**Voorwaarden en uitzonderingen:** ontbrekende, dubbele of onbetrouwbare
urenposities worden niet gekozen of aangevuld. DVK onderdrukt geen verschil
wegens een individueel acceptatiebesluit en beheert zulke besluiten niet.
Handmatige correctie vindt buiten DVK plaats; een volgende import vergelijkt opnieuw.

**Uitkomst en toelichting:** overeenkomst, afwijking of niet betrouwbaar
beoordeelbaar; uitleg over gronden en datakwaliteit.

**Demonstratie D-09:** complete kwalificerende speler zonder vrijstelling:
verwacht 10. Geregistreerd 10 geeft overeenkomst; geregistreerd 0 geeft afwijking.
Omgekeerd kan een beleidsmatig vrijgesteld lid met positieve Sportlink-A nog
operationeel kandidaat zijn, als alle overige voorwaarden dat toestaan.

**Implementatie en tests:** [`hours_control.py`](../code/Prototype/dvk/hours_control.py),
`compare_required_hours`; [`candidate_context.py`](../code/Prototype/dvk/candidate_context.py),
`CandidateContextApplicationService.propose`;
[`test_hours_control_v05.py`](../code/Prototype/tests/test_hours_control_v05.py),
`test_round2_expectation_is_used_for_a_control`;
`test_candidate_person_issues_v05.py`,
`test_sportlink_duty_for_definitive_nonplaying_member_is_not_policy_filtered`.

## B-12 — Bronactualiteit

**Soort:** broncontext en waarschuwing, geen vrijstellingsregel.

**Betekenis:** toon bekende import-/ophaalmomenten en bronproblemen eerlijk.
Geen verzonnen actualiteit of algemene maximale ouderdom. Volgens het latere
BL-09-besluit volstaat voor Functies en Commissies de laatste importdatum,
zonder waarschuwing uitsluitend wegens ouderdom.

**Brongegevens:** import-/ophaalmetadata en technische bronstatus.

**Voorwaarden en uitzonderingen:** succesvolle aanvraag, bruikbare inhoud en
bekende ophaaltijd zijn verschillende gegevens. Een geldige lege Programma-lijst
is een geslaagde bronrespons; een foutrespons bewijst geen nul wedstrijden.

**Uitkomst en toelichting:** bronstatus met bekende tijd of eerlijk onbekend;
onbruikbare wedstrijdcontext levert geen voorstellen.

**Demonstratie D-10:** geslaagde lege Programma-lijst toont nul aangeleverde
wedstrijden; transport-/responsfout meldt onbekende context en blokkeert voorstellen.

**Implementatie en tests:** `CandidateContextApplicationService.load`;
[`planning_source_presenter.py`](../code/Prototype/dvk/planning_source_presenter.py);
[`test_candidate_context_v05.py`](../code/Prototype/tests/test_candidate_context_v05.py),
`test_valid_list_and_empty_list_are_success_without_retries`,
`test_invalid_response_is_explicit_and_not_an_empty_match_list`;
[`test_planning_source_status_v05.py`](../code/Prototype/tests/test_planning_source_status_v05.py).

## B-13/BL-03 — Seizoen en historische achterstand

**Soort:** actuele taakplichtcontrole en afzonderlijke prioriteringsregel.

**Betekenis:** seizoensstart vraagt een actuele beoordeling; uren worden niet
automatisch overgeboekt. Positieve achterstand uit het vorige seizoen telt alleen
als tweede rangschikkingscriterium, na actuele E, voor diensten juli–december.

**Brongegevens:** actuele A/B/C/D/E; optionele historische urenexport op relatiecode;
dienstdatum. De planner borgt het onmiddellijk voorafgaande bronseizoen.

**Voorwaarden en uitzonderingen:** januari–juni telt historie niet mee.
Onbekende/onbetrouwbare historie sluit geen kandidaat uit en wordt niet als
bewezen nul getoond. Negatieve historie geeft geen krediet; actuele uren wijzigen niet.

**Uitkomst en toelichting:** verklaarbare rangorde met onderscheid tussen positief,
nul, negatief, onbekend, ontbrekende bron en buiten de toepassingsmaanden.

**Demonstratie D-11:** twee kandidaten met gelijke actuele E; in juli krijgt
positieve historische achterstand voorrang. In juni heeft die geen invloed.

**Implementatie en tests:** [`prioritization.py`](../code/Prototype/dvk/prioritization.py),
`prioritize_candidates`; [`test_historical_backlog_v05.py`](../code/Prototype/tests/test_historical_backlog_v05.py),
`test_priority_order_current_then_history_then_match_and_stable_id` en
`test_all_boundaries_use_service_date_and_repeat_annually`.

## Operationele selectie en planning — afzonderlijke toepassingen

Deze regels blijven ongewijzigd; zij zijn geen aanvullende taakplichtwaarheid.

| Regelgroep | Invoer, voorwaarden en uitzondering | Uitkomst en synthetische demonstratie | Implementatie en tests |
| --- | --- | --- | --- |
| BL-17 Sportlink-basis | Positieve geregistreerde A, betrouwbare eigen uren, geldige overige bron- en persoonscontext; E>0 voor prioritering | Beleidsvrijstelling sluit niet zelfstandig uit. A=0 en E>0 door een negatieve correctie creëert geen taakplicht | `candidate_context.py`, `prioritization.py`; `test_iteration1_candidates_v05.py::test_positive_open_hours_without_registered_duty_do_not_create_planning_duty` |
| BL-20 teamspeeldag | Kwalificerende spelerregistraties, dienstweekdag, minimumbezetting; vrijdag geeft geen weekendbeperking | Zondagspeler op zaterdag alleen als herkenbare noodkandidaat bij tekort; selectie begrensd tot minimum. Beide spelerdagen laten beide dagen toe | `team_matchday.py`; `test_iteration1_candidates_v05.py::test_other_day_only_if_other_suitable_candidates_insufficient` en vrijdagtests |
| Gate 8 wedstrijdcontext | Leeftijd, dienst en teamwedstrijd; bestaand twee-uursvenster en eerste-team/eerste-wedstrijdgedrag | Jeugd/weekend begint uiterlijk 12:30; 12:31 niet geschikt. Thuisoverlap bij jeugd kan ouderuitvoering toestaan | `candidate_selection.py`; `test_gate8_match_decision_tree_v05.py` |
| FR-02–FR-07 tijdelijke planning | Sportlink-bezetting, catalogusnorm, lokale indelingen en expliciete bevestiging | Voorstel alleen schrijft niets; bevestiging telt mee, undo herstelt ruimte; succesvolle sync vervangt tijdelijke planning | `planning_workqueue.py`, `application_services.py`; `test_candidate_context_v05.py::test_actual_proposal_can_be_human_approved_and_undone_without_changing_source` |
| BL-19/Gate 10 no-show | Feitelijke inroostering of bevestigde handmatige registratie, lokale kalender, dienstaanvang, seizoen en intrekkingen | Nieuwe registratie vandaag−14 t/m vandaag; oudere intrekking blijft mogelijk. Ingetrokken feiten blijven zichtbaar maar tellen niet | `no_show.py`, `NoShowApplicationService`; `test_bl19_no_show_management_v05.py::test_no_new_registration_after_window_but_revocation_remains_available`, `test_gate10a_v05.py` |

Bronvalidatie (CSV-kolommen, getallen, persoonskoppeling en tijden) blijft bij de
bestaande invoergrenzen. Zo is een ontbrekende Teamsoort een bronmelding, terwijl
B-02 zelf uitsluitend vaststelt of de geparseerde regel kwalificeert. Deze index
verzwaart geen importcontract en verandert geen sanctie- of planningsregel.

## Demonstraties uitvoeren en historische contracten onderscheiden

Alle voorbeelden zijn synthetisch. Vanuit `code/Prototype`:

```sh
python -m pytest -q -vv tests/test_bl22_policy_v05.py tests/test_bl22_b02_v05.py
```

De overige genoemde bestaande tests demonstreren de aanvullende regels. Hun
fixtures blijven gescheiden van echte lokale CKC-bronnen. De historische C/W-paden
in `dvk/rules.py` en `dvk/duty.py` beschermen eerdere geaccepteerde casecontracten.
Zij worden niet samengevoegd met de actuele adresgebaseerde afleiding in
`dvk/member_duty.py`; een historische casus is geen alternatieve actuele regel.
