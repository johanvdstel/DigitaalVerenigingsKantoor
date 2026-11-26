# v0.5 stap 2 ronde 1 — functies en commissies

Deze ronde implementeert de door CKC goedgekeurde classificatie als afzonderlijke afleiding. De bestaande `duty.py`, `DutyPolicy`, ledendienstuitkomsten en historische fixtures zijn niet gewijzigd. Ronde 2 en functionele acceptatie blijven afzonderlijke stappen.

## Baseline en broncontrole

- Start: `origin/prototype-v0.5-step2-canoniek-functies`, commit `1e921208773d19d7e956c894dae4255a580b769d`; beide GitHub-startbranches zijn op deze commit gecontroleerd.
- Werkbranch: `codex/v05-step2-ronde1-functieclassificatie`.
- Johan heeft expliciet toegestaan de remote ontwikkelbranch te gebruiken; bestaande lokale branches blijven behouden.
- Gezaghebbende bron: `DVK_stap2_CKC_functieclassificatie_definitief_concept.xlsx`, SHA256 `f713363b8eee1cf417f13431f5bfb56caff5263997715abb4ce85e87dc4c1583`.
- Alle vier werkbladen zijn gelezen. Gecontroleerd: 27 unieke functietitels, 62 unieke commissie/functiecombinaties, aggregaten 126 en 145 registraties, unieke sleutels en consistente categorie/rechten. De iteratieopdracht verklaart de classificatie goedgekeurd en vervangt de oude akkoordlabels in de werkbladen.
- De Excel-sleutel is exact `Bestuur / CKC 100`. `Bestuur / CKC100` zonder spatie wordt niet inhoudelijk gelijkgemaakt.
- Het Excel-bestand en oorspronkelijke Sportlink-persoonsgegevens worden niet opgenomen in Git.

## Representatie en configuratie

`RoleAssignment` blijft het bestaande functiebronmodel. Het is achterwaarts compatibel aangevuld met de oorspronkelijke titel en gekoppelde `Provenance`. `CommitteeMembership` behoudt commissie en functie, begindatum en nu ook einddatum en gekoppelde provenance. De read-only adapter leest optionele `Begindatum`/`Einddatum`; ontbrekende datums blijven `None`, ongeldige datums worden expliciet gesignaleerd volgens de bestaande importaanpak. Er wordt geen actieve status of ontbrekende datum uit een classificatie afgeleid.

`dvk/configuration/function_classification.csv` bevat de 27 Excel-functies en 62 Excel-combinaties, plus twee expliciet beleidsmatige functie-ingangen voor `Erelid` en `Lid van verdienste`. Die extra twee worden niet meegeteld als aangetroffen Excel-titels. Betaalde functies en eretitels geven uitsluitend persoonlijk recht. Er zijn geen persoonsgebonden uitzonderingen voor `Verzorger`. Alle aangetroffen overige registraties zijn onbetaald en geven beide rechten. Er zijn in de goedgekeurde inventaris geen concrete niet-vrijstellende registraties; de component ondersteunt die categorie met twee negatieve rechten en onderscheidt haar van onbekend.

De configuratie bevat oorspronkelijke sleutels, categorie en rechten. Alleen witruimte wordt opgeschoond bij opzoeken; hoofdletters, leestekens en verschillende trainerstitels blijven betekenisvol. De configuratie wordt als package-data meegenomen. Regelversie: `ckc-v05-step2-round1`.

`FunctionClassifier.classify` geeft een `ClassifiedFunction` terug met het ongewijzigde bronobject, configuratieregel, regelversie en provenance-soort `DERIVED`. De regel is configuratie, het gekoppelde bronobject blijft `SOURCE_FACT`. `classify_many` behoudt alle bronregistraties, combineert rechten per persoon met logische OR en bundelt onbekenden per unieke bronsoort/commissie/titel met registratieaantal. Overlap tussen beide bronnen veroorzaakt geen waarschuwing. Bekend met twee negatieve rechten blijft onderscheiden van onbekend.

`RealDataImportResult.function_classification` maakt deze afleiding apart raadpleegbaar, inclusief signalen. De afleiding wordt niet gevoed aan de bestaande ledendienstbeslislogica of UI. De persoonlijke booleans zijn classificatierechten, geen uitgevoerde vrijstellingsbesluiten. Het huishoudrecht betekent dat een functionaris huishoudvrijstelling kan onderbouwen; er wordt nog geen huishouden gevormd of vrijstelling aan medebewoners toegekend. Daardoor worden nu ook geen meerdere huishoudvrijstellingen aangemaakt.

## Voorbereiding en aandachtspunten ronde 2

`Person.address` blijft intact voor bestaande regressies. Optionele `postal_code`, `house_number`, `house_number_addition` en twee afzonderlijke `parent_names` zijn toegevoegd. Een ontbrekende toevoeging is niet automatisch bewijs dat het adres volledig is. De twee oudernaamposities bewaren broninformatie en zijn geen relatiecodes. `PersonRelationship` blijft geschikt voor werkelijk geïdentificeerde relaties; namen worden niet omgezet naar fictieve personen of relaties.

De beschikbare baseline bevestigt afzonderlijke adres- en oudernaamvelden, maar geeft geen volledige exacte Sportlink-kolommapping. Die mapping is daarom niet gegokt. Ronde 2 moet de exacte headers en bronvolledigheid vaststellen, import met provenance toevoegen en conflicten tussen dubbele ledenregels behandelen. De bestaande ledenconsolidatie bewaart deze aanvullende brongegevens nu nog niet. De nieuwe velden worden niet automatisch gevuld vanuit het vrije legacy-adres.

Verder blijft voor ronde 2: B-05 toepassen op betrouwbare volledige adressen en één huishoudvrijstelling per huishouden; B-06/B-07 rechtstreeks vergelijken met volledige ouderregistraties/adressen; geldigheid op peildatum en exportactualiteit meenemen bij beleidsbeslissingen; de nieuwe rechten expliciet aansluiten op de ledendienstlogica. Er wordt in ronde 1 geen eigen interpretatie van einddatumgrenzen ingevoerd.

## Regressiebescherming

`testdata/v05_function_classification/approved_keys.json` is de onafhankelijke transcriptie van uitsluitend de goedgekeurde 27/62 sleutels, zonder persoonsgegevens. Nieuwe parametrische tests toetsen iedere sleutel en diens categorie/rechten, uitzonderingen, overlap, onbekenden met aantallen, bekende niet-vrijstellende waarden, provenance, optionele datums, backwards compatibility en ongewijzigde ledendienstuitkomst bij dezelfde import.

Uitgangssituatie: 51 relevante bestaande tests geslaagd. De eerste aanroep via het losse pytest-script miste de lokale package-import; `python -m pytest` vanuit `code/Prototype` werkt. Na de model/configuratie-uitbreiding slaagden alle 287 bestaande tests. De gerichte suite met nieuwe regressies telt 155 geslaagde tests (104 nieuw, 51 bestaand). De volledige eindregressie slaagt met 391 tests; `git diff --check` is schoon. CI wordt na het openen van de PR gecontroleerd en in de opleveringsrapportage vermeld.
