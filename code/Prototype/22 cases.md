# DVK Prototype — geconsolideerde set van 22 testcases

## Status en doel

Dit document is de inhoudelijke masterset voor de 22 testcases van het DVK Prototype.

De cases toetsen of het DVK bronfeiten op een reproduceerbare manier kan omzetten in afgeleide kwalificaties, beleidsgevolgen, signaleringen en waar nodig vervolgacties.

De set consolideert:

- de oorspronkelijke prototypecases;
- de aanvullende stresstestcases;
- de tijdens de beoordeling afgesproken correcties en uitbreidingen.

Waar de huidige prototypecode afwijkt van dit document, geldt dit document als de gewenste functionele uitkomst voor de volgende implementatieslag.

---

## Uniform formaat

Iedere case bevat:

- **Situatie** — de werkelijkheid die wordt getest;
- **Te toetsen** — de relevante logica of beleidsregel;
- **Verwachte uitkomst** — wat het DVK moet concluderen;
- **Actie / signalering** — wat het DVK eventueel moet doen of onder de aandacht moet brengen.

---

## C01 — Actief volwassen spelend lid met openstaande ledendiensturen

**Situatie**  
Een actief volwassen spelend lid heeft 4 van de verplichte 10 uur ledendienst voltooid.

**Te toetsen**  
Actief lidmaatschap en resterende ledendienstplicht.

**Verwachte uitkomst**  
- Actief CKC-lidmaatschap.
- Ledendienstplicht bedraagt 10 uur.
- 4 uur zijn voltooid.
- Nog 6 uur te vervullen.
- Het lid is zelf de uitvoerder van de verplichting.

**Actie / signalering**  
Signaleren dat nog 6 uur openstaat.

---

## C02 — Actief volwassen spelend lid heeft ledendienst voltooid

**Situatie**  
Een actief volwassen spelend lid heeft alle 10 verplichte uren voltooid.

**Te toetsen**  
Vaststellen dat aan de ledendienstplicht is voldaan.

**Verwachte uitkomst**  
- Actief CKC-lidmaatschap.
- 10 van 10 uur voltooid.
- Geen resterende ledendiensturen.

**Actie / signalering**  
Geen actie nodig.

---

## C03 — Minderjarig eerste kind: ouder/verzorger vervult ledendienst

**Situatie**  
Een minderjarig spelend lid is het kind waarop binnen het gezin de ledendienstplicht rust.

**Te toetsen**  
Onderscheid tussen degene op wie de verplichting administratief rust en degene die de dienst feitelijk uitvoert.

**Verwachte uitkomst**  
- Actief CKC-lidmaatschap van het kind.
- Ledendienstplicht bedraagt 10 uur.
- Een ouder/verzorger voert de ledendienst namens het minderjarige lid uit.
- De uren worden bij de verplichting van het kind geregistreerd.

**Actie / signalering**  
Openstaande uren bij het kind tonen, met ouder/verzorger als feitelijke uitvoerder waar bekend.

---

## C04 — Jonger minderjarig kind: geen tweede gezinsverplichting

**Situatie**  
Een gezin heeft meerdere minderjarige spelende kinderen. De ouderlijke ledendienstplicht is al gekoppeld aan een ouder minderjarig kind.

**Te toetsen**  
De ledendienstplicht van ouders geldt slechts eenmaal voor hun minderjarige kinderen en mag niet voor ieder kind afzonderlijk worden opgelegd.

**Verwachte uitkomst**  
- Het jongere kind is actief lid.
- Voor dit kind ontstaat geen tweede 10-uursverplichting.
- De vrijstelling volgt uit de ouder-kind-/broer-zusrelaties en de bestaande gezinsverplichting; zij is niet slechts een los handmatig label.

**Actie / signalering**  
Geen afzonderlijke urenplicht voor het jongere kind aanmaken.

---

## C05 — Spelend trainer met erkende vrijwilligersfunctie

**Situatie**  
Een actief spelend lid vervult tevens de functie van trainer.

**Te toetsen**  
Meervoudige hoedanigheden en vrijstelling op grond van een erkende vrijwilligersfunctie.

**Verwachte uitkomst**  
- Persoon is actief lid en spelend lid.
- Persoon vervult tevens de functie trainer.
- De erkende vrijwilligersfunctie geeft vrijstelling van ledendienst.

**Actie / signalering**  
Geen ledendiensturen opleggen zolang de vrijstellende functie geldig is.

---

## C06 — Commissielid: statutair lid en vrijwilligersfunctie

**Situatie**  
Een persoon is lid van een CKC-commissie.

**Te toetsen**  
Commissielidmaatschap als CKC-lidmaatschap en als erkend vrijwilligerswerk.

**Verwachte uitkomst**  
- Persoon is statutair CKC-lid.
- Commissielidmaatschap is een erkende vrijwilligersfunctie.
- De functie geeft vrijstelling van ledendienst.

**Actie / signalering**  
Geen ledendiensturen opleggen zolang de vrijstellende functie geldig is.

---

## C07 — Eenmalige barvrijwilliger/ouder is geen lid

**Situatie**  
Een ouder of andere persoon verricht incidenteel een bardienst, zonder commissielid of anderszins CKC-lid te zijn.

**Te toetsen**  
Vrijwilligerswerk leidt niet automatisch tot CKC-lidmaatschap.

**Verwachte uitkomst**  
- De persoon heeft uitsluitend op grond van deze incidentele inzet geen CKC-lidmaatschap.
- De persoon krijgt daardoor geen eigen ledendienstplicht.

**Actie / signalering**  
Geen lidmaatschap of eigen urenplicht afleiden uit de incidentele bardienst.

---

## C08 — Erelid is actief lid en vrijgesteld

**Situatie**  
Een persoon heeft de status erelid.

**Te toetsen**  
Lidmaatschapsstatus en ledendienstvrijstelling van ereleden.

**Verwachte uitkomst**  
- Erelid is actief CKC-lid.
- Erelid is vrijgesteld van ledendienst.

**Actie / signalering**  
Geen ledendiensturen opleggen.

---

## C09 — Recreatieve speler is lid en vrijgesteld van ledendienst

**Situatie**  
Een persoon speelt recreatief bij CKC, bijvoorbeeld bij OldStars, Vroege Vogels of Harry's Voetbalschool.

**Te toetsen**  
Onderscheid tussen statutair lidmaatschap, competitieve voetbaldeelname en CKC-beleid voor ledendienst.

**Verwachte uitkomst**  
- Recreatieve speler is statutair CKC-lid.
- Recreatieve deelname hoeft geen competitieve voetbaldeelname te zijn.
- Recreatieve spelers zijn vrijgesteld van ledendienstplicht.

**Actie / signalering**  
Geen ledendiensturen opleggen.

**Correctie ten opzichte van prototype v0.1**  
De huidige prototypecode legt de recreant nog een 10-uursverplichting op. Dat is niet de gewenste uitkomst en moet worden aangepast.

---

## C10 — Opgezegd lid heeft CKC-kleding nog niet ingeleverd

**Situatie**  
Een lid heeft het lidmaatschap beëindigd, maar één of meer uitgegeven CKC-kledingstukken zijn nog niet ingeleverd.

**Te toetsen**  
Samenhang tussen beëindigd lidmaatschap, kledingregistratie en vrijgave voor overschrijving.

**Verwachte uitkomst**  
- Lidmaatschap is beëindigd.
- Openstaande kleding wordt vastgesteld.
- De kledingkwestie vereist opvolging.
- Het lid wordt niet vrijgegeven voor overschrijving naar een andere club zolang de kleding niet is ingeleverd of financieel is afgehandeld.

**Actie / signalering**  
1. Stuur een e-mail aan het voormalige lid met het verzoek de ontbrekende kleding in te leveren of de restwaarde te betalen.
2. Meld in dezelfde e-mail dat geen vrijgave voor overschrijving plaatsvindt zolang de kledingkwestie niet is afgehandeld.
3. Houd de blokkade/signalering actief totdat inlevering of financiële afhandeling is geregistreerd.

---

## C11 — Beheerder CKC Kleding Beheer Tool mag rechten beheren en delegeren

**Situatie**  
Een persoon vervult de functie beheerder CKC Kleding Beheer Tool en heeft daarvoor door het DB gedelegeerde bevoegdheid.

**Te toetsen**  
Samenhang tussen bestuurlijke delegatie, functie, bevoegdheid en autorisatie.

**Verwachte uitkomst**  
- Beheerder heeft raadpleegrecht.
- Beheerder heeft updaterecht.
- Beheerder heeft recht om toegang te beheren.
- Beheerder mag binnen de gedelegeerde bevoegdheid raadpleeg- en updaterechten aan anderen toekennen.

**Actie / signalering**  
Geen afwijking zolang functie, delegatie en feitelijke rechten met elkaar overeenkomen.

---

## C12 — Niet-beheerder heeft toegangsbeheerrecht voor CKC Kleding Beheer Tool

**Situatie**  
Een persoon die niet de bevoegde beheerder van de CKC Kleding Beheer Tool is, beschikt over `manage_access`.

**Te toetsen**  
Een feitelijke autorisatie mag niet ruimer zijn dan de uit functie en delegatie voortvloeiende bevoegdheid.

**Verwachte uitkomst**  
- De persoon is niet bevoegd om toegangsrechten voor de tool te beheren.
- `manage_access` is daarom een ongewenste autorisatie.

**Actie / signalering**  
Blokkeren of als kritieke afwijking signaleren en het onterechte toegangsbeheerrecht laten intrekken.

---

## C13 — Huidige ledenadministrateur heeft correcte toegang

**Situatie**  
De huidige ledenadministrateur beschikt over de toegang die nodig is voor de ledenadministratie.

**Te toetsen**  
Positieve autorisatiecase: functie, bevoegdheid, gewenste autorisatie en feitelijke toegang zijn in overeenstemming.

**Verwachte uitkomst**  
- Actuele functievervulling ledenadministrateur is bekend.
- De benodigde bevoegdheden volgen uit de functie/delegatie.
- De aanwezige toegang komt overeen met de gewenste toegang.

**Actie / signalering**  
Geen afwijking; situatie is correct.

---

## C14 — Oud-bestuurslid heeft nog toegang

**Situatie**  
Een voormalig bestuurslid vervult de bestuursfunctie niet meer, maar heeft nog toegang tot een resource die bij de oude functie hoorde.

**Te toetsen**  
Autorisaties moeten de actuele functievervulling en bevoegdheid volgen.

**Verwachte uitkomst**  
- De oude bestuursfunctie is beëindigd.
- De bijbehorende bevoegdheid is niet meer geldig, tenzij een andere actuele functie of expliciete delegatie de toegang rechtvaardigt.
- De resterende toegang is zonder zo'n grond ongewenst.

**Actie / signalering**  
Onterechte toegang signaleren en laten intrekken.

---

## C15 — Nieuwe functionaris mist benodigde toegang

**Situatie**  
Een persoon is recent in een functie benoemd, maar beschikt nog niet over de voor die functie benodigde toegang.

**Te toetsen**  
Een geldige functievervulling moet leiden tot de juiste gewenste autorisaties.

**Verwachte uitkomst**  
- Actuele functie en bevoegdheid zijn bekend.
- Benodigde autorisatie kan worden afgeleid.
- Feitelijke toegang ontbreekt.

**Actie / signalering**  
Ontbrekende toegang signaleren en laten toekennen door de bevoegde beheerder.

---

## C16 — Toegang zonder bekende functie of andere bevoegdheidsgrond

**Situatie**  
Een persoon heeft toegang tot een CKC-resource, maar het DVK kent geen actuele functie of andere geldige delegatie die deze toegang verklaart.

**Te toetsen**  
Feitelijke toegang moet herleidbaar zijn tot een geldige bevoegdheidsgrond.

**Verwachte uitkomst**  
- Toegang is aanwezig.
- Er is geen bekende actuele bevoegdheidsgrond.
- Het DVK mag niet automatisch aannemen waarom de toegang bestaat.

**Actie / signalering**  
Onverklaarde autorisatie signaleren voor onderzoek; indien geen geldige grond blijkt te bestaan, toegang intrekken.

---

## C17 — Persoon vervult twee functies

**Situatie**  
Een persoon vervult gelijktijdig twee CKC-functies.

**Te toetsen**  
Persoon en functie zijn afzonderlijke begrippen; meerdere functievervullingen kunnen gelijktijdig geldig zijn.

**Verwachte uitkomst**  
- Beide functies worden afzonderlijk geregistreerd.
- Bevoegdheden en gewenste autorisaties worden per functie bepaald.
- De uiteindelijke toegangsbehoefte kan de combinatie van beide functies omvatten.
- Het beëindigen van één functie mag niet automatisch rechten verwijderen die nog uit de andere functie voortvloeien.

**Actie / signalering**  
Alleen afwijkingen tussen de gecombineerde geldige bevoegdheden en de feitelijke toegang signaleren.

---

## C18 — Trainer zonder VOG

**Situatie**  
Een persoon vervult de functie trainer, maar er is geen geldige aangeleverde VOG geregistreerd.

**Te toetsen**  
CKC-beleid vereist dat alle trainers een VOG hebben aangeleverd.

**Verwachte uitkomst**  
- Functie trainer is bekend.
- Vereiste VOG ontbreekt of is niet als geldig geregistreerd.
- De functie zelf wordt niet ontkend; er is een beleidsafwijking.

**Actie / signalering**  
Ontbrekende VOG signaleren en opvolging starten volgens het CKC-proces voor VOG's.

---

## C19 — Barteamlid heeft update-toegang tot kassasysteem

**Situatie**  
Een lid van het barteam blijkt update-toegang tot het digitale kassasysteem te hebben.

**Te toetsen**  
Het hebben van een functie betekent niet automatisch dat iedere handeling op een resource is toegestaan. Raadplegen, gebruiken, updaten en beheren zijn afzonderlijke autorisaties.

**Verwachte uitkomst**  
- Functie barteamlid is bekend.
- Update-toegang tot het kassasysteem wordt afzonderlijk beoordeeld.
- Alleen als deze bevoegdheid expliciet uit functie/delegatie volgt, is de toegang gerechtvaardigd.

**Actie / signalering**  
Als geen geldige bevoegdheidsgrond voor update-toegang bestaat: afwijking signaleren en updaterecht laten intrekken.

---

## C20 — Jeugdlid zonder ouder/verzorger

**Situatie**  
Een minderjarig CKC-lid heeft in de beschikbare gegevens geen geregistreerde ouder-/verzorgerrelatie.

**Te toetsen**  
Een minderjarig lid moet gekoppeld kunnen worden aan een ouder/verzorger voor relevante communicatie, verantwoordelijkheid en onder meer ledendienstuitvoering.

**Verwachte uitkomst**  
- Minderjarigheid wordt vastgesteld.
- Er ontbreekt een noodzakelijke ouder-/verzorgerrelatie.
- Het DVK verzint of veronderstelt geen ouder/verzorger.

**Actie / signalering**  
Ontbrekende ouder-/verzorgerrelatie signaleren voor aanvulling door de ledenadministratie.

---

## C21 — Lid met mobiel nummer van 9 cijfers

**Situatie**  
Bij een lid is een mobiel telefoonnummer geregistreerd dat slechts 9 cijfers bevat.

**Te toetsen**  
Validatie van het mobiele telefoonnummer.

**Verwachte uitkomst**  
- Het nummer voldoet niet aan de afgesproken validatieregel voor een volledig mobiel nummer.
- Het DVK behandelt het nummer niet als betrouwbaar contactgegeven.

**Actie / signalering**  
Validatiefout signaleren en correctie van het mobiele nummer vragen.

---

## C22 — Ouder met twee kinderen op twee verschillende adressen

**Situatie**  
Eén ouder/verzorger is gekoppeld aan twee minderjarige kinderen die op verschillende woonadressen staan geregistreerd.

**Te toetsen**  
Het DVK moet complexe maar legitieme gezinssituaties ondersteunen. Een afwijkend woonadres is geen bewijs dat een ouder-kindrelatie onjuist is.

**Verwachte uitkomst**  
- Beide ouder-kindrelaties kunnen geldig zijn.
- Verschillende adressen leiden niet automatisch tot een fout of blokkade.
- Het DVK baseert gezins- en ledendienstlogica primair op expliciete ouder-kindrelaties en relevante lidmaatschaps-/leeftijdsfeiten, niet uitsluitend op een gelijk woonadres.
- De situatie mag als opvallend worden herkend zonder er een onterechte conclusie aan te verbinden.

**Actie / signalering**  
Eventueel tonen als controleerbare bijzonderheid, maar niet automatisch afkeuren of relaties wijzigen.

---

## Belangrijkste wijzigingen ten opzichte van prototype v0.1

1. **C04** — broederdienst wordt inhoudelijk gezien als afleiding uit gezinsrelaties en bestaande ledendienstplicht, niet als zelfstandig handmatig contextfeit.
2. **C09** — recreatieve spelers zijn vrijgesteld van ledendienst; de huidige prototypecode moet hierop worden aangepast.
3. **C10** — openstaande kleding leidt naast signalering tot concrete opvolging: e-mail, keuze tussen inlevering/restwaarde en blokkade van vrijgave voor overschrijving totdat de kwestie is afgehandeld.
4. **C12** — de bestaande negatieve guardrail voor onbevoegd toegangsbeheer is als volwaardige testcase in de set opgenomen.
5. **C13–C19** — governance en autorisatie worden expliciet getoetst vanuit het onderscheid tussen functie, bevoegdheid, gewenste autorisatie en feitelijke toegang.
6. **C20–C22** — datakwaliteit en relaties worden getoetst zonder onterechte aannames: ontbrekende ouderrelatie, ongeldig mobiel nummer en een legitieme gezinssituatie met verschillende adressen.

---

## Implementatieprincipe

De testcases beschrijven de gewenste functionele werkelijkheid. Implementatie moet waar mogelijk het volgende patroon volgen:

`bronfeit -> canoniek object -> afgeleide kwalificatie -> beleidsgevolg -> besluit/signalering -> eventuele vervolgactie -> geautomatiseerde test`

Een testcase is pas volledig geïmplementeerd wanneer niet alleen de verwachte conclusie, maar ook de relevante signalering en afgesproken vervolgactie reproduceerbaar kan worden getest.
