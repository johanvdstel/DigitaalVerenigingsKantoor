# PR #38 — Bezetting met optionele persoonskoppeling

## Actuele vervolgcorrectie — 5 november 2026

Expliciet CKC-besluit en goedgekeurde implementatieopdracht: iedere aangeleverde
`Afgeschermd`-regel vertegenwoordigt een afzonderlijk bezette plaats, ook bij
identieke taakcode, naam, begin/einde en locatie. Dit vervangt de eerdere beperking
uit PR #38 dat identieke afgeschermde regels de volledige synchronisatie blokkeren
en geen technisch volgnummer mogen krijgen. Overige duplicaatcontroles blijven gelden.

Uitgangsbaseline: `prototype-v0.5@d168576cc5d1e2ea1260c6b64c35f56d33b49e6e`
(merge PR #66). Werkbranch: `codex/v05-correctie-afgeschermde-inroosteringen`.
Alleen deze correctie vóór Iteratie 10; geen uitbreiding van Iteratie 9 of
integrale v0.5-acceptatie. De eerdere PR #38-oplevergegevens hieronder zijn historisch.

## Grondslag en scope — 22 oktober 2026

Expliciete vervolgopdracht van Johan/CKC: iedere geldige afzonderlijke Sportlink-inroostering telt mee, ook zonder unieke persoonskoppeling. Dit vervangt de blokkerende naamkoppelingsafspraak uit `DVK-v0.5-vrijwilligers-integratie.md`. Geen fuzzy matching, broncorrectie of reconstructie van afgeschermde personen. De eerdere weektest 19–25 oktober is door Johan lokaal bevestigd; de hieronder beschreven wijziging vereist nieuwe lokale acceptatie.

Werkbranch: `codex/vrijwilligers-planning-integratie`; uitgangscommit `51d21d1b3a7eff7ae03097847442d26bd3c626ef`. PR-doelbaseline: `prototype-v0.5@1399493e70bd35b356a0108e87a0ff8ec614b5af`, geverifieerd via GitHub PR #38. De geaccepteerde releasebaseline blijft v0.4 op main. Alleen deze Vrijwilligers-vervolgscope; de productieroadmap autoriseert hier geen productie-inrichting.

Bronhouders: Sportlink voor feitelijke inroosteringen en ledenexport; CKC voor de catalogus en functionele afspraken; DVK voor afleidingen en duurzame no-showfeiten. Geen werkelijk databasebestand of echte persoonsdata gelezen. Geen migratie of databaseherstel uitgevoerd.

## Boekingsidentiteit en bewezen bronbeperking

De actuele client vraagt uitsluitend `naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag` op. Ook de [officiële Sportlink-beschrijving](https://sportlinkservices.freshdesk.com/nl/support/solutions/articles/9000062942) noemt voor Vrijwilligers geen stabiel boekings-ID of relatiecode. Er is dus geen gedocumenteerd bron-ID om over te nemen; ongedocumenteerde ID-velden worden niet verondersteld.

Gekoppelde boekingen behouden exact de bestaande SL-sleutel uit Rel. code, taakcode en begin/einde in UTC. Daarmee blijven bestaande verwijzingen en no-shows intact.

Ongekoppelde boekingen krijgen een afzonderlijke SLU-sleutel uit bronnaam, taakcode, begin/einde in UTC en bronlocatie. Dit is een technische afleiding, geen persoonsidentiteit of bewezen Sportlink-ID. De sleutel bevat geen globale rijpositie. Een gewijzigde naam of locatie kan de sleutel wijzigen; voor deze boekingen bestaan geen toegestane persoonsgebonden no-shows.

Afgeschermde boekingen blijven ieder afzonderlijk behouden, ook bij volledig gelijke inhoud. De adapter groepeert ze op de bestaande inhoudsgebonden sleutel en kent binnen iedere groep `source_occurrence` 1, 2, 3 enzovoort toe. Voorkomen 1 behoudt exact de bestaande sleutel; vanaf voorkomen 2 wordt het nummer aan de bestaande hashinvoer toegevoegd. De teller begint opnieuw per import en per inhoudsgroep. Herordenen van dezelfde bronset behoudt de verzameling sleutels. Het optionele dataclassveld heeft standaardwaarde 1; bestaande JSON zonder dit veld blijft leesbaar en de bestaande JSON-opslag bewaart het nummer bij heropening zonder schemamigratie.

Dit nummer identificeert uitsluitend een boekingsregel binnen de actuele bronset. DVK identificeert geen individuele afgeschermde personen door de tijd heen en kan bij afname van drie naar twee identieke regels niet bepalen welke persoon verdwenen is. `person_id` en `person_name` blijven leeg; er ontstaat geen persoonsgebonden urenboeking, no-show of sanctie. De zichtbare naam blijft `Afgeschermd`; het technische nummer verschijnt niet in de UI. Iedere regel behoudt afzonderlijk het bronfeit en provenance.

Synchronisatie vervangt de volledige gevalideerde actuele boekingenset voor de gekozen periode en taakcodes. Herhaling cumuleert daarom niet; ook een afname of lege bron vervangt de eerdere aantallen. Bestaande bevestiging, transactiegrenzen, rollback en behoud van duurzame no-shows/intrekkingen blijven intact. Geen Sportlink-writeback.

Ook over verschillende broncodes heen kan DVK zonder persoonsidentiteit niet vaststellen of het dezelfde vrijwilliger betreft. Afzonderlijk onderscheidbare ongekoppelde boekingen tellen afzonderlijk; alleen bij betrouwbare persoonsidentiteit blijft deduplicatie per persoon/dienst mogelijk. Dit vraagt lokale beoordeling van de werkelijke bron, geen identiteitsreconstructie.

## Verwerking, bezetting en waarschuwingen

- Het exacte naamcontract met optioneel leeg tussenvoegsel blijft gelden. Alleen de bestaande trim voor vergelijking blijft behouden; presentatie bewaart de API-naam.
- `Afgeschermd` wordt nooit tegen leden gematcht en is geen administratieve fout.
- Nul matches en meerdere unieke relatiecodes geven een waarschuwing, maar de boeking wordt opgenomen zonder persoonskoppeling.
- Dubbele exportregels blijven afzonderlijke bronregels. Identieke regels met één Rel. code leveren een waarschuwing en een betrouwbare koppeling op. Er wordt niets in het bronbestand gecorrigeerd.
- Bij dezelfde Rel. code met tegenstrijdige waarden blijft de boeking ongekoppeld. De CSV-reader signaleert verschillen in de getrimde waarden van de aangeleverde kolommen, ook als die niet allemaal in Person worden bewaard. Dit is een conservatieve betrouwbaarheidscontrole; geen poging om één variant te kiezen.
- De vaste catalogus, vier codes, bargroep, positieve overlap en vrijdag-/minimum-/maximumregels blijven intact. Per catalogusdienst telt een betrouwbaar gekoppelde persoon eenmaal; iedere afzonderlijke ongekoppelde boeking telt eenmaal.

Databronnen toont de status Geslaagd of Geslaagd, met aandachtspunten; aantallen gepubliceerde boekingen binnen de bronperiode, Afgeschermd en zonder betrouwbare unieke koppeling; per probleemcategorie aantallen boekingen en verschillende naamwaarden. De aantallen per categorie kunnen overlappen. Een lokaal uitklapbaar overzicht toont de bronnaam en het probleem eenmaal per categorie/naam met het aantal boekingen. Afgeschermd telt uitsluitend in de eigen teller, niet als probleemnaam. Een tweede lokaal overzicht toont de broninroosteringen voor de gevalideerde gekozen periode en of no-showregistratie mogelijk is. Geen technische boekings-ID's of relatiecodes in deze normale gebruikersweergave.

De nieuwe rapportgegevens staan in bestaande lokale JSON-opslag, samen met de succesmetadata. Ze gaan niet naar gedeelde logs of transportfouten. De laatste poging bewaart alleen veilige categorieën/status, geen probleemnamen. De synchronisatieknop blijft op de bestaande plaats.

## No-shows, compatibiliteit en publicatie

`NoShowApplicationService.register()` weigert zonder betrouwbare persoonskoppeling, ook bij rechtstreekse aanroep buiten de UI. De selectie bevat alleen geschikte boekingen; ongekoppelde boekingen verdringen betrouwbare boekingen niet uit de bestaande recente-selectielimiet. Afgeschermde of onzekere boekingen veroorzaken geen no-show of sanctie.

Bestaande JSON-bookings zonder het nieuwe optionele veld blijven leesbaar. De opslagtabellen, migraties, bestaande gekoppelde sleutels en oude no-shows/intrekkingen veranderen niet. De bestaande historische contextlabels voor intrekkingen blijven behouden.

Naamwaarschuwingen blokkeren de publicatie niet. Boekingenset, tijdelijke-planningsverwijdering, tellingen, waarschuwingen en succesmetadata worden in de bestaande transactie gepubliceerd. Technische fouten, ongeldige diensten/intervallen en overige duplicaten blokkeren nog steeds de gehele publicatie; identieke afgeschermde regels zijn expliciet toegestaan. Duurzame no-shows en intrekkingen worden niet gewist door een bronverversing. De laatste poging wordt, zoals voorheen, afzonderlijk vastgelegd.

## Historische gewijzigde bestanden PR #38

| Bestand onder code/Prototype | Reden |
| --- | --- |
| dvk/model.py | Optioneel conflictkenmerk voor de vrijwilligerskoppeling |
| dvk/real_data_import.py | Tegenstrijdige exportregels signaleren zonder bronregels te wijzigen |
| dvk/vrijwilligers_adapter.py | Optionele identiteit, onderscheiden technische sleutels, waarschuwingen en lokale rapportprojectie |
| dvk/persistence/sportlink_bookings.py | Compatibele JSON-uitlezing en recente bronvolgorde zonder voorafgaande limiet voor geschiktheidsselectie |
| dvk/application_services.py | Waarschuwingen atomair publiceren en betrouwbare identiteit afdwingen voor no-shows |
| dvk/volunteer_planning.py | Ongekoppelde bezetting, publieke bronuitlezing en geslaagd-met-aandachtspunten |
| streamlit_app.py | Lokale namen/tellers/waarschuwingen en geschikte no-showselectie |
| tests/test_no_show_sportlink_v05.py | Alleen de door dit nieuwe besluit gewijzigde blokkerende naamverwachtingen aanpassen |
| tests/test_volunteer_planning_integration_v05.py | Technische foutcases behouden; naamgevallen onderbrengen in nieuwe contracttests |
| tests/test_volunteer_identity_v05.py | Synthetische keten-, opslag-, no-show-, privacy- en UI-regressies |
| Dit rapport | Besluit, bronbeperking, herleiding, risico's en lokale acceptatie |

De vooraf aanwezige lokale wijzigingen aan `streamlit_app.py` (overlapcaption) en het eerdere integratierapport blijven buiten deze commit en behouden hun inhoud.

## Nieuwe lokale acceptatie

Herstart na bijwerken van de branch. Kies de ruimere periode en ververs bewust; succes wist tijdelijke planning. Controleer catalogusdiensten, bezetting tegen Sportlink en de Afgeschermd-teller. Controleer dat identieke afgeschermde regels afzonderlijk zichtbaar blijven, correct meetellen en bij herhaling niet cumuleren. Controleer dat onbekende/ambigue namen lokaal als aandachtspunt zichtbaar zijn en de bron toch slaagt. Probeer geen fictieve no-show op echte CKC-data; synthetische tests bewijzen de weigering. Verifieer de bestaande no-show/intrekkingshistorie en de geselecteerde betrouwbare boekingen. Deel uitsluitend geanonimiseerde resultaten; geen dumps, namen, relatiecodes, technische boekings-ID's of credentials.

Historische status bij oplevering PR #38: open en ongemerged tot expliciete lokale functionele acceptatie. Er is geen live API-uitvraag door Codex uitgevoerd.

## Historische technische verificatie PR #38

18 nieuwe synthetische cases in `test_volunteer_identity_v05.py`. Twee oude blokkerende naamgevallen uit de integratietest zijn vervangen door de uitgebreide nieuwe contracttests. Bestaande naamopbouwtests blijven bestaan; alleen hun publicatieverwachting volgt het expliciete nieuwe besluit. Historische C/W/I/R-cases en de bestaande Gate 10-context-/intrekkingstests zijn niet aangepast.

Volledige suite: **794 geslaagd**, 0 mislukt, 0 overgeslagen. Gerichte selectie (identiteit, integratie, no-shows, overlap, bestaande Vrijwilligers-client/adapter en bezetting): **192 geslaagd**. `git diff --check` groen. Uitgevoerd met de bestaande tijdelijke testomgeving; geen dependencywijziging.

Tussentijdse fouten: oude blokkerende naamverwachtingen zijn op basis van de nieuwe afspraak aangepast; een nieuw overlaptestvoorbeeld selecteerde aanvankelijk het verkeerde catalogusuur en is gecorrigeerd naar 19:00–22:30; een te brede wijziging aan context-/intrekkingslabels is teruggebracht tot presentatie van actuele bronboekingen, waarna de ongewijzigde historische tests weer slagen. Geen overige bekende technische testfouten. CI en commit worden vermeld bij de oplevering van de bestaande PR.

## Technische oplevering vervolgcorrectie — 5 november 2026

| Bestand onder code/Prototype | Reden |
| --- | --- |
| dvk/vrijwilligers_adapter.py | Technisch voorkomensnummer per identieke afgeschermde inhoudsgroep; bestaande eerste en overige sleutels behouden |
| tests/test_volunteer_identity_v05.py | Synthetische regressies voor multipliciteit, opslag, bezetting, herhaling, rollback, no-showuitsluiting en UI |
| Dit rapport | Nieuw CKC-contract, boekingsidentificatie en verificatie vastleggen |

Repository-, staffing-, applicatieservice- en Streamlit-productiecode zijn niet
gewijzigd: de gerichte ketentests bewijzen dat die meerdere unieke boekingsregels
al verwerken. Geen migratie, reconstructie, wijziging van C/W/I/R-fixtures of
algemene projectdocumentatie. Geen live Sportlink-uitvraag, credentials of echte
persoonsgegevens/operationele databases gebruikt.

Verificatie in een afzonderlijke tijdelijke Python 3.11-omgeving, met dependencies
volgens de bestaande pyproject.toml (Streamlit 1.66.1, pytest 9.2.0):

- Baseline vóór wijziging: 125 gerichte tests geslaagd bij herhaling. Eerste run:
  124 geslaagd en één bestaande UI-test met een Streamlit-opstarttimeout van drie
  seconden; de ongewijzigde herhaling slaagde. Geen timeoutgrens aangepast.
- Na wijziging: **180 gerichte tests geslaagd**, waaronder **31 identiteitstests**.
  De selectie omvat identiteit, planningintegratie, no-shows, Vrijwilligers-adapter,
  client en staffing. Eén oude blokkerende Afgeschermd-verwachting vervangen;
  verwachting voor andere ongekoppelde namen behouden.
- Nieuwe dekking: 1/2/3 identieke regels, gemengde bezetting, herhaalde import,
  aantallen 1 → 3 → 2 → 0, herordening met meerdere inhoudsgroepen, opslag en
  heropening, oude payloads, overige duplicaten, no-show/sanctieweigering,
  transport-/validatiefouten en transactionele rollback, afzonderlijke UI-rijen
  en herhaalde namen zonder technisch nummer.
- Volledige regressiesuite: **1.597 geslaagd**, 0 mislukt, 0 overgeslagen.
- Syntaxcontrole adapter/Streamlit en `git diff --check`: geslaagd.

Geen bekende resterende technische afwijking binnen deze correctie. De genoemde
opstarttimeout is uitsluitend bij de eerste baseline-run waargenomen. Lokale
functionele acceptatie en afzonderlijke merge-toestemming blijven vereist.
Commit-SHA, draft-PR en CI-status worden commit-specifiek teruggerapporteerd;
deze technische oplevering is geen functionele acceptatie en geen merge.
