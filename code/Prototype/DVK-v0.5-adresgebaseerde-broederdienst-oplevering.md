# DVK v0.5 — Stap 2 ronde 4: adresgebaseerde broederdienst

## Context en herleiding

- Gecontroleerd startpunt: bestaande branch `codex/v05-stap2-ronde4-taakplichtdashboard`, HEAD `ddc829fa71361ddcad338e3285e62e5f315c2342`, schone werkboom.
- Integratiebaseline: `prototype-v0.5`; functioneel geaccepteerde releasebasis blijft v0.4 op `main`. Deze implementatie is v0.5-ontwikkeling, geen integrale functionele acceptatie.
- Bronhouder: Sportlink voor registraties; CKC voor beleid en functionele acceptatie; DVK leidt alleen verwachtingen af.
- Geaccepteerde eis in de actuele opdracht: expliciete beleidsherijking naar uitsluitend het geregistreerde adres voor B-05/B-06/B-07. Ouders, familierelatie, achternaam en contact-via-ouders bepalen de automatische uitkomst niet.
- Vastgesteld probleem in de startcode: `family_criteria` accepteert ouders naast adres; `_possible_family` gebruikt ontbrekende ouders; onbekende geboortedatums worden vóór adresvergelijking beoordeeld. Dit veroorzaakt beslissingen en onzekerheid zonder adresverband.
- Proportionele oplossing: bestaande afleiding en presenter aanpassen, adresnormalisatie consequent toepassen en synthetische regressies toevoegen. Geen nieuwe architectuur, opslag, migratie, historische reconstructie of uitzonderingsregistratie.

## Functionele formulering en implementatie

Kwalificerende minderjarige leden op hetzelfde volledige geregistreerde woonadres vormen automatisch één administratief huishouden. Verschillende volledige adressen vormen afzonderlijke huishoudens, ook bij identieke ouders. Binnen een huishouden blijven de bestaande oudste-kindregel, peildatum, leeftijdsgrenzen, lidmaatschapsvoorwaarden, overige vrijstellingen en onzekerheid bij gelijke geboortedatums gelden.

Adresvergelijking gebeurt vóór beoordeling van de geboortedatum van andere leden. Ontbrekende ouders veroorzaken geen onzekerheid. Een ontbrekend of conflicterend eigen adres bewijst geen taakplicht: adresgebonden vrijstellingen kunnen niet betrouwbaar worden uitgesloten. Bewezen vrijstellingen houden voorrang. Ontbrekende adressen van potentieel relevante andere leden kunnen nog gerichte onzekerheid veroorzaken; zij bewijzen geen huishouden.

Normalisatie blijft beperkt tot bestaande postcodeopschoning, buitenste spaties en hoofdletters in huisnummer/toevoeging. Geen parsing van samengestelde notaties of samenvoeging van verschillende toevoegingen. Importconflictcontrole gebruikt dezelfde normalisatie; oorspronkelijke provenance blijft behouden.

De gedetailleerde diagnose blijft beschikbaar en onderscheidt beoordeeld lid en ander relevant lid. Postcode, huisnummer en adresconflicten worden afzonderlijk toegelicht. Ontbrekende/ongeldige geboortedatum en gelijke geboortedatums binnen hetzelfde huishouden krijgen uitleg over de oudste-kindregel. Ouders leveren geen taakplichtdiagnose meer op. De bestaande bron- en controlediagnose en populatieselectie blijven behouden; echte bronconflicten blijven bronmeldingen.

## Gewijzigde bestanden en reden

| Bestand | Reden |
| --- | --- |
| `DVK-v0.5-herijkte-functionele-baseline-Ledendiensten.md` | Expliciete beleidsherijking B-05/B-06/B-07, consistente V-04 en adapteraanwijzing; reclamatie via Vrijwilligerscommissie/bestuur. |
| `dvk/member_duty.py` | Uitsluitend adrescriterium, adresfilter vóór geboortedatum, ontbrekend eigen adres onzeker, behoud bewezen vrijstellingen. |
| `dvk/real_data_import.py` | Hoofdletters in adresconflictcontrole consistent met canonieke sleutel. |
| `dvk/duty_control_presenter.py` | Adres- en geboortedatumdiagnose; vervallen ouderverklaringen verwijderd. |
| `tests/test_member_duty_v05.py` | Vervangen oudergebaseerde verwachtingen en synthetische dekking voor alle opdrachtgebonden adres-/contact-/leeftijdsscenario's. |
| `tests/test_family_diagnostics_dashboard_v05.py` | Nieuwe diagnoseverwachtingen, meerdere relevante oorzaken, geboortedatum uitsluitend binnen gedeeld huishouden, read-only UI. |
| `tests/test_duty_control_dashboard_v05.py` | Contactwaarde verandert overeenkomst/afwijking niet. |
| `tests/test_duty_population_dashboard_v05.py` | Synthetisch volledig adres voor selectiecases die een betrouwbare urenuitkomst verwachten. |
| `tests/test_hours_control_v05.py` | Synthetisch volledig adres voor urenvergelijkingscases; verwachtingen blijven behouden. |
| Dit opleverrapport | Herleiding, verificatie en resterende acceptatiegrenzen. |

Alle paden in deze tabel zijn relatief aan `code/Prototype`. Geaccepteerde C/W/I/R-fixtures zijn niet gewijzigd. Uitsluitend synthetische ontwikkeldata gebruikt; echte exports en lokale gebruikersdatabase niet gelezen of gewijzigd.

## Verificatie

Uitgevoerd vanuit `code/Prototype`, met de bestaande `.venv/bin/python`:

1. Baseline: `-m pytest -q tests/test_member_duty_v05.py tests/test_family_diagnostics_dashboard_v05.py tests/test_duty_control_dashboard_v05.py tests/test_duty_population_dashboard_v05.py` — **121 geslaagd, 0 overgeslagen, 0 mislukt**.
2. Definitieve gerichte suite: `-m pytest -q tests/test_member_duty_v05.py tests/test_family_diagnostics_dashboard_v05.py tests/test_duty_control_dashboard_v05.py tests/test_duty_population_dashboard_v05.py tests/test_hours_control_v05.py` — **191 geslaagd, 0 overgeslagen, 0 mislukt**. Dekt B-05/B-06/B-07, normalisatie/importconflicten, onzekerheid, diagnostiek/dashboard, B-02, selectie, uren en drie controleuitkomsten.
3. Definitieve volledige suite: `-m pytest -q` — **620 geslaagd, 0 overgeslagen, 0 mislukt**.
4. `git diff --check` — geslaagd.

Tussentijdse uitvoering: na codewijziging maar vóór aangepaste ontwikkeltests waren 104 tests geslaagd en 17 mislukt door vervallen verwachtingen en onvolledige synthetische adressen. Daarna 182 gerichte en 611 volledige tests geslaagd; na aanvullende regressies gelden bovenstaande definitieve aantallen. Enkele aanroepen hadden een verkeerd werkpad of gebruikten de niet op PATH aanwezige `pytest`; één run vanaf repositoryroot gaf vijf import-/collectiefouten. Alle controles zijn daarna vanuit het voorgeschreven prototypepad succesvol uitgevoerd.

CI is niet uitgevoerd: opdracht verbiedt push/PR/merge. Eén lokale commit; het exacte ID wordt bij oplevering gerapporteerd en is via de Git-historie van dit rapport te vinden.

## Resterende beperkingen en acceptatie

- `DVK-v0.5-stap2-ronde2-huishouden-gezin.md` beschrijft de eerdere ouder-/adresinterpretatie. `DVK-v0.5-gezinsdiagnose-specificatie.md` bevat eerdere ouderdiagnoses en teksten voor verschillende adressen. Deze eerdere iteratiedocumenten blijven historisch intact; voor de huidige regels gelden de herijkte baseline en dit rapport.
- Geen open technische regressies vastgesteld. Ontbrekende/conflicterende noodzakelijke adressen blijven bewust voorzichtig behandeld. Niet ondersteunde huisnummer-/toevoegingsnotaties worden niet geïnterpreteerd.
- Registratie van reclamatie-/uitzonderingsbesluiten blijft buiten scope. Beoordeling verloopt via Vrijwilligerscommissie en zo nodig bestuur; DVK neemt geen besluit.
- Johan/CKC moet dezelfde lokale exports met dezelfde peildatum/seizoen opnieuw beoordelen. Eerdere aantallen zijn context, geen testcriteria. Functionele acceptatie en integratie in `prototype-v0.5` zijn nog niet verleend.
