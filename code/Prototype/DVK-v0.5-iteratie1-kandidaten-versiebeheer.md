# Iteratie 1 — BL-17, BL-20, BL-21

Status: technische uitvoering; geen functionele acceptatie of afsluiting backlog.
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
