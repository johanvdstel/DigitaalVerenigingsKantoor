# DVK v0.5 — Minimale Sportlink-exportselecties

**Status:** werkafspraak voor de werkstroom Ledendiensten & Vrijwilligersbeleid  
**Datum:** 6 oktober 2026  
**Doel:** per handmatige Sportlink-export vastleggen welke velden DVK minimaal nodig heeft.

## 1. Algemene regels

1. **Relatiecode is de technische sleutel.** Naamvelden worden nooit gebruikt als unieke identificatie of als vervanging van de relatiecode.
2. **Naam wordt meegenomen waar beschikbaar.** Dit verhoogt de leesbaarheid en maakt menselijke controle van CSV-bestanden eenvoudiger.
3. **Dataminimalisatie is het uitgangspunt.** Alleen velden met een concreet functioneel doel voor deze DVK-werkstroom worden geselecteerd.
4. **Overbodige persoonsgegevens worden niet gedownload.** Denk met name aan bankgegevens, telefoon- en e-mailgegevens, nationaliteit en andere ledenvelden die voor de betreffende bronroute niet nodig zijn.
5. **Bronactualiteit en periode blijven aparte context.** Ophaaldatum en, waar relevant, seizoen/periode worden bij de import vastgelegd; zij hoeven niet als extra persoonskolom in iedere exportregel aanwezig te zijn.
6. **Onbekende extra kolommen mogen een import niet inhoudelijk veranderen.** De onderstaande selectie is het functionele broncontract.
7. **Naam voor leesbaarheid, relatiecode voor identiteit.**

## 2. Leden

### Minimale selectie

- `Rel. code`
- `Naam`
- `Geb.dat.`
- `Lidstatus`
- `Afmelddatum`
- `Lidsoort`
- `Status lidmaatschap`
- `Straatnaam`
- `Huisnummer`
- `Toevoeging`
- `Postcode`
- `Plaats`
- `Contact via ouder/verzorger`
- `Naam ouder/verzorger 1`
- `Naam ouder/verzorger 2`

### Gebruik

Deze export levert de bronfeiten voor identiteit, leeftijd, actueel lidmaatschap, huishouden en de gezinsregel voor minderjarigen.

Voor huishoudafleiding is de canonieke adresidentiteit:

`Postcode + Huisnummer + Toevoeging`

`Straatnaam` en `Plaats` blijven beschikbaar als leesbare broncontext, maar bepalen het huishouden niet zelfstandig.

Oudernaamvelden worden uitsluitend als bronregistratie gebruikt. DVK maakt daar geen fictieve ouderpersonen of relatiecodes van.

## 3. Functies

### Minimale selectie

- `Rel. code`
- `Naam`
- `Functie`

### Gebruik

De oorspronkelijke Sportlink-functienaam wordt gekoppeld aan de expliciete CKC-functieclassificatie.

De gecontroleerde Functies-export bevat geen bruikbare begin- of einddatumvelden. DVK eist daarom voor deze bron geen fictieve geldigheidsvelden.

## 4. Commissies

### Minimale selectie

- `Rel. code`
- `Naam`
- `Commissie`
- `Functie`
- `Begindatum`
- `Einddatum`

### Gebruik

De combinatie `Commissie + Functie` blijft intact en wordt aan de CKC-classificatie gekoppeld.

`Begindatum` is in de gecontroleerde export beschikbaar. `Einddatum` wordt eveneens geselecteerd, ook wanneer deze in de huidige bronregels leeg is, zodat een later door Sportlink aangeleverde einddatum als bronfeit kan worden verwerkt.

## 5. Teams

### Minimale selectie

- `Rel. code`
- `Naam`
- `Team`
- `Teamsoort`
- `Teamrol`
- `Spelend lid`

### Gebruik

Volgens B-02 is deelname aan een bondsteam alleen bewezen wanneer één en dezelfde actuele Teams-regel voldoet aan:

- `Teamsoort = Bond`
- `Teamrol = Teamspeler`
- `Spelend lid = Ja`

`Team` wordt meegenomen voor menselijke herkenbaarheid en voor de bredere planningscontext.

De in de gecontroleerde export aanwezige `Begindatum team` en `Einddatum team` zijn voor de huidige taakplichtcontrole niet nodig en behoren daarom niet tot deze minimale selectie.

### Technische aandacht

De huidige v0.5-importer vereist technisch nog het Teams-veld `Functie`, terwijl dit voor de geaccepteerde B-02-regel niet nodig is. De implementatie moet vóór gebruik van deze minimale downloadselectie hiermee in lijn worden gebracht; het veld wordt niet om die technische erfenis alsnog functioneel verplicht gemaakt.

## 6. Overzicht per periode

### Minimale selectie

- `Relatiecode`
- `Volledige naam`
- `Verplichte punten`
- `Gecorrigeerde punten`
- `Voldaan`
- `Nog ingedeeld`
- `Niet ingedeeld`

### Gebruik

De urenpositie wordt geïnterpreteerd als:

- **A — Verplichte punten:** door de Vrijwilligerscommissie vastgestelde en handmatig in Sportlink geregistreerde verplichting;
- **B — Gecorrigeerde punten:** handmatige correctie;
- **C — Voldaan:** reeds uitgevoerde uren/punten;
- **D — Nog ingedeeld:** reeds ingeplande maar nog niet uitgevoerde uren/punten;
- **E — Niet ingedeeld:** resterende positie.

Controleformule:

`E = A - B - C - D`

Een positieve B verlaagt E. Een negatieve correcte E is toegestaan.

`Volledige naam` is alleen leesbaarheids- en controlecontext; de technische koppeling gebeurt uitsluitend via `Relatiecode`.

De periode/seizoenscontext van de export wordt afzonderlijk bij import vastgelegd.

## 7. Samenvatting

| Export | Minimale velden |
| --- | --- |
| **Leden** | `Rel. code`, `Naam`, `Geb.dat.`, `Lidstatus`, `Afmelddatum`, `Lidsoort`, `Status lidmaatschap`, `Straatnaam`, `Huisnummer`, `Toevoeging`, `Postcode`, `Plaats`, `Contact via ouder/verzorger`, `Naam ouder/verzorger 1`, `Naam ouder/verzorger 2` |
| **Functies** | `Rel. code`, `Naam`, `Functie` |
| **Commissies** | `Rel. code`, `Naam`, `Commissie`, `Functie`, `Begindatum`, `Einddatum` |
| **Teams** | `Rel. code`, `Naam`, `Team`, `Teamsoort`, `Teamrol`, `Spelend lid` |
| **Overzicht per periode** | `Relatiecode`, `Volledige naam`, `Verplichte punten`, `Gecorrigeerde punten`, `Voldaan`, `Nog ingedeeld`, `Niet ingedeeld` |

## 8. Beheerregel

Nieuwe Sportlink-velden worden niet automatisch aan een DVK-export toegevoegd. Uitbreiding van een minimale selectie vereist een aantoonbaar functioneel doel en wordt expliciet in deze broninstructie vastgelegd.
