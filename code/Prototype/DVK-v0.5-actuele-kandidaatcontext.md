# Actuele kandidaatcontext — v0.5 in ontwikkeling

Baseline: `prototype-v0.5` op `5958b982` (inclusief PR #43).
Werkbranch: `codex/actuele-kandidaatcontext`. Geen functionele acceptatie of merge.
De geaccepteerde v0.4-release en historische casefamilies blijven regressiebasis.

## Besluit en aansluiting

CKC vertrouwt technisch geslaagd ontvangen Programma-lijsten, inclusief een
lege lijst. De planner beoordeelt voorstellen in de context van het programma.
DVK controleert geen volledigheid, periode-dekking, aantallen of mogelijke
API-afkapping. De bestaande aanvraag (`aantaldagen=60`, `aantalregels=500`) blijft
ongewijzigd. Dit besluit is geen garantie dat iedere gekozen periode volledig
in de ontvangen gegevens voorkomt.

De nieuwe `CandidateContextApplicationService` verbindt uitsluitend bestaande
componenten: standaardpaden → `load_duty_dashboard` (bestaande strikte CSV-validatie
met `SportlinkRealDataAdapter`) → `CkcProgrammaAdapter` / `SportlinkProgrammaClient`
→ `compare_required_hours` / `derive_member_duties` →
`PlanningApplicationService.assess_candidates` → `prioritize_candidates` →
`create_assignment_proposal` / `plan_proposals` → bestaande menselijke bevestiging.
Er is geen tweede CSV-parser, databasewijziging of Sportlink-mutatie.

De brongebonden v0.5-taakplichtuitkomst op de **dienstdatum** wordt expliciet als
`DutyQualification` aan de selectie doorgegeven. De oorspronkelijke lidstatus,
rollen, personen, urenregistratie, afleidingsgronden en broncontext blijven
beschikbaar; er wordt geen fictieve status `active` gemaakt. Bestaande aanroepen
zonder expliciete kwalificatie behouden hun historische afleiding. Onzekere
brongebonden uitkomsten en onbetrouwbare/ambigue urenposities geven geen voorstel.
Afwijking tussen verwachte A en geregistreerde A blijft een waarschuwing voor
menselijke herbeoordeling; de actuele Sportlink A/B/C/D/E wordt niet overschreven.

Technisch onbruikbare CSV-bestanden blokkeren publicatie van de context.
Persoonsgebonden bronafwijkingen sluiten alleen onbetrouwbaar beoordeelbare
personen uit; meldingscodes en aantallen blijven zichtbaar (vervolgbesluit 25 oktober). Onopgeloste teams en ongeldige
wedstrijdgegevens blokkeren eveneens de context. Dit zijn bronfouten, geen
controle op de volledigheid van een technisch geldige API-lijst.

De operationele route schakelt vorigeseizoensprioritering expliciet uit; geen
Excel-import of demoachterstanden. De demo en zijn historische prioritering
blijven ongewijzigd. BL-03 blijft open.

## Hergebruik Rooster2

Referentie: `johanvdstel/Rooster2`, `main`, `app.py`, `http_get_json()`.
De bestaande aanpak gebruikt maximaal **vier pogingen totaal** en **1,5 seconde**
tussen pogingen bij time-out, HTTP-fout en verbindings-/overdrachtsfout. SSL- en
ongeldige-JSON-fouten zijn daar direct definitief. DVK volgt die indeling met
zijn bestaande urllib-transport en behoudt de timeout van 30 seconden. Er komt
geen requests- of Rooster2-runtimeafhankelijkheid bij.

DVK neemt de eenvoudige tellers `calls`, `retries`, `failures` over en toont
per laadactie de status, datum/tijd en aantallen. Een geslaagde herhaling levert
normale context met een instabiliteitsmelding; een definitieve fout blokkeert
voorstellen en toont wedstrijdcontext als onbekend. Een geldige lege lijst
veroorzaakt geen herhaling. Ongeldige technische responsen (lege body, foutobject,
ontbrekende/ongeldige `items`, ongeldige JSON of niet-objectrijen) worden expliciet
afgewezen. Rooster2's omzetting van zulke fouten naar `[]` wordt vanwege het
nieuwe CKC-besluit niet overgenomen.

Niet overgenomen: ruwe serverresponsen/request-URL's in debuglogs, parallelle
batchfetches en algemene endpoint/cacherapportage. Ze zijn niet nodig voor deze
ene Programma-aanvraag en kunnen broninhoud of configuratie blootleggen.
Stabiliteitscijfers zijn sessiegebonden, geen nieuwe duurzame meetdatabase.

## UI en bekende beperkingen

In operationele Ledendienst Planning laadt de planner met een expliciete knop
de vijf lokale exports en het programma. Geen automatische CSV/API-import bij
het openen van de app. Het seizoen van de urenexport moet worden bevestigd en
bij de geselecteerde dienst passen. De getoonde laadtijd is geen bewijs van de
actualiteit van de handmatig gemaakte exports.

Een mislukte verversing wist de eerdere kandidaatcontext; periode- en
gegevensmoduswisseling gebruiken geen oude kandidaatcontext. De bestaande
gevalideerde Vrijwilligers-bron voor exact de periode blijft nodig om voorstellen
tegen bekende bezetting te tonen. Goedkeuren, tijdelijke planning, undo,
bronvervanging en No-Shows gebruiken hun bestaande services en controles.

Bewust behouden: de selectie gebruikt de **eerste** passende teamregistratie en
de **eerste** wedstrijd voor team/dag. De bronvolgorde kan dus van invloed zijn;
deze opdracht herziet dat gedrag niet. Persoonsconflicten met feitelijke
Sportlink-inroosteringen zijn nog niet aangesloten; de UI vermeldt dat. De
bestaande controles tegen tijdelijke DVK-indelingen blijven wel werkzaam.
Broncontext wordt alleen in de lokale Streamlit-sessie bewaard; herstart vraagt
opnieuw laden. Duurzame tijdelijke indelingen en No-Show-historie blijven intact.

## Lokale acceptatie op macOS

1. Gebruik deze werkbranch/PR-checkout met de bestaande Python-omgeving en runtime-
   instelling `SPORTLINK_CLIENT_ID`. Zet de waarde niet in gedeelde logs of Git.
2. Zorg dat de vijf handmatig vernieuwde bestanden in
   `$HOME/Documents/DVK-Sportlink-exports/` staan: `Leden.csv`, `Functies.csv`,
   `Commissies.csv`, `Teams.csv`, `Overzicht per periode.csv`. Finder kan Documents
   als Documenten weergeven; wijzig de interne padnaam niet.
3. Start in `code/Prototype` met `python -m streamlit run streamlit_app.py`.
   Gebruik de bestaande lokale databaseprocedure; kopieer of reset geen database
   voor deze test. Kies Ledendienst Planning en hervat/start de bedoelde sessie.
4. Kies de bedoelde periode en operationele gegevensmodus. Synchroniseer de
   feitelijke Sportlink-inroosteringen via de bestaande bediening in Databronnen.
   Bevestig vervanging alleen wanneer tijdelijke planning daadwerkelijk mag vervallen.
5. Selecteer een dienst met vrije capaciteit. Vul het werkelijke seizoen van de
   urenexport in en klik **Kandidaatbronnen laden / vernieuwen**. Controleer de
   API-status en eventuele bronmeldingen.
6. Controleer herkenbare kandidaten, rang, actuele open uren en wedstrijdcontext;
   toets volwassen/jeugdkandidaten aan de bron. Vorigeseizoensachterstanden worden
   expliciet niet gebruikt. Bij een bronprobleem mogen geen kandidaten uit een
   eerdere geslaagde laadactie blijven staan.
7. Een voorstel boekt nog niets. Bevestig desgewenst één bewuste keuze en controleer
   de tijdelijke indeling en undo. Controleer dat de bestaande No-Show-bediening
   uitsluitend de feitelijke Sportlink-inroosteringen blijft gebruiken.
8. Controleer periodewisseling, herladen en de demonstratiemodus. Deel alleen
   bevindingen zonder persoonsgegevens, CSV's, ruwe API-responsen of client-ID.

Technisch groene tests/CI zijn geen functionele acceptatie. De opdrachtgever
beslist na deze lokale proef over acceptatie en merge.

## Technische verificatie

Uitsluitend synthetische gegevens: 48 nieuwe gerichte tests geslaagd; volledige
regressiesuite 1071 tests geslaagd (1023 bestaande + 48 nieuwe). De tests dekken
geldige/lege/ongeldige responsen, herhalingen, definitieve bronfouten, echte-bronachtige
CSV-koppeling, v0.5-taakplicht en vrijstellingen, senioren/jeugd/ouders, actuele
uren en prioritering zonder BL-03, het behouden eerste-matchgedrag, expliciete
bronfouten, menselijke goedkeuring/undo en Streamlit-verversing/periodewisseling.
Een bevestiging blijft ook zichtbaar wanneer daarna geen voorstel meer overblijft.

Er zijn geen historische regressiecases aangepast. De eerste volledige run vond
alleen een bestaande UI-controle op tabelbegrenzing: bronmeldingaantallen staan
daarom als compacte tekst in een expander. De uiteindelijke volledige run is groen.
CI en functionele acceptatie zijn afzonderlijke controles na oplevering van de PR.


## Vervolgbesluit PR #44 — persoonsgebonden afwijkingen (25 oktober 2026)

De oorspronkelijke algemene blokkade op iedere CSV-ERROR was te ruim: één
`CONFLICTING_DUPLICATE_MEMBERSHIP` maakte ook betrouwbare andere personen
onbeschikbaar. `DUPLICATE_PERSON_SOURCE_RECORD` en `UNKNOWN_MEMBERSHIP_STATUS`
blijven diagnostiek, geen opdracht om eerst alle exports te vernieuwen.

Voor de operationele kandidaatroute is `Lidstatus = Definitief` noodzakelijk,
maar niet voldoende. De bestaande toets van afmelddatum op dienstdatum,
bondsteamdeelname, taakplicht, vrijstellingen, urenpositie en geschiktheid blijft
bepalend. `Afgemeld`, `Overschrijving spelactiviteit` en overige statussen geven
geen kandidaat, ook niet met een toekomstige afmelddatum. De algemene historische
peildatumafleiding en het taakplichtdashboard zijn niet herschreven.

De bestaande import voegt identieke relatiecodes niet tot meerdere kandidaten
samen. Tegenstrijdige identiteits-/lidmaatschapsregels worden niet willekeurig
gekozen; betreffende persoon wordt overgeslagen en de meldingen blijven behouden.
Dit geldt ook voor meerdere tegenstrijdige, uitsluitend beëindigde registraties.
In de operationele kandidaatroute geeft een ongeldige geboortedatum een
persoonsgebonden ERROR en sluit die persoon uit; de rest van het bestand blijft
leesbaar. De bestaande strikte afhandeling in het afzonderlijke taakplichtdashboard
blijft de standaard; de kandidaatroute kiest persoonsisolatie expliciet via de
bestaande importketen. Er is geen tweede importmechanisme.

De bestaande urencontrole beoordeelt fouten bij een persoon en diens relevante
ondersteunende bronfeiten. Ontbrekende/ambigue of foutieve uren leveren geen
voorstel op. Orphanregels zonder gekoppeld persoon blijven in de originele
broncontext gemeld, maar hun rijnummer wordt niet als relatiecode behandeld en
het ontbreken van hun code wordt niet als fout van ieder ander lid beschouwd.
Bronregels worden niet gerepareerd, uren worden niet herverdeeld.

`Overzicht per periode.csv` koppelt uitsluitend via `Relatiecode` aan `Rel. code`.
Gelijke namen bij verschillende codes zijn daar geen ambiguïteit en mogen niet
worden samengevoegd of op naam worden geblokkeerd. Bij de daadwerkelijke bestaande
naamkoppeling van Vrijwilligers-boekingen blijft een niet-unieke naam ongekoppeld,
met een begrijpelijke melding; andere unieke matches blijven bruikbaar. Daar is
geen nieuwe matching- of herstelprocedure voor gebouwd. No-Shows, tijdelijke
planning, Programma API/retries en prioriteringsregels blijven ongewijzigd.

Lokale heracceptatie: gebruik dezelfde ongewijzigde exports, laad opnieuw de
kandidaatbronnen en selecteer een dienst met vrije capaciteit. De drie gemelde
bronafwijkingen mogen zichtbaar blijven, terwijl betrouwbare andere kandidaten
met hun eigen urenpositie verschijnen. Er is geen databasewijziging of migratie.


Aanvullende bronafbakening: de urenregistratie van een huishoud-/functiesubject
bepaalt niet de A/B/C/D/E van een ander lid. Urenfouten blijven daarom bij de
relatiecode van die urenregistratie. Functie-, lidmaatschaps- en gezinsfeiten
blijven volgens de bestaande regels als ondersteunende context beschikbaar.


### Wijzigingen en regressie bij deze correctie

Vertrekpunt: PR #44-commit `0f0445e` op `codex/actuele-kandidaatcontext`,
basis `prototype-v0.5` / `5958b982`. Geen nieuwe branch of PR.

| Bestanden | Reden |
| --- | --- |
| `dvk/candidate_context.py` | Algemene CSV-ERROR-blokkade verwijderd; expliciet Definitief vereist; orphan-diagnostiek niet als persoonsfout van anderen gebruiken. |
| `dvk/real_data_import.py`, `dvk/duty_control_presenter.py` | Bestaande importketen biedt expliciete persoonsisolatie voor de kandidaatroute; ongeldige geboortedatum blijft standaard een strikte dashboardinvoerfout. |
| `dvk/hours_control.py` | Urenmeldingen horen alleen bij de eigenaar van die uren; geen doorslag naar andere huishoud-/functiesubjecten. |
| `streamlit_app.py` | Begrijpelijke, niet-blokkerende uitleg bij persoonsafwijkingen; bronmeldingen blijven zichtbaar. |
| `tests/test_candidate_person_issues_v05.py` | Synthetische status-, duplicaat-, uren-, naam- en technische bronfoutgevallen. |
| `tests/test_candidate_context_v05.py`, `tests/test_candidate_context_ui_v05.py` | Nog niet geaccepteerde PR-regressie aangepast aan het nieuwe besluit en UI-doorgang getoetst. |
| Dit verslag en `DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md` | Vastgesteld vervolgbesluit expliciet aangevuld, met behoud van historische afspraken. |

Verificatie: **164 gerichte tests geslaagd**, **1104 volledige regressietests
geslaagd** (33 aanvullende gevallen boven de vorige 1071). Syntaxcontrole en
`git diff --check` geslaagd. Historische geaccepteerde tests zijn niet aangepast;
ook het aparte dashboard behoudt zijn strikte invoercontrole. Uitsluitend
synthetische bronnen en tijdelijke databases gebruikt. Lokale heracceptatie met
dezelfde CKC-exports volgt afzonderlijk; PR #44 blijft open en ongemerged.
