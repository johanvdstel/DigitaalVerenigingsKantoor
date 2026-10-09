# DVK v0.5 — Broncontracten voor zeven Sportlink-bronnen

**Status: concept ter functionele verificatie — NIET geaccepteerd.**  
**Opgesteld:** 9 oktober 2026, reconstructie uit code en geaccepteerde baseline op `prototype-v0.5`.  
**Doel:** overdraagbare registratie van de *minimumgegevens* die DVK per bron nodig heeft. Geen persoonsgegevens, bronregels, authenticatiegegevens of echte exports in deze repository.

## 1. Zeven bronnen en vaste aanleveringswijze

| Nr. | Bron | Aanlevering tot nader order | Adapter |
| --- | --- | --- | --- |
| 1 | Leden | Handmatig exportbestand, lokaal in DVK laden | `dvk/real_data_import.py` |
| 2 | Functies | Handmatig exportbestand, lokaal in DVK laden | `dvk/real_data_import.py` |
| 3 | Teams | Handmatig exportbestand, lokaal in DVK laden | `dvk/real_data_import.py` |
| 4 | Commissies | Handmatig exportbestand, lokaal in DVK laden | `dvk/real_data_import.py` |
| 5 | Overzicht per periode | Handmatig exportbestand, lokaal in DVK laden | `dvk/real_data_import.py` (`vrijwilligers_periode`) |
| 6 | Vrijwilligers | Read-only Sportlink Vrijwilligers API | `dvk/vrijwilligers_adapter.py` |
| 7 | Wedstrijden / Programma | Read-only Sportlink Programma API | `dvk/programma_adapter.py` |

**Niet veronderstellen** dat de vijf exports later automatisch door API's worden vervangen. API Vrijwilligers is iets anders dan de export Overzicht per periode. De CKC ShiftCatalog is een **aanvullende configuratiebron**, niet een achtste Sportlink-bron.

## 2. Leeswijzer en status van de reconstructie

- **T — technisch verplicht:** importer weigert een CSV zonder deze kolom.
- **F — functioneel noodzakelijk:** geaccepteerd beleid of bestaande domeinlogica heeft dit veld nodig; ontbrekende waarde/kolom wordt soms alleen gesignaleerd. Dit is dus niet altijd een technisch afgedwongen minimum.
- **G — gebruikt, niet altijd vereist:** adapter verwerkt veld indien beschikbaar; exacte noodzaak voor alle situaties nog vaststellen.
- **V — verifiëren:** minimumstatus of feitelijke API-respons nog niet onafhankelijk bevestigd.

**Belangrijk:** deze reconstructie legt vast wat *aantoonbaar* in huidige code/baseline staat. Zij bewijst niet dat dit exact de volledige eerder mondeling vastgestelde minimumselectie is. Verschillen en lacunes moeten door opdrachtgever worden beoordeeld. Kolomverplichting, niet-lege waarde en semantische geldigheid zijn verschillende controles.

## 3. Bron 1 — Leden (export)

| Oorspronkelijke kolom | Status | Functie |
| --- | --- | --- |
| `Rel. code` | T | Stabiele persoonssleutel; koppeling met andere exports |
| `Naam` | T | Herkenbare presentatie, identiteitscontrole |
| `Lidstatus` | T/F | Actueel lidmaatschap, samen met afmelddatum |
| `Lidsoort` | T | Lidmaatschapscategorie |
| `Status lidmaatschap` | T | CKC-specifieke status, alleen expliciet gedefinieerde betekenissen |
| `Geb.dat.` | T (alternatief) / F | Geboortedatum, leeftijdsgrenzen en oudste-kindregel; technisch mag legacy `Geboortedatum` |
| `Afmelddatum` | F | Eerste dag waarop lidmaatschap niet meer geldig is; kan leeg zijn voor actuele leden |
| `Postcode` | F | Huishoudsleutel |
| `Huisnummer` | F | Huishoudsleutel |
| `Toevoeging` | F | Onderdeel van huishoudsleutel indien aanwezig; leeg is geldig |
| `Straatnaam` | F, nog niet T | Volledig adres, presentatie en diagnostiek; niet zelfstandig de huishoudsleutel |
| `Plaats` | F, nog niet T | Plaatsnaam, volledig adres en diagnostiek; niet zelfstandig de huishoudsleutel |
| `Naam ouder/verzorger 1`, `Naam ouder/verzorger 2`, `Contact via ouder/verzorger` | G | Broncontext/diagnostiek; **niet** gebruiken als huishoud- of gezinscriterium |
| `Spelactiviteiten (bond)` | G | Broncontext; **geen** vervanging voor Teams-bewijs |

**Controles:** niet-lege relatiecode; dubbele relatiecodes en conflicterende identiteit/status/adressen; geldige geboorte- en afmelddatums; peildatum; volledig adres voor huishoudconclusies. Niet alle functioneel noodzakelijke velden zijn al opgenomen in `REQUIRED_COLUMNS`. Bankgegevens horen niet in de DVK-minimumexport.

**Basis:** `real_data_import.py` `REQUIRED_COLUMNS`, ledenverwerking; herijkte baseline B-02/B-03/B-05/B-06.

## 4. Bron 2 — Functies (export)

| Oorspronkelijke kolom | Status | Functie |
| --- | --- | --- |
| `Rel. code` | T | Koppeling naar lid |
| `Naam` | F, nog niet T | Betekenisvolle leesbaarheid en herkenning van de functiehouder in DVK |
| `Functie` | T/F | Oorspronkelijke functietitel; CKC-classificatie betaald/onbetaald/erelid en vrijstelling |
| `Begindatum`, `Einddatum` | G, **niet aanwezig in gecontroleerde export** | Alleen verwerken als latere bronstructuur ze daadwerkelijk levert |

**Door opdrachtgever aangevuld minimum:** drie kolommen: `Rel. code`, `Naam`, `Functie`. De kolom `Naam` is vereist voor begrijpelijke weergave, ook al gebruikt de huidige importer vooral de relatiecode voor koppeling.\n\n**Controles:** bestaande relatiecode, originele functienaam bewaren, onbekende/lege functie signaleren, dubbelen niet dubbel tellen; exportmoment als geldigheidsgrens zolang begin/einddatum ontbreken. `Verzorger` blijft bronclassificatievraag BL-08. Gevoelige en bancaire exportkolommen zijn niet nodig.

**Basis:** `real_data_import.py`; herijkte baseline B-04/B-11 en broncontrole.

## 5. Bron 3 — Teams (export)

| Oorspronkelijke kolom | Status | Functie |
| --- | --- | --- |
| `Rel. code` | T | Koppeling naar lid |
| `Naam` | F, nog niet T | Herkenbare weergave van het teamlid |
| `Team` | T | Teamregistratie |
| `Teamsoort` | **F, momenteel niet T** | Onderscheid `Bond` / `Vereniging` |
| `Teamrol` | T/F | Vereist `Teamspeler` voor kwalificerende deelname |
| `Spelend lid` | T/F | Vereist `Ja` voor kwalificerende deelname |
**Door opdrachtgever bevestigd minimum:** zes kolommen: `Rel. code`, `Naam`, `Team`, `Teamsoort`, `Teamrol`, `Spelend lid`. De aanwezigheid van `Naam` en `Teamsoort` is functioneel verplicht, hoewel de huidige importer ze nog niet beide als technische minimumkolommen afdwingt.\n\n**Controles:** alleen **dezelfde actuele teamregel** met `Teamsoort = Bond`, `Teamrol = Teamspeler`, `Spelend lid = Ja` bewijst bondsteamdeelname; meerdere regels zijn toegestaan. Onbekende/ontbrekende teamsoort of ongeldige speelstatus signaleren. **Open implementatieverschil:** importer accepteert technisch een bestand zonder `Teamsoort`, maar functioneel is deze kolom noodzakelijk. `Teamrol` en `Spelend lid` zijn door Sportlink gegenereerde waarden voor ingeschreven teamleden. Geen bancaire gegevens importeren.

**Basis:** `real_data_import.py`; `tests/test_real_data_import_v04.py`; baseline B-02.

## 6. Bron 4 — Commissies (export)

| Oorspronkelijke kolom | Status | Functie |
| --- | --- | --- |
| `Rel. code` | T | Koppeling naar lid |
| `Naam` | F, nog niet T | Herkenbare weergave van het commissielid |
| `Commissie` | T/F | Commissie-identiteit voor CKC-functieclassificatie |
| `Functie` | T/F | Oorspronkelijke functie binnen commissie |
| `Begindatum` | F, nog niet T | Start van de commissieregistratie; geaccepteerde export had dit voor alle registraties |
| `Einddatum` | G / in gecontroleerde export niet ingevuld | Alleen gebruiken indien werkelijk aangeleverd |

**Door opdrachtgever bevestigd minimum:** vijf kolommen: `Rel. code`, `Naam`, `Commissie`, `Functie`, `Begindatum`. `Einddatum` blijft buiten de minimumselectie. De huidige importer dwingt `Naam` en `Begindatum` nog niet als technische kolommen af.\n\n**Controles:** combinatie commissie + functie intact houden, bronrelatie controleren, datumvalidatie waar van toepassing, geen dubbeltelling met Functies, geen zelfbedachte einddatums. Vaststellen of `Begindatum` formeel als verplicht exportveld moet gelden (momenteel niet T).

**Basis:** `real_data_import.py`; herijkte baseline B-04/B-11.

## 7. Bron 5 — Overzicht per periode (export)

**Technische naam in code:** `vrijwilligers_periode`. Dit is **niet** de Vrijwilligers API.

| Oorspronkelijke kolom | Status | Betekenis |
| --- | --- | --- |
| `Relatiecode` | T | Koppeling naar lid; let op verschil met `Rel. code` |
| `Verplichte punten` | T/F | Sportlink A — verplichte uren/punten |
| `Gecorrigeerde punten` | T/F | Sportlink B — correcties |
| `Voldaan` | T/F | Sportlink C — voldaan |
| `Nog ingedeeld` | T/F | Sportlink D — reeds ingedeeld |
| `Niet ingedeeld` | T/F | Sportlink E — resterend |

**Controles:** vijf urenwaarden moeten aanwezig zijn en geldige gehele getallen zijn; controleer `E = A − B − C − D`; negatieve E kan geldig zijn; koppel op relatiecode; leg seizoen en ophaaldatum vast als importmetadata. Betekenis en praktische correctiecyclus B/C/D/E vragen aanvullende bronverificatie (BL-07). **Sportlink A is reeds met echte CKC-export functioneel getoetst.**

**Basis:** `real_data_import.py`, `hours_control.py`, herijkte baseline B-08/B-10.

## 8. Bron 6 — Vrijwilligers (API)

**Endpoint:** `https://data.sportlink.com/vrijwilligers` (read-only).  
**Door bestaande client aangevraagde velden:** `naam,datumvanaf,datumtot,tijdvanaf,tijdtot,lokatie,heledag`.

| API-veld / parameter | Status | Functie |
| --- | --- | --- |
| `naam` | F in adapter | Vrijwilligersnaam; matching is niet automatisch unieke persoonsidentiteit |
| `datumvanaf` | F in adapter | Startdatum concrete registratie |
| `datumtot` | G/F | Einddatum concrete registratie |
| `tijdvanaf`, `tijdtot` | G/F | Tijdgrenzen; parsing/volledigheid bij acceptatie verifiëren |
| `lokatie` | G | Locatie van de dienst |
| `heledag` | G/V | Aangevraagd veld; exacte verwerking en noodzaak verifiëren |
| `vrijwilligerstaakcode` (requestparameter) | F | Taakcode voor bronopvraag en koppeling aan CKC-dienstencatalogus |
| `aantaldagen`, `weekoffset`, `client_id` (requestparameters) | G | Venster en authenticatie/configuratie; geen persoonsvelden |

**Controles:** taakcode, concrete dienstperiode, geldige tijdzone, unieke toewijzing aan dienst, feitelijke bezetting, niet-gokbare persoonsidentificatie, ontbrekende/ambigue registratie en bronactualiteit. De bestaande adapter leidt een technische boekingsidentiteit af; die is **niet hetzelfde** als een door Sportlink bevestigd stabiel boekings-ID. Live-respons en werkelijk minimumcontract zijn nog afzonderlijk te accepteren.

**Basis:** `vrijwilligers_adapter.py`, `vrijwilligers_client.py`, v0.4-baseline.

## 9. Bron 7 — Wedstrijden / Programma (API)

**Endpoint:** `https://data.sportlink.com/programma` (read-only).

**Door bestaande client aangevraagde velden (letterlijk):**

```text
wedstrijddatum,wedstrijdcode,wedstrijdnummer,teamnaam,
thuisteamclubrelatiecode,uitteamclubrelatiecode,thuisteamid,thuisteam,
uitteamid,uitteam,teamvolgorde,competitiesoort,competitie,klasse,poule,
aanvangstijd,status,accommodatie,veld,locatie,plaats
```

| Veld(en) | Status | Functie |
| --- | --- | --- |
| `wedstrijddatum` | F | Wedstrijddatum/-tijd; adapter valideert |
| `wedstrijdcode` of `wedstrijdnummer` | F/G | Wedstrijdidentificatie; adapter gebruikt fallback |
| `thuisteamclubrelatiecode`, `uitteamclubrelatiecode` | F | Bepalen of CKC thuis of uit speelt; precies één CKC-zijde |
| `thuisteamid`, `uitteamid` | F/G | Identificatie CKC-team; fallback naar teamnaam wordt gesignaleerd |
| `thuisteam`, `uitteam` | F/G | Teamnaam en eventuele fallback |
| `status` | F | Operationeel vs afgelast/uitgesteld e.d. |
| `accommodatie` | G | Locatiecontext |
| `teamnaam`, `teamvolgorde`, `competitiesoort`, `competitie`, `klasse`, `poule`, `aanvangstijd`, `veld`, `locatie`, `plaats` | G/V | Wel aangevraagd; per veld vaststellen of noodzakelijk voor planning of uitsluitend context |

**Controles:** CKC-clubrelatiecode, HOME/AWAY, teamidentiteit, geldige wedstrijdtijd, unieke wedstrijd, niet-operationele status uitsluiten van normale kandidaatcontext, bronactualiteit en wedstrijdconflicten. Een aangevraagd API-veld is niet automatisch een functioneel verplicht veld; valideer met echte API-respons zonder persoonsgegevens te publiceren.

**Basis:** `programma_adapter.py`, `programma_client.py`, v0.4-baseline.

## 10. Overkoepelende import- en bronregels

1. **Relatiesleutel:** `Rel. code` in vier exports, `Relatiecode` in Overzicht per periode; niet koppelen op alleen naam. API Vrijwilligers vereist aparte verificatie van betrouwbare persoonsmatching.
2. **Peildatum:** importtijd, aangeleverde bron-ophaaldatum en relevant seizoen/venster onderscheiden. Een oudere bron dan vorige planning of niet-vernieuwde bron signaleren.
3. **CSV-validatie:** exact herkende kolomnamen, expliciete fout bij ontbrekende technische minimumkolommen, extra onbekende kolommen tolereren, geen stille default voor ontbrekende noodzakelijke feiten.
4. **Bronwaarheid:** Sportlink blijft bronhouder. `SOURCE_FACT`, `CONFIGURATION` en `DERIVED` niet vermengen.
5. **Privacy:** alleen noodzakelijke velden importeren; geen bankgegevens, ruwe CKC-exports, persoonsrecords of API-credentials in GitHub/Codex/ChatGPT.
6. **Toekomstige productie:** veilige, beheerde upload/importfunctionaliteit voor vijf exports; twee read-only API-integraties. Productie-inrichting is een latere fase.

## 11. Open verificatiepunten vóór formele acceptatie

- **V-01:** Zijn dit werkelijk alle *eerder afgesproken* minimumvelden per bron, of bestaan nog aanvullende historische veldlijsten in oudere chats/documentatie?
- **V-02:** Leden: formeel verplicht stellen van `Afmelddatum`, `Postcode`, `Huisnummer` en eventuele andere functionele bronkolommen, met onderscheid tussen aanwezige kolom en lege toegestane waarde.
- **V-03:** Teams: `Teamsoort` van gesignaleerd ontbrekend naar technisch verplicht brengen? Dit vraagt apart code- en testbesluit, geen wijziging door dit document.
- **V-04:** Commissies: opdrachtgever bevestigde `Begindatum` en `Naam` als verplichte exportkolommen; technische importvalidatie volgt afzonderlijk.
- **V-05:** Vrijwilligers API: welke velden en stabiele identificatie levert de echte respons; hoe zijn naam en relatiecode betrouwbaar te koppelen?
- **V-06:** Programma API: welke aangevraagde velden zijn werkelijk noodzakelijk en betrouwbaar aanwezig; klopt teamkoppeling met Teams-export?
- **V-07:** Overzicht per periode: bevestig B/C/D/E en seizoenssemantiek bij planner; houd BL-03 vorigeseizoensachterstand apart van A.
- **V-08:** Controleer bestaande historische broncontractdocumenten en oorspronkelijke afspraken vóór het label *definitief minimum* wordt toegekend.

## 12. Acceptatie en change control

Dit document is een **reconstructieconcept**, geen stilzwijgende nieuwe functionele baseline. De opdrachtgever beoordeelt de veldlijsten en open punten. Pas na expliciet akkoord en zo nodig correcties mergen naar `prototype-v0.5`. Technische strengere importvalidatie volgt later in afzonderlijke, geteste ontwikkelstappen; **geen codewijzigingen in deze documentatie-PR**.

**Referenties:** `code/Prototype/dvk/real_data_import.py`, `dvk/vrijwilligers_adapter.py`, `dvk/programma_adapter.py`, `tests/test_real_data_import_v04.py`, `DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md`, `BASELINE-v0.4.md`, `BACKLOG.md`.
