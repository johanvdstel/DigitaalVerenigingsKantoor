# PR #38 — Bezetting met optionele persoonskoppeling

## Grondslag en scope — 22 oktober 2026

Expliciete vervolgopdracht van Johan/CKC: iedere geldige afzonderlijke Sportlink-inroostering telt mee, ook zonder unieke persoonskoppeling. Dit vervangt de blokkerende naamkoppelingsafspraak uit `DVK-v0.5-vrijwilligers-integratie.md`. Geen fuzzy matching, broncorrectie of reconstructie van afgeschermde personen. De eerdere weektest 19–25 oktober is door Johan lokaal bevestigd; de hieronder beschreven wijziging vereist nieuwe lokale acceptatie.

Werkbranch: `codex/vrijwilligers-planning-integratie`; uitgangscommit `51d21d1b3a7eff7ae03097847442d26bd3c626ef`. PR-doelbaseline: `prototype-v0.5@1399493e70bd35b356a0108e87a0ff8ec614b5af`, geverifieerd via GitHub PR #38. De geaccepteerde releasebaseline blijft v0.4 op main. Alleen deze Vrijwilligers-vervolgscope; de productieroadmap autoriseert hier geen productie-inrichting.

Bronhouders: Sportlink voor feitelijke inroosteringen en ledenexport; CKC voor de catalogus en functionele afspraken; DVK voor afleidingen en duurzame no-showfeiten. Geen werkelijk databasebestand of echte persoonsdata gelezen. Geen migratie of databaseherstel uitgevoerd.

## Boekingsidentiteit en bewezen bronbeperking

De actuele client vraagt uitsluitend `naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag` op. Ook de [officiële Sportlink-beschrijving](https://sportlinkservices.freshdesk.com/nl/support/solutions/articles/9000062942) noemt voor Vrijwilligers geen stabiel boekings-ID of relatiecode. Er is dus geen gedocumenteerd bron-ID om over te nemen; ongedocumenteerde ID-velden worden niet verondersteld.

Gekoppelde boekingen behouden exact de bestaande SL-sleutel uit Rel. code, taakcode en begin/einde in UTC. Daarmee blijven bestaande verwijzingen en no-shows intact.

Ongekoppelde boekingen krijgen een afzonderlijke SLU-sleutel uit bronnaam, taakcode, begin/einde in UTC en bronlocatie. Dit is een technische afleiding, geen persoonsidentiteit of bewezen Sportlink-ID. De sleutel bevat geen rijpositie en blijft bij herordenen van dezelfde bronregels gelijk. Een gewijzigde naam of locatie kan de sleutel wijzigen; voor deze boekingen bestaan geen toegestane persoonsgebonden no-shows.

Twee afgeschermde boekingen met verschillende intervallen of locaties blijven afzonderlijk, ook wanneer beide dezelfde catalogusdienst overlappen. Twee volledig gelijke boekingen binnen dezelfde taakcode zijn niet betrouwbaar te onderscheiden van een dubbel geleverde regel. De gehele verversing wordt dan geblokkeerd en de vorige bron blijft bewaard. De huidige API kan dus niet bewijzen dat twee identieke regels twee verschillende afgeschermde vrijwilligers voorstellen. Dit is de expliciet gerapporteerde ontwerpbeperking uit de opdracht; er wordt geen fictieve identiteit of volgnummer gebruikt.

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

Naamwaarschuwingen blokkeren de publicatie niet. Boekingenset, tijdelijke-planningsverwijdering, tellingen, waarschuwingen en succesmetadata worden in de bestaande transactie gepubliceerd. Technische fouten, ongeldige diensten/intervallen en ononderscheidbare duplicaten blokkeren nog steeds de gehele publicatie. Duurzame no-shows en intrekkingen worden niet gewist door een bronverversing. De laatste poging wordt, zoals voorheen, afzonderlijk vastgelegd.

## Gewijzigde bestanden en reden

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

Herstart na bijwerken van de branch. Kies de ruimere periode en ververs bewust; succes wist tijdelijke planning. Controleer 29 catalogusdiensten per volledige week, bezetting tegen Sportlink en de Afgeschermd-teller. Beoordeel lokaal of eventuele identieke afgeschermde regels de hierboven beschreven bronbeperking raken. Controleer dat onbekende/ambigue namen lokaal als aandachtspunt zichtbaar zijn en de bron toch slaagt. Probeer geen fictieve no-show op echte CKC-data; synthetische tests bewijzen de weigering. Verifieer de bestaande no-show/intrekkingshistorie en de geselecteerde betrouwbare boekingen. Deel uitsluitend geanonimiseerde resultaten; geen dumps, namen, relatiecodes, technische boekings-ID's of credentials.

PR #38 blijft open en ongemerged tot expliciete lokale functionele acceptatie. Er is geen live API-uitvraag door Codex uitgevoerd.

## Technische verificatie

18 nieuwe synthetische cases in `test_volunteer_identity_v05.py`. Twee oude blokkerende naamgevallen uit de integratietest zijn vervangen door de uitgebreide nieuwe contracttests. Bestaande naamopbouwtests blijven bestaan; alleen hun publicatieverwachting volgt het expliciete nieuwe besluit. Historische C/W/I/R-cases en de bestaande Gate 10-context-/intrekkingstests zijn niet aangepast.

Volledige suite: **794 geslaagd**, 0 mislukt, 0 overgeslagen. Gerichte selectie (identiteit, integratie, no-shows, overlap, bestaande Vrijwilligers-client/adapter en bezetting): **192 geslaagd**. `git diff --check` groen. Uitgevoerd met de bestaande tijdelijke testomgeving; geen dependencywijziging.

Tussentijdse fouten: oude blokkerende naamverwachtingen zijn op basis van de nieuwe afspraak aangepast; een nieuw overlaptestvoorbeeld selecteerde aanvankelijk het verkeerde catalogusuur en is gecorrigeerd naar 19:00–22:30; een te brede wijziging aan context-/intrekkingslabels is teruggebracht tot presentatie van actuele bronboekingen, waarna de ongewijzigde historische tests weer slagen. Geen overige bekende technische testfouten. CI en commit worden vermeld bij de oplevering van de bestaande PR.
