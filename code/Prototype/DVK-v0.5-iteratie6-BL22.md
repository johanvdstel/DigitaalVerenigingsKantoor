# Iteratie 6 — BL-22 technische oplevering

Status: technisch opgeleverd ter review en lokale CKC-acceptatie; geen functionele
acceptatie, integrale v0.5-acceptatie of merge door Codex.

## Baseline en scope

- Repository: `johanvdstel/DigitaalVerenigingsKantoor`.
- Startbranch: `prototype-v0.5`.
- Remote HEAD bij aanvang: `4699e036147e051b2958fe0e71496ae104b0d864`, exact de opgegeven baseline.
- Werkbranch: `codex/iteratie-6-bl22`.
- Geïsoleerde worktree: `/private/tmp/dvk-iteratie6-bl22`.
- PR-doel: `prototype-v0.5`, draft, geen merge.
- De oorspronkelijke checkout op `455200b83035ef54927c137bbaa3f8d19be15c2a`
  en branch `codex/vrijwilligers-planning-integratie` is niet gewijzigd. De twee
  bestaande gewijzigde bestanden en vier niet-gevolgde `.DS_Store`-bestanden
  zijn beschermd en niet meegenomen.

Geaccepteerde releasebaseline blijft v0.4 op main; v0.5 is ontwikkeling met
afzonderlijk geaccepteerde Iteraties 1–5. Sportlink beheert bronfeiten en
geregistreerde taakplicht; CKC/Johan bepaalt beleid en functionele acceptatie.
De expliciete BL-22-implementatieopdracht autoriseert alleen gedragsbehoudende
herstructurering, één gedeelde B-02-definitie, demonstraties en regelindex.

Geraadpleegd: AGENTS.md, README, backlog, prototypeplanning, productieroadmap,
ontwikkelworkflow, herijkte B-01–B-14, E-contract, broncontracten, verslagen 1–5,
actuele implementatie en regressies. Historische statusvermeldingen zijn niet
zelfstandig als actuele status gebruikt. Het broncontract blijft deels concept;
BL-22 verzwaart geen minimumvelden of validatie.

## Probleem, herleiding en wijzigingsgrens

Vastgesteld probleem: `derive_member_duties` mengde meerdere beleidsstappen in één
lus; B-02 stond als dezelfde drie voorwaarden in import en weekendplanning.
Geaccepteerde eisen: B-02, B-04–B-10, E-02/E-04/E-07 en de expliciete opdracht.
De kleine oplossing behoudt resultaten en publieke contracten en maakt de
bestaande stappen afzonderlijk reviewbaar. Geen engine of configuratielaag.

| Bestand | Doel en belangrijkste functies |
| --- | --- |
| `dvk/member_duty.py` | Vijf herkenbare stappen: `_membership_grounds`, `_personal_function_grounds`, `_household_function_grounds`, `_minor_grounds`, `_resolve_duty`. `derive_member_duties` bewaart de coördinatie, invoerindices en bronbewijsopbouw. Actueel versus historisch toepassingsgebied toegelicht. |
| `dvk/football_participation.py` | Pure, getypeerde `is_bond_team_player` met uitsluitend drie geparseerde velden; geen adapterafhankelijkheid. |
| `dvk/real_data_import.py` | Alleen de B-02-predicate vervangen door de gedeelde functie; lokale `qualifying_ids`, beide booleans, alle teamregistraties en bronmeldingen blijven. |
| `dvk/team_matchday.py` | Alleen de B-02-predicate vervangen; speeldagvalidatie, vrijdag, aggregatie en noodselectie blijven. |
| `tests/test_bl22_policy_v05.py` | Negen synthetische karakteriseringen van samenloop, bewijsvolgorde, exacte toelichting, adresonzekerheid, betaalde/onbetaalde functies en 18e verjaardag met behoud van C. |
| `tests/test_bl22_b02_v05.py` | 121 gevallen: waarheidstabel, ontbrekend/ongeldig, hoofdletters, parsinggrens, beide booleans, bronmeldingen, verdeeld bewijs, zaterdagspeler/zondagtrainer en behoud Programma-links. |
| `../../docs/DVK-v0.5-CKC-beleidsregelindex-Ledendiensten.md` | Leesbare regelgroepen B-01–B-14/E, elf genummerde demonstraties, operationele grenzen en testverwijzingen. Geen nieuwe functionele norm. |
| Dit verslag | Technische herleiding, controles, risico's en overdracht. |

De classificatie-CSV en classifier, modellen, urencontrole, historische C/W-code,
kandidaatservice, Programma-koppeling, planning/no-shows, UI en bestaande tests en
fixtures zijn ongewijzigd. README, backlog, planning en roadmap zijn niet bijgewerkt.

## Gedragsbehoud

- Gronden blijven in de bestaande volgorde: lidmaatschap, eigen functies,
  huishoudfuncties, minderjarigen; onzekerheden daarna in hun oorspronkelijke
  volgorde. Alle registraties en ondersteunende personen blijven behouden.
- Bewezen vrijstelling houdt voorrang boven onzekerheid. Zonder beide geldt
  de bestaande norm. Status-, uren- en resultaatstructuren zijn niet gewijzigd.
- B-02 blijft per registratie gelden. De importer aggregeert personen, de
  weekendfilter houdt afzonderlijke spelerteamdagen. Geen nieuwe strip-, datum-
  of booleanparsing binnen de domeinfunctie.
- Sportlink-A blijft leidend. Nieuwe en bestaande integratietests laten zien
  dat een beleidsmatig niet-spelend/vrijgesteld lid met geregistreerde taakplicht
  kandidaat kan blijven. Programma behoudt ook niet-spelerteamkoppelingen.
- 768 aanvullende synthetische vóór/na-situaties zijn rechtstreeks met de
  exacte baselinefunctie vergeleken: volledige verwachtingen (inclusief gronden,
  registraties en bronbewijs), controles en menselijke toelichtingen waren gelijk.
  De matrix varieerde vier geboortedatums, vier adrestoestanden, vier
  functiecombinaties, drie lidmaatschapstoestanden, twee invoervolgordes en twee
  peildatums. Dit is aanvullend bewijs, geen uitputtend bewijs voor alle invoer.

De karakterisering van negen gevallen is vóór de productiecodewijziging samen
met de relevante bestaande tests uitgevoerd: 393 geslaagd. Dezelfde selectie
bleef na de refactor groen. Bestaande testverwachtingen zijn niet gewijzigd.

## Verificatie en exacte commando's

Werkdirectory voor Python-commando's: `/private/tmp/dvk-iteratie6-bl22/code/Prototype`.
Interpreter: `/private/tmp/dvk-bl19-venv/bin/python` (Python 3.11.16, pytest 9.2.0,
Streamlit 1.66.1). Bestaande toolomgeving gebruikt zonder installatie of wijziging;
gecontroleerd dat `dvk` vanuit de nieuwe worktree wordt geladen.
De bestaande autouse-testfixtures isoleren lokale bronnen met synthetische data.
Geen live-validatiescripts, echte CKC-exports of operationele databases gebruikt.

Baselinekarakterisering, vóór codewijziging:

```sh
/private/tmp/dvk-bl19-venv/bin/python -m pytest -q tests/test_member_duty_v05.py tests/test_function_classification_v05.py tests/test_real_data_import_v04.py tests/test_iteration1_candidates_v05.py tests/test_candidate_context_v05.py tests/test_candidate_person_issues_v05.py tests/test_hours_control_v05.py tests/test_fb01_motivation_v05.py tests/test_bl22_policy_v05.py
```

Resultaat vóór en na refactor: **393 geslaagd, 0 overgeslagen, 0 mislukt**.

Definitieve gerichte selectie:

```sh
/private/tmp/dvk-bl19-venv/bin/python -m pytest -q tests/test_bl22_b02_v05.py tests/test_bl22_policy_v05.py tests/test_member_duty_v05.py tests/test_function_classification_v05.py tests/test_real_data_import_v04.py tests/test_iteration1_candidates_v05.py tests/test_candidate_context_v05.py tests/test_candidate_person_issues_v05.py tests/test_hours_control_v05.py tests/test_fb01_motivation_v05.py
```

Resultaat: **514 geslaagd, 0 overgeslagen, 0 mislukt**.

Volledige voorgeschreven regressie:

```sh
/private/tmp/dvk-bl19-venv/bin/python -m pytest -q
```

Resultaat: **1501 geslaagd, 0 overgeslagen, 0 mislukt**, 94,24 seconden.
Baseline: 1371 tests; toevoeging: 130 tests. Geen tests verwijderd of aangepast.

Elf voorgeschreven synthetische runners, elk uitgevoerd als
`/private/tmp/dvk-bl19-venv/bin/python <bestandsnaam>`:

```text
run_cases.py
run_workstream_cases.py
run_import_cases.py
run_candidate_cases.py
run_priority_cases.py
run_dashboard.py
run_proposal_cases.py
run_assignment_cases.py
run_dashboard_actions.py
run_integrated_acceptance.py
run_v04_demo.py
```

Alle elf: **exitcode 0**. Daarnaast:

```sh
/private/tmp/dvk-bl19-venv/bin/python -m py_compile streamlit_app.py dvk/member_duty.py dvk/football_participation.py dvk/real_data_import.py dvk/team_matchday.py
/private/tmp/dvk-bl19-venv/bin/python /private/tmp/dvk-bl22-equivalence.py
git diff --check
```

Alle geslaagd. Het laatste Python-script is een tijdelijke lokale audit buiten
de repository; het laadt de baseline via `git show` als aparte module en vergelijkt
de beschreven 768 situaties met de werkcode. De duurzame regressiebescherming
staat in de twee nieuwe testbestanden. Alle 28 lokale links in de regelindex
zijn op bestaan gecontroleerd.

Een eerste run van alleen de nieuwe tests had **128 geslaagd, 2 mislukt**:
de nieuwe Programma-behoudtest verwachtte ten onrechte de fixtureteamnaam
`Team 1`, terwijl de bestaande helper `Team 0` maakt. De assertion is gekoppeld
aan de daadwerkelijk aangeleverde synthetische teamnaam. Geen beleidsverwachting
of productiecode is hiervoor veranderd; definitieve selectie en regressie groen.

## Beperkingen, acceptatie en overdracht

- De elf bekende historische root-tests buiten `testpaths = ["tests"]` zijn
  niet gerepareerd of opnieuw opgenomen. Dit is de eerder gerapporteerde
  afzonderlijke baselinekwestie; deze oplevering claimt daarvoor geen groen.
- Geen nieuwe lokale functionele CKC-acceptatie of browserproef met echte data.
  CKC kan de regelindex en gelinkte demonstraties reviewen en gericht de
  ongewijzigde taakplichtcontrole en kandidaatgrens accepteren.
- Belangrijkste reviewpunten: bewijs-/grondvolgorde, voorrang bij onzekerheid,
  dezelfde-regelvoorwaarde B-02 en behoud van de Sportlink-kandidatenbasis.
- Geen nieuwe functionele beleidsvraag vastgesteld. ChatGPT-review en het
  afzonderlijke CKC-acceptatiebesluit blijven vereist; groene CI vervangt die niet.
- Definitieve commit, draft-PR en CI-status worden commit-specifiek in de
  terugrapportage/PR vastgelegd. Niet zelfstandig mergen of verder wijzigen.
