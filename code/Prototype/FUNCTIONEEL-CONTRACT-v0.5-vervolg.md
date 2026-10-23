# DVK Prototype v0.5 — functioneel contract na Gate 10

**Status:** functioneel vastgesteld voor vervolgontwikkeling v0.5  
**Baseline voor impactanalyse:** `362c6a817ea00a13685a07c13ade71ed14c1eda4`  
**Scope:** Ledendienst Planning (A/B), Taakplichtcontrole (E) en DVK-portaal/modulaire UI (F)

Dit document legt de functionele afspraken vast. De technische impactanalyse en implementatie volgen hieruit en ontwerpen dit contract niet opnieuw.

## A — Planning en Sportlink

### FR-01 — Sportlink is bronhouder van de feitelijke inroostering
Sportlink is de gezaghebbende bron voor de feitelijke actuele inroostering van ledendiensten. DVK leest en gebruikt deze gegevens, maar schrijft in v0.5 geen inroosteringen naar Sportlink. Een DVK-inroostering vóór verwerking in Sportlink is een tijdelijke planningshandeling.

### FR-02 — DVK ondersteunt een tijdelijke planningswerkvoorraad
De Vrijwilligerscommissie gebruikt DVK om openstaande diensten te vullen met geschikte kandidaten, in het bijzonder leden met openstaande verplichte uren. Een in DVK bevestigde kandidaat vormt een tijdelijke DVK-planningspositie. Die telt direct mee in bezetting en beschikbaarheid en blijft bestaan totdat zij wordt teruggedraaid of door een succesvolle Sportlink-synchronisatie wordt vervangen. Zij is geen zelfstandig duurzaam CKC-administratief feit.

### FR-03 — Lokale DVK-inroostering beïnvloedt onmiddellijk de openstaande bezetting
De getoonde bezetting wordt tijdens een planningscyclus bepaald uit de Sportlink-bronbezetting plus actieve tijdelijke DVK-inroosteringen. Een lokale inroostering verlaagt direct de open minimumbehoefte en resterende capaciteit van de betreffende dienst. Minimumbezetting en maximumcapaciteit blijven afzonderlijke begrippen; na bereiken van het minimum kan tot het maximum worden gepland.

### FR-04 — Een inroostering beïnvloedt beschikbaarheid voor andere diensten
Iedere actieve tijdelijke DVK-inroostering wordt meegenomen bij kandidaatstelling voor volgende diensten:
- op een andere dag kan de persoon normaal voor een passende dienst worden aangeboden;
- op dezelfde dag zonder tijdsoverlap kan de persoon alleen als nood-/uitwijkkandidaat in aanmerking komen;
- op dezelfde dag met tijdsoverlap is de persoon niet beschikbaar;
- voor exact dezelfde dienst kan de persoon niet tweemaal worden ingepland.
Na terugdraaien conform FR-05 vervallen de hierdoor ontstane beperkingen.

### FR-05 — Een tijdelijke DVK-inroostering kan vóór synchronisatie worden teruggedraaid
Zolang de tijdelijke planning nog niet door een succesvolle Sportlink-synchronisatie is vervangen, kan de planner een lokale inroostering ongedaan maken. Daardoor wordt bezettingsruimte hersteld en wordt de persoon opnieuw beschikbaar volgens FR-04. Hiervoor is geen duurzame AssignmentRevocation/audithistorie vereist.

### FR-06 — Verwerking in Sportlink blijft in v0.5 een menselijke handeling
De planner verwerkt de gewenste DVK-planning handmatig in Sportlink via de beschikbare Sportlink-functionaliteit. DVK voert geen automatische Sportlink-mutaties uit.

### FR-07 — Succesvolle Sportlink-synchronisatie vormt een harde grens
Na een bewuste en succesvolle synchronisatie geldt de nieuw opgehaalde Sportlink-positie onvoorwaardelijk als actuele werkelijkheid. Tijdelijke lokale inroosteringen worden niet individueel met Sportlink gereconcilieerd en vormen daarna geen concurrerende waarheid. Bij mislukte synchronisatie blijft de bestaande tijdelijke DVK-planningspositie intact.

### FR-08 — Tijdelijke planningshistorie hoeft niet duurzaam te worden bewaard
DVK onderscheidt bronfeiten, tijdelijke DVK-planningsinformatie en duurzame DVK-feiten. Selecteren, tijdelijk inroosteren en terugdraaien zijn werkvoorraad en hoeven na succesvolle synchronisatie geen permanente functionele historie te vormen. Technische logging voor diagnose staat hiervan los.

## B — No-showadministratie

### FR-09 — Een no-show is altijd gekoppeld aan een feitelijke Sportlink-inroostering
De bron van een no-show is altijd een concrete feitelijke Sportlink-inroostering, ongeacht of die ontstond door zelfinschrijving, directe handmatige Sportlink-planning of een eerder DVK-voorstel. Een uitsluitend tijdelijke DVK-inroostering kan geen no-show krijgen.

### FR-10 — DVK bewaart een no-show als zelfstandig duurzaam feit
Omdat Sportlink geen duurzaam no-showfeit biedt waarmee CKC de situatie later betrouwbaar kan reconstrueren, bewaart DVK de no-show zelf. Bij registratie wordt voldoende identiteit, dienstcontext en bron/provenance van de Sportlink-inroostering vastgelegd om het feit later zelfstandig te begrijpen. De technische sleutel en snapshotstructuur worden in de impactanalyse bepaald. Per concrete feitelijke Sportlink-inroostering kan maximaal één oorspronkelijke no-show worden geregistreerd.

### FR-11 — Gate 10 blijft gelden voor intrekking en actuele sanctiestatus
De geaccepteerde Gate-10-semantiek blijft: een NoShowEvent is immutable; een intrekking is een afzonderlijk duurzaam NoShowRevocation-feit met verplichte toelichting, actor en tijdstip. Actuele teller en sanctiestatus worden afgeleid uit geldige no-shows in het seizoen; ingetrokken no-shows tellen niet mee. De bronwijziging van DVK-assignment naar Sportlink-inroostering verandert deze semantiek niet.

### FR-12 — Een no-show creëert een eenvoudige Sportlink-correctiewerkvoorraad
Na no-showregistratie staat de handmatige vervolgactie `Sportlink-correctie: openstaand`. Na handmatige correctie in Sportlink kan de bevoegde gebruiker deze als `afgehandeld` markeren. DVK voert de correctie niet uit. Voor v0.5 is geen afzonderlijk reden-, toelichtings- of besluitvormingsproces nodig.

## E — Taakplichtcontrole

### E-01 — DVK leidt de verwachte ledendienstplicht zelfstandig af
DVK bepaalt uit bronfeiten en CKC-beleid of ledendienstplicht geldt en welke verplichte uren worden verwacht. Sportlink geregistreerde verplichte uren zijn bronfeit; DVK verwachte verplichte uren zijn afleiding. Deze worden niet met elkaar vereenzelvigd.

### E-02 — Vrijstelling is een afleiding
Als geldende feiten en CKC-regels vrijstelling opleveren, verwacht DVK 0 verplichte uren. Als geen vrijstellingsgrond geldt en het lid taakplichtig is, geldt de beleidsmatig vastgestelde urenverplichting; momenteel 10 uur. Dit aantal is beleid/configuratie, geen intrinsieke persoons- of domeinconstante.

### E-03 — Vrijstellende functies zijn CKC-configuratie
Het principe dat bepaalde functies/rollen vrijstelling geven behoort tot de ledendienstlogica; de concrete lijst is CKC-configuratie. De huidige prototype-lijst is niet automatisch de definitieve formele CKC-lijst. Bij live Sportlink-data wordt de werkelijk gebruikte functieset expliciet geclassificeerd. Prototype- en regressietests mogen tot die tijd een gecontroleerde testconfiguratie gebruiken.

### E-04 — Vrijstellingsgronden blijven afzonderlijk verklaarbaar
DVK toont niet alleen vrijgesteld/niet-vrijgesteld maar ook de grond. Onderscheid moet mogelijk blijven tussen onder meer eigen CKC-erkende functie/rol, recreatieve deelname, erelidmaatschap, de gezinsregel voor minderjarigen en de huishoudregel: **alle leden van een huishouden op hetzelfde adres zijn vrijgesteld wanneer een ander lid van dat huishouden op hetzelfde adres een CKC-erkende vrijstellende functie vervult**. Deze vrijstelling berust op het gedeelde huishouden/adres als relevant bronfeit en vereist geen familiaire relatie tussen de betrokken personen. De beleidsgrond is dat het vervullen van een erkende vrijwilligersfunctie al beslag legt op het huishouden; vanuit het ledendienstbeleid wordt datzelfde huishouden daarom niet met een aanvullende verplichting belast. Eventuele later vastgestelde vrijstellingsgronden blijven eveneens afzonderlijk verklaarbaar. Ontbrekende of ambigue bronfeiten worden niet gegokt.

### E-05 — DVK vergelijkt afleiding met Sportlink-registratie
Per relevant lid vergelijkt DVK verwachte verplichte uren met de in Sportlink geregistreerde verplichte uren. De controlestatus onderscheidt ten minste overeenkomst, afwijking en niet betrouwbaar beoordeelbaar. Een afwijking is een signaal voor menselijke beoordeling, geen automatische correctie.

### E-06 — De UI bevat een taakplichtcontroledashboard
Binnen Ledendienst Planning komt een dashboard voor de Vrijwilligerscommissie. Per relevante regel zijn in menselijke termen ten minste lid, DVK-afleiding, reden/grond, Sportlink-registratie en controlestatus zichtbaar. De volledige relevante populatie is raadpleegbaar; afwijkingen en datakwaliteitsproblemen zijn eenvoudig afzonderlijk zichtbaar.

### E-07 — DVK verklaart zijn afleiding
De gebruiker kan begrijpen waarom DVK een urenverplichting verwacht, bijvoorbeeld vrijstelling wegens functie/gezinsregel of taakplicht omdat geen vrijstellingsgrond is gevonden. Bij onvoldoende brongegevens toont DVK geen schijnzekerheid.

### E-08 — Taakplichtcontrole is read-only ten opzichte van Sportlink
De keten is: Sportlink-bronfeiten → DVK-afleiding → vergelijking → signalering → menselijke beoordeling → eventuele handmatige Sportlink-correctie. Een latere succesvolle synchronisatie controleert opnieuw tegen de actuele Sportlink-bronpositie.

## F — DVK-portaal en modulaire UI

### F-01 — DVK is een portaal met meerdere functionele onderdelen
Het Digitaal Verenigingskantoor is breder dan Ledendienst Planning. De UI ontwikkelt zich tot één herkenbaar DVK-portaal; Ledendienst Planning is één module en niet synoniem met DVK.

### F-02 — Functionaliteit wordt gegroepeerd in herkenbare modules
Vooralsnog worden onderkend: **Ledendienst Planning** (v0.5 in ontwikkeling), **Rooster Generator** (operationeel buiten DVK, kandidaat voor integratie), **Ledenadministratie**, **Wedstrijdsecretariaat**, **Kledingadministratie**, **Toegangsbeheer** en **Tabelonderhoud** (toekomstig). De indeling is uitbreidbaar en niet uitputtend.

### F-03 — De UI maakt de ontwikkelstatus van modules expliciet
Het portaal mag toekomstige modules tonen maar niet suggereren dat ze beschikbaar zijn. Voor v0.5 hoeft alleen Ledendienst Planning daadwerkelijk binnen het portaal functioneel beschikbaar te zijn. De Rooster Generator mag als operationeel maar nog niet geïntegreerd worden aangeduid.

### F-04 — Een module kan meerdere samenhangende functies bevatten
Binnen Ledendienst Planning horen onder meer taakplichtcontrole, openstaande uren, kandidaatselectie, planning, tijdelijke inroostering, ondersteuning van handmatige Sportlink-verwerking en no-showopvolging. Taakplichtcontrole is dus geen aparte hoofdmodule.

### F-05 — Portaalnavigatie en modulelogica blijven gescheiden
Het portaal verzorgt toegang en navigatie. Beleids- en businessregels blijven in domein/applicatielogica en niet in portaal-, Streamlit- of navigatielogica. De functionele DVK-logica moet later via een andere UI aangeboden kunnen worden.

### F-06 — Het portaal gebruikt herkenbare CKC-termen
Personen, diensten, functies, statussen en handelingen worden in menselijke CKC-termen getoond. Technische identifiers zijn geen primaire gebruikersidentificatie wanneer een menselijke aanduiding beschikbaar is.

### F-07 — Modules delen canonieke bronbegrippen zonder onnodige duplicatie
Waar modules dezelfde personen, lidmaatschappen, teams, functies, wedstrijden of andere bronfeiten gebruiken, behouden deze een gedeelde canonieke betekenis. Modules mogen daarop eigen afleidingen en processen toepassen.

### F-08 — Modulaire groei verzwaart v0.5 niet onnodig
V0.5 vereist geen generiek portalframework. Een eenvoudige navigatiestructuur volstaat om DVK als portaal herkenbaar te maken, modules en statussen zichtbaar te maken en Ledendienst Planning toegankelijk te houden. Verdere technische portalarchitectuur volgt pas wanneer toekomstige modules werkelijk worden geïntegreerd.

## Overkoepelende functionele hoofdregel

> **Sportlink blijft bronhouder van feiten die Sportlink daadwerkelijk beheert. DVK leidt daaruit CKC-betekenis, controles en planningsvoorstellen af. Tijdelijke DVK-planningshandelingen zijn werkvoorraad; alleen informatie die niet betrouwbaar uit de gezaghebbende bron kan worden gereconstrueerd en duurzaam relevant blijft voor het CKC-proces, wordt als zelfstandig duurzaam DVK-feit bewaard.**
