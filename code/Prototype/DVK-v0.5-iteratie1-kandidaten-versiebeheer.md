# Iteratie 1 — BL-17, BL-20, BL-21

Status: functioneel geaccepteerd door Johan op 29 oktober 2026; BL-17/20/21 afgesloten. Expliciete toestemming voor merge PR #53 naar prototype-v0.5 en bijwerken acceptatiedocumentatie. Eerdere uitvoeringsstatussen hieronder zijn historisch.
Baseline: `prototype-v0.5`, `81f3a5a5c3b2201af57948bb5bb00b9968c08724` (PR #52).
Werkbranch: `codex/iteratie-1-kandidaten-versiebeheer`; worktree `/private/tmp/dvk-iteratie-1`.

## Context en opdracht

Geaccepteerde releasebaseline blijft v0.4 op main; v0.5 is een prototype in
ontwikkeling. Bronhouder Sportlink levert geregistreerde taakplicht, Teams en
feitelijke inroosteringen. CKC bepaalt beleid; DVK controleert en stelt voor;
alleen menselijke bevestiging levert tijdelijke planning op.
De implementatieopdracht Iteratie 1 van Johan (28 oktober 2026) bevestigt:
- Sportlink A bepaalt planningsplicht; beleidsvrijstellingen en beleidsmatige
  onzekerheid blokkeren die niet. Persoons-, lidmaatschaps- en urencontroles blijven.
- Teams-veld Speeldag is leidend, voor alle teams. Dit vervangt de afleiding uit
  teamaanduidingen in de oudere BL-20-tekst. Alle spelerkoppelingen tellen voor
  deze filter; bestaande eerste-team-/eerste-wedstrijdlogica blijft verder intact.
- Andere weekenddag uitsluitend herkenbaar als noodkeuze bij tekort aan overige
  geschikte kandidaten voor het minimum, rekening houdend met tijdelijke planning.
- Ontbrekende/onbekende/tegenstrijdige speeldagen blokkeren kandidaten/voorstellen,
  zonder planning of historie te verwijderen. De twee team-2-identiteiten blijven.
- Actieve codeversie direct onder de hoofdtitel, gekoppeld aan het appbestand.

## Vastgestelde feiten en minimaal technisch ontwerp (vóór implementatie)

`candidate_context.py` filtert op control.status én expectation.status. Daarmee
blokkeert de beleidscontrole ook geregistreerde taakplicht bij vrijstelling of
beleidsmatige onzekerheid. De operationele kandidaatcontrole wordt hiervan
losgemaakt: één geldige urenregel met A>0, betrouwbare eigen persoonsfeiten en
actief definitief lidmaatschap; E<=0 blijft uitgesloten via bestaande prioritering.
De bestaande controls blijven beschikbaar voor diagnose en waarschuwingen.

Het uitzonderingsformulier in `streamlit_app.py` roept reject aan. Onderzoek van
applicatieservices en selectie toont geen hergebruik van afwijzingen als filter.
Alleen dit formulier en zijn uitsluitend gebruikte labels verdwijnen; reject en
opslag blijven voor historische voorstelbeslissingen en geaccepteerde tests.

Nieuwe domeinmodule `team_matchday.py` valideert het daadwerkelijke bronattribuut
vóór publicatie van kandidaatcontext en bij voorstellen. Bewezen waarden staan in
`team_linking.MATCHDAYS` (Algemeen/Zaterdag, Algemeen/Zondag) en synthetische
kandidaatfixtures (Zaterdag). Geen extra spellingen worden aangenomen.
Spelerschap volgt bestaande criteria: Bond, Teamspeler, Spelend lid=Ja.
Selectie vindt na bestaande geschiktheids- en urenprioritering plaats zodat
ongeschikte personen geen minimumtekort maskeren. Noodreden wordt in bestaande
proposal.uncertainties bewaard, doel in PlannedProposal; geen schemawijziging.
Bevestiging begrenst noodselecties opnieuw tot het actuele minimumtekort.

Nieuwe `application_version.py` leest Git met cwd gebaseerd op het appbestand,
controleert dat dit bestand in die checkout gevolgd wordt en toont branch, commit,
worktree en lokale wijzigingen. Geen afhankelijkheid van bestaande versioning.py:
die module versieert beleids-/configuratie-/runinhoud, niet de actieve checkout.

## Regressie en gegevensstatus

Gerichte synthetische tests bewijzen bovenstaande besluiten, bronfouten,
noodselectie, expliciete bevestiging/undo, UI en versie-identiteit. Alleen vervallen
operationele beleidsfilterverwachtingen worden vervangen; historische C/W/I/R
cases blijven intact. Daarna volledige pytest-suite en synthetische CI-scripts.
Geen echte exports, databases of credentials lezen; geen migratie/reconstructie:
hiervoor bestaat geen noodzaak of opdracht. Duurzame historie blijft behouden.

## Gewijzigde bestanden en herleiding

| Bestand (onder code/Prototype) | Reden / geaccepteerde eis |
| --- | --- |
| dvk/candidate_context.py | BL-17: Sportlink A en eigen bronbetrouwbaarheid; BL-20: validatie, alle spelerkoppelingen, actuele tijdelijke bezetting en domeinselectie aansluiten. |
| dvk/team_matchday.py | BL-20: validatie inclusief afgewezen bronregels, twee team-2-identiteiten, weekend-/noodselectie en minimumgrens. |
| dvk/application_services.py | BL-20: noodkeuzes bij bevestiging atomair opnieuw begrenzen tot actuele minimumbehoefte. |
| dvk/application_version.py | BL-21: appgebonden Git-identiteit, worktree, lokale wijzigingen en eerlijke terugval. |
| streamlit_app.py | BL-17: uitsluitend uitzonderingsformulier/labels weg; motivering behouden. BL-20: nooddoel en reden presenteren. BL-21: exacte hoofdtitel en versiecaption. Waarschuwing beleidsmatige onzekerheid mag geen onterechte planningsuitsluiting claimen. |
| tests/test_candidate_context_v05.py | BL-17: gezins-/functie-/huishoudvrijstellingen blokkeren Sportlink niet; ontbrekende geboortedatum blijft geblokkeerd. |
| tests/test_candidate_person_issues_v05.py | BL-17: een definitief niet-spelend lid met Sportlink-taakplicht wordt niet wegens beleidsafleiding uitgesloten. Overige bron- en lidmaatschapsregressies blijven. |
| tests/test_candidate_context_ui_v05.py | BL-17/20: geen uitzonderingsinvoer; noodstatus zichtbaar; menselijke bevestiging; bronfout verbergt voorstellen en behoudt tijdelijke planning. |
| tests/test_planning_tables_performance_v05.py | BL-17: vervallen formulierverwachtingen vervangen door afwezigheid en nul reject-aanroepen; 250 kandidaten en detailkeuze blijven gedekt. |
| tests/test_navigation_v05.py | BL-21: caption tussen hoofdtitel en bestaande functies, instellingen blijven op hun plek onder de functietitel. |
| tests/test_iteration1_candidates_v05.py | BL-17/20: bronplicht, onzekerheid, weekendrichtingen, minimumtekort, overige regels, meerdere teams, bronfouten, bevestiging/undo en historie. |
| tests/test_application_version_v05.py | BL-21: echte synthetische Git-repositories/worktrees, afwijkende cwd, commits, staged/unstaged/untracked wijzigingen, ontbrekende Git-informatie en UI-positie. |
| Dit document | Opdracht, ontwerp, testherleiding, verificatie en lokaal acceptatieprotocol vastleggen. |

Deze wijzigingen vervangen uitsluitend de in de opdracht expliciet vervallen
operationele testverwachtingen. C-/W-/I-/R-fixtures en historische domeintests
zijn niet gewijzigd. Geen opslag- of schemaverandering, migratie, verwijdering
van historie, Sportlink-writeback of uitvoering van andere backlogitems.

## Lokaal functioneel acceptatieprotocol voor Johan

Start expliciet de app uit `/private/tmp/dvk-iteratie-1/code/Prototype/streamlit_app.py`
met de bestaande Pythonomgeving (bijvoorbeeld de `.venv/bin/python` uit de
originele checkout) en `-m streamlit run` met dit absolute apppad. Laat lokale
exports/credentials op hun bestaande plaats; deel geen persoonsdetails. Deze
worktree gebruikt een eigen SQLite-bestand naast het appbestand; de bestaande
database in de oorspronkelijke checkout wordt niet verplaatst of gemigreerd.

1. **BL-21:** controleer direct onder “CKC Digitaal Verenigingskantoor (DVK)”
   branch `codex/iteratie-1-kandidaten-versiebeheer`, actuele commit en worktreepad.
   Start hetzelfde absolute apppad vanuit een andere terminalwerkmap: identiteit
   blijft gelijk. De synthetische versieproeven hieronder toetsen lokale wijzigingen,
   andere worktrees en ontbrekende Git-informatie zonder de acceptatiecheckout te wijzigen.
2. **BL-17:** open Ledendienst Planning, kies periode/seizoen, laad de lokale
   bronnen en synchroniseer de Sportlink-bezetting met bestaande bediening.
   Kies een dienst en controleer kandidaten met positieve Sportlink A/E,
   kandidaatmotivering en prioriteit. Er is geen uitzonderingsinvoer of knop.
   Vergelijk waar beschikbaar een kandidaat met DVK-vrijstelling/beleidsonzekerheid:
   die blijft kandidaat indien de overige regels dat toestaan. Taakplichtcontrole
   blijft de afzonderlijke beleidsafwijking melden. A=0 creëert geen planningsplicht.
3. **BL-20, voldoende gewone kandidaten:** kies een zaterdagdienst met voldoende
   overige geschikte kandidaten om het open minimum te vullen: zondagspelers
   ontbreken. Herhaal omgekeerd op zondag. Hetzelfde geldt wanneer Sportlink plus
   tijdelijke indelingen het minimum al vullen, ook als er ruimte tot Max is.
4. **BL-20, tekort:** kies een dienst waar overige geschikte kandidaten onvoldoende
   zijn voor het minimum. De andere weekenddag verschijnt uitsluitend met
   “Noodkandidaat — Min bezetting” en expliciete reden. Controleer beide richtingen.
   Wedstrijd-/uren-/lidmaatschapsconflicten blijven gelden; kandidaten met twee
   spelerteamspeeldagen zijn gewoon toegestaan op beide dagen; niet-spelende leden
   en doordeweekse diensten krijgen deze beperking niet.
5. **Bevestiging/undo:** aanvinken alleen maakt geen indeling. Bevestig één keuze,
   controleer tijdelijke bezetting en resterend minimum, navigeer heen en terug en
   gebruik de bestaande undo-bediening. De indeling verdwijnt; kandidaten worden
   opnieuw bepaald. Selectie van meer noodkandidaten dan het actuele minimumtekort
   wordt afgewezen, ook als er ruimte tot Max is. Bronuren en historie blijven gelijk.
6. **Bronfouten veilig toetsen:** beschadig geen echte exports. Voer vanuit deze
   worktree `code/Prototype` met de bestaande testomgeving uit:
   `python -m pytest -q tests/test_iteration1_candidates_v05.py tests/test_candidate_context_ui_v05.py tests/test_application_version_v05.py`.
   Dit test ontbrekende/onbekende/tegenstrijdige Speeldag, verweesde Teams-regels,
   de twee afzonderlijke teams 2, beide noodrichtingen, onvoldoende/genoeg reguliere
   kandidaten, bronfouten na eerdere voorstellen, behoud van tijdelijke planning,
   expliciete bevestiging/undo, historie en versiegedrag met uitsluitend synthetische data.
   De UI-bronfoutproef toont de bronmelding en verwijdert eerdere kandidaatuitkomsten.
7. Noteer per stap geslaagd/afwijking/niet lokaal beproefd. Als echte lokale data
   een scenario niet bevat, gebruik het synthetische bewijs en vermeld eerlijk dat
   het niet afzonderlijk handmatig is beproefd. Deel uitsluitend niet-herleidbare
   bevindingen. Daarna afzonderlijke controle in de functionele ontwerpchat en
   expliciete functionele acceptatie; niet mergen of backlogitems afsluiten.

## Grenzen

Er zijn geen echte CKC-bronnen, echte lokale databases of credentials gelezen.
Live bronwaarden en daadwerkelijk lokaal browsergedrag vragen Johans controle;
de implementatie herkent alleen `Algemeen/Zaterdag`, `Algemeen/Zondag` en de reeds
bestaande synthetische waarde `Zaterdag`. Andere spellingen worden geblokkeerd,
niet geraden. Bestaande eerste-team-/eerste-wedstrijdlogica buiten deze specifieke
teamspeeldagfilter blijft bewust behouden. Geen nieuw functioneel besluit nodig
voor de uitgevoerde scope; integrale v0.5-acceptatie blijft open.

## Uitgevoerde technische verificatie

Runtime: Python 3.11.16, bestaande testomgeving `/private/tmp/dvk-bl18-venv`.
- Gerichte gezamenlijke run van de zeven betrokken testmodules: **124 geslaagd**.
  Twee aanvullende bronplicht-/tijdelijke-conflictproeven zijn daarna toegevoegd
  en meegenomen in de definitieve volledige run.
- Definitieve volledige suite: `python -m pytest -q` vanuit `code/Prototype`:
  **1170 geslaagd**, 0 mislukt, 0 overgeslagen (68,58 seconden).
- `python -m py_compile streamlit_app.py`: exit 0.
- Alle elf synthetische scripts uit de bestaande CI-workflow: exit 0:
  run_cases, run_workstream_cases, run_import_cases, run_candidate_cases,
  run_priority_cases, run_dashboard, run_proposal_cases, run_assignment_cases,
  run_dashboard_actions, run_integrated_acceptance en run_v04_demo (alle .py).
  De live-validaties voor workflow_dispatch zijn niet uitgevoerd.
- `git diff --check`: schoon. Diff beperkt tot de dertien hierboven beschreven
  bestanden. Geen echte persoonsdata, exports, databases of credentials toegevoegd.
- GitHub-baseline vlak vóór oplevering opnieuw gecontroleerd: ongewijzigd op
  `81f3a5a5c3b2201af57948bb5bb00b9968c08724`.
- Oorspronkelijke werkmap blijft op `codex/vrijwilligers-planning-integratie` met
  uitsluitend de twee reeds aanwezige gewijzigde bestanden; niets gestasht of overgenomen.

Eerdere testpogingen waren niet allemaal groen: vier oude operationele
beleidsfilterverwachtingen en vier oude UI-verwachtingen zijn conform de opdracht
vervangen. Tijdens nieuwe testopzet zijn een verkeerde repository-getter en een
niet-bestaand catalogustijdstip gecorrigeerd. De versieproef onthulde een echte
padfout bij de tracked-file-controle vanuit een submap; die is hersteld vóór de
definitieve groene runs. Dit zijn technische resultaten, geen functionele acceptatie.
Commit, PR en uiteindelijke GitHub-CI-status staan in de oplevering/PR.


## Gerichte correctieronde PR #53 — 28 oktober 2026

Opdracht: uitsluitend drie reviewbevindingen binnen BL-17/20/21 corrigeren.
De oorspronkelijke opdracht is hierboven onder Context en opdracht vastgelegd;
AGENTS.md, baseline- en iteratiedocumentatie zijn opnieuw gecontroleerd.
PR-head en schone bestaande worktree waren bij aanvang beide
`18c00bb0d282b9959100c6cb669c9c77eea7ae65`; remote-head vóór commit opnieuw
geverifieerd. Baselinebranch blijft `prototype-v0.5` op
`81f3a5a5c3b2201af57948bb5bb00b9968c08724`; bestaande werkbranch en worktree
blijven behouden. Geen nieuwe branch of PR; geen functionele acceptatie of merge.

Vastgesteld probleem en geaccepteerde eis per correctie:

1. `dvk/candidate_context.py`: de algemene ERROR-filter sloot ook kandidaten uit
   bij uitsluitend beleidsgebonden datumfouten. Alleen INVALID_FUNCTION_DATE,
   INVALID_COMMITTEE_START_DATE en INVALID_COMMITTEE_END_DATE zijn nu van die
   planningsblokkade uitgezonderd. De signalen, ernst en Taakplichtcontrole blijven
   intact. Alle overige bronfoutcontroles en identiteit, lidmaatschap, leeftijd,
   uren, speler-/teamcontext en teamspeeldag blijven behouden. Dit volgt direct
   uit Sportlink A als bron voor geregistreerde taakplicht; geen nieuwe beleidsregel.
2. `streamlit_app.py`: de toelichting over een bestaande tijdelijke indeling wordt
   bepaald door de bestaande uncertainty temporary_planning_same_day_emergency,
   in plaats van de bredere suitability emergency. De bestaande teamspeeldagreden
   blijft zichtbaar. Minimumgrens, geschiktheid en bevestiging zijn ongewijzigd;
   geen opslag- of schemawijziging nodig.
3. `streamlit_app.py`: uitsluitend de achterhaalde captionverwijzing naar
   uitzonderingen via een secundaire actie verwijderd; overige uitleg behouden.

Regressies en bewijs:
- `tests/test_iteration1_candidates_v05.py`: vier nieuwe synthetische gevallen
  voor ongeldige begin-/einddatums van functie en commissie. Kandidaat blijft
  beschikbaar; ERROR blijft in bron en control; de afzonderlijke dashboardingang
  van Taakplichtcontrole blijft niet betrouwbaar beoordeelbaar en toont de
  specifieke fouttekst. Bestaande negatieve tests voor echte planningsblokkades
  zijn niet aangepast.
- `tests/test_candidate_context_ui_v05.py`: bestaande noodkandidaatproef uitgebreid
  naar alleen teamspeeldag, alleen tijdelijke indeling en beide. Toetst zowel
  aanwezigheid als afwezigheid van de twee teksten, plus afwezigheid van de
  vervallen captioninstructie en behoud van de overige uitleg. Voor de
  presentatieproef wordt de bestaande tijdelijke-indelingsreden in het voorstel
  gezet; domein-/bevestigingsregressies blijven onderdeel van de volledige suite.
- Dit verslag is bijgewerkt; totaal vijf gewijzigde bestanden.

Verificatie met Python 3.11.16 (`/private/tmp/dvk-bl18-venv`):
- Gerichte run: test_iteration1_candidates_v05, test_candidate_person_issues_v05,
  test_candidate_context_v05 en test_candidate_context_ui_v05: **116 geslaagd**
  (10,67 seconden).
- Daarna volledige `python -m pytest -q`: **1176 geslaagd**, geen mislukkingen of
  overgeslagen tests (71,03 seconden).
- `python -m py_compile streamlit_app.py`: exit 0; `git diff --check`: schoon.
- Een eerste schrijfopdracht voor de nieuwe tests gebruikte een verkeerd relatief
  pad en wijzigde niets. De gelijktijdige run zonder nieuwe tests slaagde met
  110 tests; bovenstaande definitieve runs bevatten alle nieuwe regressies.
- GitHub-CI wordt na push voor de nieuwe head gecontroleerd; definitieve commit
  en CI-resultaat worden in de PR-oplevering vermeld, zodat het verslag geen
  uitslag van een eerdere head als bewijs voor deze correctie presenteert.

Uitsluitend synthetische data gebruikt; geen echte exports of databases gelezen.
Geen historische fixtures gewijzigd. De twee bestaande wijzigingen in de
originele werkmap zijn ongemoeid gebleven. Geen resterend beleids- of
architectuurbesluit binnen deze correcties vastgesteld. Live CKC-brongedrag en
handmatige browseracceptatie zijn niet beproefd; functionele acceptatie blijft open.

## Herstel PR #53 — Geldige vrijdagteams (28 oktober 2026)

Context vooraf geverifieerd: AGENTS.md, dit iteratieverslag en de actuele GitHub
PR-head `a6623f3710514724ed85eb83858585eb718c5dcc`; bestaande schone worktree
`/private/tmp/dvk-iteratie-1` op `codex/iteratie-1-kandidaten-versiebeheer`.
Geen nieuwe branch. Integratiebaseline blijft `prototype-v0.5` op
`81f3a5a5c3b2201af57948bb5bb00b9968c08724`; v0.4 blijft functioneel geaccepteerd,
v0.5 blijft ontwikkeling. Sportlink is bronhouder; Johan/CKC bepaalt beleid.

Geaccepteerde eis: Johan bevestigt `Algemeen/Vrijdag` als geldige Teams-bronwaarde.
Vrijdag veroorzaakt geen weekendbeperking of teamspeeldagnoodstatus. Bij bestaande
Sportlink-taakplicht en positieve open uren is de speler op beide weekenddagen
gewoon kandidaat, mits de overige regels dit toestaan. Recreatieve vrijstelling
blijft uitsluitend bij Taakplichtcontrole; de planning krijgt geen vrijstellingsregel.

Vastgesteld feit: `dvk/team_matchday.py` herkende vrijdag niet en zou na alleen
uitbreiden van de waardentabel vrijdag ten onrechte als andere weekenddag behandelen.
Minimale correctie: vrijdag valideren als weekdag 4, maar niet toevoegen aan de
verzameling beperkende weekendkoppelingen. Bij vrijdag plus zaterdag/zondag telt
uitsluitend de bestaande weekendkoppeling; vrijdag voegt geen beperking of
opheffing toe. Er is hiervoor geen aanvullende beleidskeuze nodig.

Gewijzigde bestanden en reden:
- `dvk/team_matchday.py`: uitsluitend de bevestigde bronwaarde toevoegen en
  vrijdag buiten de weekendfilter houden. Programma-teamidentiteiten intact.
- `tests/test_iteration1_candidates_v05.py`: 23 nieuwe synthetische regressies voor
  laden, gewone kandidatuur op beide dagen, A=0 ondanks positieve open uren,
  minimumtekort, vrijdag naast zaterdag/zondag/beide (beide bronvolgordes),
  ongeldige waarden naast vrijdag en tegenstrijdige speeldagen voor hetzelfde team.
- Dit iteratieverslag: opdracht, herleiding, grenzen en verificatie vastleggen.

Bestaande regressies voor beide weekendkoppelingen, minimumbezettingsuitzondering,
overige geschiktheid, menselijke bevestiging en afzonderlijke Programma-teams 2
zijn ongewijzigd. Geen historische fixtures gewijzigd, migratie, schemawijziging,
nieuwe bronspellingen, echte CKC-exports of databases gelezen. Geen functionele
acceptatie of merge. Johan herhaalt lokaal de bronverversing en vervolgt acceptatie.

Gerichte verificatie (Python 3.11.16): `test_iteration1_candidates_v05.py`,
`test_programma_team_linking_v05.py`, `test_candidate_context_v05.py` en
`test_candidate_context_ui_v05.py`: **159 geslaagd**, 0 mislukt/overgeslagen.
Een eerste testaanmaakpoging gebruikte een verkeerd relatief pad en schreef niets;
de daaropvolgende lege vrijdagselectie leverde pytest-exit 5 op. Pad gecorrigeerd;
geen functionele testverwachtingen versoepeld.

Volledige regressiesuite: `python -m pytest -q` vanuit `code/Prototype`:
**1199 geslaagd**, 0 mislukt, 0 overgeslagen (72,29 seconden).
`git diff --check`: schoon. Remote-head en integratiebaseline vlak vóór commit
opnieuw gecontroleerd: ongewijzigd op respectievelijk `a6623f3` en `81f3a5a`.
Geen resterende functionele of architectuurbeslispunten binnen deze herstelopdracht.
Commit en uiteindelijke CI-status worden in de chatoplevering vastgelegd.

## Presentatiecorrectie PR #53 — 29 oktober 2026

Opdracht van Johan na lokale toets: begrijpelijke kandidaattoelichting en details
rechtstreeks bij de aangevinkte kandidaten. Geen functionele acceptatie.
Vooraf gelezen: AGENTS.md, actuele PR en dit verslag. Vastgesteld: schone worktree
`/private/tmp/dvk-iteratie-1`, bestaande branch
`codex/iteratie-1-kandidaten-versiebeheer`, lokale én GitHub-head
`4df662e811c26e991eae35a6644af227613e4320`. Integratiebaseline blijft
`prototype-v0.5` op `81f3a5a5c3b2201af57948bb5bb00b9968c08724`; geaccepteerde
releasebaseline v0.4; v0.5 is ontwikkeling. Sportlink levert de bronfeiten,
Johan/CKC bepaalt beleid en acceptatie; DVK presenteert voorstellen.

Vastgesteld probleem: de UI drukte interne prioriteitsregels letterlijk af en
gebruikte een afzonderlijke detailselectie. Geaccepteerde eis: begrijpelijke
vertaling van de berekende uitkomst en uitsluitend details van aangevinkte rijen.
De minimale wijziging introduceert geen beleids- of opslaglogica:
- `dvk/candidate_presenter.py`: kleine presentatiefunctie vertaalt berekende uren,
  beschikbaarheid/meeweging van vorig seizoen en de drie wedstrijdvoorkeuren.
- `streamlit_app.py`: geen backlognummer in broncaption; naam en toelichting per
  aangevinkte kandidaat direct onder de tabel; vervallen expander/selectbox weg.
  Sportlink-taakplicht en DVK-beleidscontrole blijven afzonderlijk benoemd.
  Bestaande wedstrijdcontext, noodredenen en waarschuwingen blijven zichtbaar.
- `tests/test_candidate_presenter_v05.py`: negen synthetische combinaties voor
  prioriteits-/wedstrijdcontext, zonder interne codes.
- `tests/test_candidate_context_ui_v05.py`: bestaande detailverwachtingen aangepast,
  naam en directe uitleg, beide noodredenen en hun combinatie behouden/getoetst.
- `tests/test_planning_tables_performance_v05.py`: vervallen bediening vervangen
  door checkboxproeven; meerdere namen/details, uitvinken, nul opslagmutaties,
  context-/dienstwisseling en 250 kandidaten blijven gedekt.
- Dit verslag: herleiding, bewijs en lokale toetsstappen.

Kandidaatselectie, prioritering, teamspeeldagfilter, noodvoorwaarden, bezetting,
opslag en bevestiging/undo zijn ongewijzigd. Geen uitvoering BL-03, nieuwe
 afhankelijkheden, historische fixturewijziging of migratie. Alleen synthetische
gegevens gebruikt; geen echte CKC-exports/databases gelezen. Oorspronkelijke
werkmap met de twee bestaande wijzigingen ongemoeid gelaten.

Korte lokale toets voor Johan:
1. Start dezelfde worktree en controleer de nieuwe commit in de versiecaption.
2. Kies een dienst: zonder vinkjes geen kandidaatdetail. Vink één en daarna
   meerdere kandidaten aan: direct afzonderlijke uitleg onder herkenbare namen.
3. Controleer uren, wedstrijdvoorkeur en waar aanwezig de juiste noodreden;
   Sportlink-taakplicht blijft onderscheiden van de DVK-beleidscontrole.
4. Vink uit en wissel dienst/broncontext: vervallen details verdwijnen.
5. Aanvinken alleen verandert geen planning. Bevestig expliciet en gebruik undo.
   Controleer bij een lange kandidatenlijst ook een kandidaat onderaan.

Bestaande acceptatiebevindingen blijven behouden: één weekendrichting is lokaal
waargenomen; de andere richting en noodkandidaten zijn synthetisch gedekt, maar
niet afzonderlijk lokaal waargenomen. Deze gewijzigde presentatie/bediening vraagt
nog afzonderlijke controle en Johans lokale toets. Geen functionele acceptatie,
backlogafsluiting of merge; geen nieuw functioneel/architectuurbesluit nodig.

Verificatie met Python 3.11.16 (`/private/tmp/dvk-bl18-venv`):
- Definitieve gerichte run van presenter, kandidaat-UI, tabel/performance,
  selectie-events (inclusief bevestiging/undo) en iteratie-1: **84 geslaagd**.
- Volledige regressiesuite daarna/overlappend uitgevoerd op dezelfde code en
  tests: **1209 geslaagd**, geen mislukkingen/overgeslagen (73,27 seconden).
- Alle elf synthetische scripts uit CI: exit 0. Geen live-validaties uitgevoerd.
- Syntaxcontrole app en presenter: exit 0; definitieve `git diff --check`: schoon.
- Eerste testbewerkingsopdracht gebruikte een verkeerd relatief pad en wijzigde
  niets; de al gestarte tests troffen nog oude detailverwachtingen. Na het
  aanpassen van uitsluitend de vervallen bediening zijn bovenstaande runs groen.
- CI voor de nieuwe commit wordt na push gecontroleerd en in de chatoplevering
  vermeld. Geen uitslag van een eerdere head als nieuw bewijs gepresenteerd.


## Functionele acceptatie en afronding — 29 oktober 2026

Johan heeft de gewijzigde kandidaattoelichting lokaal geslaagd verklaard en daarna expliciet akkoord gegeven op de integrale functionele acceptatie van Iteratie 1, merge van PR #53 naar prototype-v0.5 en bijwerken van acceptatiedocumentatie.

Geaccepteerde codecommit: `9016c8a17f631bf015308ce43ba50169c7c1aa21` (inclusief herstelcommits `a6623f3` en `4df662e`). Baseline en werkbranch blijven zoals bovenaan vastgelegd. Afsluitdocumentatie wijzigt geen code.

| Onderdeel | Lokaal resultaat / acceptatiegrens |
| --- | --- |
| Actieve versie | Geslaagd |
| Sportlink leidend | Geslaagd |
| Uitzonderingsinvoer verwijderd | Geslaagd |
| Directe begrijpelijke toelichting bij aanvinken | Na presentatiecorrectie geslaagd |
| Weekendfilter | Eén richting lokaal geslaagd; andere richting synthetisch gedekt |
| Noodkandidaten | Niet lokaal waargenomen door voldoende overige kandidaten; synthetisch gedekt |
| Bevestiging en undo | Geslaagd |
| Overige beschikbaarheid | Geslaagd |
| Vrijdagteams | Geldige bronwaarde Algemeen/Vrijdag bevestigd; correctie geaccepteerd tijdens vervolgacceptatie |

Eén richting van de weekendfilter is lokaal waargenomen; de andere richting en noodkandidaten zijn uitsluitend synthetisch getoetst. Dubbele teamkoppelingen en ongeldige bronwaarden zijn synthetisch gedekt. Integrale v0.5-acceptatie blijft open.

De ontbrekende spelers van zondag 1 werden terecht uitgesloten wegens een overlappende wedstrijd. Zonder wedstrijd werden zij wel aangeboden; geen codewijziging nodig. Recreatieve/niet-spelende leden met geregistreerde Sportlink-taakplicht blijven conform besluit kandidaat; Johan duidt onjuiste registraties als Sportlink-datakwaliteit, geen DVK-afwijking.

Bewijs bij laatste codeversie: Codex rapporteert 84 gerichte tests, 1209 volledige regressietests, elf synthetische scripts, syntax- en diff-check groen. Afzonderlijke review heeft 25 presentatie-/UI-tests opnieuw uitgevoerd (geslaagd), de codewijziging beoordeeld en [CI #381](https://github.com/johanvdstel/DigitaalVerenigingsKantoor/actions/runs/40871625935) voor de exacte codecommit groen bevestigd. De volledige suite is in die laatste review niet opnieuw lokaal gedraaid. Eerdere eigen volledige reviewruns: 1170 en 1176 geslaagd op de toenmalige commits.

Geen resterende blokkerende bevindingen binnen Iteratie 1. Geen echte persoonsgegevens in deze acceptatieregistratie; lokale broninhoud blijft lokaal. Productie- en integrale v0.5-acceptatie blijven open. Volgende iteratie is BL-03; zie de afzonderlijke overdracht. Historische uitvoeringsrapportages hieronder/boven blijven als tijdgebonden bewijs behouden en zijn geen actuele open acceptatiepunten.
