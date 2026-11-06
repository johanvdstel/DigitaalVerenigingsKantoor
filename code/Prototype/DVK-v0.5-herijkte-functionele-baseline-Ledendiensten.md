# DVK Prototype v0.5 — Herijkte functionele baseline Ledendiensten

**Status:** functioneel geaccepteerd op 2 oktober 2026; B-08 en V-05 herijkt op 26 oktober 2026  
**Datum:** 2 oktober 2026  
**Werkstroom:** Ledendiensten & Vrijwilligersbeleid  
**Reikwijdte:** herijking B-01–B-14, verificatie V-01–V-05 en aansluiting op de bestaande v0.4-baseline en het v0.5-vervolgcontract  
**Privacy:** dit document bevat geen persoonsregistraties, relatiecodes, adressen, bankgegevens of ruwe Sportlink-exports.

> Dit document is de **definitief functioneel geaccepteerde herijkte baseline**. De technische implementatie en geslaagde regressietests moeten nog afzonderlijk worden aangetoond. De drie voor de broncontrole aangeleverde leden-, functies- en commissiebestanden hoeven voor de verdere functionele besluitvorming niet te worden bewaard.

## 1. Doel, gezag en afbakening

Het Digitaal Verenigingskantoor (DVK) leidt uit Sportlink-bronfeiten en expliciet CKC-beleid af wie ledendienstplichtig is, welke verplichte uren voor het lopende seizoen verwacht worden, wie voor een dienst in aanmerking komt en waar menselijke beoordeling of correctie nodig is. Sportlink blijft bronhouder van lidmaatschappen, geregistreerde functies, teams, feitelijke dienstinroosteringen en de administratieve urenpositie. DVK voert in v0.5 **geen automatische Sportlink-mutaties** uit.

De op 13 september 2026 geaccepteerde v0.4-baseline (R01–R18, met C01–C22 en W/I-regressiebasis) blijft het uitgangspunt. Het bestaande `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` blijft van kracht voor tijdelijke planning, synchronisatie, no-shows, taakplichtdashboard en portaal. Deze herijking preciseert vooral de taakplichtafleiding, broninterpretatie en de scheiding tussen read-only taakplichtcontrole en Sportlink-registratie. Bij strijdigheid met oudere prototype-aannames gaan de hieronder expliciet herijkte besluiten voor; een eventuele spanning met eerder geaccepteerde casussen moet in de regressie-impactanalyse worden gedocumenteerd.

**Vaste scheiding:** bronfeit (`SOURCE_FACT`) ≠ CKC-beleidsconfiguratie (`CONFIGURATION`) ≠ DVK-afleiding (`DERIVED`) ≠ menselijke beslissing. DVK toont geen schijnzekerheid bij ontbrekende of tegenstrijdige brongegevens.

## 2. Geconsolideerde besluiten B-01–B-14

### B-01 — Lidmaatschap en voetbaldeelname zijn verschillende begrippen

Actueel lidmaatschap wordt afgeleid uit de Sportlink-velden `Lidstatus` en `Afmelddatum`; deelname aan een bondsteam uitsluitend uit de Teams-export. Vrije CKC-tekstvelden zoals `Status lidmaatschap` worden alleen voor expliciet vastgestelde CKC-betekenissen gebruikt. Een onduidelijke combinatie leidt tot een signaal, niet tot een verzonnen status.

### B-02 — Deelname aan een bondsteam

Een persoon is geregistreerd als speler van een bondsteam als **één en dezelfde actuele Teams-regel** voldoet aan alle drie voorwaarden: `Teamsoort = Bond`, `Teamrol = Teamspeler` en `Spelend lid = Ja`. Meerdere teamregistraties zijn toegestaan; een aanvullende rol als trainer of begeleider doet een geldige spelersregistratie niet vervallen. Ledenvelden zoals `Spelactiviteiten (bond)` vormen geen vervangend bewijs. Niet aan Sportlink doorgegeven wijzigingen kunnen door DVK niet worden ontdekt.

### B-03 — Betekenis van de afmelddatum

`Afmelddatum` geldt voor CKC als de **eerste dag waarop het lidmaatschap niet meer geldig is**. Een lid kan vóór die datum nog actueel zijn, maar niet op of na die datum. Bij `Lidstatus = Definitief` zonder afmelddatum geldt het lidmaatschap als actueel. Conflicterende lidstatussen, datums en dubbele ledenregels worden gesignaleerd. De precieze betekenis van het Sportlink-veld is hier een geaccepteerde CKC-interpretatie, geen geverifieerde algemene Sportlink-definitie. Historische gegevens blijven behouden.

### B-04 — Vrijstellende functies en eretitels

DVK combineert de actuele Sportlink-exports **Functies** en **Commissies**. De werkelijk voorkomende oorspronkelijke functienamen en, bij commissies, de combinatie van commissienaam en functienaam worden aan een expliciete CKC-configuratie gekoppeld. Algemene normalisaties zoals het samenvoegen van verschillende trainersfuncties tot `Trainer` **vervallen**; alleen technisch onschuldige tekstopschoning is toegestaan. Dubbele registraties leiden niet tot dubbele vrijstelling.

Erkende **onbetaalde** vrijwilligersfuncties, waaronder de afzonderlijk geregistreerde trainers-, teambegeleidings-, bestuurs- en commissiefuncties, geven persoonlijke **én huishoudvrijstelling**. De betaalde `Hoofdtrainer Sen.` en `Verzorger` geven alleen persoonlijke vrijstelling. `Lid van verdienste` en `Erelid` geven alleen persoonlijke vrijstelling; het zijn eretitels, geen bewijs van operationele vrijwilligersarbeid. De volledige definitieve mapping wordt uit de werkelijke exportwaarden vastgelegd en getest; niet-herkende titels worden niet stilzwijgend geclassificeerd.

**CKC-classificatiebesluit 27 oktober 2026 (BL-08 afgesloten):** beide huidige Sportlink-registraties met functienaam `Verzorger` worden bewust als betaalde functie behandeld, hoewel één van beide in werkelijkheid onbetaald is. Conform B-04 geeft dit **persoonlijke vrijstelling, maar geen huishoudvrijstelling**. Met de huidige bezetting heeft deze keuze geen effect op huishoudvrijstelling. Een onderscheidende Sportlink-functienaam is geen voorwaarde meer voor afronding van BL-08. Er komt geen persoonsgebonden hardcoded uitzondering of aanvullende DVK-functie. Als CKC later de functienaam of het beleid wijzigt, kan de classificatie opnieuw worden beoordeeld; de huidige keuze wordt niet als permanent persoonsfeit vastgelegd.

### B-05 — Huishoudvrijstelling op adres

Een erkende **onbetaalde** vrijwilligersfunctie geeft vrijstelling aan de functionaris én de andere relevante leden op **hetzelfde volledig geregistreerde woonadres**, ongeacht familieband. Ouders, achternaam en `Contact via ouders` zijn geen criterium. Het adres bestaat uit postcode, huisnummer en eventuele toevoeging; onschuldige notatieverschillen mogen worden genormaliseerd, maar ontbrekende gegevens mogen niet worden gegokt. Betaalde functies en eretitels geven geen huishoudvrijstelling. Ontbrekende of tegenstrijdige adressen leiden waar relevant tot een signaal.

### B-06 — Gezinsregel voor minderjarige leden

**Expliciete beleidsherijking — 9 oktober 2026:** uitsluitend het volledige geregistreerde woonadres (postcode, huisnummer en eventuele toevoeging) bepaalt het gezamenlijke huishouden voor B-05 en B-06/B-07. Een lege toevoeging is geldig. Kwalificerende minderjarige leden op hetzelfde adres behoren administratief tot hetzelfde huishouden, ongeacht achternaam, familierelatie, geregistreerde ouders en `Contact via ouders`. Deze gegevens zijn geen besliscriteria. Verschillende volledige woonadressen betekenen afzonderlijke huishoudens, ook bij dezelfde ouders. Ontbrekende of conflicterende noodzakelijke adresgegevens bewijzen geen huishouden en sluiten een vrijstelling niet betrouwbaar uit; bewezen vrijstellingen houden voorrang.

Ouders kunnen reclameren bij een afwijkende feitelijke gezinssituatie. De Vrijwilligerscommissie beoordeelt het verzoek; bij escalatie beslist het bestuur. DVK neemt hierover geen zelfstandig besluit. Registratie en verwerking van uitzonderingsbesluiten vallen buiten deze implementatie.

### B-07 — Peildatum en oudste minderjarige

De planningsdatum is bepalend. Binnen het volgens B-06 vastgestelde huishouden blijft de bestaande oudste-kindregel gelden, inclusief de bestaande leeftijds-, lidmaatschaps- en vrijstellingsvoorwaarden en onzekerheid bij gelijke geboortedatums. Van de relevante minderjarige kinderen draagt in beginsel het oudste kwalificerende kind de gezinsgebonden verplichting. Wanneer dit kind 18 wordt of het lidmaatschap eindigt, verschuift de gezinsverplichting naar het volgende kwalificerende minderjarige kind. Een vrijstellende vrijwilligersfunctie van het oudste kind kan juist huishoudvrijstelling opleveren; de verplichting schuift dan niet enkel vanwege diens persoonlijke vrijstelling door. Historische posities worden niet met terugwerkende kracht herberekend.

### B-08 — Meerderjarig worden (herijkt op 26 oktober 2026)

Bij het bereiken van 18 jaar ontstaat, indien aan de overige voorwaarden is voldaan, een zelfstandige verplichting voor het inmiddels meerderjarige lid; de gezinsgebonden verplichting kan tegelijk naar een jonger minderjarig kind verschuiven. Reeds gewerkte uren (`C`) blijven bij het lid dat de diensten heeft verricht. Het jongere kind kan daardoor in hetzelfde seizoen een eigen volledige verplichting krijgen, zonder overname van de gewerkte uren van het oudere kind; dit gevolg is bewust geaccepteerd. DVK berekent de verwachte taakplicht op de relevante peildatum opnieuw en signaleert eventuele verschillen met de in Sportlink geregistreerde taakplicht via de bestaande read-only taakplichtcontrole. **DVK signaleert, faciliteert, keurt goed noch verifieert urenoverdrachten tussen leden.** Handmatige urenoverdracht of -correctie in Sportlink blijft buiten DVK mogelijk en valt buiten de DVK-verantwoordelijkheid. De urenpositie blijft `E = A − B − C − D`, waarbij een negatieve E geldig kan zijn.

### B-09 — Afwijkingen tussen DVK en Sportlink

DVK berekent per relevant lid de **verwachte A** en vergelijkt die met de in Sportlink **geregistreerde A**. Een afwijking wordt bij relevante planningsruns gesignaleerd; een volledige kwaliteitscontrole voor alle leden is daarnaast mogelijk. De controle toont afwijkingen op basis van de meest recent ingelezen Sportlink-gegevens. Na een correctie in Sportlink kan een volgende import de actuele stand tonen; als het verschil dan is verdwenen, verdwijnt ook het actuele afwijkingssignaal. Ook bewust niet-gecorrigeerde afwijkingen blijven als verschil zichtbaar. DVK legt geen individuele acceptatiebesluiten, redenen, verantwoordelijken, vervaldata of toezeggingen vast en onderdrukt geen signalen op grond van zulke besluiten. Voor kandidaatselectie en voorstellen is de in Sportlink geregistreerde taakplicht leidend, ook bij verschil met de CKC-beleidsafleiding.

### B-10 — Betrouwbare fallback

Als brongegevens of regels geen betrouwbare uitkomst toelaten, toont DVK de ontbrekende of tegenstrijdige feiten en vraagt om beoordeling door de planner. DVK verzint geen gegevens en wijst niet automatisch toe wanneer de taakplicht onzeker is.

### B-11 — Geldigheid van functies op de peildatum

DVK gebruikt de **actuele** Functies- en Commissies-exports en voorkomt dubbeltelling van dezelfde persoon/functie. De broncontrole heeft bevestigd: de Functies-export bevat geen begin- of einddatumvelden; de Commissies-export bevat een begindatum, maar geen ingevulde einddatums. Aanwezige registraties gelden daarom als actueel **op het exportmoment**; de commissiebegindatum wordt bewaard. Een beëindiging die niet in de nieuwe export is verwerkt, kan DVK niet zelfstandig kennen. De eerder besproken controle op tegenstrijdige actuele versus expliciet beëindigde registraties is voor deze concrete exportstructuur niet van toepassing. Bij latere gewijzigde bronstructuur worden aanwezige geldigheidsvelden alsnog volgens de peildatum verwerkt.

### B-12 — Bronactualiteit

DVK toont per relevante bron wanneer gegevens zijn opgehaald. Bij verouderde informatie volgt een waarschuwing, zonder arbitraire algemene maximale ouderdom. Een planner kan met waarschuwing verder zolang een betrouwbare beoordeling mogelijk blijft; anders geldt B-10. Wanneer relevante bronnen sinds de vorige planning niet zijn vernieuwd, wordt vóór kandidaatselectie gewaarschuwd.

### B-13 — Seizoensovergang en verwachte uren

Elk seizoen heeft een eigen Sportlink-urenregistratie; de export *Overzicht per periode* betreft uitsluitend het huidige seizoen (BL-07, gevalideerd 27 oktober 2026). Bij seizoensstart beoordeelt DVK de taakplicht van ieder relevant lid opnieuw op basis van actuele feiten en beleid, berekent **verwachte A per lid** en bereidt daarmee de controle en eventuele handmatige instelling van A in Sportlink voor. Een planner beoordeelt verschillen en voert in v0.5 eventuele wijzigingen zelf uit; een nieuwe import controleert het resultaat. Uren uit een vorig seizoen worden niet automatisch overgeboekt. DVK beheert geen seizoensgebonden of langer geldige individuele taakplichtbesluiten. Beschikbare historische brongegevens blijven bewaard volgens de bestaande afspraken. Historische bron: `~/Documents/DVK-Sportlink-exports/Overzicht per periode vorig seizoen.csv`, dezelfde CSV-kolomstructuur als de actuele urenexport. De planner levert het onmiddellijk voorafgaande seizoen; DVK leidt of verifieert dat bronseizoen niet zelfstandig. Koppeling uitsluitend op `Relatiecode`; `Niet ingedeeld` is de bronwaarde, getoetst aan A−B−C−D. Positieve achterstand telt als tweede criterium na actuele E voor diensten in **juli tot en met december** (`7 <= on_date.month <= 12`); januari t/m juni niet. Nul betekent geen achterstand; negatieve waarden blijven als bronfeit behouden en geven geen krediet. Actuele A/B/C/D/E blijven ongewijzigd. Bij ontbrekend, onleesbaar of structureel ongeldig historisch bestand blijft planning bruikbaar met een zichtbare waarschuwing. Ontbrekende ledenregels, dubbele relatiecodes, ongeldige getallen en formuleverschillen leveren voor de betrokken kandidaat onbekende/onbetrouwbare historische achterstand op; geen uitsluiting of stilzwijgende nul. Voor rangschikking neutraal, in toelichting onderscheiden van bekende nul, ontbrekende bron en maanden buiten toepassing. Andere geldige historische records blijven bruikbaar. Taakplichtcontrole blijft onafhankelijk van deze optionele bron. Dit is de expliciet goedgekeurde BL-03-wijziging van B-13 ten opzichte van de historische 1-decembergrens; technische implementatie is nog geen functionele acceptatie van Iteratie 2.

### B-14 — Geen DVK-levenscyclus voor taakplichtbesluiten (herijkt 26 oktober 2026)

De oorspronkelijk voorziene duurzame levenscyclus van plannerbeslissingen over taakplichtafwijkingen is **vervallen** (BL-05). De planner beoordeelt de signalen in de read-only taakplichtcontrole en voert eventuele aanpassingen rechtstreeks in Sportlink uit. DVK beheert hiervoor geen openstaande correctietoezeggingen, goedkeuringen, acceptaties, redenen, verantwoordelijken, vervaldata of herbeoordelingsstatussen. Nieuwe bronimports en gewijzigde feiten of beleidsregels leiden uitsluitend tot een actuele herberekening en vergelijking volgens B-09; afwijkingen blijven zichtbaar zolang ze feitelijk bestaan. Dit besluit raakt niet aan de afzonderlijke afspraken over tijdelijke planning en no-showregistratie.

## 3. Verificatiepunten V-01–V-05: geaccepteerde uitwerking

| Punt | Vastgestelde implementatieafwijking | Vereiste correctie en regressie |
|---|---|---|
| **V-01 Voetbaldeelname** | Huidige import leidt spelen af uit ledenvelden en leest `Teamsoort` niet in. | Alle drie B-02-voorwaarden op dezelfde Teams-regel; meerdere teamregistraties, extra trainersrol, recreatieve registratie, ontbrekende/ongeldige waarden testen. |
| **V-02 Lidmaatschap** | `Afmelddatum` wordt genegeerd; dubbele regels worden gerangschikt op ogenschijnlijk actieve status. | B-03 toepassen op planningsdatum, conflicten signaleren en historie behouden; toekomstige afmelddatum, dag zelf, ontbrekende datum en dubbele regels testen. |
| **V-03 Functievrijstelling** | Commissies worden niet volledig meegenomen; legacy-lijst is geen CKC-configuratie; functienormalisatie kan betaald/onbetaald verwarren. | Beide bronnen combineren, oorspronkelijke namen bewaren, afzonderlijke zelf-/huishoudvrijstelling configureren, actuele bronstructuur respecteren en onbekende functies signaleren. |
| **V-04 Broederdienst** | De eerdere oudergebaseerde interpretatie is per 9 oktober 2026 vervallen. | Uitsluitend het volledige adres vergelijken; oudste-kindregel, toevoegingen, ontbrekende/conflicterende adressen en onafhankelijkheid van ouders/contactwaarde testen. |
| **V-05 Taakplichtafwijkingen bij meerderjarigheid** | A-vergelijking en E-formule bestaan; de oorspronkelijke eisen aan een DVK-beslisstatus en urenoverdracht zijn vervallen door de herijking van BL-05 en BL-06. | Controleer de overgang op de 18e verjaardag, verschuiving van de gezinsgebonden taakplicht, behoud van gewerkte uren bij het oorspronkelijke lid en signalering van afwijkende Sportlink-A via de bestaande taakplichtcontrole. Geen DVK-workflow of verificatie voor handmatige urenoverdracht in Sportlink. |

Alle vijf punten zijn **inhoudelijk geaccepteerd**, niet technisch afgetest.

## 4. Resultaat van de broncontrole en privacy

De broncontrole is uitgevoerd op drie tijdelijk aangeleverde Sportlink-exports. In dit document worden uitsluitend structuur- en aggregaatbevindingen bewaard, **geen individuele bronregels**.

- **Leden:** 3.134 regels, 3.133 unieke relatiecodes. Eén dubbele relatiecode met onderling verschillende afmelddatums is een relevante V-02-testcasus. `Afmelddatum`, afzonderlijke adresvelden en oudernaamvelden zijn beschikbaar. De daadwerkelijke veldnaam voor geboortedatum is `Geb.dat.`; de oudere importer verwacht `Geboortedatum`, zodat expliciete bronmapping nodig is. De oudergegevens zijn niet voor iedereen volledig: 507 ledenregels bevatten een eerste oudernaam en 37 een tweede oudernaam.
- **Functies:** 126 registraties, 27 functienamen; geen begin- of einddatumvelden. De oorspronkelijke namen blijven behouden. De bron bevatte ook voor de taakplichtcontrole overbodige gevoelige velden; deze worden niet verwerkt of in GitHub geplaatst.
- **Commissies:** 145 registraties, 19 commissies en 62 commissie-functiecombinaties. Alle registraties bevatten een begindatum; geen ingevulde einddatum. De combinatie commissie/functie blijft intact.
- **Overlap:** 43 personen komen in zowel de Functies- als de Commissies-export voor; dubbele vermelding levert geen dubbele vrijstelling op.

De ruwe bestanden maken **geen** deel uit van deze baseline. Voor ontwikkeling en regressietests worden uitsluitend synthetische of voldoende geanonimiseerde fixtures gebruikt. De oorspronkelijke bijlagen in de ChatGPT-conversatie staan los van lokale werkkopieën; de gebruiker kan de betreffende conversatie verwijderen wanneer dit document en de noodzakelijke overdracht veilig zijn gesteld.

## 5. Bestaande v0.5-afspraken die ongewijzigd blijven

1. **Tijdelijke planning:** Sportlink is bronhouder van feitelijke inroostering. DVK-planningsposities zijn tijdelijk, beïnvloeden meteen bezetting en beschikbaarheid, kunnen vóór synchronisatie worden teruggedraaid en verdwijnen bij succesvolle Sportlink-synchronisatie. Bij mislukte synchronisatie blijven ze intact. Er is geen verplichte permanente historie van iedere tijdelijke planningshandeling.
2. **No-shows:** uitsluitend op een concrete feitelijke Sportlink-inroostering; zelfstandig duurzaam en onveranderlijk no-showfeit; eventuele intrekking als afzonderlijk duurzaam feit met actor, tijdstip en toelichting; actuele seizoenteller en sanctiestatus worden afgeleid. Handmatige Sportlink-correctie blijft een aparte eenvoudige werkvoorraad.
3. **Taakplichtdashboard:** volledige relevante populatie raadpleegbaar, met DVK-afleiding, afleidingsreden, Sportlink-A, actuele vergelijkingsstatus en datakwaliteit; geen duurzame plannerafhandeling of persoonsgebonden uitzonderingsadministratie. CKC-beleid (waaronder momenteel 10 uur) blijft configureerbaar.
4. **Portaal:** Ledendienst Planning is een module binnen DVK. De UI gebruikt begrijpelijke CKC-termen, toont ontwikkelstatus van andere modules en bevat geen beleidslogica in de Streamlit-presentatielaag.
5. **Bestaande regressies:** de geaccepteerde C-, W-, I- en R-cases blijven verplicht; waar deze herijking bewust een oudere prototype-aanname wijzigt, wordt de test expliciet aangepast en de reden vastgelegd.

**Herijking 26 oktober 2026:** B-09 en B-14 zijn in overeenstemming gebracht met BL-05: geen duurzame registratie van taakplicht-/correctiebeslissingen in DVK. Tijdelijke planningshandelingen blijven onder FR-08 vallen.

## 6. Implementatie- en verificatiecontract

### 6.1 Bronadapters en canonieke feiten

- Maak een expliciete, geteste mapping van werkelijke Sportlink-kolommen naar canonieke velden; onbekende extra kolommen mogen import niet blokkeren.
- Verwerk lidmaatschapsstatus en afmelddatum volgens B-03; maak conflicten in dubbele ledenregels zichtbaar in plaats van één schijnbaar gunstige regel te kiezen.
- Verwerk Teams volgens B-02, inclusief `Teamsoort` en alle afzonderlijke teamregistraties.
- Bewaar Functies- en Commissies-registraties met originele naam, bron en eventuele begindatum; verwijder semantische samenvoegingen zoals `Trainer`.
- Verwerk het woonadres volgens B-05/B-06; ouders en contact-via-ouders zijn uitsluitend broncontext en geen taakplichtcriterium.
- Behoud herkomst en bronactualiteit, en verwerk geen overbodige financiële of identiteitsvelden.

### 6.2 Domeinlogica en taakplichtcontrole

- Bereken per peildatum en seizoen de taakplicht en verwachte A; scheid die van geregistreerde Sportlink-A.
- Maak de volledige CKC-functieclassificatie expliciete configuratie, inclusief het CKC-classificatiebesluit over `Verzorger` (BL-08).
- Behoud de bestaande read-only signalering van taakplichtafwijkingen; de planner beoordeelt en corrigeert zo nodig Sportlink buiten DVK (herijkte BL-05).
- Ondersteun geen DVK-urenoverdracht of verificatie daarvan; gewerkte uren (`C`) blijven bij het oorspronkelijke lid. Handmatige Sportlink-correcties blijven buiten DVK mogelijk.
- Respecteer read-only Sportlink-integratie in v0.5; geen verborgen automatische correcties.

### 6.3 Minimale acceptatietests

- V-01–V-05-scenario's uit §3, met positieve, negatieve en ambigue bronvarianten.
- Peildatumgrenzen: 18e verjaardag (inclusief verschuiving van gezinsgebonden taakplicht zonder urenoverdracht), afmelddatum, commissiebegindatum en seizoensovergang.
- Huishoudvrijstelling: vrijwillig/onbetaald versus betaald/eretitel; volledig adres met toevoeging; ontbrekend of tegenstrijdig adres.
- Seizoensgebonden A: herberekening en actueel afwijkingssignaal op basis van ingelezen Sportlink-A; handmatige correctie gebeurt buiten DVK en is na een nieuwe import zichtbaar; geen automatische urenoverdracht uit vorig seizoen.
- Taakplichtcontrole: verwachte A opnieuw afleiden en afwijkende Sportlink-A signaleren; geen DVK-registratie van plannerbesluiten of urenoverdracht (herijkte BL-05/BL-06).
- Bestaande v0.4- en v0.5-plannings-/no-showregressies blijven groen.

## 7. Resterende verificaties en expliciete acceptatiegrenzen

**Nog te verifiëren met echte bronbestanden:**

1. De daadwerkelijke **Teams-export**: aanwezigheid, naam en waarden van `Teamsoort`, `Teamrol` en `Spelend lid`, plus eventuele duplicaten of bronvarianten.
2. **BL-07 functioneel afgesloten op 27 oktober 2026:** in de Sportlink-export *Overzicht per periode* betekenen de velden A = `Verplichte punten`, B = `Gecorrigeerde punten`, C = `Voldaan`, D = `Nog ingedeeld`, E = `Niet ingedeeld` (E = A − B − C − D). De export bevat per definitie uitsluitend het huidige seizoen. Een praktijksteekproef van de openstaande uren en prioritering in Kandidaten en Voorstellen tegen het CSV-bestand is akkoord. Geen afzonderlijk brononderzoek of DVK-verificatie van handmatige urenoverdracht meer vereist. Dit vervangt de eerdere openstaande functionele bronverificatie, maar claimt geen volledige technische regressie.
3. De volledige functie-/commissieclassificatie als machineleesbare CKC-configuratie, één-op-één getoetst aan de gecontroleerde oorspronkelijke exportwaarden. De functionele hoofdregels en het vastgestelde CKC-classificatiebesluit voor `Verzorger` zijn bekend (BL-08 functioneel afgesloten); de uiteindelijke volledige configuratie en tests vallen onder de afzonderlijke technische verificatie, niet onder een openstaande BL-08-broncorrectie.
4. De complete code-impactanalyse en uitvoering van de volledige regressiesuite, inclusief bestaande v0.5-planning en no-shows. De eerdere controle was gericht op de baselinecontracten en kernmodules; zij is geen bewijs dat ieder v0.5-bestand en iedere test reeds is doorgelicht.

**Functionele acceptatie** van dit document kan plaatsvinden voordat alle code is gewijzigd, mits de bovenstaande punten als expliciete technische acceptatievoorwaarden blijven staan. **Technische acceptatie** mag pas na uitvoering, controle van de vereiste echte bronstructuren en een aantoonbaar geslaagde regressiesuite worden uitgesproken.

## 8. Definitief functioneel acceptatiebesluit

CKC heeft op **2 oktober 2026** de herijkte functionele baseline B-01–B-14 en V-01–V-05 definitief functioneel geaccepteerd, inclusief de verduidelijkte bronsemantiek, de CKC-functieclassificatie en de tijdelijke behandeling van `Verzorger`. De technische verificatievoorwaarden van §7 blijven onverkort van kracht. Deze functionele acceptatie houdt geen technische oplevering of acceptatie van de v0.5-implementatie in.

## 9. Referenties

- `code/Prototype/BASELINE-v0.4.md` — geaccepteerde v0.4-baseline, 13 september 2026.
- `code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` — bestaande afspraken na Gate 10.
- `code/Prototype/dvk/real_data_import.py` en `code/Prototype/dvk/duty.py` op ontwikkelbranch `prototype-v0.5` — uitgangspunt voor de gecontroleerde implementatieafwijkingen.
- De in de herijkingsgesprekken inhoudelijk geaccepteerde besluiten B-01–B-14 en V-01–V-05.


## Aanvulling 25 oktober 2026 — operationele kandidaten bij bronafwijkingen

Vastgesteld voor de kandidaatroute van PR #44 (lokale heracceptatie nog uit te
voeren): `Lidstatus = Definitief` is noodzakelijk, maar niet voldoende. De
bestaande afmeld-/peildatum-, deelname-, taakplicht-, vrijstellings- en
kandidaatcriteria blijven gelden. Andere lidstatussen, waaronder `Afgemeld` en
`Overschrijving spelactiviteit`, leveren geen operationeel kandidaatvoorstel op.
Dit verandert de historische interpretatie van bronregistraties niet.

Persoonsgebonden fouten blokkeren niet de gehele kandidaatselectie. Bij
tegenstrijdige gegevens of onzekere koppeling wordt alleen de betreffende
onbetrouwbare beoordeling uitgesloten; relevante diagnostiek blijft beschikbaar.
Dubbele bronregels geven geen dubbele kandidaten of dubbele urentoekenning.
Verschillende beëindigde registraties van dezelfde relatiecode hoeven niet eerst
administratief gecorrigeerd te worden om andere personen te beoordelen.

Uren blijven via relatiecode gekoppeld. Gelijke namen zijn alleen relevant voor
onderdelen die daadwerkelijk op naam koppelen: daar is geen automatische keuze
bij meerdere mogelijke personen. Een bestaande betrouwbare relatiecodekoppeling
wordt niet door een nieuwe naamkoppeling vervangen. Technisch ontbrekende,
onleesbare of structureel onbruikbare bronnen mogen de import blijven blokkeren.

Zie [uitwerking en heracceptatie PR #44](DVK-v0.5-actuele-kandidaatcontext.md#vervolgbesluit-pr-44--persoonsgebonden-afwijkingen-25-oktober-2026).


## Aanvulling PR #44 — kandidaatkeuze en lokale broninvoer (25 oktober 2026)

Het kandidatenaanbod omvat alle geschikte kandidaten in de bestaande rangorde.
Vrije capaciteit begrenst de te bevestigen selectie, niet de keuzelijst. De
bestaande menselijke batchgoedkeuring en controles op conflicten/duplicaten
blijven bepalend. Een lagere rang maakt een geschikte kandidaat niet ongeschikt.

Bronmeldingen zijn lokaal tot relevante registraties en afwijkende waarden
herleidbaar, met afzonderlijke regels bij duplicaten. Geen automatische correctie.
De vijf vaste lokale CSV's worden bij functiegebruik automatisch gelezen;
Brongegevens vernieuwen leest ze expliciet opnieuw. Bestanden en laadtijd worden
getoond. Kandidaten en taakplichtcontrole delen de invoer, niet hun afzonderlijke
beoordelingscontract. Technische fouten tonen geen oude uitslag als actueel;
bronbestanden blijven ongewijzigd. Prototypevoorziening, geen productiearchitectuur.

Zie [implementatie A/B/C en onderzoek D/E](DVK-v0.5-vervolgacceptatie-ABC-DE.md).
Lokale functionele acceptatie van deze implementatie volgt nog afzonderlijk.
