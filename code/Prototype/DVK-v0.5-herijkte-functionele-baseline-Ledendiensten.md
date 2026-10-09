# DVK Prototype v0.5 — Herijkte functionele baseline Ledendiensten

**Status:** definitief functioneel geaccepteerd op 2 oktober 2026  
**Datum:** 2 oktober 2026  
**Werkstroom:** Ledendiensten & Vrijwilligersbeleid  
**Reikwijdte:** herijking B-01–B-14, verificatie V-01–V-05 en aansluiting op de bestaande v0.4-baseline en het v0.5-vervolgcontract  
**Privacy:** dit document bevat geen persoonsregistraties, relatiecodes, adressen, bankgegevens of ruwe Sportlink-exports.

> Dit document is de **definitief functioneel geaccepteerde herijkte baseline**. De technische implementatie en geslaagde regressietests moeten nog afzonderlijk worden aangetoond. De drie voor de broncontrole aangeleverde leden-, functies- en commissiebestanden hoeven voor de verdere functionele besluitvorming niet te worden bewaard.

## 1. Doel, gezag en afbakening

Het Digitaal Verenigingskantoor (DVK) leidt uit Sportlink-bronfeiten en expliciet CKC-beleid af wie ledendienstplichtig is, welke verplichte uren voor het lopende seizoen verwacht worden, wie voor een dienst in aanmerking komt en waar menselijke beoordeling of correctie nodig is. Sportlink blijft bronhouder van lidmaatschappen, geregistreerde functies, teams, feitelijke dienstinroosteringen en de administratieve urenpositie. DVK voert in v0.5 **geen automatische Sportlink-mutaties** uit.

De op 13 september 2026 geaccepteerde v0.4-baseline (R01–R18, met C01–C22 en W/I-regressiebasis) blijft het uitgangspunt. Het bestaande `FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` blijft van kracht voor tijdelijke planning, synchronisatie, no-shows, taakplichtdashboard en portaal. Deze herijking preciseert vooral de taakplichtafleiding, broninterpretatie en plannerbeslissingen. Bij strijdigheid met oudere prototype-aannames gaan de hieronder expliciet herijkte besluiten voor; een eventuele spanning met eerder geaccepteerde casussen moet in de regressie-impactanalyse worden gedocumenteerd.

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

**Bewust geaccepteerde tijdelijke bronafwijking:** de huidige twee registraties `Verzorger` worden beide als betaalde functie behandeld, hoewel in werkelijkheid één van beide onbetaald is. CKC zal de onbetaalde registratie later een onderscheidende titel geven. Er komt hiervoor geen persoonsgebonden hardcoded uitzondering. Na nieuwe bronimport wordt de nieuwe titel opnieuw geclassificeerd. Volgens de bij besluitvorming bekende situatie heeft deze tijdelijke classificatie geen effect op een huishoudvrijstelling; die aanname wordt niet als permanente persoonsregel vastgelegd.

### B-05 — Huishoudvrijstelling op adres

Een erkende **onbetaalde** vrijwilligersfunctie geeft vrijstelling aan de functionaris én de andere relevante leden op **hetzelfde volledig geregistreerde woonadres**, ongeacht familieband. Ouders, achternaam en `Contact via ouders` zijn geen criterium. Het adres bestaat uit postcode, huisnummer en eventuele toevoeging; onschuldige notatieverschillen mogen worden genormaliseerd, maar ontbrekende gegevens mogen niet worden gegokt. Betaalde functies en eretitels geven geen huishoudvrijstelling. Ontbrekende of tegenstrijdige adressen leiden waar relevant tot een signaal.

### B-06 — Gezinsregel voor minderjarige leden

**Expliciete beleidsherijking — 9 oktober 2026:** uitsluitend het volledige geregistreerde woonadres (postcode, huisnummer en eventuele toevoeging) bepaalt het gezamenlijke huishouden voor B-05 en B-06/B-07. Een lege toevoeging is geldig. Kwalificerende minderjarige leden op hetzelfde adres behoren administratief tot hetzelfde huishouden, ongeacht achternaam, familierelatie, geregistreerde ouders en `Contact via ouders`. Deze gegevens zijn geen besliscriteria. Verschillende volledige woonadressen betekenen afzonderlijke huishoudens, ook bij dezelfde ouders. Ontbrekende of conflicterende noodzakelijke adresgegevens bewijzen geen huishouden en sluiten een vrijstelling niet betrouwbaar uit; bewezen vrijstellingen houden voorrang.

Ouders kunnen reclameren bij een afwijkende feitelijke gezinssituatie. De Vrijwilligerscommissie beoordeelt het verzoek; bij escalatie beslist het bestuur. DVK neemt hierover geen zelfstandig besluit. Registratie en verwerking van uitzonderingsbesluiten vallen buiten deze implementatie.

### B-07 — Peildatum en oudste minderjarige

De planningsdatum is bepalend. Binnen het volgens B-06 vastgestelde huishouden blijft de bestaande oudste-kindregel gelden, inclusief de bestaande leeftijds-, lidmaatschaps- en vrijstellingsvoorwaarden en onzekerheid bij gelijke geboortedatums. Van de relevante minderjarige kinderen draagt in beginsel het oudste kwalificerende kind de gezinsgebonden verplichting. Wanneer dit kind 18 wordt of het lidmaatschap eindigt, verschuift de gezinsverplichting naar het volgende kwalificerende minderjarige kind. Een vrijstellende vrijwilligersfunctie van het oudste kind kan juist huishoudvrijstelling opleveren; de verplichting schuift dan niet enkel vanwege diens persoonlijke vrijstelling door. Historische posities worden niet met terugwerkende kracht herberekend.

### B-08 — Meerderjarig worden en eventuele urenoverdracht

Bij het bereiken van 18 jaar ontstaat, indien aan de overige voorwaarden is voldaan, een zelfstandige verplichting voor het inmiddels meerderjarige lid; de gezinsverplichting kan tegelijk naar een jonger minderjarig kind verschuiven. Reeds gewerkte uren (`C`) blijven bij degene die ze heeft verricht. **Geen automatische overdracht.** Na expliciete menselijke goedkeuring kan geheel of gedeeltelijk worden overgedragen via **twee tegengestelde Sportlink-correcties op B**: een negatieve B bij het oudste kind en een even grote positieve B bij het jongere kind. De planner verwerkt beide handmatig; een nieuwe import verifieert beide samen. De urenpositie blijft `E = A − B − C − D`, waarbij een negatieve E geldig kan zijn. Zonder overdracht kan in hetzelfde seizoen bij het jongere kind een aanvullende volledige verplichting ontstaan; dat gevolg is bewust geaccepteerd.

### B-09 — Afwijkingen tussen DVK en Sportlink

DVK berekent per relevant lid de **verwachte A** en vergelijkt die met de in Sportlink **geregistreerde A**. Een afwijking wordt bij relevante planningsruns gesignaleerd; een volledige kwaliteitscontrole voor alle leden is daarnaast mogelijk. Een overeengekomen maar nog niet in Sportlink uitgevoerde correctie blijft zichtbaar tot een nieuwe import de wijziging bevestigt. Een bewust geaccepteerde afwijking krijgt een vastgelegde reden, verantwoordelijke en eventuele einddatum en hoeft bij ongewijzigde feiten en ongewijzigd beleid niet telkens opnieuw te worden gemeld. Opgeloste afwijkingen worden afgesloten.

### B-10 — Betrouwbare fallback

Als brongegevens of regels geen betrouwbare uitkomst toelaten, toont DVK de ontbrekende of tegenstrijdige feiten en vraagt om beoordeling door de planner. DVK verzint geen gegevens en wijst niet automatisch toe wanneer de taakplicht onzeker is.

### B-11 — Geldigheid van functies op de peildatum

DVK gebruikt de **actuele** Functies- en Commissies-exports en voorkomt dubbeltelling van dezelfde persoon/functie. De broncontrole heeft bevestigd: de Functies-export bevat geen begin- of einddatumvelden; de Commissies-export bevat een begindatum, maar geen ingevulde einddatums. Aanwezige registraties gelden daarom als actueel **op het exportmoment**; de commissiebegindatum wordt bewaard. Een beëindiging die niet in de nieuwe export is verwerkt, kan DVK niet zelfstandig kennen. De eerder besproken controle op tegenstrijdige actuele versus expliciet beëindigde registraties is voor deze concrete exportstructuur niet van toepassing. Bij latere gewijzigde bronstructuur worden aanwezige geldigheidsvelden alsnog volgens de peildatum verwerkt.

### B-12 — Bronactualiteit

DVK toont per relevante bron wanneer gegevens zijn opgehaald. Bij verouderde informatie volgt een waarschuwing, zonder arbitraire algemene maximale ouderdom. Een planner kan met waarschuwing verder zolang een betrouwbare beoordeling mogelijk blijft; anders geldt B-10. Wanneer relevante bronnen sinds de vorige planning niet zijn vernieuwd, wordt vóór kandidaatselectie gewaarschuwd.

### B-13 — Seizoensovergang en verwachte uren

Elk seizoen heeft een eigen Sportlink-urenregistratie. Bij seizoensstart beoordeelt DVK de taakplicht van ieder relevant lid opnieuw op basis van actuele feiten en beleid, berekent **verwachte A per lid** en bereidt daarmee de controle en eventuele handmatige instelling van A in Sportlink voor. Een planner beoordeelt verschillen en voert in v0.5 eventuele wijzigingen zelf uit; een nieuwe import controleert het resultaat. Uren uit een vorig seizoen worden niet automatisch overgeboekt. Seizoensgebonden individuele uitzonderingen verlopen; expliciet langer geldende besluiten worden op geldigheid en nieuwe feiten getoetst. Historische gegevens blijven bewaard. Openstaande uren uit het vorige seizoen kunnen volgens de bestaande prioriteringsregel vóór 1 december meewegen bij kandidaatselectie, maar worden niet automatisch bij de nieuwe A opgeteld.

### B-14 — Levenscyclus van plannerbeslissingen

Een afgesproken maar nog niet uitgevoerde Sportlink-correctie blijft bij relevante controles signaleren tot een nieuwe import uitvoering bevestigt. Een bewust geaccepteerde afwijking wordt duurzaam vastgelegd met reden, verantwoordelijke, beslisdatum en optionele vervaldatum; herhaalde signalen worden onderdrukt zolang feiten, beleid en geldigheid ongewijzigd blijven. Relevante bronwijzigingen, beleidswijzigingen en verlopen geldigheid leiden tot herbeoordeling. Een nieuwe import **zonder** relevante wijziging heropent een geaccepteerde afwijking niet. Bij een nieuw seizoen worden seizoensgebonden besluiten opnieuw beoordeeld; expliciet langer geldige besluiten blijven alleen bestaan als de actuele feiten en het beleid dat toelaten.

## 3. Verificatiepunten V-01–V-05: geaccepteerde uitwerking

| Punt | Vastgestelde implementatieafwijking | Vereiste correctie en regressie |
|---|---|---|
| **V-01 Voetbaldeelname** | Huidige import leidt spelen af uit ledenvelden en leest `Teamsoort` niet in. | Alle drie B-02-voorwaarden op dezelfde Teams-regel; meerdere teamregistraties, extra trainersrol, recreatieve registratie, ontbrekende/ongeldige waarden testen. |
| **V-02 Lidmaatschap** | `Afmelddatum` wordt genegeerd; dubbele regels worden gerangschikt op ogenschijnlijk actieve status. | B-03 toepassen op planningsdatum, conflicten signaleren en historie behouden; toekomstige afmelddatum, dag zelf, ontbrekende datum en dubbele regels testen. |
| **V-03 Functievrijstelling** | Commissies worden niet volledig meegenomen; legacy-lijst is geen CKC-configuratie; functienormalisatie kan betaald/onbetaald verwarren. | Beide bronnen combineren, oorspronkelijke namen bewaren, afzonderlijke zelf-/huishoudvrijstelling configureren, actuele bronstructuur respecteren en onbekende functies signaleren. |
| **V-04 Broederdienst** | De eerdere oudergebaseerde interpretatie is per 9 oktober 2026 vervallen. | Uitsluitend het volledige adres vergelijken; oudste-kindregel, toevoegingen, ontbrekende/conflicterende adressen en onafhankelijkheid van ouders/contactwaarde testen. |
| **V-05 Plannerbeslissingen/urenoverdracht** | A-vergelijking en E-formule bestaan; duurzame beslisstatus en volledige correctiecontrole ontbreken. | B-08/B-09/B-14 implementeren; volledige/gedeeltelijke overdracht, slechts één B-correctie, nog niet uitgevoerde correctie, geaccepteerde afwijking en herbeoordeling testen. |

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
3. **Taakplichtdashboard:** volledige relevante populatie raadpleegbaar, met DVK-afleiding, reden, Sportlink-A, controlestatus, datakwaliteit en plannerafhandeling. CKC-beleid (waaronder momenteel 10 uur) blijft configureerbaar.
4. **Portaal:** Ledendienst Planning is een module binnen DVK. De UI gebruikt begrijpelijke CKC-termen, toont ontwikkelstatus van andere modules en bevat geen beleidslogica in de Streamlit-presentatielaag.
5. **Bestaande regressies:** de geaccepteerde C-, W-, I- en R-cases blijven verplicht; waar deze herijking bewust een oudere prototype-aanname wijzigt, wordt de test expliciet aangepast en de reden vastgelegd.

**Belangrijk onderscheid:** duurzame taakplicht-/correctiebeslissingen uit B-14 zijn niet hetzelfde als tijdelijke planningshandelingen. De verplichting om B-14-besluiten te bewaren verandert FR-08 over tijdelijke planning niet.

## 6. Implementatie- en verificatiecontract

### 6.1 Bronadapters en canonieke feiten

- Maak een expliciete, geteste mapping van werkelijke Sportlink-kolommen naar canonieke velden; onbekende extra kolommen mogen import niet blokkeren.
- Verwerk lidmaatschapsstatus en afmelddatum volgens B-03; maak conflicten in dubbele ledenregels zichtbaar in plaats van één schijnbaar gunstige regel te kiezen.
- Verwerk Teams volgens B-02, inclusief `Teamsoort` en alle afzonderlijke teamregistraties.
- Bewaar Functies- en Commissies-registraties met originele naam, bron en eventuele begindatum; verwijder semantische samenvoegingen zoals `Trainer`.
- Verwerk het woonadres volgens B-05/B-06; ouders en contact-via-ouders zijn uitsluitend broncontext en geen taakplichtcriterium.
- Behoud herkomst en bronactualiteit, en verwerk geen overbodige financiële of identiteitsvelden.

### 6.2 Domeinlogica en plannerbeslissingen

- Bereken per peildatum en seizoen de taakplicht en verwachte A; scheid die van geregistreerde Sportlink-A.
- Maak de volledige CKC-functieclassificatie expliciete configuratie, inclusief het tijdelijke besluit over `Verzorger`.
- Ondersteun menselijke beslisstatus, reden, actor, geldigheid, herbeoordeling en controle na nieuwe import.
- Ondersteun uitsluitend na goedkeuring twee tegengestelde B-correcties voor urenoverdracht; controleer beide gezamenlijk na import. Wijzig C niet.
- Respecteer read-only Sportlink-integratie in v0.5; geen verborgen automatische correcties.

### 6.3 Minimale acceptatietests

- V-01–V-05-scenario's uit §3, met positieve, negatieve en ambigue bronvarianten.
- Peildatumgrenzen: 18e verjaardag, afmelddatum, commissiebegindatum, seizoensovergang en eventuele besluitvervaldatum.
- Huishoudvrijstelling: vrijwillig/onbetaald versus betaald/eretitel; volledig adres met toevoeging; ontbrekend of tegenstrijdig adres.
- Seizoensgebonden A: herberekening, afwijkingssignaal, handmatige correctie en bevestiging via nieuwe import; geen automatische urenoverdracht uit vorig seizoen.
- Correctie-workflow: openstaand, toegezegd, gedeeltelijk uitgevoerd, volledig bevestigd, bewust geaccepteerd en opnieuw te beoordelen.
- Bestaande v0.4- en v0.5-plannings-/no-showregressies blijven groen.

## 7. Resterende verificaties en expliciete acceptatiegrenzen

**Nog te verifiëren met echte bronbestanden:**

1. De daadwerkelijke **Teams-export**: aanwezigheid, naam en waarden van `Teamsoort`, `Teamrol` en `Spelend lid`, plus eventuele duplicaten of bronvarianten.
2. De daadwerkelijke **seizoensgebonden Vrijwilligers-/urenexport**: werkelijke veldnamen en betekenis van A/B/C/D/E, seizoensidentificatie en verificatie van twee tegengestelde B-correcties.
3. De volledige functie-/commissieclassificatie als machineleesbare CKC-configuratie, één-op-één getoetst aan de gecontroleerde oorspronkelijke exportwaarden. De functionele hoofdregels en de tijdelijke `Verzorger`-uitzondering zijn vastgesteld; de uiteindelijke configuratie en tests zijn nog niet opgeleverd.
4. De complete code-impactanalyse en uitvoering van de volledige regressiesuite, inclusief bestaande v0.5-planning en no-shows. De eerdere controle was gericht op de baselinecontracten en kernmodules; zij is geen bewijs dat ieder v0.5-bestand en iedere test reeds is doorgelicht.

**Functionele acceptatie** van dit document kan plaatsvinden voordat alle code is gewijzigd, mits de bovenstaande punten als expliciete technische acceptatievoorwaarden blijven staan. **Technische acceptatie** mag pas na uitvoering, controle van de vereiste echte bronstructuren en een aantoonbaar geslaagde regressiesuite worden uitgesproken.

## 8. Definitief functioneel acceptatiebesluit

CKC heeft op **2 oktober 2026** de herijkte functionele baseline B-01–B-14 en V-01–V-05 definitief functioneel geaccepteerd, inclusief de verduidelijkte bronsemantiek, de CKC-functieclassificatie en de tijdelijke behandeling van `Verzorger`. De technische verificatievoorwaarden van §7 blijven onverkort van kracht. Deze functionele acceptatie houdt geen technische oplevering of acceptatie van de v0.5-implementatie in.

## 9. Referenties

- `code/Prototype/BASELINE-v0.4.md` — geaccepteerde v0.4-baseline, 13 september 2026.
- `code/Prototype/FUNCTIONEEL-CONTRACT-v0.5-vervolg.md` — bestaande afspraken na Gate 10.
- `code/Prototype/dvk/real_data_import.py` en `code/Prototype/dvk/duty.py` op ontwikkelbranch `prototype-v0.5` — uitgangspunt voor de gecontroleerde implementatieafwijkingen.
- De in de herijkingsgesprekken inhoudelijk geaccepteerde besluiten B-01–B-14 en V-01–V-05.
