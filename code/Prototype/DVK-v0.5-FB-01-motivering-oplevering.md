# DVK v0.5 — Correctie FB-01: motivering bij één minderjarige

## Context en afbakening

Gecontroleerd startpunt: bestaande werkbranch `codex/v05-stap2-ronde4-taakplichtdashboard`, schone werkboom, exacte HEAD `a157f1ab8e7eb2faea76d015dfab4c47da88b6c5`. Integratiebranch is `prototype-v0.5`; de geaccepteerde releasebaseline blijft v0.4 op `main`. De herijkte functionele baseline beschrijft uitsluitend het volledige geregistreerde adres als criterium voor B-05/B-06/B-07. Sportlink houdt de bronregistraties; CKC bepaalt beleid en acceptatie.

Geaccepteerde eis uit de FB-01-opdracht: de oudste-kindmotivering verschijnt alleen bij meerdere kwalificerende minderjarigen op hetzelfde adres. Uren, taakplichtregels, selectie, vrijstellingsvoorrang, adresnormalisatie, bron- en controlediagnose en read-only gedrag blijven gelijk.

Vastgesteld feit: `derive_member_duties` kende in de taakplichtige eindtak iedere minderjarige de code `oldest_minor` toe. `present_controls` vertaalt die code rechtstreeks naar de misleidende tekst. De minimale oplossing verandert uitsluitend de keuze van deze motiveringscode nadat status en uren zijn bepaald. Er is geen nieuwe beslisregel voor taakplicht, afhankelijkheid, architectuur, opslag of migratie nodig.

## Wijzigingen

| Bestand (onder `code/Prototype`) | Reden |
| --- | --- |
| `dvk/member_duty.py` | Motivering `oldest_minor` alleen wanneer een andere actuele, spelende, niet-recreatieve minderjarige hetzelfde volledige adres heeft; anders bestaande `no_exemption_found`. Gebruikt bestaande relevantieset, leeftijden en adresvergelijking. |
| `tests/test_fb01_motivation_v05.py` | Negen synthetische scenario's: alleenstaand kwalificerend kind, twee kinderen, twee afgemelde oud-leden, verschillende achternamen, huishoudvrijstelling, verschillende adressen, niet-spelende adresgenoot, meerderjarige adresgenoot en persoonlijke vrijstelling. Controleert uren en dashboardtekst. |
| `tests/test_member_duty_v05.py` | Bestaande test met uitsluitend andere adressen verwacht nu de gewone motivering; de 10 uur en bronfeiten blijven gelijk. |
| Dit rapport | Herleiding, verificatie en acceptatiegrenzen. |

Bij meerdere kwalificerende minderjarigen blijft bij de oudste de bestaande motivering staan; de jongste houdt de vrijstelling met verwijzing naar de oudste. Bewezen persoonlijke/huishoudvrijstellingen blijven via de bestaande eerdere tak voorrang houden. Reeds afgemelde leden kunnen de nieuwe motiveringskeuze niet beïnvloeden. Ouders, achternaam en contact-via-ouders worden niet gebruikt.

## Verificatie

Alle pytest-opdrachten uitgevoerd vanuit `code/Prototype` met `.venv/bin/python`:

- Baseline: `-m pytest -q tests/test_member_duty_v05.py tests/test_duty_control_dashboard_v05.py tests/test_family_diagnostics_dashboard_v05.py`: **115 geslaagd, 0 overgeslagen, 0 mislukt**.
- Gericht na correctie: `-m pytest -q tests/test_fb01_motivation_v05.py tests/test_member_duty_v05.py tests/test_duty_control_dashboard_v05.py tests/test_family_diagnostics_dashboard_v05.py`: **124 geslaagd, 0 overgeslagen, 0 mislukt**.
- Volledige regressie: `-m pytest -q`: **629 geslaagd, 0 overgeslagen, 0 mislukt**.
- Expliciete vóór/na-controle: de afleiding uit de exacte uitgangscommit gelezen via `git show` en naast de gewijzigde afleiding uitgevoerd op dezelfde negen synthetische scenario's. Voor alle **18 ledenverwachtingen** zijn identiteit, status, verplichte uren, bronfeiten, peildatum, beleidsversie en afleidingssoort identiek. Alleen motiveringscodes kunnen verschillen.
- `git diff --check`: geslaagd.

Geen falende tests. Twee initiële leescommando's gebruikten een dubbel prototypepad en zijn met het juiste pad herhaald; dit had geen invloed op de tests.

Geen echte CKC-exports, persoonsgegevens of gebruikersdatabase gebruikt. Geaccepteerde historische fixtures, presenter, UI, bron- en controlediagnose, populatieselectie en adresnormalisatie zijn niet gewijzigd. Geen nieuwe afhankelijkheden.

## Opleverstatus

Eén lokale commit op de opgegeven werkbranch; exact ID wordt in de oplevermelding vermeld en is via Git terug te vinden. Geen push, PR, merge of wijziging aan `prototype-v0.5`. CI is daarom niet uitgevoerd. Geen resterende technische afwijking of nieuw functioneel/architecturaal beslispunt vastgesteld. Deze correctie is technisch geverifieerd; functionele acceptatie blijft bij Johan/CKC.
